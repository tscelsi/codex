import abc
import csv
from pathlib import Path
from typing import Any, Iterable

from pydantic import BaseModel, ValidationError
from pydantic_core import SchemaSerializer, SchemaValidator


class AbstractReader(abc.ABC):
    @abc.abstractmethod
    def iter(self) -> Iterable[dict[str, Any]]:
        pass


class MemoryReader(AbstractReader):
    """Reads data from a list of dictionaries in memory."""

    def __init__(self, data: list[dict[str, Any]]):
        self.data = data

    def iter(self) -> Iterable[dict[str, Any]]:
        for row in self.data:
            yield row


class LazyCsvReader(AbstractReader):
    """Reads data from a file stream, one row at a time."""

    def __init__(self, path: Path | str):
        self.path = path

    def iter(self) -> Iterable[dict[str, Any]]:
        with open(self.path, "r") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                yield row


class CsvReader(AbstractReader):
    """Loads a CSV file into memory and provides an iterable interface."""

    def __init__(self, path: Path | str):
        self.reader = LazyCsvReader(path)
        self.data = [r for r in self.reader.iter()]

    def iter(self) -> Iterable[dict[str, Any]]:
        for row in self.data:
            yield row


class CsvValidator:
    def __init__(self, schema: type[BaseModel]):
        self.schema = schema
        self.validator = SchemaValidator(self.schema.__pydantic_core_schema__)
        self.serializer = SchemaSerializer(
            self.schema.__pydantic_core_schema__,
        )

    def validate_all(self, reader: AbstractReader):
        errors: list[dict[str, Any]] = []
        data: list[dict[str, Any]] = []
        for i, row in enumerate(reader.iter()):
            try:
                validated_row = self.validator.validate_python(row)
                data.append(validated_row.model_dump())
            except ValidationError as e:
                _errors = e.errors()
                for error in _errors:
                    errors.append(
                        {
                            "data": row,
                            "msg": error["msg"],
                            "row": i,
                            "col": error["loc"][0],
                        }
                    )
        return data, errors
