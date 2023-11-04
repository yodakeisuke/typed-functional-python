from fastapi import FastAPI

from app.endopoints import order

app = FastAPI()

app.include_router(order.router, tags=["Order"], prefix="/order")
