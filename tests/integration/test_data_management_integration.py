import os
import pytest
from src.models.data_management.read_monitoring import ReadGameMonitoring
from src.models.data_management.save_monitoring import SaveMonitoring
from src.models.data_management.write_files import WriteHsgf, WriteJson, WriteSqlite, WriteFileMonitoring
from src.models.data_management.read_file import ReadSqlite, ReadHsgf, ReadJson, ReadFileMonitoring
from src.models.data_management.write_game import WriteGameSGFV4, WriteGameMonitoring
from src.models.data_management.read_game import ReadSGFV4
from tests.conftest import valid_hex_games_sample, valid_saved_game_sample, game_dictionary_sgf_v4_sample


# arrange
@pytest.fixture
def write_file_monitor():
    return  WriteFileMonitoring(strategy=WriteJson())


@pytest.fixture
def read_file_monitor():
    return ReadFileMonitoring(strategy=ReadJson())


@pytest.fixture
def read_game_monitor():
    return ReadGameMonitoring(strategy=ReadSGFV4())


@pytest.fixture
def write_game_monitor():
    return WriteGameMonitoring(strategy=WriteGameSGFV4())


def test_write_read_file_json(game_dictionary_sgf_v4_sample, write_file_monitor, read_file_monitor):
    """
    Teste que la lecture d'un fichier json ecrit par write_file peut etre lu par read_file
    """
    test_dictionary_init = game_dictionary_sgf_v4_sample[0]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "fichiers_test", "fichier_test.json")

    write_file_monitor.set_strategy(WriteJson())
    read_file_monitor.set_strategy(ReadJson())

    # ecriture du dictionnaire
    write_file_monitor.write_file([test_dictionary_init], file_path)

    # lecture du fichier
    new_dictionary = read_file_monitor.read_file(file_path)[0]

    # verification que les dictionnaires sont identiques
    for key in new_dictionary:
        assert new_dictionary[key] == test_dictionary_init[key]

    # Suppression du fichier de test
    os.remove(file_path)


def test_write_read_file_sqlite(game_dictionary_sgf_v4_sample, write_file_monitor, read_file_monitor):
    """
    Teste que la lecture d'un fichier sqlite ecrit par write_file peut etre lu par read_file
    """
    test_dictionary_init = game_dictionary_sgf_v4_sample[0]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "fichiers_test", "fichier_test.sqlite")

    write_file_monitor.set_strategy(WriteSqlite())
    read_file_monitor.set_strategy(ReadSqlite())

    # ecriture du dictionnaire
    write_file_monitor.write_file([test_dictionary_init], file_path)

    # lecture du fichier
    new_dictionary = read_file_monitor.read_file(file_path)[0]

    # verification que les dictionnaires sont identiques
    for key in new_dictionary:
        assert new_dictionary[key] == test_dictionary_init[key]

    # Suppression du fichier de test
    os.remove(file_path)


def test_write_read_file_hsgf(game_dictionary_sgf_v4_sample, write_file_monitor, read_file_monitor):
    """
    Teste que la lecture d'un fichier hsgf ecrit par write_file peut etre lu par read_file
    """
    test_dictionary_init = game_dictionary_sgf_v4_sample[0]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "fichiers_test", "fichier_test.hsgf")

    write_file_monitor.set_strategy(WriteHsgf())
    read_file_monitor.set_strategy(ReadHsgf())

    # ecriture du dictionnaire
    write_file_monitor.write_file([test_dictionary_init], file_path)

    # lecture du fichier
    new_dictionary = read_file_monitor.read_file(file_path)[0]

    # verification que les dictionnaires sont identiques
    for key in new_dictionary:
        assert new_dictionary[key] == test_dictionary_init[key]

    # Suppression du fichier de test
    os.remove(file_path)


def test_write_read_game_sgf_v4(valid_saved_game_sample, write_game_monitor, read_game_monitor):
    base_game = valid_saved_game_sample[0]
    write_game_monitor.set_strategy(WriteGameSGFV4())
    read_game_monitor.set_strategy(ReadSGFV4())
    # Convertir SavedGame en dictionnaire
    dictionary = write_game_monitor.write_game(base_game)

    # Convertir le dictionnaire en SavedGame
    new_saved_game = read_game_monitor.read_game(dictionary)

    # Vérifier que les objets SavedGame sont identiques
    assert new_saved_game.blue_player.name == base_game.blue_player.name
    assert new_saved_game.red_player.name == base_game.red_player.name
    assert new_saved_game.winner == base_game.winner
    assert new_saved_game.game.board.get_moves() == base_game.game.board.get_moves()

