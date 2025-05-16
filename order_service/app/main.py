from fastapi import FastAPI

app = FastAPI()

@app.get("/orders")
def get_orders():
    return {"message": "Order service is working!"}
