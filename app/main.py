from fastapi import FastAPI
from .database import Base, engine
from .routers import subscriptions, invoices, plans

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Subscriptions Service")

app.include_router(plans.router)
app.include_router(subscriptions.router)
app.include_router(invoices.router)
