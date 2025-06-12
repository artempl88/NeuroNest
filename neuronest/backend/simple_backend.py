from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="NeuroNest Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NeuroNest Backend работает!", "status": "success"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "neuronest-backend"}

@app.get("/api/v1/agents")
async def get_agents():
    return {
        "agents": [
            {"id": 1, "name": "Test Agent", "status": "active"},
            {"id": 2, "name": "Demo Agent", "status": "active"}
        ], 
        "message": "Список агентов (демо режим)"
    }

@app.get("/api/v1/status")
async def get_status():
    return {
        "backend": "running",
        "frontend": "available",
        "database": "mock",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 