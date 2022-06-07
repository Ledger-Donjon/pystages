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
# Copyright 2018-2020 Ledger SAS, written by Olivier Hériveaux

import numpy as np
import unittest


class Autofocus:
    """
    Utility class to add autofocus support for scanning software. Given a set
    of focused coordinates, this class can calculate the correct Z-depth for
    other points.
    """

    def __init__(self):
        self.registered_points = []

    def register(self, x, y, z):
        """
        Register a new focused point.

        :param x: Abscissa of the point.
        :param y: Ordinate of the point.
        :param z: Depth of the point.
        """
        self.registered_points.append((x, y, z))

    def clear(self):
        """Remove all registration points."""
        self.registered_points.clear()

    def focus(self, x, y):
        """
        Guess the correct focus depth given abscissa and ordinate of a new
        point. This method will raise a RuntimeError if not enough points have
        been registered.

        **Warning: Always check for the returned value bounds to prevent stage
        dangerous displacements. Bad points registration or bugs can lead to
        unexpected big displacements.**

        :param x: Abscissa of the point.
        :param y: Ordinate of the point.
        :return: Calculated depth.
        """
        if len(self.registered_points) >= 3:
            return self.__focus_3(x, y)
        else:
            raise RuntimeError("Not enough points registered for autofocus")

    def __focus_3(self, x, y):
        """
        Guess correct focus using 3 points.
        :param x: Abscissa of the point.
        :param y: Ordinate of the point.
        :return: Calculated depth.
        """
        a = np.array(self.registered_points[0])
        b = np.array(self.registered_points[1])
        c = np.array(self.registered_points[2])
        p = np.array((x, y))
        ab = b - a
        ac = c - a
        ap = p - a[:2]
        base = np.matrix([ab[:2], ac[:2]]).T
        ap_in_base = np.array((base.I * np.matrix(ap).T).T)
        z = ab[2] * ap_in_base[0, 0] + ac[2] * ap_in_base[0, 1] + a[2]
        return z

    def __len__(self):
        """:return: Number of registered points."""
        return len(self.registered_points)


class TestAutofocus(unittest.TestCase):
    def test_init(self):
        af = Autofocus()
        self.assertEqual(len(af), 0)

    def test_clear(self):
        af = Autofocus()
        af.register(1, 2, 3)
        self.assertEqual(len(af), 1)
        af.clear()
        self.assertEqual(len(af), 0)

    def test_focus(self):
        af = Autofocus()
        with self.assertRaises(RuntimeError):
            af.focus(3, 3)
        af.register(2, 2, 10)
        with self.assertRaises(RuntimeError):
            af.focus(3, 3)
        af.register(2, 3, 11)
        with self.assertRaises(RuntimeError):
            af.focus(3, 3)
        af.register(3, 2, 11)
        self.assertEqual(af.focus(3, 3), 12)


if __name__ == "__main__":
    unittest.main()
