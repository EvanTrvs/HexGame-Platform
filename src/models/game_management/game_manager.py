import asyncio
from collections import deque
from typing import List, Set, Any
from .interfaces import IGameManager, ICommand, IPlayer
from .exceptions import GameAlreadyStartedError, GameNotStartedError
from .command import CommandResult, PauseCommand, ResumeCommand


class GameManager(IGameManager):
    """Manages the game state and command execution.
    
    Attributes:
        game_board: The game board being managed.
        command_queue: Queue of commands waiting to be executed.
        observers: Set of observers (players) watching the game.
        running: Whether the game manager is currently running.
    """
    
    def __init__(self, game_board: Any, blue_player_name: str = None, red_player_name: str = None):
        """Initialize a new game manager.
        
        Args:
            game_board: The game board to manage.
            blue_player_name: Name of the blue player.
            red_player_name: Name of the red player.
        """
        self.game_board = game_board
        self.command_queue = deque()
        self.observers: Set[IPlayer] = set()
        self.running = False
        self.blue_player_name = blue_player_name if blue_player_name is not None else "BluePlayer"
        self.red_player_name = red_player_name if red_player_name is not None else "RedPlayer"

    def add_command(self, command: ICommand) -> None:
        """Add a command to the command queue.
        
        Args:
            command: The command to add.
        """
        self.command_queue.append(command)

    async def start(self) -> None:
        """Start the game manager's main loop.
        
        Raises:
            GameAlreadyStartedError: If the game is already running.
        """
        if self.running:
            raise GameAlreadyStartedError("Game is already running")
            
        self.running = True
        while self.running:
            if self.command_queue:
                command = self.command_queue.popleft()
                await self.execute_command(command)
            else:
                await asyncio.sleep(0.05)  # Small delay to prevent CPU overuse

    async def execute_command(self, command: ICommand) -> None:
        """Execute a command and notify observers.
        
        Args:
            command: The command to execute.
        """           
        result = command.execute(self.game_board, (self.blue_player_name, self.red_player_name))
        #command.player.receive_feedback(result)
        self.notify(command, result)

    def stop(self) -> None:
        """Stop the game manager's main loop."""
        self.running = False

    def get_current_player(self) -> str:
        """Get the current player.
        
        Returns:
            Any: The current player.
        """
        if self.game_board.get_current_player() == 1:
            return self.blue_player_name
        elif self.game_board.get_current_player() == 2:
            return self.red_player_name
        else:
            raise ValueError("GameManagement: get_current_player retourne 2 nom")
        

    def get_player_names(self) -> tuple[str, str]:
        """Get the names of the players.
        
        Returns:
            tuple[str, str]: The names of the blue and red players.
        """
        return self.blue_player_name, self.red_player_name 