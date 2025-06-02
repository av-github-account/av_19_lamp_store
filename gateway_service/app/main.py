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

# Added: proxy for media files (static images) from admin_service
@app.api_route("/media/{path:path}", methods=["GET", "HEAD"])
async def proxy_media(path: str, request: Request):
    target_url = f"{SERVICES['admin']}/media/{path}"
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=target_url,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
            timeout=10.0
        )
        # Фильтруем upstream-заголовки date и server
    filtered = {k: v for k, v in resp.headers.items() if k.lower() not in ("date", "server")}
    return Response(content=resp.content, status_code=resp.status_code, headers=filtered)
    # return Response(
    #     content=resp.content,
    #     status_code=resp.status_code,
    #     headers=resp.headers
    # )

# Generic proxy for all API services under /api/v1/{service}/...
@app.api_route("/api/v1/{service}/{path:path}",
               methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Unknown service")

    # Вот здесь скорректировали путь для admin:
    if service == "admin":
        target = f"{SERVICES[service]}/api/v1/admin/{path}"
    else:
        target = f"{SERVICES[service]}/api/v1/{service}/{path}"

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=target,
            headers={k: v for k, v in request.headers.items()},
            params=request.query_params,
            content=await request.body(),
            timeout=10.0
        )
    filtered = {k: v for k, v in resp.headers.items() if k.lower() not in ("date", "server")}
    return Response(content=resp.content, status_code=resp.status_code, headers=filtered)


@app.get("/health")
def health():
    return {"status": "ok"}
