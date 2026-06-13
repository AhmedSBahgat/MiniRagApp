from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from routes import base, data, nlp
from helpers.config import get_settings
from stores.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser


async def startup_span(app: FastAPI):
    settings = get_settings()

    app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongodb_conn[settings.MONGODB_DB_NAME]

    llm_provider_factory = LLMProviderFactory(settings)
    vectorDB_provider_factory = VectorDBProviderFactory(settings)

    # generation client
    app.generation_client = llm_provider_factory.create_provider(
        provider=settings.GENERATION_BACKEND
    )
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create_provider(
        provider=settings.EMBEDDING_BACKEND
    )
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE,
    )

    # vector db client

    app.vectordb_client = vectorDB_provider_factory.create_provider(
        provider=settings.VECTOR_DB_BACKEND
    )

    app.vectordb_client.connect()
    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG, default_language=settings.DEFAULT_LANG
    )


async def shutdown_span(app: FastAPI):
    app.mongodb_conn.close()
    app.vectordb_client.disconnect()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_span(app)
    yield
    await shutdown_span(app)


app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
