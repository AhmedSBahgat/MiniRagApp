from fastapi import APIRouter, Depends, FastAPI, UploadFile, status, File
from fastapi.responses import JSONResponse
import os
import aiofiles
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest

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
            content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value},
        )
    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
            "file_id": file_id,
        }
    )


# The process_endpoint is a placeholder for the file processing logic, which will be implemented in the future.
# It currently accepts a project ID and a request body containing the file ID and processing parameters, and returns the file ID as a response.
# The actual processing logic will involve reading the uploaded file, performing the necessary operations (such as chunking, vectorization, etc.), and returning the results or status of the processing.


@data_router.post("/process/{project_id}")
async def process_endpoint(
    project_id: str,
    request: ProcessRequest,
):
    # Implementation for processing the file
    file_id = request.file_id
    chunk_size = request.chunk_size
    overlap_size = request.overlap_size

    Process_controller = ProcessController(project_id=project_id)

    file_content = Process_controller.get_file_content(file_id=file_id)

    file_chunks = Process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size,
    )

    if file_chunks == None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.PROCESSING_FAILED.value},
        )

    return file_chunks
