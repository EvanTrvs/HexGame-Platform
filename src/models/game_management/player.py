from typing import Any, Optional, List, Tuple, Dict
import time
import asyncio
from .interfaces import IPlayer
from .command import Command, CommandResult, MoveCommand
from .exceptions import PlayerNotAttachedError
from ..core import HexGame, HexMove, HexCell, GameEndReason, HexState, PausedState, ActiveState, FinishedState, NotStartedState, CorruptedState

class Player(IPlayer):
    """Implementation of a game player with comprehensive game information access.
    
    This class provides a complete interface for players to:
    - Access game state and information
    - Execute commands
    - Receive notifications
    - Track game progress and statistics
    """
    
    def __init__(self, name: str, min_think_time: float = 0.1):
        """Initialize a new player.
        
        Args:
            name: The name of the player.
            min_think_time: Minimum time in seconds between notification and move command (default: 0.3)
        """
        self._name = name
        self._game_manager = None
        self._stats = {
            'moves_made': 0,
            'time_spent': 0.0,
            'invalid_moves': 0,
            'games_won': 0,
            'games_lost': 0
        }
        self._min_think_time = min_think_time
        self._last_notification_time = 0.0
        self._notification_callback = None  # New callback for notifications

    @property
    def name(self) -> str:
        """Get the player's name."""
        return self._name

    @property
    def is_attached(self) -> bool:
        """Check if the player is attached to a game."""
        return self._game_manager is not None

    @property
    def is_current_player(self) -> bool:
        """Check if it's currently this player's turn."""
        if not self.is_attached:
            return False
        try:
            return self.name == self._game_manager.get_current_player()
        except Exception:
            return False

    def _check_attached(self) -> None:
        """Check if the player is attached to a game manager.
        
        Raises:
            PlayerNotAttachedError: If the player is not attached.
        """
        if not self.is_attached:
            raise PlayerNotAttachedError("Player is not attached to any game")

    def attach_to_game(self, game_manager: Any) -> None:
        """Attach the player to a game manager.
        
        Args:
            game_manager: The game manager to attach to.
        """
        self._game_manager = game_manager
        game_manager.attach(self)

    def detach_from_game(self) -> None:
        """Detach the player from the current game manager."""
        if self._game_manager:
            self._game_manager.detach(self)
            self._game_manager = None

    def get_game_state(self) -> HexState:
        """Get the current game state.
        
        Returns:
            str: A string representation of the current game state:
                - "NOT_STARTED" for NotStartedState
                - "ACTIVE" for ActiveState
                - "PAUSED" for PausedState
                - "FINISHED" for FinishedState
                - "CORRUPTED" for CorruptedState
        """
        self._check_attached()
        state = self._game_manager.game_board.state
        
        if isinstance(state, NotStartedState):
            return HexState.NOT_STARTED
        elif isinstance(state, ActiveState):
            return HexState.ACTIVE
        elif isinstance(state, PausedState):
            return HexState.PAUSED
        elif isinstance(state, FinishedState):
            return HexState.FINISHED
        elif isinstance(state, CorruptedState):
            return HexState.CORRUPTED
        else:
            raise ValueError("Le state de la partie est inconnu")
    
    def get_moves_count(self) -> int:
        """Get the current game number of moves."""
        self._check_attached()
        return self._game_manager.game_board.board.get_total_moves()
    
    def get_board_matrix_at_move(self, int):
        """Get the current state of the board as a matrix at a certain move."""
        self._check_attached()
        return self._game_manager.game_board.board.get_board_state_at_move(int)

    def get_board_matrix(self):
        """Get the current state of the board as a matrix."""
        self._check_attached()
        return self._game_manager.game_board.board.get_board_state()

    def get_board_size(self) -> Tuple[int, int]:
        """Get the dimensions of the game board."""
        self._check_attached()
        size = self._game_manager.game_board.board.size
        return (size, size)  # Hex board is always square

    def get_remaining_time(self) -> float:
        """Get the player's remaining time."""
        self._check_attached()
        return self._game_manager.game_board.get_remaining_time(
            self._game_manager.game_board.BLUE_PLAYER if self.name == self._game_manager.blue_player_name
            else self._game_manager.game_board.RED_PLAYER
        )

    def get_opponent_remaining_time(self) -> float:
        """Get the opponent's remaining time."""
        self._check_attached()
        return self._game_manager.game_board.get_remaining_time(
            self._game_manager.game_board.RED_PLAYER if self.name == self._game_manager.blue_player_name
            else self._game_manager.game_board.BLUE_PLAYER
        )

    def get_game_duration(self) -> float:
        """Get the total duration of the game so far."""
        self._check_attached()
        return self._game_manager.game_board.get_duration() or 0.0

    def get_move_history(self) -> List[Dict[str, Any]]:
        """Get the history of moves made in the game.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing move information:
                - 'player': The player who made the move (BLUE_PLAYER or RED_PLAYER)
                - 'position': Tuple of (x, y) coordinates
                - 'timestamp': When the move was made
        """
        self._check_attached()
        moves = self._game_manager.game_board.board.get_moves()
        return [
            {
                'player': self._game_manager.blue_player_name if i % 2 == 0 else self._game_manager.red_player_name,
                'position': (move.cell.x, move.cell.y),
                'timestamp': move.timestamp
            }
            for i, move in enumerate(moves)
        ]

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get all valid moves for the current player."""
        self._check_attached()
        return self._game_manager.game_board.board.get_moves()

    def get_player_stats(self) -> Dict[str, Any]:
        """Get statistics about the player's performance."""
        return self._stats.copy()

    def get_game_result(self) -> Optional[Dict[str, Any]]:
        """Get the result of the game if it's finished."""
        self._check_attached()
        winner_num = self._game_manager.game_board.winner
        if winner_num is None:
            winner_name = None
        elif winner_num == self._game_manager.game_board.BLUE_PLAYER:
            winner_name = self._game_manager.blue_player_name
        elif winner_num == self._game_manager.game_board.RED_PLAYER:
            winner_name = self._game_manager.red_player_name
        else:
            raise ValueError("Gagnant inconnu")
            
        return (self._game_manager.game_board.game_end_reason, winner_name)

    def is_move_valid(self, x: int, y: int) -> bool:
        """Check if a move is valid."""
        self._check_attached()
        return self._game_manager.game_board.board.is_valid_move(HexCell(x, y))

    def set_notification_callback(self, callback):
        """Set a callback to be called when the player receives a notification."""
        self._notification_callback = callback

    def update(self, command: 'ICommand', result: 'CommandResult') -> None:
        """Receive notification about another player's action."""
        if not self._game_manager:
            raise PlayerNotAttachedError("Player is not attached to any game")
        
        self._last_notification_time = time.time()
        #print(f"{self.name} received notification at {self._last_notification_time}")
        self.receive_notification(command, result)
        
        # Call the notification callback if it exists
        if self._notification_callback:
            self._notification_callback()

    async def send_command(self, command: Command) -> None:
        """Send a command to the game manager.
        
        Args:
            command: The command to send.
            
        Note:
            For move commands, ensures minimum think time has elapsed since last notification.
            Uses asyncio.sleep to avoid blocking the game.
        """
        self._check_attached()
        
        # If it's a move command, check minimum think time
        if isinstance(command, MoveCommand):
            current_time = time.time()
            time_since_notification = current_time - self._last_notification_time
            
            if time_since_notification < self._min_think_time:
                sleep_time = self._min_think_time - time_since_notification
                #print(f"{self.name} waiting {sleep_time:.2f} seconds before moving...")
                await asyncio.sleep(sleep_time)
        
        command.player = self
        self._game_manager.add_command(command)
        
    def receive_notification(self, command: Command, result: CommandResult) -> None:
        """Receive notification about another player's action."""
        #if command.player != self:  # Don't notify the player about their own actions
        #print(f"{self.name} received notification: {result}")

    def __eq__(self, other: Any) -> bool:
        """Check if this player is equal to another player."""
        if not isinstance(other, Player):
            return False
        return self._name == other._name

    def __hash__(self) -> int:
        """Get the hash value of the player."""
        return hash(self._name)

    def __str__(self) -> str:
        """Get a string representation of the player."""
        return f"Player(name={self._name}, attached={self.is_attached})" 