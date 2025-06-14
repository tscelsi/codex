import os


def pytest_configure():
    os.environ["PYTEST"] = "true"
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_USER"] = "root"
    os.environ["DB_PASS"] = "password"
