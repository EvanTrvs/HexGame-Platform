from dataclasses import dataclass
from typing import Any, Optional

from ..core import HexMove
from .interfaces import ICommand
from .exceptions import CommandExecutionError

@dataclass
class CommandResult:
    """Represents the result of a command execution.
    
    Attributes:
        success: Whether the command was executed successfully.
        data: Optional data returned by the command.
        error: Optional error message if the command failed.
        command_type: The type of command that was executed.
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    command_type: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the command result."""
        if self.success:
            return f"Command {self.command_type} executed successfully: {self.data}"
        return f"Command {self.command_type} failed: {self.error}"

class Command(ICommand):
    """Base class for all game commands."""
    
    def __init__(self, player: 'Player'):
        """Initialize a new command.
        
        Args:
            player: The player executing the command.
        """
        self.player = player
        self.command_type = self.__class__.__name__

    def execute(self, game_board: Any, players_names) -> CommandResult:
        """Execute the command on the given game board.
        
        Args:
            game_board: The game board to execute the command on.
            
        Returns:
            CommandResult: The result of the command execution.
            
        Raises:
            CommandExecutionError: If the command execution fails.
        """
        try:
            result = self._execute_impl(game_board, players_names)
            return CommandResult(
                success=True,
                data=result,
                command_type=self.command_type
            )
        except Exception as e:
            return CommandResult(
                success=False,
                error=str(e),
                command_type=self.command_type
            )

    def _execute_impl(self, game_board: Any, players_names) -> Any:
        """Implementation of the command execution.
        
        Args:
            game_board: The game board to execute the command on.
            
        Returns:
            Any: The result of the command execution.
            
        Raises:
            CommandExecutionError: If the command execution fails.
        """
        raise NotImplementedError("Subclasses must implement _execute_impl")

class MoveCommand(Command):
    """Command for making a move on the game board."""
    
    def __init__(self, player: 'Player', x: int, y: int):
        """Initialize a new move command.
        
        Args:
            player: The player making the move.
            x: The x-coordinate of the move.
            y: The y-coordinate of the move.
        """
        super().__init__(player)
        self.x = x
        self.y = y

    def _execute_impl(self, game_board: Any, players_names) -> str:
        """Execute the move command.
        
        Args:
            game_board: The game board to make the move on.
            
        Returns:
            str: A message describing the move.
            
        Raises:
            CommandExecutionError: If the move is invalid.
        """
        if players_names[0] == self.player.name and game_board.get_current_player() == 1 :
            game_board.make_move(HexMove((self.x,self.y)))
            return f"Move made at position ({self.x}, {self.y})"
        elif players_names[1] == self.player.name and game_board.get_current_player() == 2 :
            game_board.make_move(HexMove((self.x,self.y)))
            return f"Move made at position ({self.x}, {self.y})"    
        else:
            raise CommandExecutionError(f"Invalid player move turn ({self.player.name} move but it's" +
                                        f"{players_names[game_board.get_current_player()-1]} turn)")
        

class ResignCommand(Command):
    """Command for resigning from the game."""
    
    def _execute_impl(self, game_board: Any, players_names) -> str:
        """Execute the resign command.
        
        Args:
            game_board: The game board to resign from.
            
        Returns:
            str: A message confirming the resignation.
        """
        if players_names[0] == self.player.name:
            game_board.resign_game(1)
        else:
            game_board.resign_game(2)
        return f"{self.player.name} has resigned from the game"

class PauseCommand(Command):
    """Command for pausing the game."""
    
    def _execute_impl(self, game_board: Any, players_names) -> str:
        """Execute the pause command.
        
        Args:
            game_board: The game board to pause.
            
        Returns:
            str: A message confirming the pause.
        """
        game_board.pause_game()
        return "Game paused"

class ResumeCommand(Command):
    """Command for resuming the game."""
    
    def _execute_impl(self, game_board: Any, players_names) -> str:
        """Execute the resume command.
        
        Args:
            game_board: The game board to resume.
            
        Returns:
            str: A message confirming the resume.
        """
        game_board.resume_game()
        return "Game resumed" 