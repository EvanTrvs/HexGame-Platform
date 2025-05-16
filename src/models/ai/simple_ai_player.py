from typing import Optional, List

from .ai_player import AIPlayer
from ..core import HexCell, IHexGame


class SimpleAIPlayer(AIPlayer):
    """
    A simple AI player that uses a basic strategy to make moves.
    This AI prefers moves that are closer to the center of the board.
    """
    def _evaluate_move(self, cell: HexCell, game: IHexGame) -> float:
        """
        Evaluate a move based on its position on the board.
        Moves closer to the center are preferred.
        
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