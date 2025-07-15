from fastapi import FastAPI
from services.common.config import Config
from services.api_service.controllers import user

app = FastAPI(title="API Service", openapi_url="/openapi.json")
app.include_router(user.router, prefix="/users")

@app.get("/")
def read_root():
    return {"message": f"API Service running on port {Config.API_PORT}"}

@app.on_event("shutdown")
def shutdown_event():
    from services.common.rabbitmq import rabbitmq_client
    rabbitmq_client.close()