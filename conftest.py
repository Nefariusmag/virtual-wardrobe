import pytest
from flask import url_for

from wardrobe.app import create_app


@pytest.fixture
def app():
    app = create_app()
    return app

#
# @pytest.fixture
# def test_myview(self):
#     assert self.client.get(url_for('/')).status_code == 200
#     print('=--')
