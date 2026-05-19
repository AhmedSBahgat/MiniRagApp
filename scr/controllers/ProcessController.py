from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from models import ProcessingEnums
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ProcessController is responsible for handling data processing operations, such as processing uploaded files and managing data-related tasks.
# Currently, it serves as a placeholder for future implementations of data processing logic, which may include
# operations like chunking, vectorization, and other transformations on the uploaded files.


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

        if file_extension == ProcessingEnums.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        elif file_extension == ProcessingEnums.PDF.value:
            return PyMuPDFLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    # ✅ MUST BE HERE (same level as others)
    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id=file_id)
        return loader.load()

    # ✅ MUST BE HERE (same level as others)
    def process_file_content(
        self,
        file_content: list,
        file_id: str,
        chunk_size: int = 100,
        overlap_size: int = 20,
    ):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=overlap_size, length_function=len
        )

        file_content_text = [doc.page_content for doc in file_content]
        file_content_metadata = [doc.metadata for doc in file_content]

        chunks = text_splitter.create_documents(
            file_content_text, metadatas=file_content_metadata
        )

        return chunks
