import pytest
from src.models.game_management.player import Player
from src.models.game_management.game_manager import GameManager
from src.models.game_management.command import MoveCommand
from src.models.game_management.exceptions import PlayerNotAttachedError
from src.models.core import HexGame, HexState, HexBoard


class MockHexGame(HexGame):
    """Mock implementation of HexGame for testing."""
    
    def __init__(self):
        super().__init__()
        self.BLUE_PLAYER = 1
        self.RED_PLAYER = 2
        self.state = HexState.ACTIVE
        self.winner = None
        self.game_end_reason = None
        self._moves = []
        self.board = HexBoard(5)
        self.size = 5
    
    def get_board_state(self):
        return [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        
    def get_board_state_at_move(self, move):
        return [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        
    def get_total_moves(self):
        return len(self._moves)
        
    def get_moves(self):
        return self._moves
        
    def get_remaining_time(self, player):
        return 100.0
        
    def get_duration(self):
        return 0.0
        
    def is_valid_move(self, cell):
        return True
        
    def get_current_player(self):
        return self.BLUE_PLAYER

class TestPlayer:
    """Test suite for the Player class."""
    
    @pytest.fixture
    def game_board(self):
        """Create a mock game board."""
        return MockHexGame()
    
    @pytest.fixture
    def game_manager(self, game_board):
        """Create a test game manager."""
        return GameManager(game_board, "TestPlayer", "Opponent")
    
    @pytest.fixture
    def player(self):
        """Create a test player."""
        return Player("TestPlayer")
    
    def test_initialization(self, player):
        """Test that Player initializes correctly."""
        assert player.name == "TestPlayer"
        assert not player.is_attached
        assert player._stats == {
            'moves_made': 0,
            'time_spent': 0.0,
            'invalid_moves': 0,
            'games_won': 0,
            'games_lost': 0
        }
    
    def test_get_player_stats(self, player):
        """Test that player statistics can be retrieved."""
        stats = player.get_player_stats()
        assert stats == {
            'moves_made': 0,
            'time_spent': 0.0,
            'invalid_moves': 0,
            'games_won': 0,
            'games_lost': 0
        }
    
    def test_not_attached_error(self, player):
        """Test that operations fail when player is not attached."""
        with pytest.raises(PlayerNotAttachedError):
            player.get_game_state()
        
        with pytest.raises(PlayerNotAttachedError):
            player.get_board_matrix()
        
        with pytest.raises(PlayerNotAttachedError):
            player.get_board_size() 