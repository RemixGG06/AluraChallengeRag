"""Ruta /api/admin — ingesta de documentos e inventario vectorizado."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from backend.common.cache import response_cache
from backend.common.upload import UploadedFile, save_uploaded_file
from backend.config.settings import settings
from backend.rag.vectorstore import ingest_file, list_indexed_sources

router = APIRouter()


class IngestResult(BaseModel):
    name: str
    success: bool
    chunks: int = 0
    error: str = ""


class IngestResponse(BaseModel):
    results: list[IngestResult]


class InventoryItem(BaseModel):
    source: str
    department: str
    chunks: int


class InventoryResponse(BaseModel):
    items: list[InventoryItem]
    total_documents: int
    total_chunks: int
    total_departments: int


@router.post("/upload", response_model=IngestResponse)
async def upload_documents(
    files: list[UploadFile] = File(...),
    department: str = Form("general"),
):
    results: list[IngestResult] = []
    for upload in files:
        try:
            content = await upload.read()
            fake_file = UploadedFile(name=upload.filename or "unknown", content=content)
            path = save_uploaded_file(fake_file, settings.raw_docs_path)
            chunks = ingest_file(path, department=department)
            results.append(
                IngestResult(name=upload.filename or "unknown", success=True, chunks=chunks)
            )
        except Exception as exc:
            results.append(
                IngestResult(
                    name=upload.filename or "unknown",
                    success=False,
                    error=str(exc),
                )
            )
    # Invalidar caché para que las nuevas preguntas usen el índice actualizado
    response_cache.clear()
    return IngestResponse(results=results)


@router.get("/inventory", response_model=InventoryResponse)
def get_inventory():
    inventory = list_indexed_sources()
    return InventoryResponse(
        items=[
            InventoryItem(
                source=item["source"],
                department=item["department"],
                chunks=item["chunks"],
            )
            for item in inventory
        ],
        total_documents=len(inventory),
        total_chunks=sum(item["chunks"] for item in inventory),
        total_departments=len({item["department"] for item in inventory}),
    )
