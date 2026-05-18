from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os


# ProjectController handles project-related operations.
# Currently, it serves as a placeholder for future project management functionalities,
# such as creating, updating, and deleting projects, as well as managing project metadata and associations with uploaded
class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str):

        # This method constructs the file path for a given project ID, ensuring that the directory exists.
        # It checks if the directory for the project exists within the assets/files directory, and if not, it creates it.

        project_dir = os.path.join(self.files_dir, project_id)

        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        return project_dir
