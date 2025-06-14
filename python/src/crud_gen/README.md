Is it more important to have a way to generate crud routers? Or is it better to specify some paradigms under which most APIs should be built? maybe the latter as it allows for more flexibility and conscious choices.

And in fact, that is where we will start. By outlining some API design choices that are more often than not, useful to implement. Then, if we need to, we can create a crud router generator as specified below.

# Coding principles

- Buy-in to technologies that you like. There's no shame in committing to something that you find useful/performant.
  - learn small set of tools well - Flume
  - buy-in to fastapi
  - buy-in to pydantic

# API Principles
- OpenAPI
  - double down on this - useful for extending APIs to SDKs etc.
- Pagination
  - when listing, always use pagination
  - slack pagination is good example of cursor-based - b64 encode
- Response model
  - what should it look like?
  - what shouldn't it look like?
    - conforming to openAPI spec means we shouldn't really have dynamic keys in response
- Sorting
  - Allow sorting on useful fields only - not all fields. Ensuring that sorting is performant through the use of indexes etc.
  - goes hand-in-hand with pagination


## Response Model

This is an enumeration of all possible response fields:

```json
{
  "<resource>": [],
  "errors": [],
  "response_metadata": {
    "total": 100,
    "page": 1,
    "limit": 10,
    "count": 10,
    "links_": [],
    "next_cursor": "asbLkIwjalk="
    }
}
```

### Successful paginated response

A successful paginated response looks like:

```json
{
  "<resource>": [...],
  "response_metadata": {
    "total": 100,
    "page": 1,
    "limit": 10,
    "count": 10,
    "refs": []
    }
}
```

or if using cursor pagination

```json
{
  "<resource>": [...],
  "response_metadata": {
    "next_cursor": "asbLkIwjalk="
  }
}
```

### Successful unpaginated response

A successful unpaginated response looks like:

```json
{
  "<resource>": {...},
  "response_metadata": {}
}
```

### Error response model

An error response looks like:

```json
{
  "errors": [...],
  "response_metadata": {}
}
```

# CRUD-gen

A crud generator for a FastAPI route.

Pass a schema file to the generator and it will generate a CRUD application with the following features:
- Create, Read, Update, Delete operations
- Pagination
- Sorting
- Filtering
- Search

## Server

```python
from crud_gen import Router
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

r = Router(prefix="/user", schema=User)
```

This will generate a CRUD application with the following endpoints:
- `POST /user`: Create a new user
- `GET /user`: Get a list of users with pagination, sorting, filtering, and search
- `GET /user/{id}`: Get a user by id
- `PUT /user/{id}`: Update a user by id
- DELETE /user/{id}`: Delete a user by id
- `GET /user/search`: Search for users by parameters

#### Insert

INSERT INTO users (id, name, email) VALUES :values

#### List

Maybe want some automatic filters, although this can be done with row-level-security.

SELECT * FROM users

#### Get

SELECT * FROM users WHERE id = :id

#### Update

Don't want to update all fields. definitely not the PK.

UPDATE users SET name = :name, email = :email WHERE id = :id

#### Delete

DELETE FROM users WHERE id = :id


## Outstanding questions

1. What about expanding FK relationships? Is it strictly needed?
2. 


Components of an API
1. Pagination
2. Response model

## Client

Autogenerate client based on openAPI