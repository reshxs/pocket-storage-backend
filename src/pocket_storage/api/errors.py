from fastapi_jsonrpc import BaseError


class WarehouseAlreadyExists(BaseError):
    CODE = 1001
    MESSAGE = 'Склад с таким именем уже существует'
