from enum import Enum


class FollowerStatus(Enum):
    FOLLOWING = 1
    FOLLOWING_BY_NETWORK = 2
    NOT_FOLLOWING = 3
    ERROR = 4
