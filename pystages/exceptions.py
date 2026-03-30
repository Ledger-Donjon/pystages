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
# Copyright 2018 Ledger SAS, written by Olivier Hériveaux

# This file regroups a set of exception classes used by the different stage
# implementations

from __future__ import annotations


class ConnectionFailure(Exception):
    pass


class ProtocolError(Exception):
    def __init__(
        self,
        query: str | None = None,
        response: str | None = None,
        expected: str | None = None,
    ):
        super().__init__(",".join([repr(query), repr(response)]))
        self.query = query
        self.response = response
        self.expected = expected

    def __str__(self):
        return f"ProtocolError(query={repr(self.query)}, response={repr(self.response)}, expected={repr(self.expected)})"


class VersionNotSupported(Exception):
    def __init__(self, version: str, expected: str | None = None):
        self.version = version
        self.expected = expected

    def __str__(self) -> str:
        return f"VersionNotSupported(version={repr(self.version)}, expected={repr(self.expected)})"
