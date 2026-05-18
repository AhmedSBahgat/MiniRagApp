from fastapi import APIRouter, Depends, FastAPI, UploadFile, status
from fastapi.responses import JSONResponse
import os
import aiofiles
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController
from models import ResponseSignal
import logging

logger = logging.getLogger("uvicorn.error")
# This module defines the API routes for handling data-related operations, such as file uploads.
data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


@data_router.post("/upload/{project_id}")
async def upload_file(
    project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)
):

    data_controller = DataController()

    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal},
        )

    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_save_path, file_id = data_controller.generate_unique_filepath(
        original_filename=file.filename, project_id=project_id
    )

    try:

        async with aiofiles.open(file_save_path, "wb") as out_file:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await out_file.write(chunk)

    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.File_Upload_Failed.value},
        )
    return JSONResponse(
        content={
            "signal": ResponseSignal.File_Uploaded_Success.value,
            "file_id": file_id,
        }
    )
