# getting top cities


class CitiesRetrievalError(Exception):
    """Exception raised for errors during top cities retrieval."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


# ServiceManager Errors
class InvalidDesignationError(Exception):
    def __init__(self, designation: str):
        self.designation = designation
        super().__init__(f"Invalid designation: {designation}")


# Mappers Errors
class MappingError(Exception):
    pass


# Repositories Errors
class RepositoryError(Exception):
    pass


class SessionNotSetError(RepositoryError):
    """Exception raised when no session is set in the repository."""


class DatabaseError(RepositoryError):
    pass


class FileWriteError(RepositoryError):
    pass


class FileReadError(RepositoryError):
    pass


# RepositoryManager
class DatabaseRepositoriesManagerError(Exception):
    pass


class InvalidSessionTypeError(DatabaseRepositoriesManagerError):
    pass


class RepositoryNotFoundError(DatabaseRepositoriesManagerError):
    pass


# Units of work Errors
class RepositoryValidationError(Exception):
    pass


# ApiClients
class ApiClientError(Exception):
    pass


class WeatherDataError(ApiClientError):
    pass


class WeatherParsingError(ApiClientError):
    pass


class WeatherFetchingError(ApiClientError):
    pass
