from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router


app = FastAPI(

    title="LegalEase API",

    version="1.0.0",

    description=(
        "AI-powered legal document "
        "draft generator."
    ),
)


app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
def root():

    return {

        "name": "LegalEase",

        "message": (
            "AI-powered legal "
            "document generator API"
        ),

        "docs": "/docs",
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }