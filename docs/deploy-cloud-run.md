# Deploy the Nimbus agent to Cloud Run

Requirements: a Google Cloud project with billing, the `gcloud` CLI, and your API key.

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com
```

## 1. Store the API key in Secret Manager

The key goes into Secret Manager, never into the image or the command line history:

```bash
printf "API key: "; read -rs KEY && printf "%s" "$KEY" | \
  gcloud secrets create google-api-key --data-file=- && unset KEY

# Allow the Cloud Run runtime account (default compute account) to read it.
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding google-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role=roles/secretmanager.secretAccessor
```

## 2. Stage a self-contained agent folder

`adk deploy cloud_run` uploads only the agent folder. The agent imports the
`helpdesk` package from `src/`, so bundle it next to the agent and put that
folder on the import path. Run from the repository root:

```bash
STAGE="$(mktemp -d)/nimbus_support"
mkdir -p "$STAGE"
cp agents/m06_multiagent_solution/agent.py "$STAGE/"
rsync -a --exclude __pycache__ src/helpdesk "$STAGE/"
cat > "$STAGE/__init__.py" <<'EOF'
import os
import sys

# Make the bundled helpdesk package importable inside the container.
sys.path.insert(0, os.path.dirname(__file__))

from . import agent  # noqa: E402,F401
EOF
```

The folder name (`nimbus_support`) becomes the app name in the web UI.
Do not put a `.env` file into this folder.

## 3. Deploy with the ADK web UI

```bash
uv run adk deploy cloud_run \
  --project YOUR_PROJECT_ID \
  --region europe-west3 \
  --service_name nimbus-support \
  --with_ui \
  --env GOOGLE_GENAI_USE_ENTERPRISE=0 \
  "$STAGE" \
  -- --update-secrets=GOOGLE_API_KEY=google-api-key:latest
```

- `--env GOOGLE_GENAI_USE_ENTERPRISE=0` is required: by default ADK sets it to `1`,
  which switches the model calls to Vertex AI instead of your API key.
- Everything after `--` is passed to `gcloud run deploy`. ADK sets `--source`,
  `--project`, `--region`, `--port` and `--update-env-vars` itself; do not repeat them there.
- `gcloud` asks whether to allow unauthenticated access. Answering yes makes the
  service public, and every visitor spends your key. Add `--no-allow-unauthenticated`
  after `--` to keep it private, then open the UI through an authenticated local proxy:
  `gcloud run services proxy nimbus-support --region europe-west3` (serves on http://localhost:8080).

## 4. Clean up

Delete the service after the exercise to avoid costs:

```bash
gcloud run services delete nimbus-support --region europe-west3
gcloud secrets delete google-api-key
rm -rf "$(dirname "$STAGE")"   # the staging copy (same shell session as step 2)
```
