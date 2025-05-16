from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
import json
import sqlite3


class WriteFileMonitoring:
    """
    Context du DP Strategy pour l'ecriture dans des fichiers
    """
    def __init__(self, strategy):
        self.strategy = strategy

    def write_file(self, dictionary, file_path):
        """
        Ecrit le contenu d'un dictionnaire dans un fichier
        :param dictionary: dictionnaire à ecrire. Contient une partie
        :param file_path: Chemin du fichier où ecrire
        :return:
        """
        self.strategy.write_file(dictionary, file_path)

    def set_strategy(self, strategy):
        self.strategy = strategy


class WriteFileStrategy(ABC):
    """
    Interface des classes/strategies d'écriture dans des fichiers
    """
    @abstractmethod
    def write_file(self, dictionnaire: dict, file_name: str) -> None:
        """
        Methode qui va écrire le dictionnaire d'une partie dans un fichier
        :param dictionnaire: le dictionnaire associé à une partie
        :param file_name: le nom du fichier à enregistrer
        :return:
        """
        pass


class WriteSqlite(WriteFileStrategy):
    """
    Strategie d'ecriture dans un fichier sqlite
    """
    def write_file(self, dictionaries: list[dict], file_name: str) -> None:
        # On verifie si la liste n'est pas vide
        if not dictionaries:
            raise ValueError("La liste de parties est vide")

        # On commence par se connecter au fichier database, s'il n'existe pas il sera créé
        connexion = sqlite3.connect(file_name)
        cursor = connexion.cursor()

        # On crééer la table si elle n'existe pas, avec les clés du premier dictionnaire
        first_dictionary = dictionaries[0]
        columns = ', '.join([f'"{key}" TEXT' for key in first_dictionary.keys()])
        cursor.execute(f'CREATE TABLE IF NOT EXISTS "Partie" ({columns})')

        # On insere les données de la partie
        placeholders = ', '.join(['?'] * len(first_dictionary))
        for dictionary in dictionaries:

            # On est obligé de dump les listes sous forme de json
            values = tuple(json.dumps(value) if isinstance(value, list) else value for value in dictionary.values())
            cursor.execute(f'INSERT INTO "Partie" VALUES ({placeholders})', values)

        connexion.commit()
        connexion.close()


class WriteXML(WriteFileStrategy):
    """
    Strategie d'ecriture dans un fichier xml (pas utilisée pour l'instant)
    """
    def write_file(self, dictionaries: list[dict], file_name: str) -> None:

        # On verifie si la liste n'est pas vide
        if not dictionaries:
            raise ValueError("La liste de parties est vide")

        root = ET.Element("root")
        for index_partie, dictionnaire in enumerate(dictionaries):
            dictinary_element = WriteXML.dict_to_xml(f"partie{index_partie+1}", dictionnaire)
            root.append(dictinary_element)

        tree = ET.ElementTree(root)
        tree.write(file_name, encoding="UTF-8", xml_declaration=True)

    @staticmethod
    def dict_to_xml(tag, dictionary: dict):
        """
        Cette fonction est propre à la strategie XML
        Convertit un dictionnaire en un élément XML
        :param tag: indice de la partie dans la liste à convertir
        :param dictionary: dictionnaire à convertir
        :return: element xml
        """
        elem = ET.Element(tag)
        for key, val in dictionary.items():
            child = ET.SubElement(elem, key)
            child.text = str(val)
        return elem


class WriteJson(WriteFileStrategy):
    """
    Strategie d'ecriture dans un fichier json
    """
    def write_file(self, dictionaries: list[dict], file_name: str) -> None:

        # On verifie si la liste n'est pas vide
        if not dictionaries:
            raise ValueError("La liste de parties est vide")

        with open(file_name, "w") as outfile:
            json.dump(dictionaries, outfile)


class WriteHsgf(WriteFileStrategy):
    """
    Strategie d'ecriture dans un fichier hsgf
    """
    def write_file(self, dictionaries: list[dict], file_name: str) -> None:
        """
        Écrit le dictionnaire d'une partie dans un fichier .SGF.
        :param dictionaries: Liste de dictionnaires associés à des parties.
        :param file_name: Nom du fichier à enregistrer.
        """
        # On verifie si la liste n'est pas vide
        if not dictionaries:
            raise ValueError("La liste de parties est vide")

        try:
            with open(file_name, 'w') as file:
                for dictionary in dictionaries:
                    # On commence l'en-tête SGF
                    file.write("(;")

                    for key, value in dictionary.items():
                        if key != 'moves':
                            file.write(f"{key}[{value}]")

                    # Ensuite les actions
                    if 'moves' in dictionary:
                        for move in dictionary['moves']:
                            for color, position in move.items():
                                file.write(f"{color}[{position}]")

                    file.write(")\n")

        except Exception as e:
            raise ValueError(f"Erreur lors de l'écriture du fichier SGF {file_name}: {e}")
