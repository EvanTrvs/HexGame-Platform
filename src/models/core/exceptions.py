class HexGameError(Exception):
    """Base class for all Hex game exceptions."""
    pass

class InvalidMoveError(HexGameError):
    """Raised when an invalid move is attempted."""
    pass

class GameOverError(HexGameError):
    """Raised when attempting to make a move in a finished game."""
    pass

class NotPlayerTurnError(HexGameError):
    """Raised when a player tries to move out of turn."""
    pass

class InvalidPlayerError(HexGameError):
    """Raised when an invalid player is referenced."""
    pass

class TimeoutError(HexGameError):
    """Raised when a player's time runs out."""
    pass

class BoardFullError(HexGameError):
    """Raised when attempting to make a move on a full board."""
    pass

class InvalidCellError(Exception):
    """Exception raised when a cell is out of the board boundaries."""
    pass

class CellAlreadyOccupiedError(Exception):
    """Exception raised when a cell is already occupied."""
    pass

class InvalidStateTransition(Exception):
    """Exception raised for invalid state transitions."""
    pass

class InvalidGameStateError(HexGameError):
    """Exception raised when an invalid game state is encountered."""
    pass

