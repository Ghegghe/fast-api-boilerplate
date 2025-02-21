from enum import Enum


class VehicleBrand(str, Enum):
    nissan = "nissan"
    mercedes = "mercedes"
    honda = "honda"
    audi = "audi"
    fiat = "fiat"


class UserRoleEnum(str, Enum):
    admin = "admin"
    user = "user"
