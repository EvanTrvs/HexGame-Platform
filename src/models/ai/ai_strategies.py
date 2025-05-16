from typing import Optional, List, Dict, Any
import random
import numpy as np

from ..core import HexCell, IHexGame

class RandomStrategy():
    """
    A simple AI strategy that selects moves randomly.
    This strategy is useful for testing and as a baseline for more sophisticated strategies.
    """
    def __init__(self, player_id: str, name: str, is_blue: bool, min_think_time: float = 0.5):
        """
        Initialize a random strategy player.
        
        Args:
            player_id: Unique identifier for the player
            name: Display name of the player
            is_blue: Whether the player plays as blue
            min_think_time: Minimum time in seconds the player must wait before making a move
        """
        super().__init__(player_id, name, is_blue, min_think_time)
        self._available_moves: List[HexCell] = []
        
    def _get_available_moves(self, game: IHexGame) -> List[HexCell]:
        """
        Get all available moves from the current game state.
        
        Args:
            game: The current game state
            
        Returns:
            List[HexCell]: List of available cells to play
        """
        available_moves = []
        for row in range(game.board_size):
            for col in range(game.board_size):
                cell = game.get_cell(row, col)
                if cell is not None and not cell.is_occupied:
                    available_moves.append(cell)
        return available_moves
        
    def select_move(self, game: IHexGame) -> Optional[HexCell]:
        """
        Select a move based on the current game state.
        This implementation selects a random move from available moves.
        
        Args:
            game: The current game state
            
        Returns:
            Optional[HexCell]: The selected cell to play, or None if no move is selected
        """
        if not self._is_my_turn:
            return None
            
        # Update available moves
        self._available_moves = self._get_available_moves(game)
        
        if not self._available_moves:
            return None
            
        # Wait for the minimum think time
        self._wait_min_think_time()
        
        # Select a random move
        return random.choice(self._available_moves)
        
    def handle_game_over(self, winner, reason: Any) -> None:
        """
        Handle the end of the game.
        For random strategy players, this clears the available moves list.
        
        Args:
            winner: The player who won, or None if there was no winner
            reason: The reason why the game ended
        """
        self._available_moves = []


class ShortestPathStrategy():
    """
    A simple AI strategy that tries to find the shortest path to win.
    This strategy evaluates moves based on their potential to create a path to victory.
    """
    def __init__(self, player_id: str, name: str, is_blue: bool, min_think_time: float = 1.0):
        """
        Initialize a shortest path strategy player.
        
        Args:
            player_id: Unique identifier for the player
            name: Display name of the player
            is_blue: Whether the player plays as blue
            min_think_time: Minimum time in seconds the player must wait before making a move
        """
        super().__init__(player_id, name, is_blue, min_think_time)
        self._available_moves: List[HexCell] = []
        
    def _get_available_moves(self, game: IHexGame) -> List[HexCell]:
        """
        Get all available moves from the current game state.
        
        Args:
            game: The current game state
            
        Returns:
            List[HexCell]: List of available cells to play
        """
        available_moves = []
        for row in range(game.board_size):
            for col in range(game.board_size):
                cell = game.get_cell(row, col)
                if cell is not None and not cell.is_occupied:
                    available_moves.append(cell)
        return available_moves
        
    def _evaluate_move(self, cell: HexCell, game: IHexGame) -> float:
        """
        Evaluate a move based on its potential to create a path to victory.
        
        Args:
            cell: The cell to evaluate
            game: The current game state
            
        Returns:
            float: A score for the move, higher is better
        """
        # Calculate distance from center
        center = game.board_size // 2
        row_dist = abs(cell.row - center)
        col_dist = abs(cell.col - center)
        
        # Prefer moves closer to center
        return -(row_dist + col_dist)
        
    def select_move(self, game: IHexGame) -> Optional[HexCell]:
        """
        Select a move based on the current game state.
        This implementation evaluates all available moves and selects the one with the highest score.
        
        Args:
            game: The current game state
            
        Returns:
            Optional[HexCell]: The selected cell to play, or None if no move is selected
        """
        if not self._is_my_turn:
            return None
            
        # Update available moves
        self._available_moves = self._get_available_moves(game)
        
        if not self._available_moves:
            return None
            
        # Wait for the minimum think time
        self._wait_min_think_time()
        
        # Evaluate all moves and select the best one
        best_move = None
        best_score = float('-inf')
        
        for move in self._available_moves:
            score = self._evaluate_move(move, game)
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move
        
    def handle_game_over(self, winner, reason: Any) -> None:
        """
        Handle the end of the game.
        For shortest path strategy players, this clears the available moves list.
        
        Args:
            winner: The player who won, or None if there was no winner
            reason: The reason why the game ended
        """
        self._available_moves = [] 