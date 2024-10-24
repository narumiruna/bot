import functools
import os
from typing import Any

from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.fastembed_common import QueryResponse
from qdrant_client.models import FieldCondition
from qdrant_client.models import Filter
from qdrant_client.models import MatchValue


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


def add_to_qdrant(text: str, chat_id: int, message_id: int) -> None:
    logger.info("upsert text: {} to qdrant", text)

    collection_name = get_collection_name()
    client = get_qdrant_client()

    client.add(
        collection_name=collection_name,
        documents=[text],
        metadata=[{"chat_id": chat_id, "message_id": message_id}],
    )


def build_url(chat_id: int, message_id: int) -> str:
    if chat_id < 0:
        chat_id += 1_000_000_000_000
        chat_id *= -1

    if message_id < 0:
        return ""

    return f"https://t.me/c/{chat_id}/{message_id}"


def build_points_str(points: list[QueryResponse]) -> str:
    s = ""

    for i, point in enumerate(points):
        # Access document directly from QueryResponse
        text = point.document
        if not text:
            continue

        # Get metadata from point attributes
        metadata: dict[str, Any] = getattr(point, "metadata", {}) or {}
        chat_id = metadata.get("chat_id")
        if not chat_id:
            continue

        message_id = metadata.get("message_id")
        if not message_id:
            continue

        s += f"{i+1}. "
        url = build_url(chat_id=chat_id, message_id=message_id)
        if url:
            s += url + "\n"

        s += text + "\n\n"

    return s


def query_qdrant(text: str, chat_id: int) -> str:
    logger.info("upsert text: {} to qdrant", text)

    collection_name = get_collection_name()
    client = get_qdrant_client()

    points: list[QueryResponse] = client.query(
        collection_name=collection_name,
        query_text=text,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="chat_id",
                    match=MatchValue(
                        value=chat_id,
                    ),
                ),
            ],
        ),
    )

    return build_points_str(points)
