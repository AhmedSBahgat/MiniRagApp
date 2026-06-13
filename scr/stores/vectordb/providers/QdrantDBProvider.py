from urllib import response

from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
import logging
import uuid
from typing import List
from models.db_schemes import RetrievedDocument


class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_method: str):
        self.client = None
        self.db_path = db_path

        raw_distance = (
            str(distance_method).strip().lower()
            if distance_method is not None
            else "cosine"
        )

        mapping = {
            "cosine": models.Distance.COSINE,
            "dot": models.Distance.DOT,
            "euclid": models.Distance.EUCLID,
            "manhattan": models.Distance.MANHATTAN,
        }

        self.distance_method = mapping.get(raw_distance, models.Distance.COSINE)
        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collection(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            self.client.delete_collection(collection_name=collection_name)

    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        if do_reset:
            self.delete_collection(collection_name=collection_name)

        if not self.is_collection_existed(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method,
                ),
            )
            return True
        return False

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        meta_data: dict = None,
        record_id: str = None,
    ):
        if not self.is_collection_existed(collection_name):
            self.logger.error(
                f"cannot insert a new record in not-existed collection: {collection_name}"
            )
            return False

        if record_id is None:
            record_id = str(uuid.uuid4())

        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=record_id,
                        vector=vector,
                        payload={"text": text, **(meta_data or {})},
                    )
                ],
            )
        except Exception as e:
            self.logger.error(f"Error while inserting record: {e}")
            return False

        return True

    def insert_many(
        self,
        collection_name: str,
        texts: list,
        vectors: list,
        meta_data: list = None,
        record_id: list = None,
        batch_size: int = 50,
    ):
        if meta_data is None:
            meta_data = [None] * len(texts)

        if record_id is None:
            record_id = [str(uuid.uuid4()) for _ in texts]

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = meta_data[i:batch_end]
            batch_record_ids = record_id[i:batch_end]

            batch_records = [
                models.PointStruct(
                    id=batch_record_ids[idx],
                    vector=batch_vectors[idx],
                    payload={"text": batch_texts[idx], **(batch_metadata[idx] or {})},
                )
                for idx in range(len(batch_texts))
            ]

            try:
                self.client.upload_points(
                    collection_name=collection_name,
                    points=batch_records,
                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False

        return True

    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        response = self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit,
        )

        points = response.points if response and response.points else []

        if len(points) == 0:
            return []

        return [
            RetrievedDocument(
                text=point.payload.get("text", ""),
                score=point.score,
            )
            for point in points
        ]
