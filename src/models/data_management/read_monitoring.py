from .read_file import ReadFileMonitoring, ReadSqlite, ReadJson, ReadXml, ReadHsgf
from .read_game import ReadGameMonitoring
from .saved_game import SavedGame


class ReadMonitoring:
    def __init__(self, strategy_game, strategy_file):
        """
        Constructeur de ReadMonitoring
        :param strategy_game: strategie de consruction de dictionnaire utilisée dans le fichier
        :param strategy_file: type de fichier à lire
        """
        self.read_game_monitor = ReadGameMonitoring(strategy_game)
        self.read_file_monitor = ReadFileMonitoring(strategy_file)

    def read(self, file_path: str)->list[SavedGame]:
        """
        Retourne les parties contenues dans un fichier
        :param file_path le chemin du fichier à lire
        """
        # on commence par detecter la strategie de lecture de fichier en fonction de l'extension du fichier
        # ça levera une erreur si ce n'est pas une extension gérée
        self.choose_right_file_strategy(file_path=file_path)

        # si aucune strategy n'est selectionné pour la lecture de partie on va lever une erreur
        if self.read_game_monitor.strategy is None:
            raise ValueError("strategy_read_game ne peut pas être None")
        else:
            # On va stocker les exceptions de lecture pour les afficher sur la page html s'il y en a
            exceptions = []

            # liste de dictionnaires contenant les parties
            games_dictionaries = []
            try:
                games_dictionaries = self.read_file_monitor.read_file(file_path)
            except Exception as e:
                exceptions.append(e)
                print(f"Erreur lors de la lecture du fichier : {e}")

            list_saved_games = []
            for game_dictionary in games_dictionaries:
                try:
                    saved_game = self.read_game_monitor.read_game(game_dictionary)
                    list_saved_games.append(saved_game)
                except ValueError as ve:
                    print(f"Erreur lors de la lecture de la partie : {ve}")
                except Exception as e:
                    print(f"Erreur lors de la lecture de la partie : {e}")

            return list_saved_games

    def set_read_game_strategy(self, strategy):
        self.read_game_monitor.set_strategy(strategy)

    def set_read_file_strategy(self, strategy):
        self.read_file_monitor.set_strategy(strategy)

    def choose_right_file_strategy(self, file_path:str)->None:
        """
        Met à jour la strategie d'ecriture dans fichier en fonction de l'extension du fichier
        """
        if file_path.endswith('.json'):
            self.read_file_monitor.set_strategy(ReadJson())
        elif file_path.endswith('.xml'):
            self.read_file_monitor.set_strategy(ReadXml())
        elif file_path.endswith('.sqlite'):
            self.read_file_monitor.set_strategy(ReadSqlite())
        elif file_path.endswith('.sgf') or file_path.endswith('.hsgf'):
            self.read_file_monitor.set_strategy(ReadHsgf())
        else:
            raise Exception('Type de fichier non reconnu.')
