# Flask PDF API

Minimal Flask app that generates a PDF dynamically using ReportLab.

## Files

- `app.py` - Minimal Flask application with `/` and `/pdf` endpoints.
- `requirements.txt` - Python dependencies.
- `.gitignore` - Common ignores.

## Usage

1. Create and activate a virtual environment (optional but recommended):

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Run the app:

```powershell
python app.py
```

4. Open a browser and visit `http://127.0.0.1:5000/pdf` to download the generated PDF.

## Notes

- The app uses ReportLab to draw a simple PDF. Modify `app.py` to change contents.
