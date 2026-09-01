# Steganography Tool — Web Edition

Hide and reveal secret text messages inside PNG images using LSB
(Least Significant Bit) steganography — a Flask web app deployable on
Vercel with zero configuration.

## Project structure

```
.
├── index.py            # Flask app + routes (Vercel entrypoint)
├── stego_engine.py     # Core LSB encode/decode logic
├── templates/
│   └── index.html      # Web UI (encode / decode / about tabs)
├── cli.py              # Original command-line script (local use only)
├── requirements.txt
└── vercel.json          # Optional: sets function timeout
```

Vercel auto-detects the Flask `app` instance in `index.py` at the
project root — no custom build/route config needed.

## Deploy to Vercel

Push to GitHub, then import the repo at https://vercel.com/new.
Vercel detects Flask automatically and deploys.

Or via CLI:
```bash
npm i -g vercel
vercel --prod
```

## Run locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python index.py
```

Visit http://localhost:5000
