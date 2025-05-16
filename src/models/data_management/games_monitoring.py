from src.models.data_management.saved_game import SavedGame
from src.models.data_management.save_monitoring import SaveMonitoring
from src.models.data_management.read_monitoring import ReadMonitoring
from src.models.data_management.GamesStatistics import GamesStatistics


class GamesMonitoring:
    """
    Classe qui est chargée de la gestion des parties sauvegardées
    """

    _instance = None  # Attribut statique qui stocke l'instance du singleton

    def __new__(cls, *args, **kwargs):
        """
        Constructeur de GamesMonitoring. Respecte le DP Singleton afin de ne pas pouvoir être appelée directement
        """
        if cls._instance is None:

            # creation de l'instance
            cls._instance = super(GamesMonitoring, cls).__new__(cls, *args, **kwargs)
            # On initialise aussi les attributs
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Methode privée pour initialiser l'instance. On ne peut pas mettre __new__ ou __init__ en privé
        donc deleguer l'initialisation à cette méthode permet d'éviter qu'elle puisse être mal appelée
        """
        self.games_list = []
        self.read_monitor = ReadMonitoring(strategy_game=None, strategy_file=None)
        self.save_monitor = SaveMonitoring(write_game_strategy=None, write_file_strategy=None)

    @classmethod
    def instance(cls):
        """
        Méthode à appeler pour accéder à GamesMonitoring
        """
        if cls._instance is None:
            cls()  # On appelle new et init
        return cls._instance

    def add_game(self, game: SavedGame):
        """
        Methode pour ajoute une partie sauvegardée
        :param game: partie à ajouté à la liste de parties sauvegardées
        :return:
        """
        self.games_list.append(game)

    def delete_games(self, indexes: list[int]):
        """
        Supprime une ou des parties de la liste des parties sauvegardées
        :param indexes: indices des parties à supprimer dans la liste
        :return:
        """
        # suppression en partant de la fin pour ne pas supprimer les mauvais indices
        for index in sorted(indexes, reverse=True):
            if 0 <= index < len(self.games_list):
                self.games_list.pop(index)

    def get_saved_games(self) -> list[SavedGame]:
        """
        Renvoie les parties sauvegardées
        :return:
        """
        return self.games_list

    def get_saved_game(self, index: int) -> SavedGame:
        """
        Renvoie une partie sauvegardée
        :param index: indice de la partie dans la liste
        :return:
        """
        return self.games_list[index]

    def add_games_from_file(self, file_path, strategy_read_game=None) ->None:
        """
        Lis un fichier et sauvegarde les parties qu'il contient
        :param file_path: le chemin du fichier à lire
        :param strategy_read_game: strategie de lecture à utiliser, par exemple ReadSgfV4
        :return:
        """
        self.read_monitor.set_read_game_strategy(strategy_read_game)
        games = self.read_monitor.read(file_path=file_path)

        for game in games:
            self.add_game(game)

    def save_games_to_file(self, indexes: list[int], file_path: str, write_game_strategy):
        """
        Ecris les parties dans un fichier en suivant une strategie d'écriture
        :param file_path: Chemin du fichier à écrire
        :param write_game_strategy: La strategie de conversion à utiliser, par exemple WriteSGFv4
        :return:
        """

        games_to_save = [self.games_list[i] for i in indexes]
        self.save_monitor.set_write_game_strategy(write_game_strategy)
        self.save_monitor.save_games(saved_games=games_to_save, file_path=file_path)

    def get_games_statistics(self, indexs: list[int]) -> dict:
        """
        Retourne un dictionnaire contenant les statistiques sur un ensemble de parties
        :param indexs: Les indices des parties à utiliser pour calculer les statistiques
        :return:
        """
        games_to_show = [self.games_list[i] for i in indexs]
        return GamesStatistics.get_statistics(games_to_show)

