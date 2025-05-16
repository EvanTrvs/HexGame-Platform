import pytest
import time
from src.models.core.hex_move import HexMove
from src.models.core.hex_cell import HexCell


@pytest.mark.parametrize("cell_input,timestamp", [
    (HexCell(5, 10), None),
    ((5, 10), None),
    (HexCell(0, 0), 1234567890.0),
    ((255, 255), 1234567890.0)
])
def test_hex_move_creation(cell_input, timestamp):
    """Test valid move creation with different inputs."""
    move = HexMove(cell_input, timestamp)
    if isinstance(cell_input, HexCell):
        assert move.cell == cell_input
    else:
        assert move.cell.x == cell_input[0]
        assert move.cell.y == cell_input[1]
    
    if timestamp is None:
        assert isinstance(move.timestamp, float)
    else:
        assert move.timestamp == timestamp


@pytest.mark.parametrize("invalid_cell", [
    "not a cell",
    (1, 2, 3),  # tuple with wrong length
    [1, 2],     # list instead of tuple
    None
])
def test_hex_move_invalid_cell(invalid_cell):
    """Test move creation with invalid cell inputs."""
    with pytest.raises(ValueError, match="cell must be an instance of HexCell or a tuple of \\(x, y\\)"):
        HexMove(invalid_cell)


def test_hex_move_immutability():
    """Test that move properties cannot be modified."""
    move = HexMove((5, 10))
    with pytest.raises(AttributeError):
        move.cell = HexCell(6, 11)
    with pytest.raises(AttributeError):
        move.timestamp = 1234567890.0


@pytest.mark.parametrize("move1,move2,expected", [
    (HexMove((5, 10)), HexMove((5, 10)), True),
    (HexMove((5, 10)), HexMove((5, 11)), False),
    (HexMove((5, 10)), "not a move", False)
])
def test_hex_move_equality(move1, move2, expected):
    """Test move equality comparison."""
    assert (move1 == move2) == expected


@pytest.mark.parametrize("move1,move2,expected", [
    (HexMove((5, 10)), HexMove((5, 10)), True),
    (HexMove((5, 10)), HexMove((5, 11)), False)
])
def test_hex_move_hash(move1, move2, expected):
    """Test move hashing."""
    assert (hash(move1) == hash(move2)) == expected
    
    # Test that moves can be used in a set
    moves = {move1, move2}
    assert len(moves) == (1 if expected else 2)


@pytest.mark.parametrize("cell,timestamp,expected_repr", [
    (HexCell(5, 10), None, "HexMove(cell=HexCell(x=5, y=10), timestamp="),
    ((5, 10), 1234567890.0, "HexMove(cell=HexCell(x=5, y=10), timestamp=1234567890.0)")
])
def test_hex_move_repr(cell, timestamp, expected_repr):
    """Test string representation."""
    move = HexMove(cell, timestamp)
    if timestamp is None:
        assert expected_repr in repr(move)
    else:
        assert repr(move) == expected_repr


def test_hex_move_timestamp_generation():
    """Test automatic timestamp generation."""
    before = time.time()
    move = HexMove((5, 10))
    after = time.time()
    
    assert isinstance(move.timestamp, float)
    assert before <= move.timestamp <= after 