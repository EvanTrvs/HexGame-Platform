import pytest
from src.models.data_management.saved_game import SavedGame
from src.models.core.hex_game import HexGame
from src.models.data_management.player_data import PlayerData
import datetime


def test_saved_game_initialization(valid_hex_games_sample):
    """
    Teste l'initialisation d'un objet SavedGame avec des valeurs valides.
    """
    hex_game = valid_hex_games_sample[0]
    blue_player = "BluePlayer"
    red_player = "RedPlayer"
    winner = "blue"
    name = "Test Game"
    val_datetime = datetime.datetime(2023, 10, 1, 12, 0, 0)

    saved_game = SavedGame(hex_game, blue_player, red_player, winner, name, val_datetime)

    assert saved_game.game == hex_game
    assert saved_game.blue_player.name == blue_player
    assert saved_game.red_player.name == red_player
    assert saved_game.winner == winner
    assert saved_game.name == name
    assert saved_game.date_time() == val_datetime


def test_saved_game_default_datetime(valid_hex_games_sample):
    """
    Teste l'initialisation d'un objet SavedGame avec une date et heure par défaut.
    """
    hex_game = valid_hex_games_sample[0]
    blue_player = "BluePlayer"
    red_player = "RedPlayer"
    winner = "red"
    name = "Test Game"

    saved_game = SavedGame(hex_game, blue_player, red_player, winner, name, val_datetime=None)

    # Vérifie que la date et l'heure sont définies à l'heure actuelle
    assert (datetime.datetime.now() - saved_game.date_time()).total_seconds() < 1


def test_saved_game_winner_setter(valid_hex_games_sample):
    """
    Teste le setter pour l'attribut winner avec des valeurs valides et invalides.
    """
    hex_game = valid_hex_games_sample[0]
    blue_player = "BluePlayer"
    red_player = "RedPlayer"
    saved_game = SavedGame(hex_game, blue_player, red_player, "blue", "Test Game", datetime.datetime.now())

    # Test avec une valeur valide
    saved_game.winner = "red"
    assert saved_game.winner == "red"

    # Test avec une valeur invalide
    with pytest.raises(ValueError, match="Erreur, il faut renseigner la couleur du gagnant 'blue' ou 'red'"):
        saved_game.winner = "green"


def test_saved_game_id_increment(valid_hex_games_sample):
    """
    Teste l'incrémentation automatique de l'ID pour chaque nouvel objet SavedGame.
    """
    hex_game = valid_hex_games_sample[0]
    blue_player = "BluePlayer"
    red_player = "RedPlayer"
    winner = "blue"
    name = "Test Game"
    val_datetime = datetime.datetime.now()

    saved_game1 = SavedGame(hex_game, blue_player, red_player, winner, name, val_datetime)
    saved_game2 = SavedGame(hex_game, blue_player, red_player, winner, name, val_datetime)

    assert saved_game1.id == saved_game2.id - 1

def test_saved_game_date_property(valid_hex_games_sample):
    """
    Teste la propriété date qui retourne uniquement la date sans l'heure.
    """
    hex_game = valid_hex_games_sample[0]
    blue_player = "BluePlayer"
    red_player = "RedPlayer"
    winner = "blue"
    name = "Test Game"
    val_datetime = datetime.datetime(2023, 10, 1, 12, 0, 0)

    saved_game = SavedGame(hex_game, blue_player, red_player, winner, name, val_datetime)

    assert saved_game.date == val_datetime.date()
