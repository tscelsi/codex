from typing import Annotated, Any

import pytest
from pydantic import AfterValidator, BaseModel

from csv_validator.validator import AbstractReader, CsvValidator, MemoryReader


class Schema(BaseModel):
    a: int
    b: str
    c: float


def create_reader(data: list[dict[str, Any]]) -> AbstractReader:
    return MemoryReader(data)


@pytest.fixture
def reader():
    x: list[dict[str, Any]] = [
        {"a": 1, "b": "hello", "c": 2.5},
        {"a": 2, "b": "world", "c": 3.0},
    ]
    return create_reader(x)


@pytest.fixture
def reader_with_error():
    x: list[dict[str, Any]] = [
        {"a": "invalid", "b": "world", "c": 3.0},
    ]
    return create_reader(x)


def test_init(reader: AbstractReader):
    CsvValidator(schema=Schema)


def test_validate(reader: AbstractReader):
    validator = CsvValidator(schema=Schema)
    data, _ = validator.validate_all(reader=reader)
    assert list(data) == [
        {"a": 1, "b": "hello", "c": 2.5},
        {"a": 2, "b": "world", "c": 3.0},
    ]


def test_validate_with_error(reader_with_error: AbstractReader):
    validator = CsvValidator(schema=Schema)
    _, errors = validator.validate_all(reader=reader_with_error)

    assert len(errors) == 1
    assert errors[0] == {
        "data": {"a": "invalid", "b": "world", "c": 3.0},
        "msg": "Input should be a valid integer, unable to parse string as an integer",  # noqa: E501
        "col": "a",
        "row": 0,
    }


@pytest.mark.parametrize(
    "data, error_len",
    [({"a": 1}, 0), ({"a": "not_an_int"}, 1), ({"a": None}, 0)],
)
def test_validate_with_null_value(data: dict[str, Any], error_len: int):
    class Schema(BaseModel):
        a: int | None

    validator = CsvValidator(
        schema=Schema,
    )
    _, errors = validator.validate_all(reader=create_reader([data]))
    assert len(errors) == error_len


@pytest.mark.parametrize(
    "data, error_len",
    [({"a": 1}, 1), ({"a": "not_an_int"}, 1), ({"a": 2}, 0)],
)
def test_with_custom_validations(data: dict[str, Any], error_len: int):
    def is_even(value: int) -> int:
        if value % 2 == 1:
            raise ValueError(f"{value} is not an even number")
        return value

    class Schema(BaseModel):
        a: Annotated[int, AfterValidator(is_even)]

    validator = CsvValidator(
        schema=Schema,
    )
    _, errors = validator.validate_all(reader=create_reader([data]))
    assert len(errors) == error_len
