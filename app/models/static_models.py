from enum import Enum

class Roles(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Category(str, Enum):
    ELECTRONICS = "electronics",
    FASHON = "fashion",
    FOOD = "food",
    HOME = "home",
    SPORTS = "sports",
    TOYS = "toys",
    VIDEOGAMES = "videogames",
    BOOKS = "books",
    SERVICES = "services"
    