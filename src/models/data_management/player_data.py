class PlayerData:
    """
    Classe responsable de la representation des joueurs dans le système
    """
    _id_count = 0

    def __init__(self, name: str):
        """
        Constructeur de PlayerData. Créé un joueur avec le bon nom
        :param name: nom du joueur
        """
        PlayerData._id_count += 1
        self._name = name
        self._id = PlayerData._id_count

    def set_name(self, name: str) -> None:
        self.name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

