from typing import Optional, Dict
import numpy as np

from .hex_game import HexGame, TimedHexGame
from .interfaces import IHexBoard, IHexMove, HexCell, GameEndReason, IHexState
from .hex_state import NotStartedState, ActiveState, PausedState, FinishedState, CorruptedState
from .exceptions import InvalidCellError, InvalidGameStateError
from .hex_board import HexBoard, MemoryHexBoard  


class HexGameFactory:
    @staticmethod
    def create_game(board_size: Optional[int] = None,
                    initial_time: Optional[float] = None,
                    state: Optional[IHexState] = None,
                    game_end_reason: Optional[GameEndReason] = None,
                    winner: Optional[int] = None,
                    start_time: Optional[float] = None,
                    end_time: Optional[float] = None,
                    total_pause_duration: Optional[float] = None,
                    last_pause_start_time: Optional[float] = None,
                    blue_player_timer: Optional[float] = None,
                    red_player_timer: Optional[float] = None,
                    existing_game: Optional[HexGame] = None,
                    use_memory_board: bool = False) -> HexGame:
        """
        Creates a HexGame or TimedHexGame instance based on the provided parameters.
        If no board is provided, a default HexBoard is created.
        If initial_time is provided, a TimedHexGame is created.
        If existing_game is provided, a new game is created based on the existing game.
        If use_memory_board is True, a MemoryHexBoard is used.
        """
        if existing_game:
            if not isinstance(existing_game, HexGame):
                raise InvalidGameStateError("The provided game is not a HexGame instance.")

            if use_memory_board:
                if board_size is None:
                    raise ValueError("Board size must be provided when using MemoryHexBoard.")
                new_board = MemoryHexBoard(board_size)
                # Copy the board state from the existing game
                new_board._board_state = existing_game.board.get_board_state()
                new_board._moves = existing_game.board.get_moves()
            else:
                new_board = existing_game.board

            if initial_time is not None:
                new_hex_game = HexGame(new_board, existing_game.state, existing_game.game_end_reason,
                                        existing_game.winner, existing_game.start_time, existing_game.end_time,
                                        existing_game.total_pause_duration, existing_game._last_pause_start_time)
                return TimedHexGame(new_hex_game, initial_time, blue_player_timer, red_player_timer)
            else:
                return HexGame(new_board, existing_game.state, existing_game.game_end_reason,
                                existing_game.winner, existing_game.start_time, existing_game.end_time,
                                existing_game.total_pause_duration, existing_game._last_pause_start_time)

        if board_size is None:
            raise ValueError("Board size must be provided.")

        if use_memory_board:
            board = MemoryHexBoard(board_size)
        else:
            board = HexBoard(board_size)

        if initial_time is not None:
            hex_game = HexGame(board, state, game_end_reason, winner, start_time, end_time, total_pause_duration, last_pause_start_time)
            return TimedHexGame(hex_game, initial_time, blue_player_timer, red_player_timer)
        else:
            return HexGame(board, state, game_end_reason, winner, start_time, end_time, total_pause_duration, last_pause_start_time)

    @staticmethod
    def convert_to_timed_game(hex_game: HexGame, initial_time: float,
                               blue_player_timer: Optional[float] = None,
                               red_player_timer: Optional[float] = None) -> TimedHexGame:
        """
        Converts a HexGame instance to a TimedHexGame instance.
        """
        if not isinstance(hex_game, HexGame):
            raise InvalidGameStateError("The provided game is not a HexGame instance.")
        return TimedHexGame(hex_game, initial_time, blue_player_timer, red_player_timer)

    @staticmethod
    def convert_to_hex_game(timed_game: TimedHexGame) -> HexGame:
        """
        Converts a TimedHexGame instance to a HexGame instance.
        """
        if not isinstance(timed_game, TimedHexGame):
            raise InvalidGameStateError("The provided game is not a TimedHexGame instance.")
        return timed_game._hex_game

    @staticmethod
    def change_board(game: HexGame, new_board: IHexBoard) -> HexGame:
        """
        Changes the board of a HexGame instance.
        """
        if not isinstance(game, HexGame):
            raise InvalidGameStateError("The provided game is not a HexGame instance.")
        game._board = new_board
        return game

    @staticmethod
    def create_from_file(file_path: str) -> HexGame:
        """
        Creates a HexGame instance from a file.
        This method should be implemented to parse the file and extract the necessary parameters.
        """
        # Implement file parsing logic here
        # For example, parse the file to get board size, initial time, state, etc.
        # Then call create_game with the extracted parameters.
        raise NotImplementedError("File parsing logic is not implemented.")
