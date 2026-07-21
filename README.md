# Ausome Seals Website

Bilingual company website for **Ausome Seals**, focused on custom oil seals and rubber sealing products for steel mills, heavy machinery, hydraulic systems, and demanding industrial equipment.

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI + Uvicorn
- API: REST endpoints for health check, products, contact inquiry, and chat
- AI: provider-agnostic chat service skeleton with DeepSeek and a local stub provider

## Project Structure

```text
Ausome/
  frontend/
    src/App.jsx
    src/styles.css
    package.json
  backend/
    app/main.py
    app/api/
    app/ai/
    app/models/
    run.py
    requirements.txt
```

## Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Backend runs at:

```text
http://localhost:5000
```

Test:

```text
http://localhost:5000/api/health
```

Interactive API documentation:

```text
http://localhost:5000/docs
```

## Minimal Chat API

The chat service supports DeepSeek in production and a local `stub` provider for
offline development and tests. The regular endpoint returns one JSON response.

```http
POST /api/chat
Content-Type: application/json

{
  "conversation_id": "optional-client-conversation-id",
  "messages": [
    {"role": "user", "content": "How do I choose an oil seal?"}
  ]
}
```

For incremental output, send the same payload to `POST /api/chat/stream`. The
response uses Server-Sent Events with `meta`, `delta`, `done`, and `error` events.

Configure the provider in `backend/.env`:

```env
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_MODEL=deepseek-v4-pro
```

The backend separates the public chat API, request/response models, AI service,
and provider implementation so a production provider can be added without
changing the frontend API contract.

## PDF Knowledge Base (RAG)

RAG is enabled by default when `AI_PROVIDER=deepseek`. Knowledge PDFs are grouped by filename:

- `Ausome*.pdf`: Ausome company information, products, specifications, and model questions.
- `Oilseal*.pdf` or `Oilseals*.pdf`: general oil-seal principles, materials, installation, selection, and failure questions.

The service searches `backend/knowledge`, the project-level `knowledge` folder, and then `backend/tests/knowledge`. Override the location when needed:

```env
RAG_ENABLED=true
RAG_KNOWLEDGE_DIR=knowledge
RAG_RESULT_LIMIT=5
```

The first RAG request extracts the PDFs and writes a local cache to `backend/.cache/rag-index.json`. Later starts reuse the cache until a PDF changes. Answers receive only documents from the selected knowledge group and are instructed to cite the PDF filename and page number.

The current Ausome Chinese catalog is image-only, so searchable product facts come from its English counterpart. The Chinese and English general oil-seal references both contain searchable text.
## Contact Form Email

The contact form sends every inquiry to:

```text
support@ausomeseals.com
```

Copy `backend/.env.example` to `backend/.env`, then fill in the Resend sender settings:

```env
CONTACT_TO_EMAIL=support@ausomeseals.com
RESEND_API_KEY=re_your_api_key
RESEND_FROM_EMAIL=Ausome Seals <onboarding@resend.dev>
```

For Railway, Resend is recommended because it sends through HTTPS instead of blocked SMTP ports. If you verify your own domain in Resend, set `RESEND_FROM_EMAIL` to an address on that domain.

## Run Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

## Frontend Environment Variable

Create `frontend/.env` if backend is not local:

```env
VITE_API_BASE=http://localhost:5000
```

For Railway or other deployment, set:

```env
VITE_API_BASE=https://your-backend-domain.up.railway.app
```

## Railway Deployment Checklist

If frontend and backend are deployed as separate Railway services, the frontend must use the backend's public domain.

Backend service variables:

```env
CONTACT_TO_EMAIL=support@ausomeseals.com
RESEND_API_KEY=re_your_api_key
RESEND_FROM_EMAIL=Ausome Seals <onboarding@resend.dev>
FRONTEND_ORIGIN=https://your-frontend-domain
```

Frontend service variables:

```env
VITE_API_BASE=https://your-backend-domain.up.railway.app
```

After changing `VITE_API_BASE`, redeploy the frontend service. Vite reads this value during build, so changing it after the build does not update the already-built JavaScript.

Check the backend in a browser:

```text
https://your-backend-domain.up.railway.app/api/health
```

It should return a small JSON response with `"status": "ok"`.

## Production Notes

Before production deployment:

1. Configure Resend or SMTP credentials and a strict FRONTEND_ORIGIN.
2. Use Redis for RATELIMIT_STORAGE_URI when running multiple backend instances.
3. Run the backend tests and frontend production build before deployment.
4. Monitor email delivery, rate-limit events, domain SSL, and Search Console indexing.


## Logo Update

The frontend now includes the official Ausome logo in:

- Header
- Hero section
- Footer

Logo file path:

```text
frontend/src/assets/logo.png
```

Main brand blue used in the UI:

```text
#234F9A
```
"# Ausome-Seals" 
