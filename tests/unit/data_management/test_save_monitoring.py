import pytest
import os
from src.models.data_management.save_monitoring import SaveMonitoring, WriteJson, WriteXML, WriteSqlite, WriteHsgf
from src.models.data_management.write_game import WriteGameSGFV4
from src.models.data_management.saved_game import SavedGame


def test_set_write_file_strategy():
    """
    Teste si le setter de write_file_strategy fonctionne correctement
    """
    save_monitoring = SaveMonitoring(WriteGameSGFV4(), WriteJson())

    save_monitoring.set_write_file_strategy(WriteXML())

    assert isinstance(save_monitoring.write_file_monitor.strategy, WriteXML)

def test_set_write_game_strategy():
    """
    Teste si le setter de write_game_strategy fonctionne correctement
    """
    save_monitoring = SaveMonitoring(WriteGameSGFV4(), WriteJson())

    save_monitoring.set_write_game_strategy(WriteGameSGFV4())

    assert isinstance(save_monitoring.write_game_monitor.strategy, WriteGameSGFV4)

def test_save_game():
    pass # TODO

def test_choose_right_file_strategy_json():
    pass # TODO