import time

from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

from api_v1.routers import router
from authbase.settings import Base,engine,DEBUG,ALLOWED_HOSTS,ALLOWED_ORIGINS

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Authentication API service",
    description="This is the user CRUD operation and authentication service API",
    version="0.1",
    debug=DEBUG,
    docs_url="/",
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(router=router, prefix="/api/v0.1")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

