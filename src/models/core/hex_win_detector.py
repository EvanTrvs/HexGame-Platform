import numpy as np
from typing import Optional, List, Tuple


class HexWinDetector:
    """
    HexWinDetector class for determining the winner in a Hex game.
    Uses depth-first search (DFS) to find winning paths and implements caching for performance.
    
    The board is represented as a numpy array where:
    - 0 represents an empty cell
    - 1 represents a blue cell (player connecting left to right)
    - 2 represents a red cell (player connecting top to bottom)
    
    The class provides both static methods for one-time checks and instance methods
    with caching for repeated checks on the same board state.
    """
    EMPTY = 0
    BLUE = 1
    RED = 2

    def __init__(self):
        """
        Initialize the HexWinDetector with an empty cache.
        The cache stores the latest board state hash and its corresponding winner.
        """
        self.cache_hash: Optional[int] = None
        self.cache_result: Optional[int] = None

    def detect_winner(self, board_state: np.ndarray) -> Optional[int]:
        """
        Detect the winner on the board using caching for performance.
        
        Args:
            board_state: The current state of the board as a numpy array
            
        Returns:
            Optional[int]: The winning player (BLUE=1, RED=2) or None if no winner
        """
        board_hash = hash(board_state.tobytes())
        
        # Return cached result if available
        if board_hash == self.cache_hash:
            return self.cache_result
            
        # Calculate winner and update cache
        winner = self.static_detect_winner(board_state)
        self.cache_hash = board_hash
        self.cache_result = winner
        return winner

    @staticmethod
    def static_detect_winner(board_state: np.ndarray) -> Optional[int]:
        """
        Static method to detect the winner without caching.
        
        Args:
            board_state: The current state of the board as a numpy array
            
        Returns:
            Optional[int]: The winning player (BLUE=1, RED=2) or None if no winner
        """
        size = board_state.shape[0]
        
        if HexWinDetector._static_check_blue_win(board_state, size):
            return HexWinDetector.BLUE
            
        if HexWinDetector._static_check_red_win(board_state, size):
            return HexWinDetector.RED
            
        return None

    @staticmethod
    def _static_check_blue_win(board_state: np.ndarray, size: int) -> bool:
        """
        Check if the blue player has won by connecting left to right.
        
        Args:
            board_state: The current state of the board
            size: The size of the board (size x size)
            
        Returns:
            bool: True if blue has won, False otherwise
        """
        visited = np.zeros_like(board_state, dtype=bool)
        
        # Start DFS from all blue cells on the left edge
        for y in range(size):
            if board_state[0, y] == HexWinDetector.BLUE:
                if HexWinDetector._static_dfs_blue(board_state, 0, y, visited, size):
                    return True
        return False

    @staticmethod
    def _static_check_red_win(board_state: np.ndarray, size: int) -> bool:
        """
        Check if the red player has won by connecting top to bottom.
        
        Args:
            board_state: The current state of the board
            size: The size of the board (size x size)
            
        Returns:
            bool: True if red has won, False otherwise
        """
        visited = np.zeros_like(board_state, dtype=bool)
        
        # Start DFS from all red cells on the top edge
        for x in range(size):
            if board_state[x, 0] == HexWinDetector.RED:
                if HexWinDetector._static_dfs_red(board_state, x, 0, visited, size):
                    return True
        return False

    @staticmethod
    def _static_dfs_blue(board_state: np.ndarray, x: int, y: int, visited: np.ndarray, size: int) -> bool:
        """
        Static DFS for blue player to check if they have connected left to right.
        The order of checks is optimized for performance
        
        Args:
            board_state: The current state of the board
            x, y: Current position coordinates
            visited: Matrix tracking visited cells
            size: The size of the board
            
        Returns:
            bool: True if a winning path is found, False otherwise
        """
        # Fast bounds check first
        if x < 0 or x >= size or y < 0 or y >= size:
            return False
            
        # Fast visited check second
        if visited[x, y]:
            return False
        
        # Mark as visited
        visited[x, y] = True
            
        # Cell color check last (slower array access)
        if board_state[x, y] != HexWinDetector.BLUE:
            return False
            
        # Victory condition third (likely to be true when close to edge)
        if x == size - 1:
            return True
        
        # Try all possible directions in hexagonal grid
        directions = [
            (1, 0),    # right (priority)
            (1, 1),    # up-right
            (0, 1),    # up
            (0, -1),   # down
            (-1, 0),   # left
            (-1, -1)   # down-left
        ]
        
        for dx, dy in directions:
            if HexWinDetector._static_dfs_blue(board_state, x + dx, y + dy, visited, size):
                return True
                
        return False

    @staticmethod
    def _static_dfs_red(board_state: np.ndarray, x: int, y: int, visited: np.ndarray, size: int) -> bool:
        """
        Static DFS for red player to check if they have connected top to bottom.
        The order of checks is optimized for performance
        
        Args:
            board_state: The current state of the board
            x, y: Current position coordinates
            visited: Matrix tracking visited cells
            size: The size of the board
            
        Returns:
            bool: True if a winning path is found, False otherwise
        """
        # Fast bounds check first
        if x < 0 or x >= size or y < 0 or y >= size:
            return False
            
        # Fast visited check second
        if visited[x, y]:
            return False
            
        # Mark as visited
        visited[x, y] = True
            
        # Cell color check last (slower array access)
        if board_state[x, y] != HexWinDetector.RED:
            return False
            
        # Victory condition third (likely to be true when close to edge)
        if y == size - 1:
            return True
        
        # Try all possible directions in hexagonal grid
        directions = [
            (0, 1),    # up (priority)
            (1, 1),    # up-right
            (1, 0),    # right
            (-1, 0),   # left
            (0, -1),   # down
            (-1, -1)   # down-left
        ]
        
        for dx, dy in directions:
            if HexWinDetector._static_dfs_red(board_state, x + dx, y + dy, visited, size):
                return True
                
        return False
