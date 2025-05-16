from fastapi import FastAPI

app = FastAPI()

@app.post("/admin/login")
def login():
    return {"message": "Admin login works!"}
