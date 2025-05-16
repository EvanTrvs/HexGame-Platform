from abc import ABC, abstractmethod
from typing import Optional, Dict, List
import time

from .hex_state import IHexState, NotStartedState, PausedState, ActiveState, CorruptedState, FinishedState
from .interfaces import HexState, IHexGame, GameEndReason, IHexBoard, IHexMove
from .exceptions import GameOverError, NotPlayerTurnError, TimeoutError, BoardFullError, InvalidCellError

# HexGame class implementing the IHexGame interface
# This class represents the core logic of a Hex game, including game state, player turns, and game rules.
class HexGame(IHexGame):
    # Constants representing the two players
    BLUE_PLAYER = 1
    RED_PLAYER = 2

    def __init__(self, board: IHexBoard,
                 state: Optional[str] = None,
                 game_end_reason: Optional[GameEndReason] = None,
                 winner: Optional[int] = None,
                 start_time: Optional[float] = None,
                 end_time: Optional[float] = None,
                 total_pause_duration: Optional[float] = None,
                 last_pause_start_time: Optional[float] = None):
        """
        Initializes a new Hex game with the given board.
        Sets the initial state to NotStartedState and initializes other game-related attributes.
        
        Args:
            board: The game board implementing the IHexBoard interface
            state: The initial state of the game
            game_end_reason: The reason why the game ended
            winner: The winner of the game
            start_time: The time when the game started
            end_time: The time when the game ended
            total_pause_duration: Total time the game has been paused
        """
        self._board = board
        self._state = state if state else NotStartedState()
        self._game_end_reason = game_end_reason
        self._winner = winner
        self._start_time = start_time
        self._end_time = end_time
        self._total_pause_duration = total_pause_duration if total_pause_duration is not None else 0.0
        self._last_pause_start_time = last_pause_start_time
        self._current_player = self.get_current_player()

    # Property to access the game board
    @property
    def board(self) -> IHexBoard:
        return self._board

    # Property to access the current state of the game
    @property
    def state(self) -> IHexState:
        return self._state

    # Setter to update the state of the game
    @state.setter
    def state(self, new_state: IHexState) -> None:
        self._state = new_state

    # Property to get the reason why the game ended
    @property
    def game_end_reason(self) -> Optional[GameEndReason]:
        return self._game_end_reason

    # Property to get the winner of the game
    @property
    def winner(self) -> Optional[int]:
        return self._winner

    # Property to get the start time of the game
    @property
    def start_time(self) -> Optional[float]:
        return self._start_time

    # Property to get the end time of the game
    @property
    def end_time(self) -> Optional[float]:
        return self._end_time

    # Property to get the total pause duration of the game
    @property
    def total_pause_duration(self) -> float:
        """Returns the total time the game has been paused."""
        if isinstance(self.state, PausedState):
            return self._total_pause_duration + (self.get_current_time() - self._last_pause_start_time)
        return self._total_pause_duration

    # Property to get the timers for both players (not implemented in this class)
    @property
    def player_timers(self) -> Dict[int, float]:
        return {self.BLUE_PLAYER: None, self.RED_PLAYER: None}

    # Starts the game by transitioning the state to the "started" state
    def start_game(self) -> None:
        self._state.start_game(self)

    # Pauses the game and records the pause time
    def pause_game(self) -> None:
        """Pauses the game and records the pause time."""
        self._state.pause_game(self)

    # Resumes the game and updates the total pause duration
    def resume_game(self) -> None:
        """Resumes the game and updates the total pause duration."""
        self._state.resume_game(self)

    # Ends the game with a specific reason (e.g., victory, resignation, draw)
    def end_game(self, reason: GameEndReason) -> None:
        self._state.end_game(self, reason)

    # Marks the game as corrupted (invalid state)
    def corrupt_game(self) -> None:
        self._state.corrupt_game(self)

    # Processes a player's move and checks for game-ending conditions
    def make_move(self, move: IHexMove) -> bool:
        """
        Handles a player's move. Validates the move, updates the board, and checks for a winner.
        Raises exceptions if the game is over, it's not the player's turn, or the move is invalid.
        """
        if self.is_game_over():
            raise GameOverError("The game is over.")
        if not self.board.is_valid_move(move.cell):
            raise InvalidCellError("Invalid move.")
        if not isinstance(self.state, ActiveState):
            if not isinstance(self.state, NotStartedState):
                raise NotPlayerTurnError("Game State is Not active for moves")

        if self.board.add_move(move):  # Adds the move to the board
            if isinstance(self.state, NotStartedState):
                self.start_game()
            self.switch_player()  # Switches to the other player
            winner = self.board.get_winner()  # Checks if there is a winner
            if winner is not None:
                self._winner = winner
                self.end_game(GameEndReason.VICTORY)  # Ends the game if there is a winner
            return True
        return False

    # Returns the current player (either BLUE_PLAYER or RED_PLAYER)
    def get_current_player(self) -> int:
        # current player is determined by the number of moves made
        # even number of moves means blue player's turn, odd means red player's turn
        self._current_player = self.BLUE_PLAYER if self.board.get_total_moves() % 2 == 0 else self.RED_PLAYER
        return self._current_player

    # Switches the current player to the other player
    def switch_player(self) -> None:
        return self.get_current_player()

    # Checks if the game is over
    def is_game_over(self) -> bool:
        return self._game_end_reason is not None

    # Allows a player to resign, automatically making the other player the winner
    def resign_game(self, player: int) -> None:
        if player == self.BLUE_PLAYER:
            self._winner = self.RED_PLAYER
        else:
            self._winner = self.BLUE_PLAYER
        self.end_game(GameEndReason.RESIGN)

    # Ends the game in a draw
    def draw_game(self) -> None:
        self._winner = None
        self.end_game(GameEndReason.DRAW)

    # Updates the timer for a specific player (not implemented in this class)
    def update_timers(self):
        return

    # Gets the remaining time for a specific player (not implemented in this class)
    def get_remaining_time(self, player: int) -> float:
        return None

    # Checks if a player has run out of time (not implemented in this class)
    def check_overtime(self) -> bool:
        return False

    # Gets the current system time
    def get_current_time(self) -> float:
        return time.time()

    # Calculates the total duration of the game, accounting for pauses
    def get_duration(self) -> Optional[float]:
        """
        Calculates the total duration of the game, accounting for pauses.
        The duration is the total time minus the total pause duration.
        
        Returns:
            Optional[float]: The total duration of the game in seconds, or None if the game hasn't started
        """
        if self._start_time is None:
            return None

        # Get the current time or end time
        current_time = self._end_time if self._end_time is not None else self.get_current_time()
        
        # Calculate total duration
        total_duration = current_time - self._start_time
            
        # The active duration is the total duration minus the total pause duration
        return total_duration - self.total_pause_duration


# TimedHexGame class extending HexGame with time management for players
class TimedHexGame(IHexGame):
    """
    TimedHexGame extends HexGame to include time management for players.
    It ensures that each player's timer is updated accurately based on the moves made.
    """

    def __init__(self,
                 hex_game: HexGame,
                 initial_time: float,
                 blue_player_timer: Optional[float] = None,
                 red_player_timer: Optional[float] = None):
        """
        Initializes a timed Hex game by wrapping an existing HexGame instance.
        Adds timers for both players with the specified initial time.
        """
        self._hex_game = hex_game
        self._initial_time = initial_time

        if blue_player_timer is not None and red_player_timer is not None:
            if blue_player_timer < 0:
                raise ValueError("Blue player timer cannot be negative.")
            if red_player_timer < 0:
                raise ValueError("Red player timer cannot be negative.")

            self._player_timers = {self._hex_game.BLUE_PLAYER: blue_player_timer,
                                   self._hex_game.RED_PLAYER: red_player_timer}
        else:
            if initial_time < 0:
                raise ValueError("Initial time cannot be negative.")

            self._player_timers = {self._hex_game.BLUE_PLAYER: initial_time,
                                   self._hex_game.RED_PLAYER: initial_time}

    # Property to access the game board
    @property
    def board(self) -> IHexBoard:
        return self._hex_game.board

    # Property to access the current state of the game
    @property
    def state(self) -> IHexState:
        return self._hex_game.state

    # Setter to update the state of the game
    @state.setter
    def state(self, new_state: IHexState) -> None:
        self._hex_game.state = new_state

    # Property to get the reason why the game ended
    @property
    def game_end_reason(self) -> Optional[GameEndReason]:
        return self._hex_game.game_end_reason

    # Property to get the winner of the game
    @property
    def winner(self) -> Optional[int]:
        return self._hex_game.winner

    # Property to get the start time of the game
    @property
    def start_time(self) -> Optional[float]:
        return self._hex_game.start_time

    # Property to get the end time of the game
    @property
    def end_time(self) -> Optional[float]:
        return self._hex_game.end_time
    
    # Property to get the total pause duration of the game
    @property
    def total_pause_duration(self) -> Optional[float]:
        """Returns the total time the game has been paused."""
        return self._hex_game.total_pause_duration

    # Property to get the timers for both players
    @property
    def player_timers(self) -> Dict[int, float]:
        self.update_timers()
        return self._player_timers

    # Starts the game and records the start time
    def start_game(self) -> None:
        self._hex_game.start_game()
        self._hex_game._start_time = self.get_current_time()

    # Pauses the game and records the pause time
    def pause_game(self) -> None:
        """Pauses the game and records the pause time."""
        self._hex_game.pause_game()
        self._pause_start_time = self.get_current_time()

    # Resumes the game and records the resume time
    def resume_game(self) -> None:
        """Resumes the game and updates the total pause duration."""
        self._hex_game.resume_game()
        if hasattr(self, '_pause_start_time'):
            pause_duration = self.get_current_time() - self._pause_start_time
            # Adjust both players' timers by adding the pause duration
            for player in self._player_timers:
                self._player_timers[player] += pause_duration
            del self._pause_start_time

    # Ends the game and records the end time
    def end_game(self, reason: GameEndReason) -> None:
        self._hex_game.end_game(reason)
        self._hex_game._end_time = self.get_current_time()

    # Marks the game as corrupted
    def corrupt_game(self) -> None:
        self._hex_game.corrupt_game()

    # Processes a player's move and checks for overtime
    def make_move(self, move: IHexMove) -> bool:
        """
        Handles a player's move. Validates the move, updates the board, and checks for a winner.
        Raises exceptions if the game is over, it's not the player's turn, or the move is invalid.
        """
        if self.check_overtime():
            raise TimeoutError("A player has run out of time.")
        if move.timestamp is None:
            raise ValueError("Timestamp cannot be None for a timed game.")
        return self._hex_game.make_move(move)

    # Returns the current player
    def get_current_player(self) -> int:
        return self._hex_game.get_current_player()

    # Switches the current player and updates their timer
    def switch_player(self) -> None:
        self._hex_game.switch_player()
        self.update_timers()

    # Checks if the game is over
    def is_game_over(self) -> bool:
        return self._hex_game.is_game_over()

    # Allows a player to resign
    def resign_game(self, player: int) -> None:
        self._hex_game.resign_game(player)

    # Ends the game in a draw
    def draw_game(self) -> None:
        self._hex_game.draw_game()

    # Gets the remaining time for a specific player
    def get_remaining_time(self, player: int) -> float:
        self.update_timers()
        return self._player_timers[player]

    # Checks if the current player has run out of time
    def check_overtime(self) -> bool:
        current_player = self.get_current_player()
        return self.get_remaining_time(current_player) <= 0

    # Gets the current system time
    def get_current_time(self) -> float:
        return time.time()

    # Gets the duration of the game
    def get_duration(self) -> Optional[float]:
        return self._hex_game.get_duration()

    def update_timers(self):
        """
        Updates the player timers based on the moves made and game state.
        Optimized for performance while maintaining robustness.
        
        Key optimizations:
        - Minimal system calls
        - Single pass through moves
        - Direct timer updates
        - Early exits for edge cases
        
        Pause handling:
        - Total pause duration is split equally between players
        - This is fair as pauses can occur during either player's turn
        """
        # Quick exits for edge cases
        if not self._hex_game.board.get_moves():
            return

        # Get current time only if game is active
        current_time = None
        if not self.is_game_over() and not isinstance(self.state, PausedState):
            current_time = self.get_current_time()

        # Initialize time tracking
        blue_time = red_time = 0.0
        moves = self._hex_game.board.get_moves()
        first_move = moves[0]

        # Validate first move
        if first_move.timestamp is None:
            raise ValueError("First move timestamp cannot be None")
        if self._hex_game.start_time is not None and first_move.timestamp < self._hex_game.start_time:
            raise ValueError("First move timestamp cannot be before game start")

        # Calculate time from start to first move
        if self._hex_game.start_time is not None:
            time_to_first = first_move.timestamp - self._hex_game.start_time
            blue_time = time_to_first  # Blue always starts

        # Process all moves in a single pass
        for i in range(1, len(moves)):
            curr, prev = moves[i], moves[i-1]
            if curr.timestamp is None or prev.timestamp is None:
                raise ValueError("Move timestamp cannot be None")
            
            time_spent = curr.timestamp - prev.timestamp
            if i % 2 == 0:  # Blue's move
                blue_time += time_spent
            else:  # Red's move
                red_time += time_spent

        # Add time since last move if game is active
        if current_time is not None:
            last_move = moves[-1]
            if last_move.timestamp is not None:
                if last_move.timestamp > current_time:
                    raise ValueError("Last move timestamp cannot be in the future")
                
                time_since_last = current_time - last_move.timestamp
                if len(moves) % 2 == 0:  # Blue's turn
                    blue_time += time_since_last
                else:  # Red's turn
                    red_time += time_since_last

        # Get pause duration and split it equally between players
        # TODO later : add a attribut thats store whoses pause is for player
        pause_duration = self._hex_game.total_pause_duration
        half_pause = pause_duration / 2.0

        # Update timers with equal pause adjustment
        self._player_timers[self._hex_game.BLUE_PLAYER] = max(0.0, self._initial_time - blue_time + half_pause)
        self._player_timers[self._hex_game.RED_PLAYER] = max(0.0, self._initial_time - red_time + half_pause)
