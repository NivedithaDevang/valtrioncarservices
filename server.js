// Basic Express server to simulate Cloudflare Pages Functions locally
import express from 'express';
import { onRequest as helloHandler } from './functions/api/hello.js';

const app = express();
const port = process.env.PORT || 8787;

app.get('/api/hello', async (req, res) => {
  const response = await helloHandler({ request: req });
  const text = await response.text();
  res.set('content-type', response.headers.get('content-type'));
  res.status(response.status).send(text);
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
