import pytest
import numpy as np
from src.models.core.hex_win_detector import HexWinDetector


@pytest.fixture
def win_detector():
    """Fixture to provide a fresh HexWinDetector instance for each test."""
    return HexWinDetector()


@pytest.mark.parametrize("board_state,expected_winner", [
    # Empty board
    (np.zeros((3, 3), dtype=int), None),
    
    # Simple blue win (top to bottom)
    (np.array([
        [1, 0, 0],
        [1, 0, 0],
        [1, 0, 0]
    ]), 1),
    
    # Simple red win (left to right)
    (np.array([
        [2, 2, 2],
        [0, 0, 0],
        [0, 0, 0]
    ]), 2),
    
    # Complex blue win (top to bottom with zigzag)
    (np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ]), 1),
    
    # Complex red win (left to right with zigzag)
    (np.array([
        [2, 0, 0],
        [0, 2, 0],
        [0, 0, 2]
    ]), 2),
    
    # Larger board with complex blue win
    (np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]), 1),
    
    # Edge case: single cell
    (np.array([[1]]), 1),
])
def test_static_detect_winner(board_state, expected_winner):
    """Test static winner detection with various board states."""
    assert HexWinDetector.static_detect_winner(board_state) == expected_winner


@pytest.mark.parametrize("board_state,expected_winner", [
    # Complex blue win with multiple paths (top to bottom)
    (np.array([
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1]
    ]), 1),
    
    # Complex red win with multiple paths (left to right)
    (np.array([
        [2, 2, 0, 0],
        [0, 2, 2, 0],
        [0, 0, 2, 2],
        [0, 0, 0, 2]
    ]), 2),
])
def test_cached_detect_winner(win_detector, board_state, expected_winner):
    """Test cached winner detection with complex patterns."""
    # First call should calculate
    result1 = win_detector.detect_winner(board_state)
    assert result1 == expected_winner
    
    # Second call should use cache
    result2 = win_detector.detect_winner(board_state)
    assert result2 == expected_winner


def test_cache_invalidation(win_detector):
    """Test that cache is properly invalidated with different boards."""
    # Create two different winning boards
    board1 = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ])
    
    board2 = np.array([
        [2, 0, 0],
        [0, 2, 0],
        [0, 0, 2]
    ])
    
    # First board
    result1 = win_detector.detect_winner(board1)
    assert result1 == 1
    
    # Second board should not use cache
    result2 = win_detector.detect_winner(board2)
    assert result2 == 2
    
    # Verify cache is updated
    result3 = win_detector.detect_winner(board2)
    assert result3 == 2


def test_performance_with_large_board():
    """Test performance with a large board to ensure reasonable execution time."""
    size = 11  # Large enough to be meaningful but not too slow
    board = np.zeros((size, size), dtype=int)
    
    # Create a winning path for blue (top to bottom)
    for i in range(size):
        board[i, 0] = 1
    
    # Should complete in reasonable time
    assert HexWinDetector.static_detect_winner(board) == 1


@pytest.mark.parametrize("board_state,expected_winner", [
    # Complex blue win with multiple paths (top to bottom)
    (np.array([
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 1]
    ]), 1),
    
    # Complex blue win with obstacles (top to bottom)
    (np.array([
        [1, 2, 0, 0],
        [1, 1, 2, 0],
        [0, 1, 1, 2],
        [0, 0, 1, 1]
    ]), 1),
    
    # Complex red win with multiple paths (left to right)
    (np.array([
        [2, 2, 0, 0],
        [0, 2, 2, 0],
        [0, 0, 2, 2],
        [0, 0, 0, 2]
    ]), 2),
    
    # No Win
    (np.array([
        [2, 2, 0, 0],
        [0, 2, 2, 0],
        [0, 0, 2, 0],
        [1, 1, 1, 1]
    ]), None)
])
def test_complex_win_patterns(board_state, expected_winner):
    """Test detection of complex win patterns with obstacles and multiple paths."""
    assert HexWinDetector.static_detect_winner(board_state) == expected_winner


def test_cache_consistency(win_detector):
    """Test that cache remains consistent across multiple operations."""
    # Create a complex board state
    board = np.array([
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1]
    ])
    
    # Multiple operations with same board
    results = []
    for _ in range(5):
        results.append(win_detector.detect_winner(board))
    
    # All results should be the same
    assert all(r == results[0] for r in results)
    
    # Modify board slightly
    board[0, 0] = 2
    new_result = win_detector.detect_winner(board)
    assert new_result != results[0]  # Cache should be invalidated


@pytest.mark.parametrize("board_state", [
    # Early game state
    np.array([
        [1, 0, 0],
        [0, 2, 0],
        [0, 0, 0]
    ]),
    
    # Mid game state
    np.array([
        [1, 2, 1, 0],
        [0, 1, 2, 0],
        [0, 0, 1, 2],
        [0, 0, 0, 0]
    ]),
    
    # Almost complete board
    np.array([
        [1, 2, 1, 2],
        [2, 1, 2, 1],
        [1, 2, 1, 2],
        [2, 1, 2, 0]
    ]),
    
    # Complex non-winning pattern
    np.array([
        [1, 0, 0, 0],
        [0, 2, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 2]
    ])
])
def test_unfinished_boards(board_state):
    """Test detection on unfinished boards (no winner yet)."""
    assert HexWinDetector.static_detect_winner(board_state) is None


def test_cache_with_unfinished_boards(win_detector):
    """Test cache behavior with unfinished boards."""
    # Create an unfinished board
    board = np.array([
        [1, 0, 0],
        [0, 2, 0],
        [0, 0, 0]
    ])
    
    # First call
    result1 = win_detector.detect_winner(board)
    assert result1 is None
    
    # Second call should use cache
    result2 = win_detector.detect_winner(board)
    assert result2 is None
    
    # Modify board to create a blue win (top to bottom)
    board[0, 0] = 1
    board[1, 0] = 1
    board[2, 0] = 1
    result3 = win_detector.detect_winner(board)
    assert result3 == 1  # Cache should be invalidated and new result calculated 