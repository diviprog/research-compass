#!/usr/bin/env node
/**
 * Test auth API (signin/signup) without opening the browser.
 * Usage: node frontend/scripts/test-auth.mjs
 * Requires: backend running at VITE_API_URL or http://localhost:8000
 */

const API_BASE = process.env.VITE_API_URL || 'http://localhost:8000';
const BASE = `${API_BASE}/api`;

const testUser = {
  email: 'test@example.com',
  password: 'TestPass123',
  name: 'Test User',
};

async function request(method, path, body = null, token = null) {
  const url = `${BASE}${path}`;
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  return { ok: res.ok, status: res.status, data };
}

async function main() {
  console.log('Auth API test');
  console.log('Base URL:', BASE);
  console.log('');

  // Health
  try {
    const health = await fetch(`${API_BASE}/health`).then((r) => r.json());
    console.log('Backend health:', health.status);
  } catch (e) {
    console.error('Backend not reachable at', API_BASE, '-', e.message);
    process.exit(1);
  }

  // Sign in (test user from seed_test_user.py)
  console.log('\nSign in as', testUser.email, '...');
  const signin = await request('POST', '/auth/signin', {
    email: testUser.email,
    password: testUser.password,
  });

  if (signin.ok) {
    console.log('Sign in OK');
    console.log('  user:', signin.data.user?.name, signin.data.user?.email);
    const token = signin.data.access_token;
    console.log('  access_token length:', token?.length ?? 0);

    // GET /auth/me with token
    const me = await request('GET', '/auth/me', null, token);
    if (me.ok) {
      console.log('  GET /auth/me OK:', me.data.name);
    } else {
      console.log('  GET /auth/me failed:', me.status, me.data);
    }
  } else {
    console.log('Sign in failed:', signin.status, JSON.stringify(signin.data, null, 2));
    console.log('\nTip: Run "python backend/seed_test_user.py" to create the test user.');
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
