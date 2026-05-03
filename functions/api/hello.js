export async function onRequest(context) {
  return new Response('Hello from Cloudflare Pages Functions!', {
    headers: { 'content-type': 'text/plain' },
  });
}
