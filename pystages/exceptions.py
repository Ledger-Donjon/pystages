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


class ConnectionFailure(Exception):
    pass


class ProtocolError(Exception):
    def __init__(self, query=None, response=None):
        super().__init__(",".join([repr(query), repr(response)]))
        self.query = query
        self.response = response

    def __str__(self):
        return f"ProtocolError({repr(self.query)}, {repr(self.response)})"


class VersionNotSupported(Exception):
    def __init__(self, version):
        self.version = version

    def __str__(self):
        return self.version
