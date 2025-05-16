import pytest
import numpy as np
from src.models.core.hex_board import HexBoard, MemoryHexBoard
from src.models.core.hex_cell import HexCell
from src.models.core.hex_move import HexMove
from src.models.core.exceptions import InvalidCellError, BoardFullError, CellAlreadyOccupiedError


@pytest.fixture
def empty_board():
    """Fixture to provide a fresh empty board for each test."""
    return HexBoard(3)


@pytest.fixture
def memory_board():
    """Fixture to provide a fresh empty memory board for each test."""
    return MemoryHexBoard(3)


@pytest.mark.parametrize("size", [
    3,  # Minimum size
    5,  # Medium size
    11, # Large size
    255 # Maximum size
])
def test_board_initialization(size):
    """Test board initialization with different sizes."""
    board = HexBoard(size)
    assert board.size == size
    assert np.all(board.get_board_state() == 0)
    assert len(board.get_occupied_cells()) == 0
    assert not board.is_full()
    assert board.get_last_move() is None
    assert board.get_winner() is None


@pytest.mark.parametrize("invalid_size", [
    0, 1, 2, 256, 1000
])
def test_invalid_board_size(invalid_size):
    """Test board initialization with invalid sizes."""
    with pytest.raises(ValueError, match="Board size must be between 3 and 255"):
        HexBoard(invalid_size)


def test_add_move(empty_board):
    """Test adding valid moves to the board."""
    # First move (blue)
    move1 = HexMove(HexCell(0, 0))
    assert empty_board.add_move(move1)
    assert empty_board.get_player_at(HexCell(0, 0)) == 1
    assert len(empty_board.get_occupied_cells()) == 1
    
    # Second move (red)
    move2 = HexMove(HexCell(1, 1))
    assert empty_board.add_move(move2)
    assert empty_board.get_player_at(HexCell(1, 1)) == 2
    assert len(empty_board.get_occupied_cells()) == 2


@pytest.mark.parametrize("invalid_cell", [
    HexCell(3, 0),   # x out of bounds
    HexCell(0, 3),   # y out of bounds
])
def test_invalid_cell_moves(empty_board, invalid_cell):
    """Test adding moves with invalid cell coordinates."""
    move = HexMove(invalid_cell)
    with pytest.raises(InvalidCellError):
        empty_board.add_move(move)


def test_occupied_cell_move(empty_board):
    """Test adding a move to an already occupied cell."""
    move1 = HexMove(HexCell(0, 0))
    empty_board.add_move(move1)
    
    move2 = HexMove(HexCell(0, 0))
    with pytest.raises(CellAlreadyOccupiedError):
        empty_board.add_move(move2)


def test_full_board():
    """Test behavior when board is full."""
    board = HexBoard(3)  # Small board for testing
    moves = [
        HexMove(HexCell(0, 0)),
        HexMove(HexCell(0, 1)),
        HexMove(HexCell(1, 0)),
        HexMove(HexCell(1, 1)),
        HexMove(HexCell(2, 0)),
        HexMove(HexCell(2, 1)),
        HexMove(HexCell(2, 2)),
        HexMove(HexCell(1, 2)),
        HexMove(HexCell(0, 2)),
    ]
    
    for move in moves:
        board.add_move(move)
    
    assert board.is_full()
    with pytest.raises(BoardFullError):
        board.add_move(HexMove(HexCell(0, 0)))


def test_winner_detection():
    """Test winner detection in different scenarios."""
    # Blue win (left to right)
    board = HexBoard(3)
    moves = [
        HexMove(HexCell(0, 0)),  # Blue
        HexMove(HexCell(0, 1)),  # Red
        HexMove(HexCell(1, 0)),  # Blue
        HexMove(HexCell(1, 1)),  # Red
        HexMove(HexCell(2, 0))   # Blue
    ]
    for move in moves:
        board.add_move(move)
    assert board.get_winner() == 1
    
    # Red win (top to bottom)
    board = HexBoard(3)
    moves = [
        HexMove(HexCell(0, 0)),  # Blue
        HexMove(HexCell(0, 1)),  # Red
        HexMove(HexCell(2, 2)),  # Blue
        HexMove(HexCell(0, 2)),  # Red
        HexMove(HexCell(2, 0)),  # Blue
        HexMove(HexCell(1, 0)),   # Red
        HexMove(HexCell(2, 1)),  # Blue
        HexMove(HexCell(1, 1))   # Red
    ]
    for move in moves:
        board.add_move(move)
    assert board.get_winner() == 2


def test_board_state_at_move():
    """Test getting board state at specific move indices."""
    board = HexBoard(3)
    moves = [
        HexMove(HexCell(0, 0)),  # Blue
        HexMove(HexCell(1, 1)),  # Red
        HexMove(HexCell(2, 2))   # Blue
    ]
    
    for move in moves:
        board.add_move(move)
    
    # Check state after first move
    state1 = board.get_board_state_at_move(1)
    assert isinstance(state1, np.ndarray)
    assert state1.shape == (3, 3)
    assert state1[0, 0] == 1  # Blue
    assert np.sum(state1) == 1
    
    # Check state after second move
    state2 = board.get_board_state_at_move(2)
    assert isinstance(state2, np.ndarray)
    assert state2.shape == (3, 3)
    assert state2[0, 0] == 1  # Blue
    assert state2[1, 1] == 2  # Red
    assert np.sum(state2) == 3
    
    # Check current state
    current_state = board.get_board_state()
    assert isinstance(current_state, np.ndarray)
    assert current_state.shape == (3, 3)
    assert current_state[0, 0] == 1  # Blue
    assert current_state[1, 1] == 2  # Red
    assert current_state[2, 2] == 1  # Blue
    assert np.sum(current_state) == 4


def test_empty_board_state():
    """Test board state of an empty board."""
    board = HexBoard(3)
    state = board.get_board_state()
    assert isinstance(state, np.ndarray)
    assert state.shape == (3, 3)
    assert np.all(state == 0)
    assert np.sum(state) == 0


def test_full_board_state():
    """Test board state of a full board."""
    board = HexBoard(3)
    # Fill the board with alternating moves
    for i in range(3):
        for j in range(3):
            board.add_move(HexMove(HexCell(i, j)))
    
    state = board.get_board_state()
    assert isinstance(state, np.ndarray)
    assert state.shape == (3, 3)
    assert np.count_nonzero(state) == 9  # All cells are occupied
    # Check pattern of alternating players
    for i in range(3):
        for j in range(3):
            expected = 1 if (i + j) % 2 == 0 else 2
            assert state[i, j] == expected


def test_memory_board_conversion(empty_board):
    """Test conversion between HexBoard and MemoryHexBoard."""
    # Add some moves
    moves = [
        HexMove(HexCell(0, 0)),
        HexMove(HexCell(1, 1))
    ]
    for move in moves:
        empty_board.add_move(move)
    
    # Convert to memory board
    memory_board = empty_board.to_memory_hex_board()
    assert isinstance(memory_board, MemoryHexBoard)
    assert memory_board.size == empty_board.size
    assert len(memory_board.get_moves()) == len(empty_board.get_moves())
        
    # Convert back
    new_board = memory_board.to_hex_board()
    
    assert isinstance(new_board, HexBoard)
    assert new_board.size == empty_board.size
    assert len(new_board.get_moves()) == len(empty_board.get_moves())
    assert np.array_equal(new_board.get_board_state(), empty_board.get_board_state())


def test_get_player_at():
    """Test getting player at specific cells."""
    board = HexBoard(3)
    moves = [
        HexMove(HexCell(0, 0)),  # Blue
        HexMove(HexCell(1, 1))   # Red
    ]
    for move in moves:
        board.add_move(move)
    
    assert board.get_player_at(HexCell(0, 0)) == 1
    assert board.get_player_at(HexCell(1, 1)) == 2
    assert board.get_player_at(HexCell(2, 2)) is None


def test_total_moves():
    """Test getting total number of moves."""
    board = HexBoard(3)
    moves = [
        HexMove(HexCell(0, 0)),
        HexMove(HexCell(1, 1)),
        HexMove(HexCell(2, 2))
    ]
    for move in moves:
        board.add_move(move)
    
    assert board.get_total_moves() == 3 