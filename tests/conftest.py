import pytest

from src.arena import ArenaMap


@pytest.fixture
def arena_map():
    return ArenaMap()


@pytest.fixture
def hello_world():
    return "hello world"


@pytest.fixture
def v_max():
    return 100
