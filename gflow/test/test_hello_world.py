def test_hello_world(hello_world):
    print(hello_world)
    assert True


def test_some_other_test(hello_world, v_max):
    assert v_max == 90
