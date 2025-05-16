import pytest
import os
from unittest.mock import MagicMock, patch, mock_open
from src.models.data_management.games_monitoring import GamesMonitoring
from src.models.data_management.saved_game import SavedGame
from src.models.data_management.player_data import PlayerData
from src.models.core.hex_game import HexGame
from src.models.data_management.write_game import WriteGameSGFV4
from tests.conftest import valid_saved_game_sample
import datetime

def test_singleton_instance():
    """
    Teste que GamesMonitoring est un singleton et retourne toujours la même instance.
    """
    instance1 = GamesMonitoring.instance()
    instance2 = GamesMonitoring.instance()
    assert instance1 is instance2


def test_add_game(valid_saved_game_sample):
    """
    Teste l'ajout d'un jeu à la liste des jeux sauvegardés.
    """
    monitoring = GamesMonitoring.instance()

    # On est obligé de faire ça car la taille peut varier si d'autre test ont ajouté des parties à l'instance
    base_size = len(monitoring.get_saved_games())
    monitoring.add_game(valid_saved_game_sample[0])
    assert len(monitoring.get_saved_games()) == base_size + 1
    assert monitoring.get_saved_games()[-1] == valid_saved_game_sample[0]


def test_delete_games(valid_saved_game_sample):
    """
    Teste la suppression de jeux de la liste des jeux sauvegardés.
    """
    monitoring = GamesMonitoring.instance()
    monitoring.add_game(valid_saved_game_sample[0])
    monitoring.add_game(valid_saved_game_sample[0])

    base_size = len(monitoring.get_saved_games())
    monitoring.delete_games([0])

    # On verifie que la suppression a bien enlevé une partie
    assert len(monitoring.get_saved_games()) == base_size - 1

    monitoring.delete_games([0])
    assert len(monitoring.get_saved_games()) == base_size - 2


def test_get_saved_game(valid_saved_game_sample):
    """
    Teste la récupération d'un jeu spécifique par son index.
    """
    monitoring = GamesMonitoring.instance()
    monitoring.add_game(valid_saved_game_sample[0])
    index = len(monitoring.get_saved_games()) - 1  # Index ou devrait être placée la partie
    assert monitoring.get_saved_game(index) == valid_saved_game_sample[0]


def test_add_games_from_file(valid_saved_game_sample):
    """
    Teste l'ajout de jeux à partir d'un fichier.
    """
    monitoring = GamesMonitoring.instance()
    monitoring.read_monitor.read = MagicMock(return_value=[valid_saved_game_sample[0]])

    base_size = len(monitoring.get_saved_games())

    monitoring.add_games_from_file("dummy_path")
    assert len(monitoring.get_saved_games()) == base_size + 1
    assert monitoring.get_saved_games()[-1] == valid_saved_game_sample[0]


def test_save_games_to_file(valid_saved_game_sample):
    """
    Teste la sauvegarde de jeux dans un fichier en utilisant un mock.
    """
    monitoring = GamesMonitoring.instance()
    monitoring.add_game(valid_saved_game_sample[0])

    file_path = "dummy_path/fichier_test_games_monitoring_write.hsgf"

    # Utilisation de patch pour remplacer l'ouverture de fichier par un mock
    with patch("builtins.open", mock_open()) as mock_file:
        monitoring.save_games_to_file([0], file_path, WriteGameSGFV4())

        mock_file.assert_called_once_with(file_path, 'w')

        mock_file().write.assert_called()

