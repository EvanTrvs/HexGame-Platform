from abc import ABC, abstractmethod
import sqlite3
import xml.etree.ElementTree as ET
import json
import re


class ReadFileMonitoring:
    """
    Context du desing Pattern Strategy pour la lecture de fichiers.
    """
    def __init__(self, strategy):
        """
        Constructeur de ReadFileMonitoring
        :param strategy: Strategie de lecture de fichier à utiliser
        """
        self.strategy = strategy

    def set_strategy(self, strategy):
        """
        Mets la bonne strategie de lecture à utiliser
        :param strategy:
        :return:
        """
        self.strategy = strategy

    def read_file(self, filename: str) -> list[dict]:
        """
        lit le fichier
        :param filename: nom du fichier à lire
        :return: contenu du fichier sous forme de dictionnaire
        """
        return self.strategy.read(filename)


class ReadFileStrategy(ABC):
    """
    Interface pour la lecture de fichiers
    Prend en entrée un fichier et retourne un dictionnaire
    """
    @abstractmethod
    def read(self, file_name):
        pass


class ReadSqlite(ReadFileStrategy):
    """
    Lecture de fichiers sqlite
    """

    def read(self, file_name):

        try:
            # connexion à la base sqlite du fichier
            connexion = sqlite3.connect(file_name)
            cursor = connexion.cursor()

            # on récupere les colonnes de la table partie
            cursor.execute("PRAGMA table_info(Partie)")
            columns = [column[1] for column in cursor.fetchall()]

            # On récupère les données des parties
            cursor.execute("SELECT * FROM Partie")
            rows = cursor.fetchall()

            # On convertit chaque ligne en dictionnaire
            dictionaries = []
            for row in rows:
                dictionary = {}
                for i in range(len(columns)):

                    # cas où c'est une liste (d'actions par exemple)
                    if row[i].startswith('[') or row[i].startswith('{'):
                        dictionary[columns[i]] = json.loads(row[i])
                    else:
                        dictionary[columns[i]] = row[i]
                dictionaries.append(dictionary)

            connexion.close()
            return dictionaries

        except sqlite3.OperationalError:
            raise FileNotFoundError(f"Le fichier SQLite {file_name} n'existe pas.")


class ReadXml(ReadFileStrategy):
    """
    Lecture de fichiers xml (pas utilisée)
    """
    def read(self, file_name):
        try:
            tree = ET.parse(file_name)
            root = tree.getroot()

            dictionaries = []
            for child in root:
                dictionary = {elem.tag: elem.text for elem in child}
                dictionaries.append(dictionary)

            return dictionaries

        except FileNotFoundError:
            raise FileNotFoundError(f"Le fichier XML {file_name} n'existe pas.")
        except ET.ParseError:
            raise ValueError("Le fichier {file_name} n'est pas une fichier XML valide")


class ReadJson(ReadFileStrategy):
    """
    Lecture de fichiers json
    """
    def read(self, file_name):
        try:
            with open(file_name) as json_file:
                data = json.load(json_file)

                if isinstance(data, dict):
                    data = [data]
                return data

        except FileNotFoundError:
            raise FileNotFoundError(f"Le fichier JSON {file_name} n'existe pas.")
        except json.JSONDecodeError:
            raise ValueError(f"Le fichier {file_name} n'est pas un fichier JSON valide.")


class ReadHsgf(ReadFileStrategy):
    """
    Lecture de fichiers sgf
    """
    def read(self, file_name):
        """
        Récupère la liste des dictionnaires de parties à partir d'un fichier .sgf (encodage variant de txt)
        :param file_name: chemin du fichier à lire
        :return: liste de dictionnaires contenant les données de chaque partie
        """
        try:
            with open(file_name, 'r') as file:
                content = file.read()

            # on divise le contenu en parties distinctes
            game_sections = content.split('(;')[1:]  # Ignorer le premier élément vide

            dictionaries = []

            for section in game_sections:
                # On utilise une expression régulière pour extraire les propriétés SGF
                properties = re.findall(r'([A-Za-z]+)\[([^\]]+)\]', section)

                # On créé le dictionnaire pour stocker les données de cette partie
                sgf_data = {}
                sgf_data['moves'] = []

                for prop in properties:
                    key = prop[0]
                    value = prop[1]

                    if key in ['W', 'B']:
                        # On ajoute les mouvements à la liste des mouvements
                        sgf_data['moves'].append({key: value})
                    else:
                        # On ajoute les métadonnées au dictionnaire
                        sgf_data[key] = value

                dictionaries.append(sgf_data)

            return dictionaries

        except FileNotFoundError:
            raise FileNotFoundError(f"Le fichier SGF {file_name} n'existe pas.")
        except Exception as e:
            raise ValueError(f"Erreur lors de la lecture du fichier SGF {file_name}: {e}")
