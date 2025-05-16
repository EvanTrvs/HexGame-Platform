import pytest

from src.models.core.hex_cell import HexCell


@pytest.mark.parametrize("x,y", [
    (0, 0),
    (255, 255),
    (5, 10),
    (100, 200)
])
def test_hex_cell_creation(x, y):
    """Test valid cell creation and property access."""
    cell = HexCell(x, y)
    assert cell.x == x
    assert cell.y == y


def test_hex_cell_immutability():
    """Test that cell coordinates cannot be modified."""
    cell = HexCell(5, 10)
    with pytest.raises(AttributeError):
        cell.x = 6
    with pytest.raises(AttributeError):
        cell.y = 11


@pytest.mark.parametrize("x,y,expected_error", [
    (-1, 0, "x coordinate must be between 0 and 255"),
    (256, 0, "x coordinate must be between 0 and 255"),
    (0, -1, "y coordinate must be between 0 and 255"),
    (0, 256, "y coordinate must be between 0 and 255")
])
def test_hex_cell_invalid_coordinates(x, y, expected_error):
    """Test coordinate validation for invalid inputs."""
    with pytest.raises(ValueError, match=expected_error):
        HexCell(x, y)


@pytest.mark.parametrize("cell1,cell2,expected", [
    (HexCell(5, 10), HexCell(5, 10), True),
    (HexCell(5, 10), HexCell(5, 11), False),
    (HexCell(5, 10), "not a cell", False)
])
def test_hex_cell_equality(cell1, cell2, expected):
    """Test cell equality comparison."""
    assert (cell1 == cell2) == expected


@pytest.mark.parametrize("cell1,cell2,expected", [
    (HexCell(5, 10), HexCell(5, 10), True),
    (HexCell(5, 10), HexCell(5, 11), False)
])
def test_hex_cell_hash(cell1, cell2, expected):
    """Test cell hashing."""
    assert (hash(cell1) == hash(cell2)) == expected
    
    # Test that cells can be used in a set
    cells = {cell1, cell2}
    assert len(cells) == (1 if expected else 2)


@pytest.mark.parametrize("x,y,expected_repr", [
    (5, 10, "HexCell(x=5, y=10)"),
    (0, 0, "HexCell(x=0, y=0)"),
    (255, 255, "HexCell(x=255, y=255)")
])
def test_hex_cell_repr(x, y, expected_repr):
    """Test string representation."""
    cell = HexCell(x, y)
    assert repr(cell) == expected_repr 