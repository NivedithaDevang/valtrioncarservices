Vercel deployment options for Valtrion

Overview
- Your project is a Flask + SocketIO app. Vercel is a serverless platform and does not support long-lived SocketIO connections or running a persistent Flask server.
- Two practical approaches:
  1) Recommended: Host the Python backend on Railway/Render/Fly and deploy frontend (static) to Vercel. Keep SocketIO on the backend-host.
  2) Advanced: Re-implement HTTP API endpoints as serverless functions on Vercel (Node.js or Python) and remove SocketIO.

Quick Option 1 — Frontend on Vercel, backend elsewhere (recommended)
1. Deploy backend to Railway (or Render) using the provided `Dockerfile`. Set required env vars (`DATABASE_URL`, `SECRET_KEY`, mail creds, etc.).
2. Expose backend URL (e.g., `https://valtrion-backend.fly.dev`).
3. Prepare the frontend as static files under `public/` (copy or render your templates to static HTML). Ensure frontend JS uses the backend URL for API calls and sockets.
4. Use `vercel_static.json` (provided) as a template. Rename to `vercel.json` if you want Vercel to treat the repo as static + Node API.
5. Deploy to Vercel:

```bash
npm i -g vercel
vercel login
vercel --prod
```

Notes:
- SocketIO must remain hosted on the backend (Railway). Vercel will serve static site and optional lightweight API routes.
- Set CORS and API base URL in frontend to allow cross-origin calls to your backend.

Quick Option 2 — Port APIs to Vercel functions (not recommended if you need SocketIO)
1. Remove SocketIO or migrate to an alternate solution (e.g., Pusher, WebSockets on a separate host).
2. Create serverless API endpoints in `api/` (Node.js recommended). Example included: `api/hello.js`.
3. Move any DB calls to use cloud DB (Postgres) via `DATABASE_URL` env var.
4. Update `vercel.json` (see `vercel_static.json` for example) and deploy using `vercel --prod`.

Example: Test the included demo route locally
- Install Vercel CLI and run:

```bash
vercel dev
# then open http://localhost:3000/api/hello
```

Environment variables you must set when deploying backend elsewhere
- `DATABASE_URL` (Postgres connection)
- `SECRET_KEY` (Flask secret)
- `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_SERVER`, `MAIL_PORT` (if using email)
- `TWILIO_*`, `RAZORPAY_*`, etc. depending on features
- `RAZORPAY_*`, etc. depending on features

If you want, I can:
- Add proxy API wrappers in `api/` for a subset of your Flask endpoints so you can migrate incrementally.
- Create a `Procfile` and GitHub Actions workflow to build and push your Docker image to Railway or Docker Hub.
- Help render your Jinja templates to static HTML suitable for Vercel.
