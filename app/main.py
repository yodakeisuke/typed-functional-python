from fastapi import FastAPI

from app.integrations import order

app = FastAPI()

app.include_router(order.router, tags=["Order"], prefix="/order")
