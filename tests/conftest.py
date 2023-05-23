import os

import pytest
from airflow.models.connection import Connection


@pytest.fixture(scope="session")
def login():
    return os.environ["SOFTPHONE_LOGIN"]


@pytest.fixture(scope="session")
def password():
    return os.environ["SOFTPHONE_PASSWORD"]


@pytest.fixture(scope="session")
def tenant():
    return os.environ["SOFTPHONE_TENANT"]

@pytest.fixture
def connection():
    return Connection(
        conn_id="softphone_default",
        conn_type="http",
        host=""
    )