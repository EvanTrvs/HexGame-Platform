"""
Core module for the Hex game.
This module contains the fundamental elements of the game such as cells, board, moves, and game logic.
"""

from .interfaces import IHexMove, IHexBoard, IHexGame, GameEndReason, HexState, IHexState

from .hex_cell import HexCell
from .hex_move import HexMove
from .hex_win_detector import HexWinDetector
from .hex_board import HexBoard, MemoryHexBoard
from .hex_state import NotStartedState, ActiveState, PausedState, FinishedState, CorruptedState
from .hex_game import HexGame, TimedHexGame
from .hex_game_factory import HexGameFactory

from .exceptions import HexGameError, InvalidMoveError, GameOverError, NotPlayerTurnError, InvalidPlayerError, TimeoutError, BoardFullError, InvalidCellError, CellAlreadyOccupiedError, InvalidStateTransition

__all__ = [
    # Core classes
    'HexCell',
    'HexMove',
    'HexWinDetector',
    'HexBoard',
    'MemoryHexBoard',
    'HexGame',
    'TimedHexGame',
    
    # State classes
    'HexState',
    'NotStartedState',
    'ActiveState',
    'PausedState',
    'FinishedState',
    'CorruptedState',
    'GameEndReason',
    
    # Interfaces
    'IHexMove',
    'IHexBoard',
    'IHexGame',
    'IHexState',
    
    # Factory
    'HexGameFactory',
    
    # Exceptions
    'HexGameError',
    'InvalidMoveError',
    'GameOverError',
    'NotPlayerTurnError',
    'InvalidPlayerError',
    'TimeoutError',
    'BoardFullError',
    'InvalidCellError',
    'CellAlreadyOccupiedError',
    'InvalidStateTransition'
]