import functools
import os

from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import Distance
from qdrant_client.models import PointStruct
from qdrant_client.models import VectorParams

from .llm import create_embeddings


@functools.cache
def get_qdrant_client() -> QdrantClient:
    url = os.getenv("QDRANT_URL")

    if not url:
        logger.warning("QDRANT_URL is not set, using in-memory database")
        return QdrantClient(location=":memory:")

    return QdrantClient(url=url)


@functools.cache
def get_collection_name() -> str:
    collection_name = os.getenv("QDRANT_COLLECTION_NAME")
    if not collection_name:
        logger.warning("QDRANT_COLLECTION_NAME is not set, using default collection name")
        collection_name = "telegram"
    return collection_name


def create_collection(size: int = 1536) -> None:
    collection_name = get_collection_name()
    client = get_qdrant_client()

    if client.collection_exists(collection_name):
        return

    client.create_collection(
        collection_name,
        vectors_config=VectorParams(
            size=size,
            distance=Distance.COSINE,
        ),
    )


def create_points(texts: str | list[str], **kwargs) -> list[PointStruct]:
    if isinstance(texts, str):
        texts = [texts]

    response = create_embeddings(texts)

    return [
        PointStruct(
            id=idx,
            vector=data.embedding,
            payload={"text": text} | kwargs,
        )
        for idx, (data, text) in enumerate(zip(response.data, texts))
    ]


def upsert_to_qdrant(text: str | list[str], **kwargs) -> None:
    collection_name = get_collection_name()
    client = get_qdrant_client()
    create_collection()
    points = create_points(text, **kwargs)
    client.upsert(collection_name, points)
