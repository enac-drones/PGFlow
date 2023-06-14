import pytest

from src.arena import ArenaMap


def test_arena_map_inflate():
    with pytest.raises(Exception):
        ArenaMap()
