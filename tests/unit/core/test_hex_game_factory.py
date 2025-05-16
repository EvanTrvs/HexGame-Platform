import pytest
import time
from typing import Optional
import numpy as np

from src.models.core.hex_game_factory import HexGameFactory
from src.models.core.hex_game import HexGame, TimedHexGame
from src.models.core.hex_board import HexBoard, MemoryHexBoard
from src.models.core.hex_cell import HexCell
from src.models.core.hex_move import HexMove
from src.models.core.interfaces import GameEndReason, HexState
from src.models.core.exceptions import InvalidGameStateError
from src.models.core.hex_state import NotStartedState, ActiveState, PausedState, FinishedState, CorruptedState

@pytest.fixture
def sample_game():
    """Fixture to provide a sample game for testing."""
    game = HexGame(HexBoard(3))
    game.start_game()
    game.make_move(HexMove(HexCell(0, 0)))  # Blue
    game.make_move(HexMove(HexCell(1, 1)))  # Red
    return game

def test_create_basic_game():
    """Test creating a basic HexGame."""
    game = HexGameFactory.create_game(board_size=3)
    assert isinstance(game, HexGame)
    assert game.board.size == 3
    assert isinstance(game.board, HexBoard)
    assert isinstance(game.state, NotStartedState)
    assert game.game_end_reason is None
    assert game.winner is None

def test_create_memory_game():
    """Test creating a game with MemoryHexBoard."""
    game = HexGameFactory.create_game(board_size=3, use_memory_board=True)
    assert isinstance(game, HexGame)
    assert game.board.size == 3
    assert isinstance(game.board, MemoryHexBoard)

def test_create_timed_game():
    """Test creating a timed game."""
    game = HexGameFactory.create_game(board_size=3, initial_time=300.0)
    assert isinstance(game, TimedHexGame)
    assert game.board.size == 3
    assert game.player_timers[game.BLUE_PLAYER] == 300.0
    assert game.player_timers[game.RED_PLAYER] == 300.0

def test_create_game_with_custom_timers():
    """Test creating a timed game with custom timers."""
    game = HexGameFactory.create_game(
        board_size=3,
        initial_time=300.0,
        blue_player_timer=250.0,
        red_player_timer=200.0
    )
    assert isinstance(game, TimedHexGame)
    assert game.player_timers[game.BLUE_PLAYER] == 250.0
    assert game.player_timers[game.RED_PLAYER] == 200.0

def test_create_game_with_state():
    """Test creating a game with specific state."""
    game = HexGameFactory.create_game(
        board_size=3,
        state=ActiveState(),
        start_time=time.time()
    )
    assert isinstance(game.state, ActiveState)
    assert game.start_time is not None

def test_create_game_with_end_condition():
    """Test creating a game with end condition."""
    game = HexGameFactory.create_game(
        board_size=3,
        game_end_reason=GameEndReason.VICTORY,
        winner=HexGame.BLUE_PLAYER,
        end_time=time.time()
    )
    assert game.game_end_reason == GameEndReason.VICTORY
    assert game.winner == HexGame.BLUE_PLAYER
    assert game.end_time is not None

def test_create_game_from_existing(sample_game):
    """Test creating a game from an existing game."""
    new_game = HexGameFactory.create_game(
        board_size=3,
        existing_game=sample_game
    )
    assert isinstance(new_game, HexGame)
    assert new_game.board.size == sample_game.board.size
    assert new_game.state, sample_game.state
    assert new_game.board.get_total_moves() == sample_game.board.get_total_moves()

def test_create_memory_game_from_existing(sample_game):
    """Test creating a memory game from an existing game."""
    # Get the original board state
    original_state = sample_game.board.get_board_state()
    
    # Create new game with memory board
    new_game = HexGameFactory.create_game(
        board_size=3,
        existing_game=sample_game,
        use_memory_board=True
    )
    
    # Verify game type and board type
    assert isinstance(new_game, HexGame)
    assert isinstance(new_game.board, MemoryHexBoard)
    
    # Verify board state is preserved
    new_state = new_game.board.get_board_state()
    assert np.array_equal(original_state, new_state)
    
    # Verify moves are preserved
    assert new_game.board.get_total_moves() == sample_game.board.get_total_moves()
    
    # Verify specific cells
    assert new_game.board.get_player_at(HexCell(0, 0)) == sample_game.BLUE_PLAYER
    assert new_game.board.get_player_at(HexCell(1, 1)) == sample_game.RED_PLAYER

def test_create_timed_game_from_existing(sample_game):
    """Test creating a timed game from an existing game."""
    new_game = HexGameFactory.create_game(
        board_size=3,
        existing_game=sample_game,
        initial_time=300.0
    )
    assert isinstance(new_game, TimedHexGame)
    assert new_game.board.get_total_moves() == sample_game.board.get_total_moves()
    assert new_game.player_timers[new_game.BLUE_PLAYER] >= 300.0 - 1

def test_convert_to_timed_game(sample_game):
    """Test converting a game to a timed game."""
    timed_game = HexGameFactory.convert_to_timed_game(
        sample_game,
        initial_time=300.0
    )
    assert isinstance(timed_game, TimedHexGame)
    assert timed_game.board.get_total_moves() == sample_game.board.get_total_moves()
    assert timed_game.player_timers[timed_game.BLUE_PLAYER] >= 300.0 - 1

def test_convert_to_hex_game():
    """Test converting a timed game back to a regular game."""
    timed_game = TimedHexGame(HexGame(HexBoard(3)), initial_time=300.0)
    game = HexGameFactory.convert_to_hex_game(timed_game)
    assert isinstance(game, HexGame)
    assert not isinstance(game, TimedHexGame)

def test_change_board(sample_game):
    """Test changing the board of a game."""
    new_board = MemoryHexBoard(3)
    game = HexGameFactory.change_board(sample_game, new_board)
    assert game.board == new_board
    assert isinstance(game.board, MemoryHexBoard)

def test_invalid_board_size():
    """Test creating a game with invalid board size."""
    with pytest.raises(ValueError, match="Board size must be provided"):
        HexGameFactory.create_game(board_size=None)

    with pytest.raises(ValueError, match="Board size must be between 3 and 255"):
        HexGameFactory.create_game(board_size=2)

def test_invalid_existing_game():
    """Test creating a game with invalid existing game."""
    with pytest.raises(InvalidGameStateError, match="The provided game is not a HexGame instance"):
        HexGameFactory.create_game(board_size=3, existing_game="not a game")

def test_create_game_with_pause_state():
    """Test creating a game with pause state and duration."""
    pause_start = time.time()
    game = HexGameFactory.create_game(
        board_size=3,
        state=PausedState(),
        total_pause_duration=10.0,
        last_pause_start_time=pause_start
    )
    assert isinstance(game.state, PausedState)
    assert game.total_pause_duration == 10.0
    assert game._last_pause_start_time == pause_start

def test_create_game_with_full_state():
    """Test creating a game with all possible state parameters."""
    start_time = time.time()
    end_time = start_time + 100
    game = HexGameFactory.create_game(
        board_size=3,
        state=FinishedState(),
        game_end_reason=GameEndReason.VICTORY,
        winner=HexGame.BLUE_PLAYER,
        start_time=start_time,
        end_time=end_time,
        total_pause_duration=10.0,
        last_pause_start_time=start_time + 50
    )
    assert isinstance(game.state, FinishedState)
    assert game.game_end_reason == GameEndReason.VICTORY
    assert game.winner == HexGame.BLUE_PLAYER
    assert game.start_time == start_time
    assert game.end_time == end_time
    assert game.total_pause_duration == 10.0
    assert game._last_pause_start_time == start_time + 50

def test_create_from_file_not_implemented():
    """Test that create_from_file raises NotImplementedError."""
    with pytest.raises(NotImplementedError, match="File parsing logic is not implemented"):
        HexGameFactory.create_from_file("test.txt") 