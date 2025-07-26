from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse
import subprocess
import threading
from fastapi.staticfiles import StaticFiles

app = FastAPI()
#router = APIRouter(prefix="/dashboard")

#@app.get("/")
#def root():
#    return {"status": "FastAPI server running"}

@app.post("/run-benchtest")
def run_test():
    def target():
        subprocess.run(["python3", "BenchHost.py"])
    threading.Thread(target=target).start()
    return {"msg": "Bench test started"}

@app.get("/meta_stats.json")
def get_stats():
	return FileResponse("meta_stats.json")

app.mount("/", StaticFiles(directory="static/dashboard", html=True), name="dashboard")
