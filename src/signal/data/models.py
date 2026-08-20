"""Domain model for datasets entering an investigation."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class DatasetFormat(StrEnum):
    """Supported dataset formats."""

    CSV = "csv"
    PARQUET = "parquet"


@dataclass(frozen=True, slots=True)
class Dataset:
    """Immutable identity and source metadata for a dataset.

    The model describes a dataset; it does not load, clean, transform,
    or mutate its contents.
    """

    name: str
    path: Path
    format: DatasetFormat

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Dataset name must not be empty")
        if not self.path.name:
            raise ValueError("Dataset path must include a filename")
