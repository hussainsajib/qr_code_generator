# QR Code Generator

A web-based QR code generator deployed as a Google Cloud Function. Enter a URL, adjust the size and border via sliders, preview the result live, and download as a PNG.

## Features

- Live preview with debounced updates
- Adjustable box size (4–30) and border width (0–10)
- One-click PNG download
- Deployed as a serverless Google Cloud Function

## Tech Stack

- **Runtime:** Python 3
- **Framework:** Google Cloud Functions (`functions-framework`)
- **QR generation:** `qrcode` + `Pillow`

## Local Development

### Prerequisites

- Python 3.9+
- [Google Cloud Functions Framework](https://github.com/GoogleCloudPlatform/functions-framework-python)

### Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r cloud_function/requirements.txt
```

### Run locally

```bash
cd cloud_function
functions-framework --target qr_handler --debug
```

Open `http://localhost:8080` in your browser.

## Deployment

Deploy to Google Cloud Functions:

```bash
gcloud functions deploy qr-code-generator \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --source cloud_function \
  --entry-point qr_handler
```

## API

### `GET /`

Returns the HTML UI.

### `POST /`

Generates a QR code image.

**Request body (JSON):**

| Field    | Type    | Range  | Description              |
|----------|---------|--------|--------------------------|
| `url`    | string  | —      | URL to encode            |
| `size`   | integer | 4–30   | Box size in pixels       |
| `border` | integer | 0–10   | Border width (in boxes)  |

**Response:** `image/png`

## License

MIT — see [LICENSE](LICENSE)
