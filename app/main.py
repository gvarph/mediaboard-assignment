from fastapi import FastAPI

from app.routers.crawl import router as crawl_router

app = FastAPI()

app.include_router(crawl_router)
