import pytest
from unittest.mock import patch, mock_open
from src.models.data_management.read_file import ReadFileStrategy, ReadXml, ReadJson, ReadSqlite, ReadFileMonitoring
import os


def test_read_file_monitoring_set_strategy():
    """
    Teste que la stratégie de lecture de fichier peut être changée.
    """
    read_file_monitoring = ReadFileMonitoring(ReadSqlite())
    read_file_monitoring.set_strategy(ReadJson())

    assert isinstance(read_file_monitoring.strategy, ReadJson)


def test_read_not_existing_file_sqlite():
    """
    Teste que la classe ReadSqlite lève la bonne erreur si le fichier n'existe pas.
    """
    read_sqlite = ReadSqlite()
    not_existing_file = "ce_fichier_existe_pas.sqlite"

    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError()

        with pytest.raises(FileNotFoundError, match=f"Le fichier SQLite {not_existing_file} n'existe pas."):
            read_sqlite.read(not_existing_file)


def test_read_not_existing_file_json():
    """
    Teste que la classe ReadJson lève la bonne erreur si le fichier n'existe pas.
    """
    read_json = ReadJson()
    not_existing_file = "ce_fichier_existe_pas.json"

    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError()

        with pytest.raises(FileNotFoundError, match=f"Le fichier JSON {not_existing_file} n'existe pas."):
            read_json.read(not_existing_file)


def test_read_not_existing_file_xml():
    """
    Teste que la classe ReadXml lève la bonne erreur si le fichier n'existe pas.
    """
    read_xml = ReadXml()
    not_existing_file = "ce_fichier_existe_pas.xml"

    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError()

        with pytest.raises(FileNotFoundError, match=f"Le fichier XML {not_existing_file} n'existe pas."):
            read_xml.read(not_existing_file)
