import pytest
import time
from typing import Optional
import numpy as np

from src.models.core.hex_game import HexGame, TimedHexGame
from src.models.core.hex_board import HexBoard, MemoryHexBoard
from src.models.core.hex_cell import HexCell
from src.models.core.hex_move import HexMove
from src.models.core.interfaces import GameEndReason, HexState
from src.models.core.hex_state import NotStartedState, ActiveState, PausedState, FinishedState, CorruptedState
from src.models.core.exceptions import (
    GameOverError, NotPlayerTurnError, InvalidCellError,
    BoardFullError, CellAlreadyOccupiedError
)

@pytest.fixture
def empty_game():
    """Fixture to provide a fresh empty game for each test."""
    return HexGame(HexBoard(3))

@pytest.fixture
def memory_game():
    """Fixture to provide a fresh empty memory game for each test."""
    return HexGame(MemoryHexBoard(3))

@pytest.fixture
def timed_game():
    """Fixture to provide a fresh timed game for each test."""
    return TimedHexGame(HexGame(HexBoard(3)), initial_time=300.0)

def test_game_initialization():
    """Test game initialization with different board sizes."""
    for size in [3, 5, 11, 255]:  # Valid sizes
        game = HexGame(HexBoard(size))
        assert game.board.size == size
        assert isinstance(game.state, NotStartedState)
        assert game.game_end_reason is None
        assert game.winner is None
        assert game.start_time is None
        assert game.end_time is None
        assert game.total_pause_duration == 0.0

def test_invalid_board_size():
    """Test game initialization with invalid board sizes."""
    for size in [0, 1, 2, 256, 1000]:  # Invalid sizes
        with pytest.raises(ValueError, match="Board size must be between 3 and 255"):
            HexGame(HexBoard(size))

def test_game_states(empty_game):
    """Test game state transitions."""
    # Start game
    empty_game.start_game()
    assert isinstance(empty_game.state, ActiveState)
    assert empty_game.start_time is not None

    # Pause game
    empty_game.pause_game()
    assert isinstance(empty_game.state, PausedState)
    assert empty_game._last_pause_start_time is not None

    # Resume game
    empty_game.resume_game()
    assert isinstance(empty_game.state, ActiveState)
    assert empty_game._last_pause_start_time is not None

    # End game
    empty_game.end_game(GameEndReason.VICTORY)
    assert isinstance(empty_game.state, FinishedState)
    assert empty_game.game_end_reason == GameEndReason.VICTORY
    assert empty_game.end_time is not None

    # Corrupt game
    empty_game.corrupt_game()
    assert isinstance(empty_game.state, CorruptedState)
    assert empty_game.game_end_reason == GameEndReason.VICTORY

def test_make_moves(empty_game):
    """Test making moves in a game."""
    empty_game.start_game()
    
    # First move (blue)
    move1 = HexMove(HexCell(0, 0))
    assert empty_game.make_move(move1)
    assert empty_game.get_current_player() == empty_game.RED_PLAYER
    assert empty_game.board.get_player_at(HexCell(0, 0)) == empty_game.BLUE_PLAYER
    
    # Second move (red)
    move2 = HexMove(HexCell(1, 1))
    assert empty_game.make_move(move2)
    assert empty_game.get_current_player() == empty_game.BLUE_PLAYER
    assert empty_game.board.get_player_at(HexCell(1, 1)) == empty_game.RED_PLAYER

def test_invalid_moves(empty_game):
    """Test various invalid move scenarios."""
    empty_game.start_game()
    
    # Move out of bounds
    with pytest.raises(InvalidCellError):
        empty_game.make_move(HexMove(HexCell(3, 0)))
    
    # Move to occupied cell
    move1 = HexMove(HexCell(0, 0))
    empty_game.make_move(move1)
    with pytest.raises(CellAlreadyOccupiedError):
        empty_game.make_move(HexMove(HexCell(0, 0)))
    
    # Move after game is over
    empty_game.end_game(GameEndReason.VICTORY)
    with pytest.raises(GameOverError):
        empty_game.make_move(HexMove(HexCell(1, 1)))

def test_win_detection():
    """Test win detection in different scenarios."""
    # Blue win (left to right)
    game = HexGame(HexBoard(3))
    game.start_game()
    moves = [
        HexMove(HexCell(0, 0)),  # Blue
        HexMove(HexCell(0, 1)),  # Red
        HexMove(HexCell(1, 0)),  # Blue
        HexMove(HexCell(1, 1)),  # Red
        HexMove(HexCell(2, 0))   # Blue
    ]
    for move in moves:
        game.make_move(move)
    assert game.winner == game.BLUE_PLAYER
    assert game.game_end_reason == GameEndReason.VICTORY
    
    # Red win (top to bottom)
    game = HexGame(HexBoard(3))
    game.start_game()
    moves = [
        HexMove(HexCell(0, 0)),  # Blue
        HexMove(HexCell(1, 0)),  # Red
        HexMove(HexCell(0, 1)),  # Blue
        HexMove(HexCell(1, 1)),  # Red
        HexMove(HexCell(0, 2)),  # Blue
        HexMove(HexCell(1, 2))   # Red
    ]
    for move in moves:
        game.make_move(move)
    assert game.winner == game.RED_PLAYER
    assert game.game_end_reason == GameEndReason.VICTORY

def test_game_duration(empty_game):
    """Test game duration calculation."""
    empty_game.start_game()
    start_time = empty_game.start_time
    
    # Simulate some game time
    time.sleep(0.1)
    duration = empty_game.get_duration()
    assert duration is not None
    assert duration > 0
    
    # Pause and resume
    empty_game.pause_game()
    time.sleep(0.1)
    empty_game.resume_game()
    time.sleep(0.1)
    
    # End game
    empty_game.end_game(GameEndReason.VICTORY)
    final_duration = empty_game.get_duration()
    assert final_duration is not None
    assert final_duration > duration

def test_resignation(empty_game):
    """Test game resignation."""
    empty_game.start_game()
    
    # Blue resigns
    empty_game.resign_game(empty_game.BLUE_PLAYER)
    assert empty_game.winner == empty_game.RED_PLAYER
    assert empty_game.game_end_reason == GameEndReason.RESIGN
    
    # Red resigns
    game = HexGame(HexBoard(3))
    game.start_game()
    game.resign_game(game.RED_PLAYER)
    assert game.winner == game.BLUE_PLAYER
    assert game.game_end_reason == GameEndReason.RESIGN

def test_draw_game(empty_game):
    """Test game draw."""
    empty_game.start_game()
    empty_game.draw_game()
    assert empty_game.winner is None
    assert empty_game.game_end_reason == GameEndReason.DRAW

def test_timed_game(timed_game):
    """Test timed game functionality."""
    timed_game.start_game()
    
    # Check initial timers
    assert timed_game.player_timers[timed_game.BLUE_PLAYER] == 300.0
    assert timed_game.player_timers[timed_game.RED_PLAYER] == 300.0
    
    # Make a move and check timer update
    time.sleep(0.5)
    move = HexMove(HexCell(0, 0))
    timed_game.make_move(move)
    assert timed_game.player_timers[timed_game.BLUE_PLAYER] < 300.0
    
    # Check overtime
    assert not timed_game.check_overtime()  # Should not be overtime yet

def test_full_board():
    """Test behavior when board is full."""
    game = HexGame(HexBoard(3))
    game.start_game()
    
    # Fill the board
    moves = [
        HexMove(HexCell(0, 0)), HexMove(HexCell(0, 1)), HexMove(HexCell(0, 2)),
        HexMove(HexCell(1, 0)), HexMove(HexCell(1, 1)), HexMove(HexCell(1, 2)),
        HexMove(HexCell(2, 0)), HexMove(HexCell(2, 1)), HexMove(HexCell(2, 2))
    ]
    
    for move in moves:
        game.make_move(move)
    
    assert game.board.is_full()
    with pytest.raises(GameOverError):
        game.make_move(HexMove(HexCell(0, 0)))

def test_memory_game(memory_game):
    """Test memory game functionality."""
    memory_game.start_game()
    
    # Make some moves
    moves = [
        HexMove(HexCell(0, 0)),  # Blue
        HexMove(HexCell(1, 1)),  # Red
        HexMove(HexCell(2, 2))   # Blue
    ]
    
    for move in moves:
        memory_game.make_move(move)
    
    # Check board state
    state = memory_game.board.get_board_state()
    assert isinstance(state, np.ndarray)
    assert state.shape == (3, 3)
    assert state[0, 0] == memory_game.BLUE_PLAYER
    assert state[1, 1] == memory_game.RED_PLAYER
    assert state[2, 2] == memory_game.BLUE_PLAYER

def test_game_state_persistence(empty_game):
    """Test game state persistence through state transitions."""
    # Start game
    empty_game.start_game()
    assert isinstance(empty_game.state, ActiveState)
    assert empty_game.start_time is not None
    
    # Make some moves
    moves = [
        HexMove(HexCell(0, 0)),  # Blue
        HexMove(HexCell(1, 1))   # Red
    ]
    for move in moves:
        empty_game.make_move(move)
    
    # Pause game
    empty_game.pause_game()
    assert isinstance(empty_game.state, PausedState)
    assert empty_game._last_pause_start_time is not None
    
    # Resume game
    empty_game.resume_game()
    assert isinstance(empty_game.state, ActiveState)
    assert empty_game._last_pause_start_time is not None
    
    # End game
    empty_game.end_game(GameEndReason.VICTORY)
    assert isinstance(empty_game.state, FinishedState)
    assert empty_game.game_end_reason == GameEndReason.VICTORY
    assert empty_game.end_time is not None
    
    # Verify board state is preserved
    assert empty_game.board.get_player_at(HexCell(0, 0)) == empty_game.BLUE_PLAYER
    assert empty_game.board.get_player_at(HexCell(1, 1)) == empty_game.RED_PLAYER 