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

from __future__ import annotations

from collections.abc import Sequence
from typing import SupportsIndex, cast, overload


class Vector:
    """
    Some basic vector manipulation class for stages control.
    """

    def __init__(self, *args: int | float, dim: int | None = None):
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
    def x(self) -> int | float:
        """First element of the vector."""
        return self.data[0]

    @x.setter
    def x(self, value: int | float):
        self.data[0] = value

    @property
    def y(self) -> int | float:
        """Second element of the vector."""
        return self.data[1]

    @y.setter
    def y(self, value: int | float):
        self.data[1] = value

    @property
    def z(self) -> int | float:
        """Third element of the vector."""
        return self.data[2]

    @z.setter
    def z(self, value: int | float):
        self.data[2] = value

    @property
    def w(self) -> int | float:
        """Fourth element of the vector."""
        return self.data[3]

    @w.setter
    def w(self, value: int | float):
        self.data[3] = value

    @property
    def xy(self) -> Vector:
        """First and second elements of the vector, as a 2D Vector."""
        return Vector(self.data[0], self.data[1])

    @xy.setter
    def xy(self, value: Vector):
        self.data[0] = value.data[0]
        self.data[1] = value.data[1]

    @overload
    def __getitem__(self, key: SupportsIndex) -> int | float: ...

    @overload
    def __getitem__(self, key: slice) -> list[int | float]: ...

    def __getitem__(
        self, key: SupportsIndex | slice
    ) -> int | float | list[int | float]:
        """
        :return: Vector element if key is an integer, or a list of items if key
            is a slice.
        :param key: int or slice.
        """
        return self.data[key]

    @overload
    def __setitem__(self, key: SupportsIndex, value: int | float) -> None: ...
    @overload
    def __setitem__(self, key: slice, value: list[int | float]) -> None: ...

    def __setitem__(
        self, key: SupportsIndex | slice, value: int | float | list[int | float]
    ):
        """
        Set an item of the vector.
        :param key: int or slice.
        :param value: New value.
        """
        if isinstance(key, slice):
            if isinstance(value, (int, float)):
                value_list = [value] * (key.stop - key.start)
            else:
                value_list = list(value)
            for i in range(key.start, key.stop):
                self.data[i] = value_list[i]
        else:
            if isinstance(value, list):
                self.data[key] = value[0]
            else:
                self.data[key] = value

    def __str__(self):
        """
        :return: String representation of the vector. For instance '(1, 2, 3)'.
        """
        return "(" + ",".join(str(x) for x in self.data) + ")"

    def __add__(self, other: Vector) -> Vector:
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

    def __sub__(self, other: Vector) -> Vector:
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

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        """ """
        return "Vector(" + ",".join(str(x) for x in self.data) + ")"

    def __eq__(self, other: object) -> bool:
        """
        :return: True if the vectors are equal, False otherwise.
        :param other: A Vector instance of same dimension, or a Sequence of int or float.
        """
        if isinstance(other, Vector):
            other_seq: Sequence[int | float] = other.data
        elif isinstance(other, Sequence):
            other_seq = cast(Sequence[int | float], other)
        else:
            return False
        if len(self) != len(other_seq):
            return False
        for i in range(len(self)):
            if self[i] != other_seq[i]:
                return False
        return True

    def __mul__(self, other: Vector | int | float) -> Vector:
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

    def __truediv__(self, other: int | float) -> Vector:
        """
        :return: Scalar division between this vector and the other.
        :param other: An integer or a float.
        """
        if not isinstance(other, (int, float)):
            raise TypeError(
                "Incorrect type for second operand. int or float is expected."
            )
        return self * (1.0 / other)
