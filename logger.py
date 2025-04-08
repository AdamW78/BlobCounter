import logging

__LOGGER__ = logging.getLogger(__name__)
logging.basicConfig()
__LOGGER__.setLevel(logging.DEBUG)


def LOGGER():
    return __LOGGER__