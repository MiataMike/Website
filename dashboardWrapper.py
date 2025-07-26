from fastapi import FastAPI
import subprocess
import threading

app = FastAPI()

@app.get("/")
def root():
    return {"status": "FastAPI server running"}

@app.post("/run-benchtest")
def run_test():
    def target():
        subprocess.run(["python3", "BenchHost.py"])
    threading.Thread(target=target).start()
    return {"msg": "Bench test started"}
