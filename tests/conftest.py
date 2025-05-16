import pytest
import datetime

from src.models.core import HexBoard, HexMove, HexCell
from src.models.core.hex_game import HexGame
from src.models.data_management.player_data import PlayerData
from src.models.data_management.saved_game import SavedGame
from app import app


@pytest.fixture
def game_dictionary_sgf_v4_sample():
    return [
        {'moves': [{'W': 'oa'}, {'B': 'le'}, {'W': 'dl'}, {'B': 'fe'}, {'W': 'de'}, {'B': 'eh'}, {'W': 'ig'},
                   {'B': 'gj'}, {'W': 'ji'}, {'B': 'jd'}, {'W': 'kd'}, {'B': 'je'}, {'W': 'ke'}, {'B': 'jk'},
                   {'W': 'kk'}, {'B': 'kj'}, {'W': 'lh'}, {'B': 'mi'}, {'W': 'ii'}, {'B': 'jg'}, {'W': 'hf'},
                   {'B': 'ih'}, {'W': 'hh'}, {'B': 'gk'}, {'W': 'hi'}, {'B': 'hl'}, {'W': 'lj'}, {'B': 'li'},
                   {'W': 'gl'}, {'B': 'hk'}, {'W': 'fj'}, {'B': 'gi'}, {'W': 'fi'}, {'B': 'gh'}, {'W': 'fh'},
                   {'B': 'gg'}, {'W': 'fg'}, {'B': 'fd'}, {'W': 'gf'}, {'B': 'gc'}, {'W': 'hd'}, {'B': 'resign'}],
         'FF': '4', 'EV': 'hex.cv.HEX15.6.1.1', 'PB': 'lazyplayer', 'PW': 'bootscity', 'SZ': '15', 'RE': 'B',
         'GC': ' game #2493549', 'SO': 'https://www.littlegolem.net'}
        ]


@pytest.fixture
def valid_hex_games_sample():
    sample = []
    # Red win (top to bottom)
    game = HexGame(HexBoard(3))
    game.start_game()
    moves = [
        HexMove(HexCell(0, 0)),  # Blue
        HexMove(HexCell(1, 0)),  # Red
        HexMove(HexCell(0, 1)),  # Blue
        HexMove(HexCell(1, 1)),  # Red
        HexMove(HexCell(0, 2)),  # Blue
        HexMove(HexCell(1, 2))  # Red
    ]
    for move in moves:
        game.make_move(move)

    sample.append(game)
    return sample

@pytest.fixture
def valid_saved_game_sample(valid_hex_games_sample):
    sample = []
    blue_player = "Joueur 1"
    red_player = "Joueur 2"

    for hex_game in valid_hex_games_sample:
        saved_game = SavedGame(hex_game, blue_player, red_player, winner="red", name="",
                               val_datetime=datetime.datetime.now())
        sample.append(saved_game)

    return sample

@pytest.fixture
def client():
    """Fixture pour configurer un client de test Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
