from enum import Enum


class ResponseSignal(Enum):
    PROCESSING_FAILED = "File processing failed."
    PROCESSING_SUCCESS = "File processed successfully."
    NO_FILES_TO_PROCESS = "No files available for processing."
    FILE_VALIDATED_SUCCESS = "File validated successfully."
    FILE_TYPE_NOT_SUPPORTED = "File type is not supported."
    FILE_SIZE_EXCEEDED = "File size exceeds the maximum allowed size."
    FILE_UPLOADED_SUCCESS = "File uploaded successfully."
    FILE_UPLOAD_FAILED = "File upload failed."
    FILE_ID_ERROR = "No file found with the provided ID."
