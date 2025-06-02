from enum import Enum

class Roles(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"