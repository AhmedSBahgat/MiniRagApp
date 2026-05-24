from fastapi import APIRouter, Depends, FastAPI, UploadFile, status, File, Request
from fastapi.responses import JSONResponse
import os
import aiofiles
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk, Asset
from models.enums.AssetTybeEnum import AssetTypeEnum

logger = logging.getLogger("uvicorn.error")
# This module defines the API routes for handling data-related operations, such as file uploads.
data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])

# The upload_file endpoint allows users to upload files to a specific project.
# It validates the uploaded file, generates a unique file path, and saves the file asynchronously.
# If the upload is successful, it returns a success signal along with the file ID; otherwise, it returns an error signal.


@data_router.post("/upload/{project_id}")
async def upload_file(
    request: Request,
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings),
):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

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
    # ssrore the asset record in the database
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file.filename,
        asset_size=os.path.getsize(file_save_path),
        asset_config={"stored_file_id": file_id},
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)

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
    request: Request,
    project_id: str,
    process_request: ProcessRequest,
):
    # Implementation for processing the file
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    project_file_ids = {}

    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id, asset_name=process_request.file_id
        )
        if asset_record is None:
            return JSONResponse(
                content={
                    "signal": ResponseSignal.FILE_ID_ERROR.value,
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        project_file_ids = {
            asset_record.id: asset_record.asset_config.get("stored_file_id")
        }

    else:

        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id, asset_type=AssetTypeEnum.FILE.value
        )
        # project_file_ids = [str(asset["_id"]) for asset in project_files]
        project_file_ids = {
            record.id: record.asset_config.get("stored_file_id")
            for record in project_files
            if record.asset_config and record.asset_config.get("stored_file_id")
        }

    if not project_file_ids:
        return JSONResponse(
            content={
                status_code: status.HTTP_400_BAD_REQUEST,
                "signal": ResponseSignal.NO_FILES_TO_PROCESS.value,
            }
        )

    Process_controller = ProcessController(project_id=project_id)

    no_records = 0
    no_files = 0

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    if do_reset:
        deleted = await chunk_model.delete_chunk_by_project_id(project.id)

    for asset_id, file_id in project_file_ids.items():

        file_content = Process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.error(f"File with ID {file_id} not found for processing.")
            continue

        file_chunks = Process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )

        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.PROCESSING_FAILED.value},
            )

        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=1 + i,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id,
            )
            for i, chunk in enumerate(file_chunks)
        ]

        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_files += 1

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": no_files,
        }
    )
