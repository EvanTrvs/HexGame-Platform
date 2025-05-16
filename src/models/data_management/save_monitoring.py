from .write_files import WriteFileMonitoring, WriteHsgf, WriteJson, WriteXML, WriteSqlite
from .write_game import WriteGameMonitoring
from .saved_game import SavedGame


class SaveMonitoring:
    """
    Classe responsable de la logique de sauvegarde des parties vers des fichiers
    """
    def __init__(self, write_game_strategy, write_file_strategy):
        """
        Constructeur de SaveMonitoring
        :param write_game_strategy: Strategy d'ecriture des parties à utiliser
        :param write_file_strategy: Strategy d'ecriture des fichiers à utiliser
        """
        self.write_game_monitor = WriteGameMonitoring(write_game_strategy)
        self.write_file_monitor = WriteFileMonitoring(write_file_strategy)

    def set_write_file_strategy(self, write_file_strategy):
        """
        Setter de la strategie d'ecriture de fichier
        :param write_file_strategy:
        :return:
        """
        self.write_file_monitor.set_strategy(write_file_strategy)

    def set_write_game_strategy(self, write_game_strategy):
        """
        Setter de la strategie d'ecriture de dictionnaire
        :param write_game_strategy:
        :return:
        """
        self.write_game_monitor.set_strategy(write_game_strategy)

    def save_games(self, saved_games: list[SavedGame], file_path: str) -> None:
        """
        Gère la sauvegarde d'une liste de parties dans un fichier
        :param saved_games: les parties à sauvegarder
        """
        self.choose_right_write_file_strategy(file_path)
        if self.write_file_monitor.strategy is None:
            raise ValueError("strategy_write_file ne peut pas être None")
        else:
            dictionaries = []  # liste des dictionnaires à ecrire

            # creation des dictionnaires à partir des parties
            for saved_game in saved_games:
                dictionaries.append(self.write_game_monitor.write_game(saved_game))

            # ecriture des dictionnaires dans le fichier
            if dictionaries:
                self.write_file_monitor.write_file(dictionaries, file_path)

    def choose_right_write_file_strategy(self, file_path: str) -> None:
        """
        Met à jour la strategie d'ecriture dans fichier en fonction de l'extension du fichier
        """
        if file_path.endswith('.json'):
            self.write_file_monitor.set_strategy(WriteJson())
        elif file_path.endswith('.xml'):
            self.write_file_monitor.set_strategy(WriteXML())
        elif file_path.endswith('.sqlite'):
            self.write_file_monitor.set_strategy(WriteSqlite())
        elif file_path.endswith('.sgf') or file_path.endswith('.hsgf'):
            self.write_file_monitor.set_strategy(WriteHsgf())
        else:
            raise Exception('Type de fichier non reconnu.')
