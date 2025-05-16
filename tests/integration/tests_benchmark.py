import pytest
import os
from tests.conftest import client
from werkzeug.datastructures import FileStorage


def test_benchmark_games_reading(benchmark, client):
    """
    On va tester le debut du cas end to end, donc la lecture d'une partie dans un fichier
    :param benchmark:
    :param client:
    :return:
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(base_dir, '..', 'fichiers_test', 'valid_games_list.hsgf')

    # On créé le répertoire temporaire s'il n'existe pas, c'est utilisé dans le controller
    tmp_dir = os.path.join(base_dir, 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    # On prépare les données pour la requête POST
    with open(test_file_path, 'rb') as f:
        file_data = FileStorage(stream=f, filename=os.path.basename(test_file_path))
        data = {
            'file': file_data,
            'type': 'sgf'
        }

        benchmark(client.post("/games_list", data=data, content_type='multipart/form-data'))

    assert benchmark.stats["mean"] < 0.5

def test_benchmark_index(client, benchmark):
    """Benchmark de la route '/' (Page d'accueil)"""
    result = benchmark(client.get, '/')
    assert benchmark.stats["mean"] < 0.1
