import os
import pytest
from flask import json
from werkzeug.datastructures import FileStorage
from src.models.data_management.write_game import WriteGameSGFV4
from src.models.data_management.games_monitoring import GamesMonitoring
from src.models.data_management.saved_game import SavedGame
from src.models.data_management.read_game import ReadSGFV4
from tests.conftest import client


def test_end_to_end_controllers(client) -> None:
    """
    Test end to end en utilisant les controllers.
    Scenario:
    - Ajout de parties depuis le gestionnaire de parties en lisant un fichier hsgf
    - Accés aux statistiques de l'une des parties
    - Suppression de certaines parties
    - Ecriture d'une partie dans un fichier json
    """
    # Construire le chemin correct vers le fichier de test
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(base_dir, '..', 'fichiers_test', 'valid_games_list.hsgf')

    # On créé le répertoire temporaire s'il n'existe pas, c'est utilisé dans le controller
    tmp_dir = os.path.join(base_dir, 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    # On prépare les données pour la requête POST
    with open(test_file_path, 'rb') as f:
        file_data = FileStorage(stream=f, filename=os.path.basename(test_file_path))
        data = {
            'file': file_data,
            'type': 'sgf'
        }

        # Envoyer la requête POST
        response = client.post("/games_list", data=data, content_type='multipart/form-data')

        # Vérifier la réponse
        assert response.status_code == 200
        assert response.json['message'] == "Fichier chargé avec succès!"

    # On ouvre les statistiques de l'une des parties importées
    selected_indexes = [0]

    response = client.post("/statistiques",
                           data=json.dumps({"indexes": selected_indexes}),
                           content_type='application/json')

    assert response.status_code == 200
    assert response.json['message'] == 'Indices reçus avec succès!'

    # On supprime la première partie
    selected_delete_indexes = [0]

    response = client.delete("/games_list",
                             data=json.dumps({"indexes": selected_delete_indexes}),
                             content_type='application/json')

    # On verrifie que la réponse contient le message de succès attendu
    assert response.status_code == 200
    assert response.json['message'] == "Parties supprimées avec succès!"

    # Maintenant on teste l'ecriture d'une partie dans un fichier json
    selected_indexes_to_save = [0]
    selected_format = 'json'
    file_name = f'saved_games.{selected_format}'

    downloaded_file_path = os.path.join(tmp_dir, file_name)

    # on supprime le fichier au cas ou il existerait
    if os.path.exists(downloaded_file_path):
        os.remove(downloaded_file_path)

    response = client.post("/sauvegarder_parties",
                           data=json.dumps({"indexes": selected_indexes_to_save, "file_name": file_name}),
                           content_type='application/json')

    assert response.status_code == 200



def test_end_to_end_game_read_write():
    """
    Teste end to end du scenario suivant plus complet qu'avec les controllers:
    - Lecture de parties dans un fichier hsgf
    - Suppression de parties
    - Ecriture d'une des parties dans un fichier json
    - Lecture de la partie via le fichier json, et verification que la partie est identique à celle écrite
    """

    games_monitor = GamesMonitoring.instance()

    # 1) Lecture d'un fichier contenant des parties
    read_game_strategy = ReadSGFV4()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "fichiers_test", "valid_games_list.hsgf")

    # obligé de faire ça à cause du DP singleton
    initial_size = len(games_monitor.get_saved_games())
    games_monitor.add_games_from_file(file_path, read_game_strategy)
    base_saved_games_size = len(games_monitor.get_saved_games())
    assert base_saved_games_size > initial_size  # Test que des parties ont bien été lues

    # 2) Suppression de certaines parties
    games_monitor.delete_games([0, 1, 2])

    # test que certaines parties ont bien été supprimées
    saved_games_size_after_delete = len(games_monitor.get_saved_games())
    assert saved_games_size_after_delete < base_saved_games_size

    # 3) Ecriture d'une partie dans un fichier json
    game_to_save: SavedGame = games_monitor.get_saved_games()[0]
    json_path = os.path.join(base_dir, "..", "fichiers_test", "new_file.json")
    games_monitor.save_games_to_file([0], json_path, WriteGameSGFV4())

    # verification de la creation du fichier
    assert os.path.exists(json_path), "Le fichier n'a pas été créé."

    # 4) Lecture du nouveau fichier
    games_monitor.add_games_from_file(json_path, read_game_strategy)

    # verification que les deux parties ont bien été ajoutées
    saved_games_size_after_import_json = len(games_monitor.get_saved_games())
    assert saved_games_size_after_import_json == saved_games_size_after_delete + 1

    # verification que la partie lue est bien identique à celle qui avait été envoyé
    new_game: SavedGame = games_monitor.get_saved_games()[-1]
    assert new_game.winner == game_to_save.winner
    assert new_game.red_player.name == game_to_save.red_player.name
    assert new_game.blue_player.name == game_to_save.blue_player.name
    assert new_game.game.board.size == game_to_save.game.board.size
    assert new_game.game.winner == game_to_save.game.winner
    assert new_game.game.game_end_reason == game_to_save.game.game_end_reason
    assert new_game.game.board.get_moves()[0] == game_to_save.game.board.get_moves()[0]

    # suppression du fichier json de test
    os.remove(json_path)
