from fastapi_jsonrpc import BaseError


class WrongCredentials(BaseError):
    CODE = 1001
    MESSAGE = "Wrong credentials"


class AccessDenied(BaseError):
    CODE = 1002
    MESSAGE = "Access denied"


class WarehouseAlreadyExists(BaseError):
    CODE = 2001
    MESSAGE = "Склад с таким именем уже существует"
