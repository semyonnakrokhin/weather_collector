class SessionNotSetError(Exception):
    """Exception raised when no session is set in the repository."""


class RepositoryValidationException(Exception):
    pass


class InvalidDesignationError(Exception):
    def __init__(self, designation: str):
        self.designation = designation
        super().__init__(f"Invalid designation: {designation}")
