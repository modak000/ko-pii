"""확장자 기반 자동 디스패처."""
from __future__ import annotations

import os

from k_pii.io_ import csv_reader, docx, hwpx, plain, xlsx

SUPPORTED_EXTENSIONS: tuple[str, ...] = (
    ".txt", ".md", ".log",
    ".csv", ".tsv",
    ".hwpx",
    ".docx",
    ".xlsx",
)


def read_text(path: str) -> str:
    """파일 확장자에 따라 적절한 reader 로 텍스트를 반환."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".hwpx":
        return hwpx.read_text(path)
    if ext == ".docx":
        return docx.read_text(path)
    if ext == ".xlsx":
        return xlsx.read_text(path)
    if ext in (".csv", ".tsv"):
        return csv_reader.read_text(path)
    # 기본 plain
    return plain.read_text(path)


def read_records(path: str) -> list[dict[str, str]]:
    """CSV/TSV/XLSX 같은 표 형식만 의미가 있는 정형 reader.

    그 외 포맷은 빈 리스트 반환 — 호출자가 분기 처리.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".tsv"):
        return csv_reader.read_records(path)
    if ext == ".xlsx":
        return xlsx.read_records(path)
    return []
