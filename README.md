# QR Hub — Free QR Code Generator

Live at **[qrhub.tech](https://qrhub.tech)**

A fast, free, no-signup QR code generator. Enter a URL, adjust size and border, preview live, download as PNG.

## Project Structure

```
qr_code_generator/
├── frontend/               # Static site — deploy to Vercel
│   ├── index.html          # Main page (SEO, ads, tool, FAQ)
│   ├── privacy.html        # Privacy Policy
│   ├── terms.html          # Terms of Service
│   ├── sitemap.xml         # For Google Search Console
│   ├── robots.txt          # Crawler directives
│   └── vercel.json         # Vercel deployment config
└── api/                    # Cloud Function — deploy to GCP
    ├── main.py             # POST /generate endpoint
    └── requirements.txt
```

## Tech Stack

- **Frontend:** Static HTML/CSS/JS — hosted on Vercel
- **Backend:** Python 3, Google Cloud Functions (`functions-framework`, `qrcode`, `Pillow`)

## Local Development

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r api/requirements.txt

cd api
functions-framework --target qr_handler --debug
```

API available at `http://localhost:8080`.

## Deployment

CI/CD is handled by `.github/workflows/deploy.yml`. Pushing to `master` automatically deploys:
- changes under `frontend/` → Vercel
- changes under `api/` → Google Cloud Functions

### First-time setup

#### 1. Vercel

1. Import the repo into [vercel.com](https://vercel.com) — set root directory to `frontend/`
2. Add custom domain `qrhub.tech` in Vercel project settings
3. Run `vercel link` locally inside `frontend/` to generate `.vercel/project.json` — you'll need the org/project IDs for secrets
4. Add these to GitHub → Settings → Secrets → Actions:

| Secret | Where to find it |
|--------|-----------------|
| `VERCEL_TOKEN` | vercel.com → Account Settings → Tokens |
| `VERCEL_ORG_ID` | `.vercel/project.json` → `orgId` (after `vercel link`) |
| `VERCEL_PROJECT_ID` | `.vercel/project.json` → `projectId` |

#### 2. Google Cloud Functions (Workload Identity Federation — no long-lived keys)

```bash
# 1. Create a service account
gcloud iam service-accounts create github-actions \
  --display-name "GitHub Actions deployer"

# 2. Grant it Cloud Functions deployer permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.developer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# 3. Create a Workload Identity Pool
gcloud iam workload-identity-pools create github \
  --location=global \
  --display-name="GitHub Actions pool"

# 4. Create a provider inside the pool
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location=global \
  --workload-identity-pool=github \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='YOUR_GITHUB_USERNAME/YOUR_REPO_NAME'"

# 5. Bind the service account to the pool
gcloud iam service-accounts add-iam-policy-binding \
  github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/YOUR_PROJECT_NUMBER/locations/global/workloadIdentityPools/github/attribute.repository/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"
```

Then add these to GitHub Secrets:

| Secret | Value |
|--------|-------|
| `GCP_PROJECT_ID` | your GCP project ID |
| `GCP_SERVICE_ACCOUNT` | `github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com` |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `projects/YOUR_PROJECT_NUMBER/locations/global/workloadIdentityPools/github/providers/github-provider` |

After the first GCP deploy, copy the Cloud Function URL and update `API_URL` in `frontend/index.html`.

## After Deployment Checklist

- [ ] Update `API_URL` in `frontend/index.html` with the deployed Cloud Function URL
- [ ] Submit `sitemap.xml` to [Google Search Console](https://search.google.com/search-console)
- [ ] Apply for [Google AdSense](https://adsense.google.com) — replace ad placeholder divs with real ad units
- [ ] Uncomment the AdSense `<script>` tag in `index.html` and add your publisher ID

## API

### `POST /`

**Request body (JSON):**

| Field    | Type    | Range | Default | Description             |
|----------|---------|-------|---------|-------------------------|
| `url`    | string  | —     | —       | URL to encode (required)|
| `size`   | integer | 4–30  | 10      | Box size in pixels      |
| `border` | integer | 0–10  | 4       | Border width (in boxes) |

**Response:** `image/png`

## License

MIT — see [LICENSE](LICENSE)
