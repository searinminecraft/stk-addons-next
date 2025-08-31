class DatabaseError(Exception):
    """Database Exception"""

    pass

class UserException(Exception):
    """Base class for user-related exceptions"""

    pass


class UsernameLengthError(UserException):
    def __init__(self):
        super().__init__("Username must be between 3 and 30 characters long")


class PasswordLengthError(UserException):
    def __init__(self):
        super().__init__("Password must be between 8 and 64 characters long")


class BadPassword(UserException):
    def __init__(self):
        super().__init__((
            "Passwords may only contain ASCII letters, numbers, or any "
            "of the following characters: ! @ # $ % ^ & * \ / _ + = - { "
            "} ~ > < \" ' ; [ ] , . | `"
        ))


class InvalidEmail(UserException):
    def __init__(self):
        super().__init__("Invalid email")


class BadUsername(UserException):
    def __init__(self):
        super().__init__("Username contains one or more blacklisted words or phrases")


class InvalidUsername(UserException):
    def __init__(self):
        super().__init__(
            (
                "Usernames may only contain ASCII letters, numbers, "
                "dots (.), dashes and underscores"
            )
        )


class UsernameTaken(UserException):
    def __init__(self):
        super().__init__("This username is already taken.")


class EmailTaken(UserException):
    def __init__(self):
        super().__init__("This email is already used.")


class InvalidCredentials(UserException):
    """Raised when invalid credentials are provided"""

    def __init__(self):
        super().__init__("Username or password is invalid.")


class UserNotFound(UserException):
    """Raised when a user does not exist"""

    def __init__(self):
        super().__init__("User does not exist")


class InvalidSession(UserException):
    """Raised when a session isn't valid anymore"""

    def __init__(self):
        super().__init__("Session not valid. Please sign in.")
