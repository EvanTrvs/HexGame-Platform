import os
from flask import Blueprint, request, jsonify, send_file, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from src.models.data_management.games_monitoring import GamesMonitoring
from src.models.data_management.write_game import WriteGameSGFV4
from src.models.data_management.read_game import ReadSGFV4, ReadOther


class GamesListController:
    def __init__(self):
        self.blueprint = Blueprint('games_list', __name__)
        self.blueprint.add_url_rule('/games_list', 'list_games', self.list_games, methods=['GET', 'POST'])
        self.blueprint.add_url_rule('/games_list', 'delete_games', self.delete_games, methods=['DELETE'])
        self.blueprint.add_url_rule('/sauvegarder_parties', 'save_selected_games', self.save_selected_games, methods=['POST'])

    def list_games(self):
        instance_games_monitoring = GamesMonitoring.instance()

        if request.method == 'POST':
            return self.handle_post_request()

        # Partie GET
        # mise à jour des parties à afficher sur la page
        games = instance_games_monitoring.get_saved_games()
        return render_template('pages/gestionnaire_parties.html', games=games)

    def handle_post_request(self):
        file = request.files['file']
        game_type = request.form['type']

        # On ne peut pas récuperer le chemin complet du fichier pour des raisons de securité
        # donc à la place on créé une version temporaire qu'on utilisera puis supprimera
        tmp_dir = os.path.join(os.getcwd(), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        instance_games_monitoring = GamesMonitoring.instance()

        filename = secure_filename(file.filename)
        file_path = os.path.join(tmp_dir, filename)

        file.save(file_path)
        try:
            read_game_strategy = self.get_read_game_strategy(game_type)

            # lecture du fichier et ajout de la partie à la liste
            instance_games_monitoring.add_games_from_file(file_path, read_game_strategy)
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        finally:
            os.remove(file_path)

        games = instance_games_monitoring.get_saved_games()
        return jsonify({"message": "Fichier chargé avec succès!"})

    def get_read_game_strategy(self, game_type):
        if game_type == 'sgf':
            return ReadSGFV4()
        elif game_type == 'play_hex':
            return ReadOther()
        else:
            raise ValueError('Erreur: Il faut une stratégie de lecture valide')

    def delete_games(self):
        data = request.get_json()
        indexes = data.get('indexes', [])

        instance_games_monitoring = GamesMonitoring.instance()
        try:
            instance_games_monitoring.delete_games(indexes)
            return jsonify({"message": "Parties supprimées avec succès!"})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def save_selected_games(self):
        data = request.get_json()
        indexes = data.get('indexes', [])
        file_name = data.get('file_name', 'saved_games.hsgf')

        instance_games_monitoring = GamesMonitoring.instance()

        # On va être obligé de créer un fichier temporaire que l'utilisateur va pouvoir télécharger
        tmp_dir = os.path.join(os.getcwd(), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        file_path = os.path.join(tmp_dir, file_name)

        try:
            instance_games_monitoring.save_games_to_file(indexes, file_path, WriteGameSGFV4())
            return send_file(file_path, as_attachment=True, download_name='saved_games.hsgf')
        except Exception as e:
            return jsonify({"error": str(e)}), 400
