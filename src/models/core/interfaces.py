from abc import ABC, abstractmethod
from typing import Optional, Set, Dict, List
from enum import Enum, auto
import numpy as np

from .hex_cell import HexCell


# Enum for game end reasons
class GameEndReason(Enum):
    NOT_FINISHED = auto()
    RESIGN = auto()
    OVERTIME = auto()
    VICTORY = auto()
    DRAW = auto()
    CORRUPTED = auto()


# Enum for game states
class HexState(Enum):
    NOT_STARTED = auto()
    ACTIVE = auto()
    PAUSED = auto()
    FINISHED = auto()
    CORRUPTED = auto()


class IHexMove(ABC):
    """Interface for Hex moves."""

    @property
    @abstractmethod
    def cell(self) -> HexCell:
        pass

    @property
    def timestamp(self) -> Optional[float]:
        return None


class IHexBoard(ABC):
    """Interface for the Hex game board."""

    @abstractmethod
    def add_move(self, move: IHexMove) -> bool:
        """Add a move to the board."""
        pass
    
    @property
    @abstractmethod
    def size(self) -> int:
        """Get the size lenth of the square board."""
        pass

    @abstractmethod
    def get_board_state(self) -> np.ndarray:
        """Get the current board state as a numpy array."""
        pass

    @abstractmethod
    def is_valid_move(self, cell: HexCell) -> bool:
        """Check if a move is valid."""
        pass

    @abstractmethod
    def get_last_move(self) -> Optional[IHexMove]:
        """Get the last move made on the board."""
        pass

    @abstractmethod
    def get_occupied_cells(self) -> Set[HexCell]:
        """Get the set of occupied cells."""
        pass

    @abstractmethod
    def is_full(self) -> bool:
        """Check if the board is full."""
        pass

    @abstractmethod
    def get_player_at(self, cell: HexCell) -> Optional[int]:
        """Get the player at a specific cell."""
        pass

    @abstractmethod
    def to_memory_hex_board(self) -> 'MemoryHexBoard':
        """Convert to MemoryHexBoard."""
        pass

    @abstractmethod
    def to_hex_board(self) -> 'HexBoard':
        """Convert to HexBoard."""
        pass
    
    @abstractmethod
    def get_board_state_at_move(self, move_index: int) -> np.ndarray:
        """Get the board state at a specific move index."""
        pass

    @abstractmethod
    def get_total_moves(self) -> int:
        """Get the total number of moves made."""
        pass
    
    @abstractmethod
    def get_winner(self) -> Optional[int]:
        """
        Check for a winner.

        Returns:
            Optional[int]: The value of the winning player (1 for BLUE, 2 for RED), or None if there is no winner.
        """
        pass
    
    @abstractmethod
    def get_moves(self) -> List['IHexMove']:
        """Get the list of all moves made on the board."""
        pass


# Interface for HexGameState (State Design Pattern)
class IHexState(ABC):
    @abstractmethod
    def start_game(self) -> None:
        """Start the game."""
        pass

    @abstractmethod
    def pause_game(self) -> None:
        """Pause the game."""
        pass

    @abstractmethod
    def resume_game(self) -> None:
        """Resume the game."""
        pass

    @abstractmethod
    def end_game(self, reason: GameEndReason) -> None:
        """End the game with a specific reason."""
        pass

    @abstractmethod
    def corrupt_game(self) -> None:
        """Mark the game as corrupted."""
        pass


# Interface for HexGame
class IHexGame(ABC):
    BLUE_PLAYER = 1
    RED_PLAYER = 2

    @property
    @abstractmethod
    def board(self) -> IHexBoard:
        """Get the game board."""
        pass

    @property
    @abstractmethod
    def state(self) -> IHexState:
        """Get the current state of the game."""
        pass

    @property
    @abstractmethod
    def game_end_reason(self) -> Optional[GameEndReason]:
        """Get the reason why the game ended."""
        pass

    @property
    @abstractmethod
    def winner(self) -> Optional[int]:
        """Get the winner of the game."""
        pass

    @property
    @abstractmethod
    def start_time(self) -> Optional[float]:
        """Get the start time of the game."""
        pass

    @property
    @abstractmethod
    def end_time(self) -> Optional[float]:
        """Get the end time of the game."""
        pass
    
    @property
    def total_pause_duration(self) -> Optional[float]:
        """Returns the total time the game has been paused."""
        pass

    @property
    @abstractmethod
    def player_timers(self) -> Dict[int, float]:
        """Get the timers for each player."""
        pass

    @abstractmethod
    def start_game(self) -> None:
        """Start the game."""
        pass

    @abstractmethod
    def pause_game(self) -> None:
        """Pause the game."""
        pass

    @abstractmethod
    def resume_game(self) -> None:
        """Resume the game."""
        pass

    @abstractmethod
    def end_game(self, reason: GameEndReason) -> None:
        """End the game with a specific reason."""
        pass

    @abstractmethod
    def corrupt_game(self) -> None:
        """Mark the game as corrupted."""
        pass

    @abstractmethod
    def make_move(self, move: IHexMove) -> bool:
        """Make a move on the board."""
        pass

    @abstractmethod
    def get_current_player(self) -> int:
        """Get the current player."""
        pass

    @abstractmethod
    def switch_player(self) -> None:
        """Switch to the other player."""
        pass

    @abstractmethod
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        pass

    @abstractmethod
    def resign_game(self, player: int) -> None:
        """Resign the game for a specific player."""
        pass

    @abstractmethod
    def draw_game(self) -> None:
        """End the game in a draw."""
        pass

    @abstractmethod
    def update_timers(self) -> None:
        """Update the timers for players."""
        pass

    @abstractmethod
    def get_remaining_time(self, player: int) -> float:
        """Get the remaining time for a specific player."""
        pass

    @abstractmethod
    def check_overtime(self) -> bool:
        """Check if any player has run out of time."""
        pass
