from typing import Optional, Union
import time

from .interfaces import IHexMove
from .hex_cell import HexCell

class HexMove(IHexMove):
    """
    Represents a move in the Hex game, containing the cell and a timestamp.

    Attributes:
        cell (HexCell): The cell on the Hex board.
        timestamp (float): The timestamp of the move.
    """

    __slots__ = ('_cell', '_timestamp')

    def __init__(self, cell: Union[HexCell, tuple], timestamp: Optional[float] = None):
        """
        Initialize the HexMove with a cell and an optional timestamp.

        Args:
            cell (Union[HexCell, tuple]): The cell on the Hex board, either as a HexCell object
                                          or a tuple of (x, y) coordinates.
            timestamp (Optional[float]): The timestamp of the move. Defaults to the current time.

        Raises:
            ValueError: If the cell is not a HexCell instance or a valid (x, y) tuple.
        """
        if isinstance(cell, HexCell):
            self._cell = cell
        elif isinstance(cell, tuple) and len(cell) == 2:
            self._cell = HexCell(*cell)
        else:
            raise ValueError("cell must be an instance of HexCell or a tuple of (x, y)")

        self._timestamp = timestamp if timestamp is not None else time.time()

    @property
    def cell(self) -> HexCell:
        """Get the cell of the move."""
        return self._cell

    @property
    def timestamp(self) -> float:
        """Get the timestamp of the move."""
        return self._timestamp

    def __repr__(self):
        """Return a string representation of the HexMove."""
        return f"HexMove(cell={self.cell}, timestamp={self.timestamp})"

    def __eq__(self, other):
        """Check if two HexMove objects are equal."""
        if isinstance(other, HexMove):
            return self.cell == other.cell
        return False

    def __hash__(self):
        """Return the hash of the HexMove."""
        return hash((self.cell, self.timestamp))