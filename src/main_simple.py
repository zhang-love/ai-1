"""
客服培训机器人 - 简化版本
"""
import sys
from pathlib import Path

src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

templates = Jinja2Templates(directory=str(src_dir / "templates"))

static_dir = src_dir / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/hello")
async def hello():
    """Test endpoint"""
    return {"message": "Hello! Server is working!", "status": "ok"}


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("  Customer Service Training Bot")
    print("=" * 50)
    print()
    print("Starting server...")
    print()
    print("  Open your browser and go to:")
    print("  http://localhost:8000")
    print()
    print("  Or try:")
    print("  http://127.0.0.1:8000")
    print()
    print("=" * 50)
    print()

    try:
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except Exception as e:
        print()
        print(f"ERROR: {e}")
        print()
        print("Trying port 8001...")
        print("Open http://localhost:8001")
        try:
            uvicorn.run(app, host="127.0.0.1", port=8001)
        except Exception as e2:
            print()
            print(f"ERROR: {e2}")
            print()
            input("Press Enter to exit...")
