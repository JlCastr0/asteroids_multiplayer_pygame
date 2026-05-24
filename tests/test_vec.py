"""Tests for the Vec class in core.utils."""

import math

import pytest

from core.utils import Vec


def test_default_constructor_is_origin():
    v = Vec()
    assert v.x == 0.0 and v.y == 0.0


def test_xy_constructor_stores_floats():
    v = Vec(3, 4)
    assert v.x == 3.0 and v.y == 4.0


def test_tuple_constructor():
    v = Vec((3, 4))
    assert v.x == 3.0 and v.y == 4.0


def test_copy_constructor():
    a = Vec(7, 8)
    b = Vec(a)
    assert b.x == 7.0 and b.y == 8.0
    b.x = 99.0
    assert a.x == 7.0, "copy must not alias"


def test_addition_returns_new_vec():
    a = Vec(1, 2)
    b = Vec(3, 4)
    c = a + b
    assert (c.x, c.y) == (4.0, 6.0)
    assert (a.x, a.y) == (1.0, 2.0)


def test_subtraction():
    a = Vec(5, 7)
    b = Vec(3, 4)
    c = a - b
    assert (c.x, c.y) == (2.0, 3.0)


def test_scalar_multiplication_left_and_right():
    a = Vec(2, 3)
    assert (a * 2.5).x == 5.0
    assert (a * 2.5).y == 7.5
    assert (2.5 * a).x == 5.0


def test_in_place_add():
    a = Vec(1, 1)
    a += Vec(2, 3)
    assert (a.x, a.y) == (3.0, 4.0)


def test_in_place_sub():
    a = Vec(5, 5)
    a -= Vec(1, 2)
    assert (a.x, a.y) == (4.0, 3.0)


def test_in_place_mul():
    a = Vec(2, 3)
    a *= 4
    assert (a.x, a.y) == (8.0, 12.0)


def test_xy_property_is_mutable_tuple():
    v = Vec(1, 2)
    v.xy = (10, 20)
    assert (v.x, v.y) == (10.0, 20.0)
    assert v.xy == (10.0, 20.0)


def test_length_classic_345_triangle():
    assert Vec(3, 4).length() == 5.0


def test_length_squared_avoids_sqrt():
    assert Vec(3, 4).length_squared() == 25.0


def test_normalize_unit_vector():
    n = Vec(3, 4).normalize()
    assert math.isclose(n.length(), 1.0, abs_tol=1e-9)


def test_normalize_zero_returns_zero_without_error():
    n = Vec(0, 0).normalize()
    assert (n.x, n.y) == (0.0, 0.0)


def test_repr_is_readable():
    assert repr(Vec(1, 2)) == "Vec(1.0, 2.0)"


def test_slots_prevents_attribute_addition():
    v = Vec(1, 2)
    with pytest.raises(AttributeError):
        v.z = 3
