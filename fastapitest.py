
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def hello():
    return {"msg": "FastAPI is running!"}