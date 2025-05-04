from enum import Enum, auto


class ProgramStatus(Enum):
    MAX_POSTS = auto()
    MAX_POSTS_PER_RUN = auto()
    MAX_GOOD_USER_STREAK = auto()
    NO_POST_FOUND = auto()
    NO_MORE_POSTS_FOUND = auto()
    NO_USERNAME = auto()
    NO_USER_STATUS = auto()
