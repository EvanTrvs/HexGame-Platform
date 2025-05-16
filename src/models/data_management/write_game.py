from abc import ABC, abstractmethod
from src.models.data_management.saved_game import SavedGame
from src.models.core.interfaces import GameEndReason


class WriteGameMonitoring:
    """
    Context du DP Strategy pour l'ecriture de parties à partir de dictionnaires
    """
    def __init__(self, strategy):
        """
        Constructeur de la classe de gestion de conversion des parties en dictionnaires
        :param strategie (ConvertGameStrategy): strategie de conversion à adopter
        """
        self.strategy = strategy

    def write_game(self, saved_game: SavedGame):
        """
        Créé un dictionnaire à partir d'une partie en suivant une certaine strategie
        :param saved_game: SavedGame: la partie à convertir
        :return: dictionnaire
        """
        return self.strategy.write_game(saved_game)

    def set_strategy(self, strategy):
        """
        Setter de la strategie à utiliser
        :param strategy: strategie à utiliser. classe fille de WriteGameStrategy
        :return:
        """
        self.strategy = strategy


class WriteGameStrategy(ABC):
    @abstractmethod
    def write_game(self, saved_game: SavedGame) -> dict:
        """
        Methode qui convertie une partie en un dictionnaire en suivant une strategie de conversion
        :param saved_game: SavedGame:
        :return:
        """
        pass


class WriteGameSGFV4(WriteGameStrategy):
    """
    Pour convertir une partie en dictionnaire au format SGF v4. Type de format commun sur internet
    """
    def write_game(self, saved_game: SavedGame) -> dict:
        """
        Methode qui convertie une partie en un dictionnaire en suivant la structure de données SGF v4
        :param saved_game:
        :return:
        """
        dictionary = {}  # le dictionnaire où on va stocker les données
        dictionary['FF'] = '4'
        dictionary["SZ"] = saved_game.game.board.size
        if dictionary["SZ"] > 26:
            raise ValueError("On ne gere pas les plateaux de plus de 256 lignes/colonnes")

        dictionary["PW"] = saved_game.blue_player.name
        dictionary["PB"] = saved_game.red_player.name
        looser = None
        if saved_game.winner == "blue":
            dictionary["RE"] = 'B'  # c'est inversé dans nos fichiers
            looser = 'B'

        elif saved_game.winner == "red":
            dictionary["RE"] = "W"
            looser = 'W'

        # On convertit les mouvements
        dictionary['moves'] = self.convert_moves_to_sgf(saved_game.game.board.get_moves())

        # en fonction de la raison de fin on va ajouter un coup specifique (resign)
        if saved_game.game.game_end_reason == GameEndReason.RESIGN:
            dictionary['moves'].append({looser: "resign"})

        return dictionary

    @staticmethod
    def convert_coordinates_to_sgf(x, y):

        # Cas standard pour les plateaux jusqu'à 26x26
        col_part = chr(ord('a') + x)
        row_part = chr(ord('a') + y)

        return row_part + col_part

    @staticmethod
    def convert_moves_to_sgf(moves) -> list[dict]:
        """
        Convertit une liste d'actions en une liste de mouvements au format SGF.
        :param moves: Liste des actions (mouvements) de la partie.
        :return: Liste de mouvements au format SGF.
        """
        moves_sgf = []
        for index, move in enumerate(moves):

            # c'est toujours le bleu qui commence la partie, donc quand c'est pair c'est bleu
            key = "W" if index % 2 == 0 else "B"
            sgf_position = WriteGameSGFV4.convert_coordinates_to_sgf(move.cell.x, move.cell.y)
            moves_sgf.append({key: sgf_position})

        return moves_sgf


class ConvertOther(WriteGameStrategy):
    def write_game(self, saved_game: SavedGame) -> dict:
        pass  # TODO
