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
    PROJECT_NOT_FOUND_ERROR = "project not found"
    INSERT_INTO_VECTORDB_ERROR = "insert into vector db error"
    INSERT_INTO_VECTORDB_SUCCESS = "insert into vector db success"
    VECTORDB_COLLECTION_RETRIEVED = "vector db collection retrieved"
    VECTORDB_SEARCH_SUCCESS = "vector db search success"
    VECTORDB_SEARCH_ERROR = "vector db search error"
    RAG_ANSWER_ERROR = "rag answer generation error"
    RAG_ANSWER_SUCCESS = "rag answer generation success"
