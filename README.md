# Ausome Seals Technology Website Starter

This is a professional full-stack starter website for **Ausome Seals Technology**, an industrial sealing product company serving steel production hydraulic gate systems.

## Tech Stack

- Frontend: React + Vite
- Backend: Flask
- API: REST endpoints for health check, products, and contact inquiry

## Project Structure

```text
ausome-seals-starter/
  frontend/
    src/App.jsx
    src/styles.css
    package.json
  backend/
    app/__init__.py
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

## Production Notes

Before real production use:

1. Replace placeholder contact information.
2. Add real product photos and product datasheets.
3. Save inquiries into PostgreSQL or MySQL instead of memory.
4. Add email notification through SMTP or SendGrid.
5. Add admin authentication before exposing `/api/admin/inquiries`.
6. Configure domain, SSL, SEO metadata, and analytics.


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
