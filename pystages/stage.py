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
from abc import ABC, abstractmethod


class Stage(ABC):
    """
    Stage is an abstract class from which all stage implementation must inherit to get a consistent
    behavior and value checking for getting and setting position, setting software limits...
    """

    def __init__(self, num_axis=1):
        """
        :param num_axis: The number of axis of the stage, can be updated or set after initialisation
         of the object.
        """
        self.num_axis = num_axis
        # The wait routine is a function that is called when the wait_move_finished is looping.
        # It can be used to add some temporisation and/or UI updates.
        self.wait_routine = None

        # Minimum and maximum software limits
        self._minimums: Optional[Vector] = None
        self._maximums: Optional[Vector] = None

    @property
    @abstractmethod
    def position(self) -> Vector:
        """
        Current stage position. Vector.

        :getter: Query and return stage position.
        :setter: Move the stage.
        """
        ...

    @position.setter
    def position(self, value: Vector):
        """
        Set stage to a new destination.
        """
        # Checks dimension according to number of axis, and range according to minimums/maximums
        # (raises an exception if incorrect)
        self.check_dimension(value)
        self.check_range(value)

    @property
    @abstractmethod
    def is_moving(self) -> bool:
        """Queries the status of the stage to determine if it is moving"""
        ...

    def wait_move_finished(self):
        """
        Wait until all axis are ready.
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

    def check_dimension(self, value: Vector):
        """
        Check if the given value's dimension is consistent according to the number of axes of the
        Stage.
        :param value: The vector to check
        :raises ValueError: If dimension is inconsistent with the number of axis of the Stage.
        """
        if self.num_axis != len(value):
            raise ValueError(
                f"The given vector's dimension {len(value)} is incorrect: expected {self.num_axis}"
            )

    def check_range(self, value: Vector):
        """
        Check if the given value is in range according to minimums/maximums.
        If it is not the case, a ValueException is raised.

        :param value: The vector to check if it is within authorized range.
        """
        if self._minimums is None and self._maximums is None:
            # No restriction, we can return
            return
        # Get minimums and/or maximums. If one of them is None, we use the value.
        mins = value if self._minimums is None else self._minimums
        maxs = value if self._maximums is None else self._maximums

        # Check if the dimensions are correct.
        if len(mins) != len(value) or len(maxs) != len(value):
            raise ValueError(
                "Invalid vector dimension according to minimums and/or maximums"
            )

        for i in range(len(value)):
            if mins[i] is not None and value[i] < mins[i]:
                raise ValueError(
                    f"Invalid value for dimension {i}: {value[i]} "
                    f"is smaller that minimum {mins[i]}."
                )
            if maxs[i] is not None and value[i] > maxs[i]:
                raise ValueError(
                    f"Invalid value for dimension {i}: {value[i]} "
                    f"is greater that maximum {maxs[i]}."
                )

    @property
    def minimums(self) -> Optional[Vector]:
        return self._minimums

    @minimums.setter
    def minimums(self, value: Optional[Vector]):
        if value is not None:
            self.check_dimension(value)
        self._minimums = value

    @property
    def maximums(self) -> Optional[Vector]:
        return self._maximums

    @maximums.setter
    def maximums(self, value: Optional[Vector]):
        if value is not None:
            self.check_dimension(value)
        self._maximums = value
