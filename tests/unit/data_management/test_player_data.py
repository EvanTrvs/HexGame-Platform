import pytest
from src.models.data_management.player_data import PlayerData


def test_player_data_initialization():
    """
    Teste l'initialisation d'un objet PlayerData avec un nom valide.
    """
    ancien_id = PlayerData._id_count
    player = PlayerData(name="TestPlayer")
    assert player.name == "TestPlayer"
    assert player.id == ancien_id + 1  # Vérifie que l'ID est correctement incrémenté


def test_player_data_id_increment():
    """
    Teste que l'ID est correctement incrémenté pour chaque nouvel objet PlayerData.
    """
    player1 = PlayerData(name="Player1")
    player2 = PlayerData(name="Player2")

    assert player2.id == player1.id + 1


def test_player_data_set_name():
    """
    Teste le setter pour le nom.
    """
    player = PlayerData(name="InitialName")
    player.name = "NewName"

    assert player.name == "NewName"


def test_player_data_name_property():
    """
    Teste le getter pour le nom.
    """
    player = PlayerData(name="TestPlayer")
    assert player.name == "TestPlayer"

