import io

import functions_framework
import qrcode
from qrcode.image.pil import PilImage

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>QR Code Generator</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f5f5f5;
      font-family: system-ui, sans-serif;
    }
    .card {
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 4px 24px rgba(0,0,0,.08);
      padding: 2rem;
      width: 100%;
      max-width: 420px;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }
    h1 { font-size: 1.4rem; font-weight: 600; color: #111; }
    label { font-size: .85rem; font-weight: 500; color: #374151; }
    input[type="url"] {
      width: 100%;
      padding: .65rem .85rem;
      border: 1.5px solid #d1d5db;
      border-radius: 8px;
      font-size: 1rem;
      outline: none;
      transition: border-color .15s;
    }
    input[type="url"]:focus { border-color: #6366f1; }
    .options {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: .75rem;
    }
    .option-group { display: flex; flex-direction: column; gap: .3rem; }
    .option-group input[type="range"] { width: 100%; accent-color: #6366f1; }
    .option-group .range-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: .5rem;
    }
    .option-group .range-row span {
      font-size: .85rem;
      font-weight: 600;
      color: #6366f1;
      min-width: 1.5rem;
      text-align: right;
    }
    /* preview box */
    .preview-box {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: .6rem;
      border: 1.5px dashed #d1d5db;
      border-radius: 10px;
      padding: 1.25rem;
      min-height: 200px;
      justify-content: center;
      transition: border-color .2s;
      position: relative;
    }
    .preview-box.has-image { border-style: solid; border-color: #e5e7eb; }
    .preview-box .placeholder {
      color: #9ca3af;
      font-size: .9rem;
      text-align: center;
    }
    .preview-box img {
      width: 200px;
      height: 200px;
      border-radius: 6px;
      transition: opacity .2s;
    }
    .preview-box img.loading { opacity: .35; }
    .spinner {
      display: none;
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 28px;
      height: 28px;
      border: 3px solid #e0e7ff;
      border-top-color: #6366f1;
      border-radius: 50%;
      animation: spin .7s linear infinite;
    }
    .preview-box.loading .spinner { display: block; }
    @keyframes spin { to { transform: translate(-50%,-50%) rotate(360deg); } }
    /* buttons row */
    .actions { display: flex; gap: .75rem; }
    button {
      flex: 1;
      padding: .65rem;
      background: #6366f1;
      color: #fff;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      transition: background .15s;
    }
    button:hover { background: #4f46e5; }
    button:disabled { background: #a5b4fc; cursor: not-allowed; }
    #download-btn {
      display: none;
      flex: 1;
      padding: .65rem;
      background: #f0fdf4;
      color: #16a34a;
      border: 1.5px solid #86efac;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 500;
      text-align: center;
      text-decoration: none;
      cursor: pointer;
      transition: background .15s;
    }
    #download-btn:hover { background: #dcfce7; }
    #error { color: #dc2626; font-size: .9rem; display: none; }
  </style>
</head>
<body>
  <div class="card">
    <h1>QR Code Generator</h1>

    <div>
      <label for="url">URL</label>
      <input id="url" type="url" placeholder="https://example.com" autocomplete="off" style="margin-top:.3rem" />
    </div>

    <div class="options">
      <div class="option-group">
        <label for="size">Box size</label>
        <div class="range-row">
          <input id="size" type="range" min="4" max="30" value="10" oninput="onSlider('size-val',this.value)" />
          <span id="size-val">10</span>
        </div>
      </div>
      <div class="option-group">
        <label for="border">Border</label>
        <div class="range-row">
          <input id="border" type="range" min="0" max="10" value="4" oninput="onSlider('border-val',this.value)" />
          <span id="border-val">4</span>
        </div>
      </div>
    </div>

    <!-- live preview -->
    <div id="preview-box" class="preview-box">
      <p class="placeholder" id="placeholder">Enter a URL to see a preview</p>
      <img id="qr" src="" alt="QR code" style="display:none" />
      <div class="spinner"></div>
    </div>

    <p id="error"></p>

    <div class="actions">
      <button id="btn" onclick="generate()">Generate</button>
      <a id="download-btn" download="qrcode.png">Download PNG</a>
    </div>
  </div>

  <script>
    let debounceTimer = null;
    let currentObjectUrl = null;

    function onSlider(valId, val) {
      document.getElementById(valId).textContent = val;
      schedulePreview();
    }

    function schedulePreview() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(preview, 500);
    }

    async function preview() {
      const url = document.getElementById('url').value.trim();
      if (!url) { clearPreview(); return; }
      await fetchQR(url, /* isPreview */ true);
    }

    async function generate() {
      const url = document.getElementById('url').value.trim();
      if (!url) { showError('Please enter a URL.'); return; }
      await fetchQR(url, /* isPreview */ false);
    }

    async function fetchQR(url, isPreview) {
      const btn      = document.getElementById('btn');
      const box      = document.getElementById('preview-box');
      const qrImg    = document.getElementById('qr');
      const errEl    = document.getElementById('error');
      const dlBtn    = document.getElementById('download-btn');
      const ph       = document.getElementById('placeholder');

      errEl.style.display = 'none';

      const size   = parseInt(document.getElementById('size').value, 10);
      const border = parseInt(document.getElementById('border').value, 10);

      // show loading state
      box.classList.add('loading');
      if (qrImg.src) qrImg.classList.add('loading');
      if (!isPreview) { btn.disabled = true; btn.textContent = 'Generating…'; }

      try {
        const res = await fetch('', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url, size, border }),
        });
        if (!res.ok) throw new Error(await res.text() || res.statusText);

        const blob = await res.blob();
        if (currentObjectUrl) URL.revokeObjectURL(currentObjectUrl);
        currentObjectUrl = URL.createObjectURL(blob);

        qrImg.src = currentObjectUrl;
        qrImg.style.display = 'block';
        qrImg.classList.remove('loading');
        ph.style.display = 'none';
        box.classList.add('has-image');

        dlBtn.href = currentObjectUrl;
        dlBtn.style.display = 'block';
      } catch (e) {
        showError(e.message);
      } finally {
        box.classList.remove('loading');
        if (!isPreview) { btn.disabled = false; btn.textContent = 'Generate'; }
      }
    }

    function clearPreview() {
      const qrImg = document.getElementById('qr');
      const box   = document.getElementById('preview-box');
      const ph    = document.getElementById('placeholder');
      const dl    = document.getElementById('download-btn');
      qrImg.src = '';
      qrImg.style.display = 'none';
      ph.style.display = 'block';
      box.classList.remove('has-image');
      dl.style.display = 'none';
    }

    function showError(msg) {
      const el = document.getElementById('error');
      el.textContent = msg;
      el.style.display = 'block';
    }

    document.getElementById('url').addEventListener('input', schedulePreview);
    document.getElementById('url').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { clearTimeout(debounceTimer); generate(); }
    });
  </script>
</body>
</html>"""


@functions_framework.http
def qr_handler(request):
    if request.method == "GET":
        return (HTML, 200, {"Content-Type": "text/html; charset=utf-8"})

    if request.method == "POST":
        try:
            body = request.get_json(silent=True) or {}
            url = (body.get("url") or "").strip()
            if not url:
                return ("Missing 'url' in request body.", 400)

            box_size = int(body.get("size", 10))
            border   = int(body.get("border", 4))
            box_size = max(4, min(box_size, 30))
            border   = max(0, min(border, 10))

            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=box_size,
                border=border,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(image_factory=PilImage).get_image()

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            return (buf.read(), 200, {"Content-Type": "image/png"})

        except Exception as exc:
            return (str(exc), 500)

    return ("Method not allowed.", 405)
