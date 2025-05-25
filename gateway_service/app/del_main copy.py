from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "products": "http://product_service:8000",
    "orders":   "http://order_service:8000",
    "admin":    "http://admin_service:8000",
}

@app.api_route("/api/v1/{service}/{path:path}",
               methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Unknown service")
    # target = f"{SERVICES[service]}/{service}/{path}"
    target = f"{SERVICES[service]}/api/v1/{service}/{path}"
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=target,
            headers=dict(request.headers),
            params=request.query_params,
            content=await request.body(),
            timeout=10.0
        )
    return Response(content=resp.content,
                    status_code=resp.status_code,
                    headers=resp.headers)

@app.get("/health")
def health():
    return {"status": "ok"}
