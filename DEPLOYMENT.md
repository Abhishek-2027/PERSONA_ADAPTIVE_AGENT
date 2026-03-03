# Deployment Guide

## Local Development

For local development, the app uses `http://localhost:8000` by default.

1. Start the FastAPI backend:
```bash
python -m uvicorn app.main:app --reload
```

2. In another terminal, start Streamlit:
```bash
streamlit run demo/streamlit_app.py
```

## Streamlit Cloud Deployment

### Step 1: Deploy FastAPI Backend

You need to deploy your FastAPI backend to a cloud service. Options include:

#### Option A: Railway (Recommended - Easy)
1. Go to [railway.app](https://railway.app)
2. Create a new project and connect your GitHub repo
3. Add a Procfile:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
4. Copy your deployed API URL (e.g., `https://your-app.railway.app`)

#### Option B: Render
1. Go to [render.com](https://render.com)
2. Create a new Web Service
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
4. Copy your deployed API URL

#### Option C: Heroku
1. Install Heroku CLI
2. Deploy using: `git push heroku main`
3. Copy your deployed API URL

#### Option D: Google Cloud Run
1. Push to Google Cloud Registry
2. Deploy to Cloud Run
3. Copy your service URL

### Step 2: Update Streamlit Secrets

1. Go to [streamlit.io](https://streamlit.io) and create an account
2. Create a new app pointing to your GitHub repo (`demo/streamlit_app.py`)
3. After deployment, click on your app settings ⚙️
4. Go to **Secrets** section
5. Add your secret:
```toml
API_URL = "https://your-deployed-api-url.com"
```

**Example:**
```toml
API_URL = "https://persona-agent-api.railway.app"
```

### Step 3: Redeploy

Once you've added the secret, Streamlit Cloud will automatically redeploy your app with the new environment variable.

## Environment Variables

The app uses these environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `API_URL` | `http://localhost:8000` | URL of the FastAPI backend |
| `APP_NAME` | `Persona Adaptive Agent` | App name |
| `DEBUG` | `True` | Debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama LLM service URL |
| `OLLAMA_MODEL` | `phi` | Ollama model to use |

## Troubleshooting

### "Cannot reach API at http://localhost:8000"
- Ensure your FastAPI backend is deployed to a cloud service
- Update the `API_URL` secret in Streamlit Cloud settings
- Check that your API endpoint is accessible from the internet
- Verify CORS is enabled in your FastAPI app

### API Connection Issues
1. Check if the API URL is correct in Streamlit secrets
2. Verify your API service is running and reachable
3. Check API logs for errors
4. Test the API endpoint directly: `curl https://your-api-url/health`

### Local Errors but Cloud Works Fine
- Make sure FastAPI backend is deployed
- The `.env` file with `API_URL=http://localhost:8000` is for local development only
- In Streamlit Cloud, the `API_URL` secret overrides the `.env` file

## Testing Your Deployment

1. Go to your Streamlit Cloud app URL
2. Check the sidebar for "✅ Connected to API" message
3. Send a test message to verify the backend is working

## Next Steps

1. Deploy your FastAPI backend to a cloud service
2. Add the API URL to Streamlit Cloud secrets
3. Test the connection in Streamlit Cloud
4. Monitor logs for any issues
