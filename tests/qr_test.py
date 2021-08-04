import os
from dynamic_qr import routes


def test_qr_code_generation():
    path = routes.generate_qr('test')
    assert os.path.exists(path)
    os.remove(path)
