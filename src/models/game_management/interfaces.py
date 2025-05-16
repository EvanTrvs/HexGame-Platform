from abc import ABC, abstractmethod
from typing import Any, Optional, List, Tuple, Dict, Set
from ..core.hex_game import HexGame

    
class ICommand(ABC):
    """Interface for all game commands."""
    
    @abstractmethod
    def execute(self, game_board: Any) -> 'CommandResult':
        """Execute the command on the given game board.
        
        Args:
            game_board: The game board to execute the command on.
            
        Returns:
            CommandResult: The result of the command execution.
        """
        pass
    
class Subject(ABC):
    def __init__(self):
        self.observers: Set[Observer] = set()

    def attach(self, observer: 'Observer') -> None:
        """Attach an observer to the game manager.

        Args:
            observer: The observer to attach.
        """
        self.observers.add(observer)

    def detach(self, observer: 'Observer') -> None:
        """Detach an observer from the game manager.

        Args:
            observer: The observer to detach.
        """
        self.observers.discard(observer)

    def notify(self, command: ICommand, result: 'CommandResult') -> None:
        """Notify all players about a command execution.

        Args:
            command: The command that was executed.
            result: The result of the command execution.
        """
        for observer in self.observers:
            observer.update(command, result)

class Observer(ABC):
    @abstractmethod
    def update(self, command: ICommand, result: 'CommandResult') -> None:
        """Receive notification about another player's action.
        
        Args:
            command: The command that was executed.
            result: The result of the command execution.
        """
        pass
    
    @abstractmethod
    def receive_notification(self, command: ICommand, result: 'CommandResult') -> None:
        """Receive notification about another player's action.
        
        Args:
            command: The command that was executed.
            result: The result of the command execution.
        """
        pass
    

class IPlayer(Observer, ABC):
    """Interface for game players with comprehensive game information access.
    
    This interface provides methods for:
    - Basic player information
    - Game state access
    - Board information
    - Player statistics
    - Game timing information
    - Command execution
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the player's name."""
        pass
    
    @property
    @abstractmethod
    def is_attached(self) -> bool:
        """Check if the player is attached to a game."""
        pass
    
    @property
    @abstractmethod
    def is_current_player(self) -> bool:
        """Check if it's currently this player's turn."""
        pass
    
    @abstractmethod
    def get_game_state(self) -> str:
        """Get the current game state.
        
        Returns:
            str: The current state of the game (e.g., 'NOT_STARTED', 'IN_PROGRESS', 'PAUSED', 'FINISHED').
        """
        pass
    
    def get_moves_count(self) -> int:
        """Get the current game number of moves."""
        self._check_attached()
        return self._game_manager.game_board.board.get_total_moves()
    
    def get_board_matrix_at_move(self, int):
        """Get the current state of the board as a matrix at a certain move."""
        self._check_attached()
        return self._game_manager.game_board.board.get_board_state_at_move(int)
    
    @abstractmethod
    def get_board_matrix(self):
        """Get the current state of the board as a matrix.
        
        Returns:
            List[List[int]]: 2D matrix representing the board state.
        """
        pass
    
    @abstractmethod
    def get_board_size(self) -> Tuple[int, int]:
        """Get the dimensions of the game board.
        
        Returns:
            Tuple[int, int]: (width, height) of the board.
        """
        pass
    
    @abstractmethod
    def get_remaining_time(self) -> float:
        """Get the player's remaining time.
        
        Returns:
            float: Remaining time in seconds.
        """
        pass
    
    @abstractmethod
    def get_opponent_remaining_time(self) -> float:
        """Get the opponent's remaining time.
        
        Returns:
            float: Opponent's remaining time in seconds.
        """
        pass
    
    @abstractmethod
    def get_game_duration(self) -> float:
        """Get the total duration of the game so far.
        
        Returns:
            float: Game duration in seconds.
        """
        pass
    
    @abstractmethod
    def get_move_history(self) -> List[Dict[str, Any]]:
        """Get the history of moves made in the game.
        
        Returns:
            List[Dict[str, Any]]: List of moves with their details.
        """
        pass
    
    @abstractmethod
    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get all valid moves for the current player.
        
        Returns:
            List[Tuple[int, int]]: List of valid (x, y) coordinates.
        """
        pass
    
    @abstractmethod
    def get_player_stats(self) -> Dict[str, Any]:
        """Get statistics about the player's performance.
        
        Returns:
            Dict[str, Any]: Dictionary containing player statistics.
        """
        pass
    
    @abstractmethod
    def get_game_result(self) -> Optional[Dict[str, Any]]:
        """Get the result of the game if it's finished.
        
        Returns:
            Optional[Dict[str, Any]]: Game result information or None if game is not finished.
        """
        pass
    
    @abstractmethod
    def is_move_valid(self, x: int, y: int) -> bool:
        """Check if a move is valid.
        
        Args:
            x: X coordinate of the move.
            y: Y coordinate of the move.
            
        Returns:
            bool: True if the move is valid, False otherwise.
        """
        pass
    
    @abstractmethod
    def send_command(self, command: Any) -> None:
        """Send a command to the game manager.
        
        Args:
            command: The command to send.
        """
        pass

class IGameManager(Subject, ABC):
    """Interface for game managers."""
    
    @abstractmethod
    def add_command(self, command: ICommand) -> None:
        """Add a command to the command queue.
        
        Args:
            command: The command to add.
        """
        pass
    
    @abstractmethod
    async def start(self) -> None:
        """Start the game manager's main loop."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the game manager's main loop."""
        pass