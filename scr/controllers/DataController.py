from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import os
import re


# DataController handles file validation
# and processing for uploaded files in the application.
# It ensures that the uploaded files meet the specified criteria for type
# and size before further processing.
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048567  # 1 MB in bytes

    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATED_SUCCESS.value

    def generate_unique_filepath(self, original_filename: str, project_id: str):
        # This method generates a unique filepath by appending a timestamp and project ID to the original filename.
        # It ensures that files with the same name do not overwrite each other when uploaded to the same project directory.
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_filename = self.get_clean_filename(original_filename=original_filename)

        new_file_path = os.path.join(project_path, f"{random_key}_{cleaned_filename}")

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path, f"{random_key}_{cleaned_filename}"
            )

        return new_file_path, random_key + "_" + cleaned_filename

    def get_clean_filename(self, original_filename: str):
        # This method cleans the original filename by removing special characters and replacing spaces with underscores.
        # It ensures that the filename is safe for use in the filesystem and does not contain characters that could cause issues when saving or accessing the file.
        clean_filename = re.sub(r"[^\w.]", "", original_filename.strip())
        clean_filename = clean_filename.replace(" ", "_")
        return clean_filename
