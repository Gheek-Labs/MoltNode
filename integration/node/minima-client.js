/**
 * Minima RPC Client for Node.js
 *
 * Safe, typed interface to a Minima node's RPC endpoint.
 * Normalizes responses so the default API path prevents common mistakes.
 *
 * @example
 * import { MinimaClient } from './minima-client.js';
 *
 * const client = new MinimaClient();
 * const bal = await client.balance();       // normalized, no 'total' trap
 * const status = await client.status();
 * const tx = await client.send('MxG08...', 1);
 */

class MinimaError extends Error {
  constructor(message) {
    super(message);
    this.name = 'MinimaError';
  }
}

class MinimaConnectionError extends Error {
  constructor(message) {
    super(message);
    this.name = 'MinimaConnectionError';
  }
}

class MinimaClient {
  /**
   * @param {Object} [options]
   * @param {string} [options.host='localhost']
   * @param {number} [options.port=9005]
   * @param {number} [options.retries=3]
   * @param {number} [options.retryDelay=1000] - Base retry delay in ms
   * @param {number} [options.timeout=30000] - Request timeout in ms
   */
  constructor({ host = 'localhost', port = 9005, retries = 3, retryDelay = 1000, timeout = 30000 } = {}) {
    this.baseUrl = `http://${host}:${port}`;
    this.retries = retries;
    this.retryDelay = retryDelay;
    this.timeout = timeout;
  }

  /**
   * Execute a raw RPC command.
   * @param {string} cmd - RPC command (e.g., "balance", "send address:MxG.. amount:1")
   * @returns {Promise<Object>} Full parsed JSON response
   * @throws {MinimaError} When status is false
   * @throws {MinimaConnectionError} When node is unreachable after retries
   */
  async command(cmd) {
    const encoded = encodeURIComponent(cmd);
    const url = `${this.baseUrl}/${encoded}`;

    let lastError;
    for (let attempt = 0; attempt < this.retries; attempt++) {
      try {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), this.timeout);

        const resp = await fetch(url, { signal: controller.signal });
        clearTimeout(timer);

        const text = await resp.text();
        const result = JSON.parse(text);

        if (!result.status) {
          throw new MinimaError(result.error || 'Unknown RPC error');
        }

        return result;
      } catch (e) {
        if (e instanceof MinimaError) throw e;
        lastError = e;
        if (attempt < this.retries - 1) {
          await sleep(this.retryDelay * (attempt + 1));
        }
      }
    }

    throw new MinimaConnectionError(
      `Failed to connect to ${this.baseUrl} after ${this.retries} attempts: ${lastError?.message}`
    );
  }

  /**
   * Get wallet balances with safe field naming.
   *
   * The dangerous 'total' field (token max supply) is moved to
   * supply.total so it cannot be confused with wallet balance.
   *
   * @param {Object} [options]
   * @param {string} [options.tokenid] - Optional token ID filter
   * @param {boolean} [options.tokenDetails=false] - Include rich token metadata
   * @returns {Promise<Array<{
   *   token: string|Object,
   *   tokenid: string,
   *   sendable: string,
   *   confirmed: string,
   *   unconfirmed: string,
   *   coins: string,
   *   supply: { total: string },
   *   details?: { decimals: number, scale: string, script: string, totalamount: string, created: string }
   * }>>}
   */
  async balance({ tokenid, tokenDetails = false } = {}) {
    const cmd = tokenDetails ? 'balance tokendetails:true' : 'balance';
    const result = await this.command(cmd);
    let entries = result.response || [];

    const normalized = entries.map(entry => {
      const item = {
        token: entry.token || '',
        tokenid: entry.tokenid || '',
        sendable: entry.sendable || '0',
        confirmed: entry.confirmed || '0',
        unconfirmed: entry.unconfirmed || '0',
        coins: entry.coins || '0',
        supply: {
          total: entry.total || '0',
        },
      };
      if (tokenDetails && entry.details) {
        item.details = entry.details;
      }
      return item;
    });

    if (tokenid) {
      return normalized.filter(b => b.tokenid === tokenid);
    }
    return normalized;
  }

  /**
   * List Non-Fungible Tokens (NFTs) in the wallet.
   * NFTs are tokens with decimals:0 (indivisible, quantity = whole units).
   * @returns {Promise<Array>} Same as balance() but only NFT entries
   */
  async nfts() {
    const balances = await this.balance({ tokenDetails: true });
    return balances.filter(b => b.details?.decimals === 0);
  }

  /**
   * Get a simple balance summary for one token.
   * @param {string} [tokenid='0x00'] - Token ID
   * @returns {Promise<{ sendable: number, confirmed: number, unconfirmed: number, coins: number }>}
   */
  async balanceSummary(tokenid = '0x00') {
    const balances = await this.balance({ tokenid });
    if (!balances.length) {
      return { sendable: 0, confirmed: 0, unconfirmed: 0, coins: 0 };
    }
    const b = balances[0];
    return {
      sendable: parseFloat(b.sendable) || 0,
      confirmed: parseFloat(b.confirmed) || 0,
      unconfirmed: parseFloat(b.unconfirmed) || 0,
      coins: parseInt(b.coins, 10) || 0,
    };
  }

  /**
   * Get node status with numeric fields parsed.
   * @returns {Promise<{
   *   version: string,
   *   chainHeight: number,
   *   block: number,
   *   locked: boolean,
   *   mempool: number,
   *   connections: number,
   *   uptime: string,
   *   blockTime: string,
   *   raw: Object
   * }>}
   */
  async status() {
    const result = await this.command('status');
    const resp = result.response || {};
    const chain = resp.chain || {};
    const txpow = resp.txpow || {};
    const network = resp.network || {};

    return {
      version: resp.version || '',
      chainHeight: safeInt(resp.length),
      block: safeInt(chain.block),
      locked: resp.locked || false,
      mempool: safeInt(txpow.mempool),
      connections: safeInt(network.connected),
      uptime: resp.uptime || '',
      blockTime: chain.time || '',
      raw: resp,
    };
  }

  /**
   * Send Minima or tokens to an address.
   * @param {string} address - Destination (MxG... or 0x...)
   * @param {number|string} amount - Amount to send
   * @param {Object} [options]
   * @param {string} [options.tokenid] - Token ID (default: native Minima)
   * @param {number} [options.split] - Split into N outputs (1-10)
   * @param {number|string} [options.burn] - Burn amount as fee
   * @returns {Promise<{ txpowid: string, explorerUrl: string, block: string, date: string, raw: Object }>}
   */
  async send(address, amount, { tokenid, split, burn } = {}) {
    let cmd = `send address:${address} amount:${amount}`;
    if (tokenid) cmd += ` tokenid:${tokenid}`;
    if (split) cmd += ` split:${split}`;
    if (burn) cmd += ` burn:${burn}`;

    const result = await this.command(cmd);
    const resp = result.response || {};
    const txpowid = resp.txpowid || '';

    return {
      txpowid,
      explorerUrl: `https://explorer.minima.global/transactions/${txpowid}`,
      block: resp.header?.block || '',
      date: resp.header?.date || '',
      raw: resp,
    };
  }

  /**
   * Hash data using Minima's Keccak-256 / SHA3.
   *
   * WARNING: This is a LOCAL operation. It does NOT write to the blockchain
   * and does NOT return a txpowid. To create an on-chain record, use
   * recordOnChain() instead.
   *
   * @param {string} data - String or 0x-prefixed hex data
   * @returns {Promise<{ input: string, data: string, type: string, hash: string }>}
   */
  async hash(data) {
    const result = await this.command(`hash data:${data}`);
    const resp = result.response || {};
    return {
      input: resp.input || '',
      data: resp.data || '',
      type: resp.type || '',
      hash: resp.hash || '',
    };
  }

  /**
   * Post data to the blockchain permanently via a self-send transaction.
   *
   * Records data as state variables in a transaction. Returns the txpowid
   * which is the on-chain proof, searchable on the explorer.
   *
   * State layout:
   *   <port> = data (your payload — string or hash)
   *   <port+1> = label (optional description, only if port < 255)
   *   255 = timestamp (ISO 8601 UTC, auto-generated)
   *   extraState entries override any of the above
   *
   * @param {string} data - String or 0x-prefixed hash to record on-chain
   * @param {Object} [options]
   * @param {string} [options.label] - Optional label/description
   * @param {number} [options.port=0] - State variable port for the data
   * @param {string|number} [options.burn] - Optional burn amount for priority fee
   * @param {Object} [options.extraState] - Additional state entries {key: value}
   * @returns {Promise<{ txpowid: string, explorerUrl: string, data: string, label: string, port: number, timestamp: string, block: string, date: string, raw: Object }>}
   */
  async recordOnChain(data, { label = '', port = 0, burn, extraState = {} } = {}) {
    const addr = await this.getaddress();
    const address = addr.miniaddress;
    const timestamp = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');

    const state = { [String(port)]: String(data), '255': timestamp };
    if (label && port < 255) state[String(port + 1)] = String(label);
    for (const [k, v] of Object.entries(extraState)) {
      state[String(k)] = String(v);
    }

    const stateJson = JSON.stringify(state);
    let cmd = `send address:${address} amount:0.000000001 state:${stateJson}`;
    if (burn) cmd += ` burn:${burn}`;

    const result = await this.command(cmd);
    const resp = result.response || {};
    const txpowid = resp.txpowid || '';

    return {
      txpowid,
      explorerUrl: `https://explorer.minima.global/transactions/${txpowid}`,
      data,
      label,
      port,
      timestamp,
      block: resp.header?.block || '',
      date: resp.header?.date || '',
      raw: resp,
    };
  }

  /**
   * Generate 256-bit cryptographic random value.
   * @returns {Promise<{ random: string, hashed: string, keycode: string, size: string, type: string }>}
   */
  async random() {
    const result = await this.command('random');
    const resp = result.response || {};
    return {
      random: resp.random || '',
      hashed: resp.hashed || '',
      keycode: resp.keycode || '',
      size: resp.size || '',
      type: resp.type || '',
    };
  }

  /**
   * List all tokens known to this node.
   * Note: In the tokens response, the name field is 'name' (not 'token' as in balance).
   * Note: decimals and scale are already integers from the node.
   * @returns {Promise<Array<{ tokenid: string, name: string, supplyTotal: string, decimals: number, scale: number }>>}
   */
  async tokens() {
    const result = await this.command('tokens');
    const entries = result.response || [];

    return entries.map(entry => {
      const nameField = entry.name ?? entry.token;
      const name = typeof nameField === 'string' ? nameField : (nameField?.name || String(nameField));

      return {
        tokenid: entry.tokenid || '',
        name,
        supplyTotal: entry.total || '0',
        decimals: safeInt(entry.decimals),
        scale: safeInt(entry.scale),
      };
    });
  }

  /**
   * Get the node's default receiving address.
   * @returns {Promise<{ address: string, miniaddress: string, publickey: string }>}
   */
  async getaddress() {
    const result = await this.command('getaddress');
    const resp = result.response || {};
    return {
      address: resp.address || '',
      miniaddress: resp.miniaddress || '',
      publickey: resp.publickey || '',
    };
  }

  /**
   * Get Maxima identity and contact details.
   * @returns {Promise<{ name: string, publickey: string, mxpublickey: string, staticmls: boolean, mls: string, p2pidentity: string, localidentity: string, contact: string, logs: boolean, poll: number }>}
   */
  async maximaInfo() {
    const result = await this.command('maxima action:info');
    const resp = result.response || {};
    return {
      name: resp.name || '',
      publickey: resp.publickey || '',
      mxpublickey: resp.mxpublickey || '',
      staticmls: resp.staticmls || false,
      mls: resp.mls || '',
      p2pidentity: resp.p2pidentity || '',
      localidentity: resp.localidentity || '',
      contact: resp.contact || '',
      logs: resp.logs || false,
      poll: resp.poll || 0,
    };
  }

  /**
   * List Maxima contacts.
   * @returns {Promise<Array<{ id: number, name: string, publickey: string, address: string, lastseen: string, samechain: boolean }>>}
   */
  async contacts() {
    const result = await this.command('maxcontacts action:list');
    const entries = result.response || [];

    return entries.map(entry => ({
      id: entry.id || 0,
      name: entry.extradata?.name || '',
      publickey: entry.publickey || '',
      address: entry.currentaddress || '',
      lastseen: entry.date || '',
      samechain: entry.samechain || false,
    }));
  }
}

/** @param {string|number} val */
function safeInt(val) {
  const n = parseInt(val, 10);
  return isNaN(n) ? 0 : n;
}

/** @param {number} ms */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export { MinimaClient, MinimaError, MinimaConnectionError };
