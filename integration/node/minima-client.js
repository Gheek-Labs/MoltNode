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
   * @param {string} [tokenid] - Optional token ID filter
   * @returns {Promise<Array<{
   *   token: string,
   *   tokenid: string,
   *   sendable: string,
   *   confirmed: string,
   *   unconfirmed: string,
   *   coins: string,
   *   supply: { total: string }
   * }>>}
   */
  async balance(tokenid) {
    const result = await this.command('balance');
    let entries = result.response || [];

    const normalized = entries.map(entry => ({
      token: entry.token || '',
      tokenid: entry.tokenid || '',
      sendable: entry.sendable || '0',
      confirmed: entry.confirmed || '0',
      unconfirmed: entry.unconfirmed || '0',
      coins: entry.coins || '0',
      supply: {
        total: entry.total || '0',
      },
    }));

    if (tokenid) {
      return normalized.filter(b => b.tokenid === tokenid);
    }
    return normalized;
  }

  /**
   * Get a simple balance summary for one token.
   * @param {string} [tokenid='0x00'] - Token ID
   * @returns {Promise<{ sendable: number, confirmed: number, unconfirmed: number, coins: number }>}
   */
  async balanceSummary(tokenid = '0x00') {
    const balances = await this.balance(tokenid);
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
   *   devices: number,
   *   mempool: number,
   *   uptime: string,
   *   raw: Object
   * }>}
   */
  async status() {
    const result = await this.command('status');
    const resp = result.response || {};
    const chain = resp.chain || {};
    const txpow = resp.txpow || {};

    return {
      version: resp.version || '',
      chainHeight: safeInt(resp.length),
      block: safeInt(chain.block),
      devices: safeInt(resp.devices),
      mempool: safeInt(txpow.mempool),
      uptime: chain.date || '',
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
   * Hash data using Minima's Keccak-256.
   * @param {string} data - String or 0x-prefixed hex data
   * @returns {Promise<{ input: string, hash: string }>}
   */
  async hash(data) {
    const result = await this.command(`hash data:${data}`);
    const resp = result.response || {};
    return {
      input: resp.input || '',
      hash: resp.hash || '',
    };
  }

  /**
   * Generate 256-bit cryptographic random value.
   * @returns {Promise<string>} 0x-prefixed random hex
   */
  async random() {
    const result = await this.command('random');
    return result.response?.random || '';
  }

  /**
   * List all tokens known to this node.
   * @returns {Promise<Array<{ tokenid: string, name: string, supplyTotal: string, decimals: number, scale: number }>>}
   */
  async tokens() {
    const result = await this.command('tokens');
    const entries = result.response || [];

    return entries.map(entry => {
      const token = entry.token;
      const name = typeof token === 'string' ? token : (token?.name || String(token));

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
   * @returns {Promise<{ name: string, publickey: string, mls: string, p2pidentity: string, localidentity: string, contact: string }>}
   */
  async maximaInfo() {
    const result = await this.command('maxima action:info');
    const resp = result.response || {};
    return {
      name: resp.name || '',
      publickey: resp.publickey || '',
      mls: resp.mls || '',
      p2pidentity: resp.p2pidentity || '',
      localidentity: resp.localidentity || '',
      contact: resp.contact || '',
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
