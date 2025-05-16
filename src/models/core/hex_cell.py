import numpy as np

class HexCell:
    """
    Represents a cell on the Hex board with x and y coordinates.
    Immutable to ensure thread safety and prevent accidental modifications.
    """
    __slots__ = ('_x', '_y')

    def __init__(self, x: int, y: int):
        """Initialize the HexCell with x and y coordinates."""
        if not (0 <= x <= 255):
            raise ValueError("x coordinate must be between 0 and 255")
        if not (0 <= y <= 255):
            raise ValueError("y coordinate must be between 0 and 255")

        self._x = np.uint8(x)
        self._y = np.uint8(y)

    @property
    def x(self) -> int:
        """Get the x coordinate of the cell."""
        return int(self._x)

    @property
    def y(self) -> int:
        """Get the y coordinate of the cell."""
        return int(self._y)

    def __repr__(self):
        return f"HexCell(x={self.x}, y={self.y})"

    def __eq__(self, other):
        if isinstance(other, HexCell):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return hash((self.x, self.y))
