from fastapi import FastAPI, APIRouter
import subprocess
import threading
from fastapi.staticfiles import StaticFiles

app = FastAPI()
router = APIRouter(prefix="/dashboard")
app.mount("/dashboard", StaticFiles(directory="static/dashboard", html=True), name="dashboard")

@app.get("/")
def root():
    return {"status": "FastAPI server running"}

@router.post("/run-benchtest")
def run_test():
    def target():
        subprocess.run(["python3", "BenchHost.py"])
    threading.Thread(target=target).start()
    return {"msg": "Bench test started"}

app.include_router(router)
