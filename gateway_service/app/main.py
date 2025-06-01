# gateway_service/app/main.py

import os
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import httpx
from jose import JWTError, jwt

app = FastAPI()

# Разрешаем CORS отовсюду (при необходимости можно сузить)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# 1. Настройки для проверки JWT
# ----------------------------

# Секретный ключ, которым подписывает токены admin_service.
# ДОЛЖЕН совпадать с тем же SECRET_KEY, что и в admin_service.
SECRET_KEY = os.getenv("ADMIN_JWT_SECRET", "your-admin-secret-key")
ALGORITHM = "HS256"

def verify_admin_token(request: Request):
    """
    Извлекает JWT из заголовка Authorization и проверяет, что в payload role == "admin".
    В случае ошибки выбрасывает HTTPException(401) или HTTPException(403).
    """
    auth_hdr = request.headers.get("Authorization")
    if not auth_hdr or not auth_hdr.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth_hdr.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Проверяем наличие поля role и его значение
    role = payload.get("role")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")


# ----------------------------
# 2. Словарь с адресами «внутренних» сервисов
# ----------------------------

SERVICES = {
    "products": os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8000"),
    "orders":   os.getenv("ORDER_SERVICE_URL",   "http://order_service:8000"),
    "admin":    os.getenv("ADMIN_SERVICE_URL",   "http://admin_service:8000"),
}

# Клиент httpx для проксирования
client = httpx.AsyncClient(timeout=10.0)


# ----------------------------
# 3. Health‐чек gateway
# ----------------------------

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


# ----------------------------
# 4. Прокси для статики админки (/media/…)
# ----------------------------

@app.api_route("/media/{path:path}", methods=["GET", "HEAD"])
async def proxy_media(path: str, request: Request):
    """
    Проксируем запросы /media/... → admin_service:8000/media/...
    (например, отдаём картинки, которые лежат в /media внутри admin_service).
    """
    target_url = f"{SERVICES['admin']}/media/{path}"
    try:
        resp = await client.request(
            method=request.method,
            url=target_url,
            headers={key: value for key, value in request.headers.items() if key.lower() != "host"},
            params=request.query_params,
        )
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Bad gateway while proxying /media")

    excluded = {"content-encoding", "transfer-encoding", "connection"}
    headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}
    return Response(content=resp.content, status_code=resp.status_code, headers=headers)


# ----------------------------
# 5. Универсальный proxy‐роутер для API
# ----------------------------

@app.api_route(
    "/api/v1/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
)
async def proxy(service: str, path: str, request: Request):
    """
    1) Проверяем, что service — одна из допустимых (products, orders, admin).
    2) Если это защищённые методы (по списку), проверяем JWT → роль admin.
    3) Проксируем запрос дальше в соответствующий микросервис.
    """

    # 1. Проверяем, что сервис известен
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Unknown service '{service}'")

    # 2. Определяем, нужно ли для данного service+метода проверять роль admin
    method = request.method.upper()
    need_admin = False

    # 2.1. Для products: защищаем POST, PUT, PATCH
    if service == "products" and method in ("POST", "PUT", "PATCH"):
        need_admin = True

    # 2.2. Для orders: защищаем только PUT (изменение заказа)
    if service == "orders" and method == "PUT":
        need_admin = True

    # 2.3. Для admin: оставляем всю логику (при необходимости, можно добавить дополнительные проверки),
    # но сейчас сопоставляем пути так, чтобы /api/v1/admin/* проксировалось на /api/v1/admin/* в admin_service.
    if service == "admin":
        # При необходимости можно также заставить проверять токен для определённых admin‐методов,
        # но за авторизацию самого админа отвечает admin_service.
        pass

    # 2.4. Если нужно админ‐токен, проверяем его
    if need_admin:
        verify_admin_token(request)

    # 3. Строим target URL для проксирования
    if service == "admin":
        # Переправляем /api/v1/admin/{path} → http://admin_service:8000/api/v1/admin/{path}
        target = f"{SERVICES['admin']}/api/v1/admin/{path}"
    else:
        # Переправляем /api/v1/{service}/{path} → http://<service>:8000/api/v1/{service}/{path}
        target = f"{SERVICES[service]}/api/v1/{service}/{path}"

    # 4. Выполняем сам прокси‐запрос
    try:
        resp = await client.request(
            method=request.method,
            url=target,
            headers={key: value for key, value in request.headers.items() if key.lower() != "host"},
            params=request.query_params,
            content=await request.body(),
        )
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Bad gateway while proxying request")

    # 5. Возвращаем ответ «как есть» клиенту
    excluded_headers = {"content-encoding", "transfer-encoding", "connection"}
    headers = {key: value for key, value in resp.headers.items() if key.lower() not in excluded_headers}

    return Response(content=resp.content, status_code=resp.status_code, headers=headers)
