# from ucall.posix import Server
from pydantic import BaseModel
from ucall.rich_posix import Server

from .validator import CsvReader, CsvValidator

# from ucall.uring import Server on 5.19+


class Schema(BaseModel):
    a: int
    b: int


server = Server()
v = CsvValidator(schema=Schema)


@server
def validate_csv(data: bytes):
    reader = CsvReader()


server.run()
