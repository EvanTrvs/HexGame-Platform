import datetime

from src.models.data_management.read_game import ReadGameMonitoring, ReadSGFV4
from src.models.data_management.saved_game import SavedGame
from src.models.core.hex_game import HexGame


def test_read_game_monitoring_init():
    """
    Teste qu'une strategie de lecture est bien ajoutée par le constructeur
    :return:
    """
    read_game_monitor = ReadGameMonitoring(ReadSGFV4())
    assert isinstance(read_game_monitor.strategy, ReadSGFV4)


def test_read_game_monitoring_set_strategy():
    """
    Teste le seter de strategie de ReadGameMonitoring
    :return:
    """
    read_game_monitor = ReadGameMonitoring(strategy=None)
    assert read_game_monitor.strategy is None
    read_game_monitor.set_strategy(ReadSGFV4())
    assert isinstance(read_game_monitor.strategy, ReadSGFV4)


def test_make_game_with_valid_moves():
    """
    Teste la logique de conversion d'actions de sgf vers des coordonnées correctes
    """
    strategy = ReadSGFV4()
    board_size = 11
    moves = [
        {"W": "aa"},
        {"B": "bb"},
        {"W": "ca"},
    ]
    hex_game = strategy.make_game(board_size, moves)
    assert hex_game.board.size == board_size
    assert len(hex_game.board.get_moves()) == 3
    assert hex_game.board.get_moves()[0].cell.x == 0
    assert hex_game.board.get_moves()[0].cell.y == 0
    assert hex_game.board.get_moves()[2].cell.x == 0
    assert hex_game.board.get_moves()[2].cell.y == 2

def test_convert_sgf_to_coordinates_valid():
    """
    Vérifie que la méthode convert_sgf_to_coordinates convertit correctement
    les positions SGF en coordonnées pour des plateaux de taille standard.
    """
    board_size = 11

    # Test avec une position valide
    position = "ca"
    x, y = ReadSGFV4.convert_sgf_to_coordinates(position, board_size)
    assert x == 0
    assert y == 2


def test_convert_sgf_to_coordinates_invalid():
    """
    Vérifie que la méthode convert_sgf_to_coordinates leve une erreur pour des positions invalides
    """
    board_size = 11

    # Test avec une position invalide
    try:
        ReadSGFV4.convert_sgf_to_coordinates("a", board_size)
        assert False, "Expected ValueError for invalid SGF position"
    except ValueError as e:
        assert str(e) == "Position SGF invalide : a"


def test_read_game_sgf_v4_read_game(game_dictionary_sgf_v4_sample):
    """
    Verrifie que la méthode read_game de la strategie ReadSGFV4 retourne la bonne SavedGame
    :param game_dictionary_sgf_v4_sample:
    :return:
    """
    valid_dictionary = game_dictionary_sgf_v4_sample[0]
    instance_read_monitoring_sgf_v4 = ReadGameMonitoring(ReadSGFV4())
    test_saved_game = instance_read_monitoring_sgf_v4.read_game(valid_dictionary)
    assert test_saved_game.red_player.name == valid_dictionary['PB']
    assert test_saved_game.blue_player.name == valid_dictionary['PW']
    assert isinstance(test_saved_game.name, str)

    # verification que le winner est le même que dans le dictionnaire
    winner = "B" if test_saved_game.winner == 'blue' else "W"
    assert winner == valid_dictionary['RE']

    # On verifie que la taille du plateau est la même que dans le dictionnaire
    assert test_saved_game.game.board.size == int(valid_dictionary['SZ'])

    # on regarde si le premier move correspond bien dans le dictionnaire et dans la partie
    # d'abord on trouve les coordonnees du premier move à partie du dictionnaire
    coordonnees_dict_0 = ReadSGFV4.convert_sgf_to_coordinates(valid_dictionary["moves"][0]["W"],
                                                               int(valid_dictionary['SZ']))

    assert test_saved_game.game.board.get_moves()[0].cell.x == coordonnees_dict_0[0]
    assert test_saved_game.game.board.get_moves()[0].cell.y == coordonnees_dict_0[1]

