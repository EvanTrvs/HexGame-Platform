class GameManagementError(Exception):
    """Base exception for game management errors."""
    pass

class CommandExecutionError(GameManagementError):
    """Exception raised when a command fails to execute."""
    pass

class InvalidPlayerError(GameManagementError):
    """Exception raised when an invalid player is specified."""
    pass

class GameNotStartedError(GameManagementError):
    """Exception raised when trying to perform an action on a game that hasn't started."""
    pass

class GameAlreadyStartedError(GameManagementError):
    """Exception raised when trying to start a game that is already running."""
    pass

class InvalidCommandError(GameManagementError):
    """Exception raised when an invalid command is provided."""
    pass

class PlayerNotAttachedError(GameManagementError):
    """Exception raised when a player tries to perform an action without being attached to a game."""
    pass 