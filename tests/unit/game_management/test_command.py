import pytest
from src.models.game_management.command import Command, MoveCommand, ResignCommand, PauseCommand, ResumeCommand, CommandResult
from src.models.game_management.player import Player

class TestCommand:
    """Test suite for the Command class and its subclasses."""
    
    @pytest.fixture
    def player(self):
        """Create a test player."""
        return Player("TestPlayer")
    
    @pytest.fixture
    def game_board(self):
        """Create a mock game board."""
        class MockBoard:
            def make_move(self, move):
                return True
                
            def resign_game(self, player):
                return True
                
            def pause_game(self):
                return True
                
            def resume_game(self):
                return True
                
            def get_current_player(self):
                return 1
        return MockBoard()
    
    def test_move_command_execution(self, player, game_board):
        """Test that MoveCommand executes correctly."""
        command = MoveCommand(player, 1, 2)
        result = command.execute(game_board, ("TestPlayer", "Opponent"))
        assert result.success
        assert result.command_type == "MoveCommand"
    
    def test_resign_command_execution(self, player, game_board):
        """Test that ResignCommand executes correctly."""
        command = ResignCommand(player)
        result = command.execute(game_board, ("TestPlayer", "Opponent"))
        assert result.success
        assert result.command_type == "ResignCommand"
    
    def test_pause_command_execution(self, player, game_board):
        """Test that PauseCommand executes correctly."""
        command = PauseCommand(player)
        result = command.execute(game_board, ("TestPlayer", "Opponent"))
        assert result.success
        assert result.command_type == "PauseCommand"
    
    def test_resume_command_execution(self, player, game_board):
        """Test that ResumeCommand executes correctly."""
        command = ResumeCommand(player)
        result = command.execute(game_board, ("TestPlayer", "Opponent"))
        assert result.success
        assert result.command_type == "ResumeCommand"
    
    @pytest.mark.parametrize("success,data,error,expected_str", [
        (True, "Success data", None, "Command TestCommand executed successfully: Success data"),
        (False, None, "Error message", "Command TestCommand failed: Error message")
    ])
    def test_command_result_str(self, success, data, error, expected_str):
        """Test the string representation of CommandResult."""
        result = CommandResult(success, data, error, "TestCommand")
        assert str(result) == expected_str 