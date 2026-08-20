from pathlib import Path

import pytest

from src.signal.data.models import Dataset, DatasetFormat


def test_dataset_preserves_identity_and_source() -> None:
    dataset = Dataset(
        name="orders",
        path=Path("data/orders.csv"),
        format=DatasetFormat.CSV,
    )

    assert dataset.name == "orders"
    assert dataset.path == Path("data/orders.csv")
    assert dataset.format is DatasetFormat.CSV


def test_dataset_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="name"):
        Dataset(name="  ", path=Path("orders.csv"), format=DatasetFormat.CSV)


def test_dataset_is_immutable() -> None:
    dataset = Dataset(
        name="orders",
        path=Path("data/orders.csv"),
        format=DatasetFormat.CSV,
    )

    with pytest.raises(AttributeError):
        dataset.name = "customers"  # type: ignore[misc]
