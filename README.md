# Ausome Seals Website

Bilingual company website for **Ausome Seals**, focused on custom oil seals and rubber sealing products for steel mills, heavy machinery, hydraulic systems, and demanding industrial equipment.

## Tech Stack

- Frontend: React + Vite
- Backend: Flask
- API: REST endpoints for health check, products, and contact inquiry

## Project Structure

```text
Ausome/
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
