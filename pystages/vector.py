# This file is part of pystages
#
# pystages is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# Copyright 2018 Ledger SAS, written by Olivier Hériveaux and Manuel San Pedro


import unittest
from typing import Union


class Vector(object):
    """
    Some basic vector manipulation class for stages control.
    """

    def __init__(self, *args, dim=None):
        """
        :param args: Initial values of the vector.
        :param dim: Dimension of the vector.
        """
        if dim is not None:
            if len(args) > dim:
                raise ValueError("Too many initial values for this dimension.")
            self.data = list(args)
            while len(self.data) < dim:
                self.data.append(0)
        else:
            self.data = list(args)

    @property
    def x(self):
        """First element of the vector."""
        return self.data[0]

    @x.setter
    def x(self, value):
        self.data[0] = value

    @property
    def y(self):
        """Second element of the vector."""
        return self.data[1]

    @y.setter
    def y(self, value):
        self.data[1] = value

    @property
    def z(self):
        """Third element of the vector."""
        return self.data[2]

    @z.setter
    def z(self, value):
        self.data[2] = value

    @property
    def w(self):
        """Fourth element of the vector."""
        return self.data[3]

    @w.setter
    def w(self, value):
        self.data[3] = value

    @property
    def xy(self):
        """First and second elements of the vector, as a 2D Vector."""
        return Vector(self.data[0], self.data[1])

    @xy.setter
    def xy(self, value):
        self.data[0] = value.data[0]
        self.data[1] = value.data[1]

    def __getitem__(self, key):
        """
        :return: Vector element if key is an integer, or a list of items if key
            is a slice.
        :param key: int or slice.
        """
        return self.data[key]

    def __setitem__(self, key, value):
        """
        Set an item of the vector.
        :param key: int or slice.
        :param value: New value.
        """
        self.data[key] = value

    def __str__(self):
        """
        :return: String representation of the vector. For instance '(1, 2, 3)'.
        """
        return "(" + ",".join(str(x) for x in self.data) + ")"

    def __add__(self, other):
        """
        :return: Sum of this vector to the other.
        :param other: A Vector instance of same dimension.
        """
        dim = len(self)
        if len(other) != dim:
            raise ValueError("Incorrect vector size")
        result = Vector(*self.data)
        for i in range(dim):
            result.data[i] += other[i]
        return result

    def __sub__(self, other):
        """
        :return: Difference between this vector and the other.
        :param other: A Vector instance of same dimension.
        """
        dim = len(self)
        if len(other) != dim:
            raise ValueError("Incorrect vector size")
        result = Vector(*self.data)
        for i in range(dim):
            result.data[i] -= other[i]
        return result

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        """ """
        return "Vector(" + ",".join(str(x) for x in self.data) + ")"

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

    def __mul__(self, other: Union["Vector", int, float]):
        """
        :return: Scalar multiplication between this vector and the other.
        :param other: A Vector instance of same dimension, or an integer or a float.
        """
        dim = len(self)
        if isinstance(other, (int, float)):
            result = Vector(dim=dim)
            for i in range(dim):
                result[i] = self[i] * other
            return result

        result = Vector(dim=dim)
        if len(other) != dim:
            raise ValueError("Incorrect vector size")
        for i in range(dim):
            result[i] = self[i] * other[i]
        return result

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return self * (1.0 / other)
        else:
            raise TypeError(
                "Incorrect type for second operand. int or float is expected."
            )


class TestVector(unittest.TestCase):
    def test_init(self):
        v = Vector(1)
        self.assertEqual(len(v), 1)
        self.assertEqual(v.data, [1])
        v = Vector(1, 2)
        self.assertEqual(len(v), 2)
        self.assertEqual(v.data, [1, 2])
        v = Vector(1, 2, 3)
        self.assertEqual(len(v), 3)
        self.assertEqual(v.data, [1, 2, 3])
        v = Vector(1, 2, 3, 4)
        self.assertEqual(len(v), 4)
        self.assertEqual(v.data, [1, 2, 3, 4])

        for i in range(5):
            v = Vector(dim=i)
            self.assertEqual(len(v), i)

        v = Vector(1, dim=1)
        self.assertEqual(len(v), 1)
        self.assertEqual(v.data, [1])
        v = Vector(1, 2, dim=2)
        self.assertEqual(len(v), 2)
        self.assertEqual(v.data, [1, 2])
        v = Vector(1, 2, 3, dim=3)
        self.assertEqual(len(v), 3)
        self.assertEqual(v.data, [1, 2, 3])
        v = Vector(1, 2, 3, 4, dim=4)
        self.assertEqual(len(v), 4)
        self.assertEqual(v.data, [1, 2, 3, 4])

        # Test padding with 0
        v = Vector(dim=4)
        self.assertEqual(len(v), 4)
        self.assertEqual(v.data, [0, 0, 0, 0])
        v = Vector(1, dim=4)
        self.assertEqual(len(v), 4)
        self.assertEqual(v.data, [1, 0, 0, 0])
        v = Vector(1, 2, dim=4)
        self.assertEqual(len(v), 4)
        self.assertEqual(v.data, [1, 2, 0, 0])
        v = Vector(1, 2, 3, dim=4)
        self.assertEqual(len(v), 4)
        self.assertEqual(v.data, [1, 2, 3, 0])

        # Test number of args checking
        with self.assertRaises(ValueError):
            _ = Vector(1, 2, 3, 4, 5, dim=4)

    def test_xyzw(self):
        v = Vector(1, 2, 3, 4)
        self.assertEqual(v[0], 1)
        self.assertEqual(v[1], 2)
        self.assertEqual(v[2], 3)
        self.assertEqual(v[3], 4)
        self.assertEqual(v.x, 1)
        self.assertEqual(v.y, 2)
        self.assertEqual(v.z, 3)
        self.assertEqual(v.w, 4)
        self.assertEqual(v.xy, Vector(1, 2))
        v[0] = 11
        v[1] = 12
        v[2] = 13
        v[3] = 14
        self.assertEqual(v[0], 11)
        self.assertEqual(v[1], 12)
        self.assertEqual(v[2], 13)
        self.assertEqual(v[3], 14)
        self.assertEqual(v.x, 11)
        self.assertEqual(v.y, 12)
        self.assertEqual(v.z, 13)
        self.assertEqual(v.w, 14)
        v.x = 101
        v.y = 102
        v.z = 103
        v.w = 104
        self.assertEqual(v[0], 101)
        self.assertEqual(v[1], 102)
        self.assertEqual(v[2], 103)
        self.assertEqual(v[3], 104)
        self.assertEqual(v.x, 101)
        self.assertEqual(v.y, 102)
        self.assertEqual(v.z, 103)
        self.assertEqual(v.w, 104)
        v.xy = Vector(1001, 1002)
        self.assertEqual(v[0], 1001)
        self.assertEqual(v[1], 1002)
        self.assertEqual(v[2], 103)
        self.assertEqual(v[3], 104)
        self.assertEqual(v.x, 1001)
        self.assertEqual(v.y, 1002)
        self.assertEqual(v.z, 103)
        self.assertEqual(v.w, 104)

    def test_add(self):
        v1 = Vector(2, 3, 5)
        v2 = Vector(7, 11, 13)
        v3 = v1 + v2
        self.assertEqual(v3.data, [9, 14, 18])

    def test_sub(self):
        v1 = Vector(2, 3, 5)
        v2 = Vector(7, 11, 13)
        v3 = v1 - v2
        self.assertEqual(v3.data, [-5, -8, -8])

    def test_eq(self):
        self.assertEqual(Vector(), ())
        self.assertEqual(Vector(), [])
        self.assertEqual(Vector(1), Vector(1))
        self.assertEqual(Vector(1, 2), Vector(1, 2))
        self.assertEqual(Vector(1, 2, 3), Vector(1, 2, 3))
        self.assertNotEqual(Vector(1, 2, 3), Vector(4, 2, 3))
        self.assertNotEqual(Vector(1, 2, 3), Vector(1, 4, 3))
        self.assertNotEqual(Vector(1, 2, 3), Vector(1, 2, 4))
        self.assertNotEqual(Vector(1, 2, 3), Vector(1, 2))

    def test_mult(self):
        self.assertEqual(Vector() * 10, ())
        self.assertEqual(Vector(1) * 10, Vector(10))
        self.assertEqual(Vector(1, 2, 3) * 10, Vector(10, 20, 30))
        self.assertEqual(
            Vector(1.0, 2.0, 3.0) / 10,
            Vector(1.0 * (1.0 / 10), 2.0 * (1.0 / 10), 3.0 * (1.0 / 10)),
        )


if __name__ == "__main__":
    unittest.main()
