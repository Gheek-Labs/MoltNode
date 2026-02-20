/**
 * Minima Node Web Dashboard
 *
 * Reference implementation showing correct 3-balance display.
 * Uses the Minima integration kit to prevent accidental misuse of 'total'.
 *
 * Usage:
 *   1. Copy this template to your project
 *   2. Copy ../../integration/node/minima-client.js alongside it
 *   3. npm install express
 *   4. node server.js
 *   5. Open http://localhost:3000
 */

import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { MinimaClient } from '../../integration/node/minima-client.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const client = new MinimaClient();
const PORT = process.env.DASHBOARD_PORT || 3000;

app.use(express.static(join(__dirname, 'public')));

app.get('/api/balance', async (req, res) => {
  try {
    const balances = await client.balance();
    res.json({ ok: true, balances });
  } catch (e) {
    res.json({ ok: false, error: e.message });
  }
});

app.get('/api/status', async (req, res) => {
  try {
    const status = await client.status();
    res.json({ ok: true, status });
  } catch (e) {
    res.json({ ok: false, error: e.message });
  }
});

app.get('/api/contacts', async (req, res) => {
  try {
    const contacts = await client.contacts();
    res.json({ ok: true, contacts });
  } catch (e) {
    res.json({ ok: false, error: e.message });
  }
});

app.get('/api/address', async (req, res) => {
  try {
    const address = await client.getaddress();
    res.json({ ok: true, address });
  } catch (e) {
    res.json({ ok: false, error: e.message });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Dashboard running on http://localhost:${PORT}`);
});
