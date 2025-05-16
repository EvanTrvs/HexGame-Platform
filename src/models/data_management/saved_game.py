import datetime

from src.models.core.hex_game import HexGame
from src.models.data_management.player_data import PlayerData


class SavedGame:
    """
    Cette classe va stocker une partie (model core HexGame) et toutes les informations utiles la concernant
    """

    _id_count = 1

    def __init__(self, game: HexGame, blue_player_name: str, red_player_name: str,
                 winner: str = None, name = None, val_datetime: datetime.datetime = None):
        """
        Le constructeur de SavedGame. Il peut gérer la creation de name, winner et val_datetime
        :param game: Instance de HexGame
        :param blue_player_name: nom du joueur bleu
        :param red_player_name: nom du joueur rouge
        :param winner: gagnant de la partie (peut etre None)
        :param name: nom de la partie (peut etre None)
        :param val_datetime: moment de creation de la partie (peut etre None)
        """
        self._game = game
        self._blue_player = PlayerData(blue_player_name)
        self._red_player = PlayerData(red_player_name)
        self._winner = winner
        self._name = name
        self._id = SavedGame._id_count
        SavedGame._id_count += 1
        if name is None:
            self.name = "game" + datetime.datetime.now().__str__()
        if val_datetime is None:
            self._date_time = datetime.datetime.now()
        else:
            self._date_time = val_datetime
        if winner is None:
            self._winner = "blue" if self.game.winner == 1 else "red"

    # Getters et setters
    @property
    def game(self):
        return self._game

    @game.setter
    def game(self, game: HexGame):
        self._game = game

    @property
    def blue_player(self):
        return self._blue_player

    @blue_player.setter
    def blue_player(self, player: PlayerData):
        self._blue_player = player

    @property
    def red_player(self):
        return self._red_player

    @red_player.setter
    def red_player(self, player: PlayerData):
        self._red_player = player

    # Getter for winner
    @property
    def winner(self):
        return self._winner

    # Setter for winner
    @winner.setter
    def winner(self, color: str):
        """
        setter de winner (couleur du gagnant)
        :param color: couleur du gagnant
        """
        if color != "blue" and color != "red":
            raise ValueError("Erreur, il faut renseigner la couleur du gagnant 'blue' ou 'red'")
        else:
            self._winner = color

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def id(self):
        return self._id

    @property
    def date(self):
        return self._date_time.date()

    def date_time(self):
        return self._date_time

