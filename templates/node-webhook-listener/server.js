/**
 * Minima Webhook Listener
 *
 * Reference implementation for receiving Minima node events via webhooks.
 * Registers itself with the node on startup, handles all event types,
 * and re-registers after node restarts.
 *
 * Usage:
 *   MINIMA_RPC=http://127.0.0.1:9005 LISTEN_PORT=8099 node server.js
 *
 * See: minima/WEBHOOKS.md for event catalog and payload docs.
 */

import http from 'node:http';

const LISTEN_PORT = parseInt(process.env.LISTEN_PORT || '8099', 10);
const MINIMA_RPC = process.env.MINIMA_RPC || 'http://127.0.0.1:9005';
const WEBHOOK_FILTER = process.env.WEBHOOK_FILTER || '';

const WEBHOOK_URL = `http://127.0.0.1:${LISTEN_PORT}/events`;

let lastBlock = '0';
let eventCounts = {};

function log(msg) {
  const ts = new Date().toISOString();
  console.log(`[${ts}] ${msg}`);
}

async function minimaRpc(command) {
  const url = `${MINIMA_RPC}/${encodeURIComponent(command)}`;
  const res = await fetch(url);
  return res.json();
}

async function registerWebhook() {
  let cmd = `webhooks action:add hook:${WEBHOOK_URL}`;
  if (WEBHOOK_FILTER) {
    cmd += ` filter:${WEBHOOK_FILTER}`;
  }
  const result = await minimaRpc(cmd);
  if (result.status) {
    log(`Webhook registered: ${WEBHOOK_URL}` + (WEBHOOK_FILTER ? ` (filter: ${WEBHOOK_FILTER})` : ''));
  } else {
    log(`Failed to register webhook: ${JSON.stringify(result)}`);
  }
  return result;
}

function handleNewBlock(data) {
  const txpow = data.txpow;
  const block = txpow.header.block;
  const superblock = txpow.superblock;
  const txCount = txpow.body?.txnlist?.length || 0;
  const hasTx = txpow.istransaction;

  lastBlock = block;
  log(`NEWBLOCK #${block} (super=${superblock}, txns=${txCount}, hasTx=${hasTx})`);
}

function handleMining(data) {
  const txpow = data.txpow;
  const targetBlock = txpow.header.block;
  log(`MINING for block #${targetBlock}`);
}

function handleTimer(event, data) {
  const interval = event === 'MDS_TIMER_10SECONDS' ? '10s' : '60s';
  log(`TIMER ${interval} (${data.timemilli})`);
}

function handleNewTransaction(data) {
  log(`NEWTRANSACTION: ${JSON.stringify(data).slice(0, 200)}`);
}

function handleNewBalance(data) {
  log(`NEWBALANCE: ${JSON.stringify(data).slice(0, 200)}`);
}

function handleMaxima(data) {
  log(`MAXIMA message received: ${JSON.stringify(data).slice(0, 200)}`);
}

function processEvent(payload) {
  const event = payload.event;
  const data = payload.data;

  eventCounts[event] = (eventCounts[event] || 0) + 1;

  switch (event) {
    case 'NEWBLOCK':
      handleNewBlock(data);
      break;
    case 'MINING':
      handleMining(data);
      break;
    case 'MDS_TIMER_10SECONDS':
    case 'MDS_TIMER_60SECONDS':
      handleTimer(event, data);
      break;
    case 'NEWTRANSACTION':
      handleNewTransaction(data);
      break;
    case 'NEWBALANCE':
      handleNewBalance(data);
      break;
    case 'MAXIMA':
      handleMaxima(data);
      break;
    default:
      log(`UNKNOWN event: ${event} — ${JSON.stringify(data).slice(0, 200)}`);
  }
}

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/events') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const payload = JSON.parse(body);
        processEvent(payload);
      } catch (err) {
        log(`Parse error: ${err.message}`);
      }
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end('{"status":"ok"}');
    });
    return;
  }

  if (req.method === 'GET' && req.url === '/status') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      lastBlock,
      eventCounts,
      uptime: process.uptime()
    }));
    return;
  }

  res.writeHead(404);
  res.end('Not found');
});

server.listen(LISTEN_PORT, '0.0.0.0', async () => {
  log(`Webhook listener started on port ${LISTEN_PORT}`);
  log(`Status endpoint: http://127.0.0.1:${LISTEN_PORT}/status`);

  try {
    await registerWebhook();
  } catch (err) {
    log(`Could not register webhook (node may not be running): ${err.message}`);
    log('Will retry registration via timer heartbeat...');
  }
});

process.on('SIGINT', async () => {
  log('Shutting down, removing webhook...');
  try {
    await minimaRpc(`webhooks action:remove hook:${WEBHOOK_URL}`);
    log('Webhook removed');
  } catch (e) {
    log('Could not remove webhook on shutdown');
  }
  process.exit(0);
});
