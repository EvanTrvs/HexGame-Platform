from src.models.data_management.saved_game import SavedGame


class GamesStatistics:
    """
    Classe statique responsable du calcul de diferentes statistiques sur des parties
    """
    @staticmethod
    def get_statistics(games: list[SavedGame]) -> dict:
        """
        Fonction qui calcule les differentes statistiques
        :param games: parties à analyser
        :return:
        """
        statistics_dict = {}

        number_win_blue = 0
        number_win_red = 0
        total_number_moves = 0
        for game in games:
            if game.winner == "blue":
                number_win_blue += 1
            elif game.winner == "red":
                number_win_red += 1

            total_number_moves += len(game.game.board.get_moves())

        statistics_dict["win_blue"] = number_win_blue
        statistics_dict["win_red"] = number_win_red
        statistics_dict["average_number_moves"] = total_number_moves / len(games)

        return statistics_dict