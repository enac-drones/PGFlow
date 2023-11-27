import pytest

from gflow.arena import ArenaMap


@pytest.fixture
def arena_map():
    return ArenaMap()


@pytest.fixture
def hello_world():
    return "hello world"


@pytest.fixture
def v_max():
    return 100
