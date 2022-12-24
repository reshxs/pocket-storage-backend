from fastapi_jsonrpc import BaseError


class WrongCredentials(BaseError):
    CODE = 1001
    MESSAGE = "Wrong credentials"


class AccessDenied(BaseError):
    CODE = 1002
    MESSAGE = "Access denied"


class WarehouseAlreadyExists(BaseError):
    CODE = 2001
    MESSAGE = "Warehouse already exists"


class ProductCategoryAlreadyExists(BaseError):
    CODE = 3001
    MESSAGE = "Product category already exists"


class ProductCategoryNotFound(BaseError):
    CODE = 3002
    MESSAGE = "Product category not found"


class ProductAlreadyExists(BaseError):
    CODE = 4001
    MESSAGE = "Product already exists"


class ProductNotFound(BaseError):
    CODE = 4002
    MESSAGE = "Product not found"


class EmployeePositionAlreadyExists(BaseError):
    CODE = 5001
    MESSAGE = "Employee position already exists"


class EmployeePositionNotFound(BaseError):
    CODE = 5002
    MESSAGE = "Employee position not found"


class EmployeeNotFound(BaseError):
    CODE = 6002
    MESSAGE = "Employee not found"
