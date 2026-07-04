"""
Super Simple Test Server
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()

template_path = Path(__file__).parent / "templates" / "index.html"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page"""
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    else:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Customer Service Training Bot</title>
        </head>
        <body>
            <h1>Server is working!</h1>
            <p>Template file missing: index.html</p>
        </body>
        </html>
        """


@app.get("/api/test")
async def test():
    """Test endpoint"""
    return {"status": "ok", "message": "Server is working!"}


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("  Test Server")
    print("=" * 50)
    print(f"Template path: {template_path}")
    print(f"Template exists: {template_path.exists()}")
    print()
    print("Open browser at: http://localhost:8000")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)
