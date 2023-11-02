class ValidationError(Exception):
    """Your struct doesn't match requirements"""


class WritingError(Exception):
    """Something went wrong while write on resourse"""


class DataNotFoundError(Exception):
    """No such data you looking for"""
