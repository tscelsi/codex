import abc
import csv
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import polars as pl
from pydantic import BaseModel, ValidationError
from pydantic_core import SchemaSerializer, SchemaValidator


class AbstractIterReader(abc.ABC):
    @abc.abstractmethod
    def read(self) -> Iterable[dict[str, Any]]:
        """Read data from a source and return it."""
        pass


class CsvReader(AbstractIterReader):
    def __init__(self, path: Path | str):
        self.path = Path(path)
        with open(self.path, "r") as file:
            reader = csv.DictReader(file)
            self.data = list(reader)

    def read(self) -> Iterable[dict[str, Any]]:
        """Read data from a source and return it."""
        return self.data


class PolarsReader:
    def __init__(self, df: pl.DataFrame):
        self.df = df

    def read(self):
        return self.df


class PandasReader:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def read(self):
        return self.df


class PolarsValidator:
    def __init__(self, schema: type[BaseModel], reader: PolarsReader):
        self.schema = schema
        self.reader = reader
        self.v = SchemaValidator(self.schema.__pydantic_core_schema__)

    def validate_all(self):
        errors: list[dict[str, Any]] = []
        df = self.reader.read().with_columns(
            pl.struct(pl.all())
            .map_elements(lambda row: self.v.validate_python(row).model_dump())
            .alias("validated_row")
        )
        return df.to_dict()["validated_row"], errors


class PandasValidator:
    def __init__(self, schema: type[BaseModel], reader: PandasReader):
        self.schema = schema
        self.reader = reader
        self.v = SchemaValidator(self.schema.__pydantic_core_schema__)

    def _validate_row(self, row: pd.Series) -> dict[str, Any]:
        """Validate a single row against the schema."""
        try:
            validated_row = self.v.validate_python(row.to_dict()).model_dump()
            return validated_row
        except ValidationError as e:
            raise e

    def validate_all(self):
        errors: list[dict[str, Any]] = []
        df = self.reader.read().apply(self._validate_row, axis=1)
        return df.to_list(), errors


class SlowerIterValidator:
    def __init__(self, schema: type[BaseModel], reader: AbstractIterReader):
        self.schema = schema
        self.reader = reader

    def validate_all(self):
        errors: list[dict[str, Any]] = []
        data: list[dict[str, Any]] = []
        for i, row in enumerate(self.reader.read()):
            try:
                validated_row = self.schema(**row)
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


class IterValidator:
    def __init__(self, schema: type[BaseModel], reader: AbstractIterReader):
        self.schema = schema
        self.reader = reader
        self.validator = SchemaValidator(self.schema.__pydantic_core_schema__)
        self.serializer = SchemaSerializer(
            self.schema.__pydantic_core_schema__
        )

    def validate_all(self):
        errors: list[dict[str, Any]] = []
        data: list[dict[str, Any]] = []
        for i, row in enumerate(self.reader.read()):
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
