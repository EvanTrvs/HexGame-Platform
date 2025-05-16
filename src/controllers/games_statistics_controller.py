from flask import Blueprint, render_template, request, jsonify, session
from src.models.data_management.games_monitoring import GamesMonitoring

class GamesStatisticsController:
    def __init__(self):
        self.blueprint = Blueprint('games_statistics', __name__)
        self.blueprint.add_url_rule('/statistiques', 'view_statistics', self.view_statistics, methods=['GET', 'POST'])

    def view_statistics(self):
        if request.method == 'POST':
            return self.handle_post_request()

        return self.render_statistics_template()

    def handle_post_request(self):
        data = request.get_json()
        indexes = data.get('indexes', [])
        session['selected_indexes'] = indexes  # Stockez les index dans la session
        return jsonify({"message": "Indices reçus avec succès!"})

    def render_statistics_template(self):
        selected_indexes = session.get('selected_indexes', [])
        instance_games_monitoring = GamesMonitoring.instance()
        stats = instance_games_monitoring.get_games_statistics(selected_indexes)
        return render_template('pages/statistiques_parties.html', stats=stats)
