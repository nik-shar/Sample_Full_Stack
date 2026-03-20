# Vercel Deployment Guide

This project is easiest to deploy as two separate Vercel projects:

1. backend
2. frontend

## Backend project

Set the Vercel project root directory to:

```text
backend
```

### Why `backend/index.py` exists

Vercel's Python runtime looks for a Python entry file from the project root.
This project now includes:

```text
backend/index.py
```

That file re-exports the FastAPI app from:

```text
backend/app/main.py
```

### Backend environment variables

Create this environment variable in Vercel:

```text
CORS_ALLOWED_ORIGINS=https://your-frontend-project.vercel.app
```

If you want to allow multiple origins, use a comma-separated list:

```text
CORS_ALLOWED_ORIGINS=https://your-frontend-project.vercel.app,https://another-origin.example
```

If you also want Vercel preview frontend deployments to work without updating
the backend on every preview URL, add:

```text
CORS_ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

Use that only if you want to allow Vercel preview origins broadly.

### Backend deploy steps

1. Create a new Vercel project.
2. Import this repository.
3. Set the root directory to `backend`.
4. Add the `CORS_ALLOWED_ORIGINS` environment variable.
5. Deploy.
6. Copy the generated backend URL.

## Frontend project

Set the Vercel project root directory to:

```text
frontend
```

### Why `VITE_API_BASE_URL` exists

The frontend should not hardcode the backend URL. It now reads:

```text
VITE_API_BASE_URL
```

from the environment.

### Frontend environment variables

Create this environment variable in Vercel:

```text
VITE_API_BASE_URL=https://your-backend-project.vercel.app
```

The frontend no longer falls back to `localhost` in production. If this
variable is missing in a deployed environment, requests will fail fast with a
clear configuration error instead of calling the wrong host.

### Frontend deploy steps

1. Create a second Vercel project.
2. Import this repository again.
3. Set the root directory to `frontend`.
4. Add the `VITE_API_BASE_URL` environment variable using your deployed backend URL.
5. Deploy.

## Recommended order

1. Deploy backend first.
2. Copy backend URL.
3. Set `VITE_API_BASE_URL` in the frontend project.
4. Deploy frontend.
5. Update backend `CORS_ALLOWED_ORIGINS` to the final frontend URL if needed.
6. Redeploy backend if you changed backend environment variables.
