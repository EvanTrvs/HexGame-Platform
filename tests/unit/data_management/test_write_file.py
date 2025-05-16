import pytest

from src.models.data_management.write_files import WriteJson,  WriteSqlite, WriteXML, WriteHsgf, WriteFileMonitoring
from tests.conftest import game_dictionary_sgf_v4_sample
import os


def test_write_json_single_dict(game_dictionary_sgf_v4_sample):
    """
    Verrifie que le fichier est bien créé par la methode
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "..", "fichiers_test", "fichier_test.json")
    dictionary = [game_dictionary_sgf_v4_sample[0]]
    instance_write_file = WriteJson()
    instance_write_file.write_file(dictionary, file_name=file_path)
    assert os.path.exists(file_path), "Le fichier n'a pas été créé."

    # Suppression du fichier de test
    os.remove(file_path)


def test_write_sqlite_single_dict(game_dictionary_sgf_v4_sample):
    """
    Verrifie que le fichier est bien créé par la méthode
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "..", "fichiers_test", "fichier_test.sqlite")
    dictionary = [game_dictionary_sgf_v4_sample[0]]
    instance_write_file = WriteSqlite()
    instance_write_file.write_file(dictionary, file_name=file_path)
    assert os.path.exists(file_path), "Le fichier n'a pas été créé."

    # Suppression du fichier de test
    os.remove(file_path)


def test_write_xml_single_dict(game_dictionary_sgf_v4_sample):
    """
    Verrifie que le fichier est bien créé par la méthode
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "..", "fichiers_test", "fichier_test.xml")
    dictionary = [game_dictionary_sgf_v4_sample[0]]
    instance_write_file = WriteXML()
    instance_write_file.write_file(dictionary, file_name=file_path)
    assert os.path.exists(file_path), "Le fichier n'a pas été créé."

    # Suppression du fichier de test
    os.remove(file_path)


def test_write_sgf_single_dict(game_dictionary_sgf_v4_sample):
    """
    Verrifie que le fichier est bien créé par la méthode
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "..", "fichiers_test", "fichier_test.sqlite")
    dictionary = [game_dictionary_sgf_v4_sample[0]]
    instance_write_file = WriteHsgf()
    instance_write_file.write_file(dictionary, file_name=file_path)
    assert os.path.exists(file_path), "Le fichier n'a pas été créé."

    # Suppression du fichier de test
    os.remove(file_path)


def test_write_file_empty_list():
    """
    Verifie que l'ecriture d'un fichier avec une liste de dictionnaires vide lève une erreur
    :return:
    """
    list_dictionaries = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "fichiers_test", "fichier_test_vide")
    instances_write_file = [WriteJson(), WriteXML(), WriteSqlite(), WriteHsgf()]

    for instance in instances_write_file:
        with pytest.raises(ValueError, match="La liste de parties est vide"):
            instance.write_file(list_dictionaries, file_path)

    assert not os.path.exists(file_path)

    # Si le test échoue on supprime le fichier
    if os.path.exists(file_path):
        os.remove(file_path)


