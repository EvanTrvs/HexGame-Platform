from flask import Blueprint, render_template, jsonify, request
from src.models.game_management.game_environment_manager import GameEnvironmentManager
from src.models.game_management import MoveCommand, PauseCommand, ResumeCommand, ResignCommand
from src.models.core import HexGame, HexBoard, HexMove, HexState, GameEndReason
from src.models.data_management.games_monitoring import GamesMonitoring
from src.models.data_management.saved_game import SavedGame
import asyncio
from functools import wraps

class GameController:
    game_bp = Blueprint('game', __name__)
    _last_action_message = None  # Cache for the last action message

    @staticmethod
    def async_route(f):
        """Decorator to handle async routes in Flask."""
        @wraps(f)
        def wrapper(*args, **kwargs):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(f(*args, **kwargs))
                return result
            finally:
                loop.close()
        return wrapper

    @classmethod
    def register_routes(cls):
        """Register all routes for the game controller."""
        cls.game_bp.route('/game')(cls.game_page)
        cls.game_bp.route('/api/game/start', methods=['POST'])(cls.async_route(cls.start_game))
        cls.game_bp.route('/api/game/move', methods=['POST'])(cls.async_route(cls.make_move))
        cls.game_bp.route('/api/game/state', methods=['GET'])(cls.get_game_state)
        cls.game_bp.route('/api/game/pause', methods=['POST'])(cls.async_route(cls.pause_game))
        cls.game_bp.route('/api/game/resume', methods=['POST'])(cls.async_route(cls.resume_game))
        cls.game_bp.route('/api/game/resign', methods=['POST'])(cls.async_route(cls.resign_game))
        cls.game_bp.route('/api/game/save', methods=['POST'])(cls.save_game)
        cls.game_bp.route('/api/game/load/<int:game_index>', methods=['POST'])(cls.async_route(cls.load_game))
        cls.game_bp.route('/api/game/prev-move', methods=['POST'])(cls.prev_move)
        cls.game_bp.route('/api/game/next-move', methods=['POST'])(cls.next_move)

    @staticmethod
    def game_page():
        """Render the main game page."""
        return render_template('pages/game.html')

    @classmethod
    def _get_players(cls, env_manager):
        """Get the players from the environment manager."""
        if not env_manager.is_environment_active():
            return None, None, None
        players = env_manager.players
        return players[0], players[1], players[2]  # blue, red, spectator

    @classmethod
    def _get_current_player(cls, env_manager):
        """Get the player whose turn it is."""
        blue, red, _ = cls._get_players(env_manager)
        if blue and blue.is_current_player:
            return blue
        if red and red.is_current_player:
            return red
        return None

    @classmethod
    def _generate_game_state_message(cls, state, game_end_reason=None, winner=None):
        """Generate a standardized game state message based on the current state."""
        if state == HexState.NOT_STARTED:
            return "Game is NOT STARTED"
        elif state == HexState.ACTIVE:
            return "Game is ACTIVE"
        elif state == HexState.PAUSED:
            return "Game is PAUSED"
        elif state == HexState.FINISHED:
            if game_end_reason == GameEndReason.VICTORY:
                return f"Game is FINISHED - {winner} won the game!"
            elif game_end_reason == GameEndReason.RESIGN:
                return f"Game is FINISHED - {winner} won by resignation!"
            elif game_end_reason == GameEndReason.OVERTIME:
                return f"Game is FINISHED - {winner} won by timeout!"
            else:
                return "Game is FINISHED"
        elif state == HexState.CORRUPTED:
            return "Game is CORRUPTED! Limited access!"
        elif state == "REPLAY":
            "Game REPLAY MODE - No Action available !"
        else:
            return "Unknown game state"
        
    @classmethod
    def _generate_game_state_info(cls, state):
        """Generate a standardized game state message based on the current state."""
        if state == HexState.NOT_STARTED:
            return "NOT_STARTED"
        elif state == HexState.ACTIVE:
            return "ACTIVE"
        elif state == HexState.PAUSED:
            return "PAUSED"
        elif state == HexState.FINISHED:
            return "FINISHED"
        return "CORRUPTED"

    @classmethod
    def _generate_action_message(cls, action, **kwargs):
        """Generate an optional message for specific actions."""
        if action == "move":
            x, y = kwargs.get('x'), kwargs.get('y')
            player = kwargs.get('player')
            return f"Move made at ({x}, {y}) by {player}"
        elif action == "start":
            return "New game started"
        elif action == "pause":
            return "Game paused"
        elif action == "resume":
            return "Game resumed"
        elif action == "resign":
            player = kwargs.get('player')
            return f"{player} resigned"
        elif action == "save":
            return "Game saved"
        return None

    @classmethod
    def _generate_base_response(cls, env_manager):
        """Generate the base response structure with common game data."""
        if not env_manager.is_environment_active():
            return {
                'game_state': {
                    'state': 'NOT_INITIALIZED',
                    'message': 'Game not initialized'
                },
                'board_state': None,
                'current_player': None,
                'players': None
            }

        _, _, spectator = cls._get_players(env_manager)
        current_player = cls._get_current_player(env_manager)
        state = spectator.get_game_state()
        state_code = cls._generate_game_state_info(state)
        game_end_reason, winner = spectator.get_game_result() if state == HexState.FINISHED else (None, None)

        if env_manager.move_replay is None:
            board_state = env_manager.game_manager.game_board.board.get_board_state().tolist()
        else:
            board_state = env_manager.game_manager.game_board.board.get_board_state_at_move(env_manager.move_replay).tolist()
            state_code = "REPLAY"
            state = "REPLAY"

        return {
            'game_state': {
                'state': state_code,
                'message': cls._generate_game_state_message(state, game_end_reason, winner)
            },
            'board_state': board_state,
            'current_player': current_player.name if current_player else None,
            'players': {
                'blue': "Blue Player Name: " + env_manager.current_players[0].name,
                'red': "Red Player Name: " + env_manager.current_players[1].name
            }
        }

    @classmethod
    def _generate_response_data(cls, env_manager, action=None, **kwargs):
        """Generate standardized response data structure."""
        response_data = cls._generate_base_response(env_manager)
        
        # Update action message if provided
        if action:
            cls._last_action_message = cls._generate_action_message(action, **kwargs)
        
        # Always include the last action message in the response
        response_data['action_message'] = cls._last_action_message
            
        return response_data

    @classmethod
    def get_game_state(cls):
        """Get the current game state."""
        try:
            env_manager = GameEnvironmentManager()
            response_data = cls._generate_response_data(env_manager)
            
            return jsonify({
                'status': 'success',
                'data': response_data
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400

    @classmethod
    def _handle_response(cls, func, action=None, **kwargs):
        """Central handler for all game responses and updates."""
        try:
            result = func()
            env_manager = GameEnvironmentManager()
            
            # Get the standardized response data
            response_data = cls._generate_response_data(env_manager, action, **result if result else {})
            
            # If the function returned additional data, merge it
            if result and isinstance(result, dict):
                response_data.update(result)
                
            return jsonify({
                'status': 'success',
                'data': response_data
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400

    @classmethod
    async def start_game(cls):
        """Start a new game with the specified parameters."""
        data = request.get_json()
        
        board_size = data.get('board_size', 11)
        
        env_manager = GameEnvironmentManager()
        env_manager.load_default_environment(board_size)            

        try:
            await env_manager.current_game_manager.start()
            return cls._handle_response(
                lambda: {'board_size': board_size},
                action="start"
            )
        except Exception as e:
            return cls._error_response(str(e))

    @classmethod
    async def make_move(cls):
        """Make a move in the game."""
        try:
            data = request.get_json()
            x = data.get('x')
            y = data.get('y')
            
            env_manager = GameEnvironmentManager()
            player_turn = cls._get_current_player(env_manager)
            
            if not all([x is not None, y is not None, player_turn]):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid move data'
                }), 400
            
            player_command = env_manager.current_players[0] if env_manager.current_players[0].name == player_turn.name else env_manager.current_players[1]
            command = MoveCommand(player_command, x, y)
            await player_command.send_command(command)
            
            return cls._handle_response(
                lambda: {'x': x, 'y': y, 'player': player_turn.name},
                action="move"
            )
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400

    @classmethod
    async def pause_game(cls):
        """Pause the current game."""
        try:
            env_manager = GameEnvironmentManager()
            current_player = cls._get_current_player(env_manager)
            if not current_player:
                return jsonify({
                    'status': 'error',
                    'message': 'No active player'
                }), 400
            
            command = PauseCommand(current_player)
            await current_player.send_command(command)
            
            return cls._handle_response(
                lambda: None,
                action="pause"
            )
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400

    @classmethod
    async def resume_game(cls):
        """Resume the paused game."""
        try:
            env_manager = GameEnvironmentManager()
            current_player = cls._get_current_player(env_manager)
            if not current_player:
                return jsonify({
                    'status': 'error',
                    'message': 'No active player'
                }), 400
            
            command = ResumeCommand(current_player)
            await current_player.send_command(command)
            
            return cls._handle_response(
                lambda: None,
                action="resume"
            )
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400

    @classmethod
    async def resign_game(cls):
        """Resign from the current game."""
        try:
            env_manager = GameEnvironmentManager()
            current_player = cls._get_current_player(env_manager)
            
            if not current_player:
                return jsonify({
                    'status': 'error',
                    'message': 'Player color not specified'
                }), 400
            
            command = ResignCommand(current_player)
            await current_player.send_command(command)
            
            return cls._handle_response(
                lambda: None,
                action="resign"
            )
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400

    @classmethod
    def save_game(cls):
        """Save the current game state."""
        try:
            env_manager = GameEnvironmentManager()
            
            data = request.get_json()
            blue_player_name = data.get('blue_player_name')
            red_player_name = data.get('red_player_name')
            
            if not all([blue_player_name, red_player_name]):
                return jsonify({
                    'status': 'error',
                    'message': 'Player names not specified'
                }), 400

            # Créer une copie de la partie à sauvegarder
            save_game = SavedGame(
                game=env_manager.current_game_manager.game_board,
                blue_player_name=blue_player_name,
                red_player_name=red_player_name
            )
            
            instance_games_monitoring = GamesMonitoring.instance()
            instance_games_monitoring.add_game(save_game)
            
            return cls._handle_response(
                lambda: None,
                action="save"
            )
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
    
    @classmethod
    async def load_game(cls, game_index):
        """Load a new game from data storage."""
        
        instance_games_monitoring = GamesMonitoring.instance()

        game = instance_games_monitoring.get_saved_game(game_index)
        if not game:
            raise IndexError("Partie non trouvée")
        
        # Créer une copie manuelle de la partie
        game_copy = SavedGame(
            game=game.game,  # Le jeu est déjà une copie dans SavedGame
            blue_player_name=game.blue_player.name,
            red_player_name=game.red_player.name
        )
        
        env_manager = GameEnvironmentManager()
        env_manager.load_environment_from_game(game_copy.game, game_copy.blue_player.name, game_copy.red_player.name)
        
        board_size = game_copy.game.board.size  

        try:
            await env_manager.current_game_manager.start()
            return cls._handle_response(
                lambda: {'board_size': board_size},
                action="start"
            )
        except Exception as e:
            return cls._error_response(str(e))

    @classmethod
    def prev_move(cls):
        """Move to the previous move in replay mode."""
        try:
            env_manager = GameEnvironmentManager()
            
            if env_manager.move_replay is None:
                # Si on n'est pas en mode replay, on commence au dernier coup
                total_moves = env_manager.current_game_manager.game_board.board.get_total_moves()
                env_manager.move_replay = max(0, total_moves - 1)
            else:
                # On recule d'un coup, minimum 0
                env_manager.move_replay = max(0, env_manager.move_replay - 1)
            
            return cls._handle_response(
                lambda: None,
                action="prev_move"
            )
        except Exception as e:
            return cls._error_response(str(e))

    @classmethod
    def next_move(cls):
        """Move to the next move in replay mode."""
        try:
            env_manager = GameEnvironmentManager()
            total_moves = env_manager.current_game_manager.game_board.board.get_total_moves()
            
            if env_manager.move_replay is None:
                # Si on n'est pas en mode replay, on commence au premier coup
                env_manager.move_replay = 0
            else:
                # On avance d'un coup
                env_manager.move_replay += 1
                # Si on atteint le dernier coup, on sort du mode replay
                if env_manager.move_replay >= total_moves:
                    env_manager.move_replay = None
            
            return cls._handle_response(
                lambda: None,
                action="next_move"
            )
        except Exception as e:
            return cls._error_response(str(e))

# Register all routes when the module is imported
GameController.register_routes() 