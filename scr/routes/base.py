from fastapi import APIRouter, Depends, FastAPI
import os
from helpers.config import get_settings, Settings

base_router = APIRouter(prefix="/api/v1", tags=["api_v1"])
# The base_router defines a simple endpoint that returns the application's name and version.
# This serves as a basic health check or welcome message for the API, providing essential information about the application to clients.


@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):

    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION

    return {
        "app_name": app_name,
        "app_version": app_version,
    }
