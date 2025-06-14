import cProfile

from pydantic import BaseModel

from csv_validator.validator import CsvReader, IterValidator


class BenchmarkSchema(BaseModel):
    a: int
    b: str
    c: float


def main():
    filename = "src/csv_validator/benchmark_1m.csv"
    csv_reader = CsvReader(filename)
    v = IterValidator(BenchmarkSchema, csv_reader)
    with cProfile.Profile() as pr:
        for _ in range(10):
            v.validate_all()
    pr.dump_stats("benchmark_1m.prof")


def print_profile():
    import pstats

    p = pstats.Stats("benchmark_1m.prof")
    p.strip_dirs().sort_stats("time").print_stats(10)


if __name__ == "__main__":
    print_profile()
    # main()
