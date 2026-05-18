from enum import Enum


class ResponseSignal(Enum):
    File_Validated_Success = "File Validated Successfully"
    File_Type_Not_Supported = "File type is not supported."
    File_Size_Exceeded = "File size exceeds the maximum allowed size."
    File_Uploaded_Success = "File uploaded successfully."
    File_Upload_Failed = "File upload failed."
