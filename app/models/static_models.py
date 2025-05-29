from enum import Enum

class Roles(Enum):
    ADMIN = "admin"
    CLIENT = "client"

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"