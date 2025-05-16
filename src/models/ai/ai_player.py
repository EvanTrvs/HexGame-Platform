from typing import Optional, Dict, Any, List
import time
import random

from ..core import HexCell, IHexGame

class AIPlayer():
    """
    Base class for AI players implementing common AI functionality.
    This class provides a foundation for different AI strategies.
    """
    def __init__(self, player_id: str, name: str, is_blue: bool, min_think_time: float = 1.0):
        """
        Initialize an AI player.
        
        Args:
            player_id: Unique identifier for the player
            name: Display name of the player
            is_blue: Whether the player plays as blue
            min_think_time: Minimum time in seconds the AI must wait before making a move
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
        
    def _select_random_move(self, game: IHexGame) -> Optional[HexCell]:
        """
        Select a random move from available moves.
        
        Args:
            game: The current game state
            
        Returns:
            Optional[HexCell]: A randomly selected cell, or None if no moves are available
        """
        if not self._available_moves:
            return None
        return random.choice(self._available_moves)
        
    def select_move(self, game: IHexGame) -> Optional[HexCell]:
        """
        Select a move based on the current game state.
        This base implementation selects a random move after the minimum think time.
        
        Args:
            game: The current game state
            
        Returns:
            Optional[HexCell]: The selected cell to play, or None if no move is selected
        """
        if not self._is_my_turn:
            return None
            
        # Update available moves
        self._available_moves = self._get_available_moves(game)
        
        # Wait for the minimum think time
        time.sleep(self._min_think_time)
        
        # Select and return a move
        return self._select_random_move(game)
        
    def handle_game_over(self, winner, reason: Any) -> None:
        """
        Handle the end of the game.
        For AI players, this clears the available moves list.
        
        Args:
            winner: The player who won, or None if there was no winner
            reason: The reason why the game ended
        """
        self._available_moves = [] 