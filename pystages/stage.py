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
# Copyright 2018-2022 Ledger SAS, written by Michaël Mouchous

from .vector import Vector
from typing import Optional


class Stage:
    def __init__(self, num_axis=1):
        """
        :param num_axis: The number of axis of the stage, can be updated or set after initialisation of the object.
        """
        self.num_axis = num_axis
        self.wait_routine = None

    @property
    def position(self) -> Vector:
        """
        Current stage position. Vector.

        :getter: Query and return stage position.
        :setter: Move the stage.
        """
        raise RuntimeError("This function should not be called")

    @position.setter
    def position(self, value: Vector):
        """
        Set stage to a new destination.
        """
        raise RuntimeError("This function should not be called")

    @property
    def is_moving(self) -> bool:
        """Queries the status of the stage to determine if it is moving"""
        raise RuntimeError("This function should not be called")

    def wait_move_finished(self):
        """
        Wait until all axis are ready.

        :param wait_routine: An optional routine to be executed between each query of move.
        """
        while self.is_moving:
            if self.wait_routine is not None:
                self.wait_routine()

    def move_to(self, value: Vector, wait: bool = True):
        """
        Move stage to a new position, with the possibility to poll device until the move finishes.

        :param value: New stage position.
        :param wait: If True, wait for stage to be at the new position,
            otherwise return immediately.
        """
        self.position = value
        if wait:
            self.wait_move_finished()
