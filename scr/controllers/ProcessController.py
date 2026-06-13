from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from models import ProcessingEnums
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ProcessController is responsible for handling data processing operations, such as processing uploaded files and managing data-related tasks.
# It inherits from BaseController to utilize common functionalities and configurations,
# and it interacts with ProjectController to manage project-specific file paths and operations.
# The ProcessController includes methods for determining the appropriate file loader based on the file type,
# loading file content, and processing the content by splitting it into manageable chunks for further use in the application.


class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):
        file_path = os.path.join(self.project_path, file_id)
        file_extension = self.get_file_extension(file_id)

        if not os.path.exists(file_path):
            return None

        if file_extension == ProcessingEnums.TXT.value:
            return TextLoader(file_path, encoding="utf-8")

        elif file_extension == ProcessingEnums.PDF.value:
            return PyMuPDFLoader(file_path)

        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id=file_id)
        if loader:
            return loader.load()
        return None 

    def process_file_content(
        self,
        file_content: list,
        file_id: str,
        chunk_size: int = 100,
        overlap_size: int = 20,
    ):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )

        chunks = text_splitter.split_documents(file_content)

        return chunks
