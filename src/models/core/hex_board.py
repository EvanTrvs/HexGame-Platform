from typing import List, Optional, Set
import numpy as np

from .hex_cell import HexCell
from .interfaces import IHexMove, IHexBoard
from .hex_win_detector import HexWinDetector
from .exceptions import InvalidCellError, BoardFullError, CellAlreadyOccupiedError


class MemoryHexBoard(IHexBoard):
    """
    Represents the Hex game board optimized for memory storage.
    Manages the state of the board and validates moves.
    """
    EMPTY = 0
    BLUE = 1
    RED = 2

    def __init__(self, size: int):
        """
        Initialize a new Hex board.

        Args:
            size: The size of the board (n x n)

        Raises:
            ValueError: If size is not between 3 and 255
        """
        if not (3 <= size <= 255):
            raise ValueError("Board size must be between 3 and 255")
        self._size = np.uint8(size)
        self._moves: List[IHexMove] = []

    def add_move(self, move: IHexMove) -> bool:
        """
        Add a move to the board.

        Args:
            move: The move to add

        Returns:
            bool: True if the move was successfully added

        Raises:
            BoardFullError: If the board is full
            InvalidCellError: If the cell is out of the board boundaries
            CellAlreadyOccupiedError: If the cell is already occupied
        """
        if self.is_full():
            raise BoardFullError("Cannot make move: board is full")

        if not self.is_valid_move(move.cell):
            raise CellAlreadyOccupiedError(f"Cell already occupied: {move.cell}")

        self._moves.append(move)
        return True
    
    @property
    def size(self) -> int:
        return int(self._size)

    def get_board_state(self) -> np.ndarray:
        """Get the current board state as a numpy array."""
        board_state = np.zeros((self._size, self._size), dtype=np.uint8)
        for index, move in enumerate(self._moves):
            if move.cell:
                value = self.BLUE if index % 2 == 0 else self.RED
                board_state[move.cell.x, move.cell.y] = value
        return board_state

    def is_valid_move(self, cell: HexCell) -> bool:
        """
        Check if a move is valid.

        Args:
            cell: The cell to check

        Returns:
            bool: True if the move is valid

        Raises:
            InvalidCellError: If the cell coordinates are out of bounds
        """
        if not (0 <= cell.x < self._size and 0 <= cell.y < self._size):
            raise InvalidCellError(f"Cell coordinates out of bounds: {cell}")

        return all(move.cell != cell for move in self._moves)

    def get_last_move(self) -> Optional[IHexMove]:
        """Get the last move made on the board."""
        return self._moves[-1] if self._moves else None

    def get_occupied_cells(self) -> Set[HexCell]:
        """Get the set of occupied cells."""
        return {move.cell for move in self._moves if move.cell}

    def is_full(self) -> bool:
        """Check if the board is full."""
        return len(self._moves) == self._size * self._size

    def get_player_at(self, cell: HexCell) -> Optional[int]:
        """
        Get the player at a specific cell.

        Args:
            cell: The cell to check

        Returns:
            Optional[int]: The player at the cell (BLUE=1, RED=2) or None if empty

        Raises:
            InvalidCellError: If the cell coordinates are out of bounds
        """
        if not (0 <= cell.x < self._size and 0 <= cell.y < self._size):
            raise InvalidCellError(f"Cell coordinates out of bounds: {cell}")

        for index, move in enumerate(self._moves):
            if move.cell == cell:
                return self.BLUE if index % 2 == 0 else self.RED
        return None

    def to_memory_hex_board(self) -> 'MemoryHexBoard':
        """Convert to MemoryHexBoard (no-op for this class)."""
        return self

    def to_hex_board(self) -> 'HexBoard':
        """Convert to HexBoard."""
        hex_board = HexBoard(self._size)
        hex_board._memory_board = self
        hex_board._board_state = self.get_board_state()
        hex_board._occupied_cells = self.get_occupied_cells()
        hex_board._is_full = self.is_full()
        return hex_board
    
    def get_board_state_at_move(self, move_index: int) -> np.ndarray:
        """
        Get the board state at a specific move index.

        Args:
            move_index: The index of the move

        Returns:
            np.ndarray: The board state at the specified move index
        """
        if not (0 <= move_index <= len(self._moves)):
            raise ValueError("Move index out of range")

        board_state = np.zeros((self._size, self._size), dtype=np.uint8)
        for i in range(move_index):
            move = self._moves[i]
            if move.cell:
                value = self.BLUE if i % 2 == 0 else self.RED
                board_state[move.cell.x, move.cell.y] = value
        return board_state

    def get_total_moves(self) -> int:
        """Get the total number of moves made."""
        return len(self._moves)
    
    def get_winner(self) -> Optional[int]:
        """
        Check for a winner on the board using the static detector.

        Returns:
            Optional[int]: The value of the winning player (1 for BLUE, 2 for RED), or None if there is no winner.
        """
        board_state = self.get_board_state()
        return HexWinDetector.static_detect_winner(board_state)
    
    def get_moves(self) -> List[IHexMove]:
        """Get the list of all moves made on the board."""
        return self._moves.copy()
    
    
class HexBoard(IHexBoard):
    """
    Represents the Hex game board optimized for computation time.
    Manages the state of the board and validates moves.
    """
    EMPTY = 0
    BLUE = 1
    RED = 2

    def __init__(self, size: int):
        """
        Initialize a new Hex board.

        Args:
            size: The size of the board (n x n)

        Raises:
            ValueError: If size is not between 3 and 255
        """
        if not (3 <= size <= 255):
            raise ValueError("Board size must be between 3 and 255")
        self._memory_board = MemoryHexBoard(size)
        self._board_state = np.zeros((size, size), dtype=np.uint8)
        self._occupied_cells: Set[HexCell] = set()
        self._is_full = False
        self._win_detector = HexWinDetector()

    def add_move(self, move: IHexMove) -> bool:
        """
        Add a move to the board.

        Args:
            move: The move to add

        Returns:
            bool: True if the move was successfully added

        Raises:
            BoardFullError: If the board is full
            InvalidCellError: If the cell is out of the board boundaries
            CellAlreadyOccupiedError: If the cell is already occupied
        """
        if self._is_full:
            raise BoardFullError("Cannot make move: board is full")

        cell = move.cell
        if not (0 <= cell.x < self._memory_board._size and 0 <= cell.y < self._memory_board._size):
            raise InvalidCellError(f"Cell coordinates out of bounds: {cell}")

        if cell in self._occupied_cells:
            raise CellAlreadyOccupiedError(f"Cell already occupied: {cell}")
        
        # Synchronize with _memory_board
        self._memory_board._moves.append(move)

        self._occupied_cells.add(cell)
        value = self.BLUE if self._memory_board.get_total_moves() % 2 == 1 else self.RED
        self._board_state[cell.x, cell.y] = value


        if len(self._occupied_cells) == self._memory_board._size * self._memory_board._size:
            self._is_full = True

        return True
    
    @property
    def size(self) -> int:
        return self._memory_board.size

    def get_board_state(self) -> np.ndarray:
        """Get the current board state as a numpy array."""
        return self._board_state.copy()

    def is_valid_move(self, cell: HexCell) -> bool:
        """
        Check if a move is valid.

        Args:
            cell: The cell to check

        Returns:
            bool: True if the move is valid

        Raises:
            InvalidCellError: If the cell coordinates are out of bounds
            CellAlreadyOccupiedError: If the cell is already occupied
        """
        if not (0 <= cell.x < self._memory_board._size and 0 <= cell.y < self._memory_board._size):
            raise InvalidCellError(f"Cell coordinates out of bounds: {cell}")

        if cell in self._occupied_cells:
            raise CellAlreadyOccupiedError(f"Cell already occupied: {cell}")

        return True

    def get_last_move(self) -> Optional[IHexMove]:
        """Get the last move made on the board."""
        return self._memory_board.get_last_move()

    def get_occupied_cells(self) -> Set[HexCell]:
        """Get the set of occupied cells."""
        return self._occupied_cells.copy()

    def is_full(self) -> bool:
        """Check if the board is full."""
        return self._is_full

    def get_player_at(self, cell: HexCell) -> Optional[int]:
        """
        Get the player at a specific cell.

        Args:
            cell: The cell to check

        Returns:
            Optional[int]: The player at the cell (BLUE=1, RED=2) or None if empty

        Raises:
            InvalidCellError: If the cell coordinates are out of bounds
        """
        if not (0 <= cell.x < self._memory_board._size and 0 <= cell.y < self._memory_board._size):
            raise InvalidCellError(f"Cell coordinates out of bounds: {cell}")

        value = self._board_state[cell.x, cell.y]
        return value if value != self.EMPTY else None

    def to_memory_hex_board(self) -> 'MemoryHexBoard':
        """Convert to MemoryHexBoard."""
        memory_board = MemoryHexBoard(self._memory_board._size)
        memory_board._moves = self._memory_board._moves.copy()
        return memory_board

    def to_hex_board(self) -> 'HexBoard':
        """Convert to HexBoard (no-op for this class)."""
        return self
    
    def get_board_state_at_move(self, move_index: int) -> np.ndarray:
        """
        Get the board state at a specific move index.

        Args:
            move_index: The index of the move

        Returns:
            np.ndarray: The board state at the specified move index
        """
        return self._memory_board.get_board_state_at_move(move_index)

    def get_total_moves(self) -> int:
        """Get the total number of moves made."""
        return self._memory_board.get_total_moves()
    
    def get_winner(self) -> Optional[int]:
        """
        Check for a winner on the board using the cached detector.

        Returns:
            Optional[int]: The value of the winning player (1 for BLUE, 2 for RED), or None if there is no winner.
        """
        board_state = self.get_board_state()
        return self._win_detector.detect_winner(board_state)
    
    def get_moves(self) -> List[IHexMove]:
        """Get the list of all moves made on the board."""
        return self._memory_board.get_moves()