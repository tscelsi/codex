# CSV Validator

Frequently in my coding travels, I have found myself needing to upload and validate a CSV file, ensuring that it contains the correct headers and data types. This is a simple CSV validator that uses pydantic to validate the CSV file against a predefined schema. If there are errors, it will return a list of the errors along with the row number and column name, so they're easy to display to a user or log.

## Usage

```python

from csv_validator import IterValidator, CsvReader

class MySchema:
    name: str
    age: int
    email: str

csv_file_path = 'path/to/your/file.csv'

reader = CsvReader(file=csv_file_path)
validator = IterValidator(schema=MySchema, reader=reader)
data, errors = validator.validate_all(reader=reader)
```


## Benchmarks

The benchmark notebook can be found [here](/src/csv_validator/benchmark.ipynb).

| Benchmark | Dataset | Time (seconds) | Rows per second (rps) |
|-----------|----------------|----------------|------------------|
| PandasValidator | 1m | 5.46 s ± 101 ms per loop | 183,150rps
| PolarsValidator | 1m | 1.68 s ± 8.25 ms per loop | 595,238rps
| SlowerIterValidator | 1m | 1.37 s ± 3.65 ms per loop | 729,927rps
| IterValidator (using `model_dump`) | 1m | 1.22 s ± 8.51 ms per loop | 819,672rps
| IterValidator (using pydantic-code `SchemaValidator`) | 1m | 1.03 s ± 94.3 ms per loop | 970,873rps
