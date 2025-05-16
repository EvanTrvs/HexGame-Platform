from abc import ABC, abstractmethod
from src.models.data_management.saved_game import SavedGame
from src.models.core.hex_game_factory import HexGameFactory
from src.models.core.hex_move import HexMove


class ReadGameMonitoring():
    """
    Classe responsable de la lecture des dictionnaires des parties.
    Fait partie du DP strategy
    """
    def __init__(self, strategy):
        """
        Constructeur de ReadGameMonitoring.
        :param strategy(ReadGameStrategy): Strategie utilisée dans le dictionnaire à convertire en partie
        """
        self.strategy = strategy

    def read_game(self, dictionary: dict) -> SavedGame:
        """
        Transforme le dictionnaire obtenu par la lecture d'un fichier en une instance de la classe SavedGame
        :param dictionary: dictionnaire contenant les données
        :return: objet de la classe SavedGame correspondant aux données
        """
        return self.strategy.read_game(dictionary)

    def set_strategy(self, strategy):
        self.strategy = strategy


class ReadGameStrategy(ABC):
    """
    Interface de lecture de dictionnaire. Transforme des dictionnaires en SavedGamee
    """
    @abstractmethod
    def read_game(self, dictionary: dict) -> SavedGame:
        pass


class ReadSGFV4(ReadGameStrategy):
    def read_game(self, dictionary: dict) -> SavedGame:
        """
        Transforme le dictionnaire obtenu par la lecture d'un fichier au format sgf_v4 en une instance de la classe SavedGame
        :param dictionary: dictionnaire contenant les données
        :return: objet de la classe SavedGame correspondant aux données
        """
        try:
            version_sgf = dictionary['FF']

            if version_sgf != '4':
                raise ValueError("ERREUR: Le dictionnaire ne contient pas un encodage de type SGF V4")

            moves = dictionary["moves"]

            # Joueur noir = bleu chez nous, et blanc = rouge
            blue_player_name = dictionary["PW"]  # les blancs commencent toujours et bleu commence toujours
            red_player_name = dictionary["PB"]
            board_size = int(dictionary["SZ"])  # à utiliser pour génerer la partie

            # La clé RE donne le perdant mais tous les fichiers sgf ne la précisent pas forcement
            winner = None
            if 'RE' in dictionary:
                if dictionary['RE'] == 'B':
                    winner = "blue"
                elif dictionary['RE'] == 'W':
                    winner = "red"

            # appel de la fonction make_game pour faire la partie
            hex_game = self.make_game(board_size, moves)
            saved_game = SavedGame(game=hex_game, blue_player_name=blue_player_name, red_player_name=red_player_name,
                                   winner=winner, name=None, val_datetime=None)
            return saved_game

        except KeyError as e:
            raise ValueError(f"ERREUR: La clé {e} est manquante dans le dictionnaire.")

    @staticmethod
    def make_game(board_size, moves):
        """
        Construit l'objet HexGame à partir des données récupérées dans le dictionnaire.
        """
        # Creation de l'objet HexGame à l'aide d'une factory
        hex_game_factory = HexGameFactory()
        hex_game = hex_game_factory.create_game(board_size=board_size)

        # A partir de maintenant on va construire la partie en la simulant
        # On fait ça car la gestion des differentes erreurs possibles est implémentée

        hex_game.start_game()

        for move in moves:
            for color, position in move.items():
                if position == "resign":
                    # cas d'abandon d'un joueur
                    if color == "W":
                        hex_game.resign_game(hex_game.RED_PLAYER)
                    else:
                        hex_game.resign_game(hex_game.BLUE_PLAYER)
                    break
                elif position == "swap":
                    # On ne gère le swap dans notre implementation pour l'instant
                    raise ValueError("Le swap n'est pas pris en charge par notre application")
                else:
                    # On convertit la position SGF en coordonnées (x, y)
                    x, y = ReadSGFV4.convert_sgf_to_coordinates(position, board_size)
                    hex_move = HexMove((x, y))

                    # On applique le mouvement
                    hex_game.make_move(hex_move)

        return hex_game

    @staticmethod
    def convert_sgf_to_coordinates(position, board_size):
        """
        Convertit une position SGF en coordonnées (x, y) en fonction de la taille du plateau.
        :param position: Position en notation SGF.
        :param board_size: Taille du plateau (utilisé pour valider les coordonnées).
        :return: Coordonnées (x, y) correspondantes.
        """

        # Cas standard pour les plateaux jusqu'à 26x26
        if len(position) != 2:
            raise ValueError(f"Position SGF invalide : {position}")

        # Convertir les lettres en indices
        col = ord(position[0].lower()) - ord('a')
        row = ord(position[1].lower()) - ord('a')

        # Vérifier que les coordonnées sont dans les limites du plateau
        if col >= board_size or row >= board_size:
            raise ValueError(f"Coordonnées {position} hors des limites du plateau de taille {board_size}.")

        return row, col


class ReadOther(ReadGameStrategy):
    def read_game(self, dictionary: dict) -> SavedGame:
        pass
