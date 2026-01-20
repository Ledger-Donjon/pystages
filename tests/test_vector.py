import pytest

from pystages.vector import Vector


def test_vector_init():
    v = Vector(1)
    assert len(v) == 1
    assert v.data == [1]
    v = Vector(1, 2)
    assert len(v) == 2
    assert v.data == [1, 2]
    v = Vector(1, 2, 3)
    assert len(v) == 3
    assert v.data == [1, 2, 3]
    v = Vector(1, 2, 3, 4)
    assert len(v) == 4
    assert v.data == [1, 2, 3, 4]

    for i in range(5):
        v = Vector(dim=i)
        assert len(v) == i

    v = Vector(1, dim=1)
    assert len(v) == 1
    assert v.data == [1]
    v = Vector(1, 2, dim=2)
    assert len(v) == 2
    assert v.data == [1, 2]
    v = Vector(1, 2, 3, dim=3)
    assert len(v) == 3
    assert v.data == [1, 2, 3]
    v = Vector(1, 2, 3, 4, dim=4)
    assert len(v) == 4
    assert v.data == [1, 2, 3, 4]

    # Test padding with 0
    v = Vector(dim=4)
    assert len(v) == 4
    assert v.data == [0, 0, 0, 0]
    v = Vector(1, dim=4)
    assert len(v) == 4
    assert v.data == [1, 0, 0, 0]
    v = Vector(1, 2, dim=4)
    assert len(v) == 4
    assert v.data == [1, 2, 0, 0]
    v = Vector(1, 2, 3, dim=4)
    assert len(v) == 4
    assert v.data == [1, 2, 3, 0]

    # Test number of args checking
    with pytest.raises(ValueError):
        _ = Vector(1, 2, 3, 4, 5, dim=4)


def test_vector_xyzw():
    v = Vector(1, 2, 3, 4)
    assert v[0] == 1
    assert v[1] == 2
    assert v[2] == 3
    assert v[3] == 4
    assert v.x == 1
    assert v.y == 2
    assert v.z == 3
    assert v.w == 4
    assert v.xy == Vector(1, 2)
    v[0] = 11
    v[1] = 12
    v[2] = 13
    v[3] = 14
    assert v[0] == 11
    assert v[1] == 12
    assert v[2] == 13
    assert v[3] == 14
    assert v.x == 11
    assert v.y == 12
    assert v.z == 13
    assert v.w == 14
    v.x = 101
    v.y = 102
    v.z = 103
    v.w = 104
    assert v[0] == 101
    assert v[1] == 102
    assert v[2] == 103
    assert v[3] == 104
    assert v.x == 101
    assert v.y == 102
    assert v.z == 103
    assert v.w == 104
    v.xy = Vector(1001, 1002)
    assert v[0] == 1001
    assert v[1] == 1002
    assert v[2] == 103
    assert v[3] == 104
    assert v.x == 1001
    assert v.y == 1002
    assert v.z == 103
    assert v.w == 104


def test_vector_add():
    v1 = Vector(2, 3, 5)
    v2 = Vector(7, 11, 13)
    v3 = v1 + v2
    assert v3.data == [9, 14, 18]


def test_vector_sub():
    v1 = Vector(2, 3, 5)
    v2 = Vector(7, 11, 13)
    v3 = v1 - v2
    assert v3.data == [-5, -8, -8]


def test_vector_eq():
    assert Vector() == ()
    assert Vector() == []
    assert Vector(1) == Vector(1)
    assert Vector(1, 2) == Vector(1, 2)
    assert Vector(1, 2, 3) == Vector(1, 2, 3)
    assert Vector(1, 2, 3) != Vector(4, 2, 3)
    assert Vector(1, 2, 3) != Vector(1, 4, 3)
    assert Vector(1, 2, 3) != Vector(1, 2, 4)
    assert Vector(1, 2, 3) != Vector(1, 2)


def test_vector_mult():
    assert Vector() * 10 == ()
    assert Vector(1) * 10 == Vector(10)
    assert Vector(1, 2, 3) * 10 == Vector(10, 20, 30)
    assert Vector(1.0, 2.0, 3.0) / 10 == Vector(
        1.0 * (1.0 / 10), 2.0 * (1.0 / 10), 3.0 * (1.0 / 10)
    )
