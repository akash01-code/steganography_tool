# Steganography Tool — Web Edition

Hide and reveal secret text messages inside PNG images using LSB
(Least Significant Bit) steganography, now running as a Flask web app
deployable on Vercel.

## Why the GUI was replaced

Your original `app_gui.py` used **Tkinter**, a desktop GUI toolkit that
needs a local display — it cannot run on Vercel's serverless functions.
This project keeps your exact encode/decode logic (`stego_engine.py`,
untouched) and adds a Flask web app + browser UI on top, so the same
tool now runs anywhere.

## Project structure

```
.
├── api/
│   ├── index.py           # Flask app + API routes (Vercel entrypoint)
│   ├── stego_engine.py    # Core LSB encode/decode logic (your original)
│   └── templates/
│       └── index.html     # Web UI (encode / decode / about tabs)
├── cli.py                 # Your original command-line script (local use only)
├── requirements.txt       # Flask + Pillow
├── vercel.json            # Vercel build/route config
└── .vercelignore
```

Everything runs **in-memory** — no uploaded images or outputs are ever
written to disk on the server.

## Deploy to Vercel

**Option A — Vercel dashboard**
1. Push this folder to a GitHub repo.
2. Go to [vercel.com/new](https://vercel.com/new) and import the repo.
3. Vercel auto-detects `vercel.json` and the Python runtime — click **Deploy**.

**Option B — Vercel CLI**
```bash
npm i -g vercel
cd stego-vercel
vercel        # follow prompts, deploys a preview
vercel --prod # deploy to production
```

No environment variables or extra configuration needed.

## Run locally

```bash
cd stego-vercel
python -m venv venv && source venv/bin/activate   # optional
pip install -r requirements.txt
python api/index.py
```

Visit `http://localhost:5000`.

## API endpoints

| Method | Path            | Body (multipart/form-data)      | Returns                          |
|--------|-----------------|----------------------------------|-----------------------------------|
| POST   | `/api/capacity` | `image`                          | `{ "capacity": <max chars> }`     |
| POST   | `/api/encode`   | `image`, `message`                | PNG file download + `X-Stats` header |
| POST   | `/api/decode`   | `image`                          | `{ "message": "..." }`            |

## Notes

- Always use **PNG** carrier images — JPEG's lossy compression destroys
  hidden data (same rule as your original tool).
- Upload limit is 10 MB per image (adjustable in `api/index.py` via
  `MAX_CONTENT_LENGTH`).
- Vercel's free tier serverless functions have execution/time limits;
  very large images may be slow to process pixel-by-pixel in Python.
