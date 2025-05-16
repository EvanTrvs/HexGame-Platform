from .interfaces import GameEndReason, IHexState, HexState
from .exceptions import InvalidStateTransition


# Concrete State: NotStartedState
class NotStartedState(IHexState):
    value = HexState.NOT_STARTED
    
    def start_game(self, game) -> None:
        game.state = ActiveState()
        game._start_time = game.get_current_time()

    def pause_game(self, game) -> None:
        raise InvalidStateTransition("Game is not started yet. Cannot pause.")

    def resume_game(self, game) -> None:
        raise InvalidStateTransition("Game is not started yet. Cannot resume.")

    def end_game(self, game, reason: GameEndReason) -> None:
        raise InvalidStateTransition("Game is not started yet. Cannot end.")

    def corrupt_game(self, game) -> None:
        game.state = CorruptedState()

# Concrete State: ActiveState
class ActiveState(IHexState):
    value = HexState.ACTIVE
    
    def start_game(self, game) -> None:
        raise InvalidStateTransition("Game is already active.")

    def pause_game(self, game) -> None:
        game.state = PausedState()
        game._last_pause_start_time = game.get_current_time()

    def resume_game(self, game) -> None:
        raise InvalidStateTransition("Game is already active. Cannot resume.")

    def end_game(self, game, reason: GameEndReason) -> None:
        game.state = FinishedState()
        game._end_time = game.get_current_time()
        game._game_end_reason = reason

    def corrupt_game(self, game) -> None:
        game.state = CorruptedState()

# Concrete State: PausedState
class PausedState(IHexState):
    value = HexState.PAUSED
    
    def start_game(self, game) -> None:
        raise InvalidStateTransition("Game is paused. Cannot start.")

    def pause_game(self, game) -> None:
        raise InvalidStateTransition("Game is already paused.")

    def resume_game(self, game) -> None:
        game.state = ActiveState()
        game._total_pause_duration += game.get_current_time() - game._last_pause_start_time

    def end_game(self, game, reason: GameEndReason) -> None:
        game.state = FinishedState()
        game._end_time = game.get_current_time()
        game._game_end_reason = reason

    def corrupt_game(self, game) -> None:
        game.state = CorruptedState()

# Concrete State: FinishedState
class FinishedState(IHexState):
    value = HexState.FINISHED
    
    def start_game(self, game) -> None:
        raise InvalidStateTransition("Game is finished. Cannot start.")

    def pause_game(self, game) -> None:
        raise InvalidStateTransition("Game is finished. Cannot pause.")

    def resume_game(self, game) -> None:
        raise InvalidStateTransition("Game is finished. Cannot resume.")

    def end_game(self, game, reason: GameEndReason) -> None:
        raise InvalidStateTransition("Game is already finished.")

    def corrupt_game(self, game) -> None:
        game.state = CorruptedState()

# Concrete State: CorruptedState
class CorruptedState(IHexState):
    value = HexState.CORRUPTED
    
    def start_game(self, game) -> None:
        raise InvalidStateTransition("Game is corrupted. Cannot start.")

    def pause_game(self, game) -> None:
        raise InvalidStateTransition("Game is corrupted. Cannot pause.")

    def resume_game(self, game) -> None:
        raise InvalidStateTransition("Game is corrupted. Cannot resume.")

    def end_game(self, game, reason: GameEndReason) -> None:
        raise InvalidStateTransition("Game is corrupted. Cannot end.")

    def corrupt_game(self, game) -> None:
        raise InvalidStateTransition("Game is already corrupted.")
