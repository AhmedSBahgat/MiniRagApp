from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.LLMEnums import DocumentTypeEnum
from typing import List


class NLPController(BaseController):
    def __init__(self, vectordb_client, generation_client, embedding_client):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()

    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(
            collection_name=collection_name
        )

        return collection_info

    """
    def index_into_vector_db(
        self, project: Project, chunks: List[DataChunk], do_reset: bool = False
    ):
        # step 1 Get collection_name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step 2 Manage items
        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]
        vectors = [
            self.embedding_client.embed_text(
                text=text, document_type=DocumentTypeEnum.DOCUMENT.value
            )
            for text in texts
        ]

        # step 3 Create collection if not exist
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # step 4
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            meta_data=metadata,
        )

        return True
    """

    def index_into_vector_db(
        self, project: Project, chunks: List[DataChunk], do_reset: bool = False
    ):
        collection_name = self.create_collection_name(project_id=project.project_id)

        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]
        vectors = [
            self.embedding_client.embed_text(
                text=text, document_type=DocumentTypeEnum.DOCUMENT.value
            )
            for text in texts
        ]

        if not vectors or not vectors[0]:
            return False

        real_embedding_size = len(vectors[0])

        if any(len(v) != real_embedding_size for v in vectors):
            return False

        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=real_embedding_size,
            do_reset=do_reset,
        )

        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            meta_data=metadata,
        )

        return True

    def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):
        collection_name = self.create_collection_name(project_id=project.project_id)
        vector = self.embedding_client.embed_text(
            text=text, document_type=DocumentTypeEnum.QUERY.value
        )

        print("query vector len =", len(vector))

        if not vector or len(vector) == 0:

            return False
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name, vector=vector, limit=limit
        )
        return results
