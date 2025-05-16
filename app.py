from flask import Flask, render_template, redirect, url_for, request, jsonify
from src.controllers.games_list_controller import GamesListController
from src.controllers.games_statistics_controller import GamesStatisticsController
from src.controllers.game_controller import GameController

app = Flask(__name__)
app.secret_key = 'clé secrete'  # nécessaire pour faire des sessions

# Initialisation des contrôleurs
games_list_controller = GamesListController()
games_statistics_controller = GamesStatisticsController()
game_controller = GameController()

# Enregistrement des blueprints
app.register_blueprint(games_list_controller.blueprint)
app.register_blueprint(games_statistics_controller.blueprint)
app.register_blueprint(game_controller.game_bp)


@app.route('/')
def home():
    return render_template('pages/index.html')

if __name__ == '__main__':
    app.run(debug=True)