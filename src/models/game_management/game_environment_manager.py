from typing import List, Optional, Dict, Any, Tuple
import asyncio
from .game_manager import GameManager
from .player import Player
from ..core.hex_game import HexGame
from ..core.hex_game_factory import HexGameFactory

class GameEnvironmentManager:
    """Singleton class for managing game environments and their persistence.
    
    This class provides a centralized way to manage game environments, including:
    - Current active game environment
    - Creation of new game environments
    - Loading of existing game environments
    - Persistence of game state
    
    Attributes:
        _instance: The singleton instance of this class
        current_game_manager: The currently active game manager
        current_players: List of players in the current game
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance of the class exists."""
        if cls._instance is None:
            cls._instance = super(GameEnvironmentManager, cls).__new__(cls)
            cls._instance.current_game_manager = None
            cls._instance.current_players = []
            cls.move_replay = None
        return cls._instance
    
    @property
    def game_manager(self) -> Optional[GameManager]:
        """Get the current game manager."""
        return self.current_game_manager
    
    @property
    def players(self) -> List[Player]:
        """Get the current players."""
        return self.current_players
    
    def _create_player(self, name: str) -> Player:
        """Create a player with appropriate configuration.
        
        Args:
            name: Name of the player
            
        Returns:
            Player instance with appropriate configuration
        """
        config = {}
        if "bot" in name.lower():
            config["min_think_time"] = 0.5
        return Player(name, **config)
    
    def load_default_environment(self, board_size=11) -> None:
        """Load a default game environment with standard settings."""
        self.load_environment_from_game(
            HexGameFactory.create_game(board_size=board_size),
            blue_player_name="Blue Player",
            red_player_name="Red Player"
        )
    
    def load_environment_from_game(self, 
                                 game: HexGame,
                                 blue_player_name: Optional[str] = None,
                                 red_player_name: Optional[str] = None) -> None:
        """Load an environment from an existing HexGame.
        
        Args:
            game: The HexGame instance to load
            blue_player_name: Optional name for blue player
            red_player_name: Optional name for red player
        """
        # Reset current environment
        self.reset()
        
        # Create game manager with optional player names
        self.current_game_manager = GameManager(
            game,
            blue_player_name=blue_player_name,
            red_player_name=red_player_name
        )
        
        # Create players with optional names
        self.current_players = [
            self._create_player(blue_player_name),
            self._create_player(red_player_name),
            self._create_player("Spectator")
        ]
        
        # Attach players
        for player in self.current_players:
            player.attach_to_game(self.current_game_manager)
    
    def load_environment_with_players(self,
                                    game: HexGame,
                                    players: List[Player]) -> None:
        """Load an environment with a custom list of players.
        
        Args:
            game: The HexGame instance to load
            players: List of players to use in the game
        """
        # Reset current environment
        self.reset()
        
        # Create game manager
        self.current_game_manager = GameManager(game)
        
        # Set players and add spectator if not present
        self.current_players = players.copy()
        has_spectator = any("spectator" in p.name.lower() for p in players)
        if not has_spectator:
            self.current_players.append(self._create_player("Spectator"))
        
        # Attach players
        for player in self.current_players:
            player.attach_to_game(self.current_game_manager)
    
    def export_environment(self) -> Tuple[HexGame, Optional[str], Optional[str]]:
        """Export the current environment to its basic components.
        
        Returns:
            Tuple containing:
            - The HexGame instance
            - Blue player name (if available)
            - Red player name (if available)
        """
        if not self.current_game_manager:
            raise ValueError("No active environment to export")
            
        blue_name = None
        red_name = None
        if self.current_players:
            if len(self.current_players) > 0:
                blue_name = self.current_players[0].name
            if len(self.current_players) > 1:
                red_name = self.current_players[1].name
                
        return self.current_game_manager.game_board, blue_name, red_name
    
    def reset(self) -> None:
        """Reset the current game environment to a clean state."""
        # Stop the game manager if it exists
        if self.current_game_manager:
            self.current_game_manager.stop()
        
        # Clear all attributes
        self.current_game_manager = None
        self.current_players = []
        self.move_replay = None
    
    def is_environment_active(self) -> bool:
        """Check if there is an active game environment.
        
        Returns:
            bool: True if there is an active environment
        """
        return self.current_game_manager is not None and len(self.current_players) > 0 