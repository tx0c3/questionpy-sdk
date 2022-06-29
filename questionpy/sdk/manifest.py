from pydantic import BaseModel


class Manifest(BaseModel):
    name: str
    version: str
    api_version: str
    entrypoint: str
