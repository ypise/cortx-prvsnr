#!/usr/bin/env python
#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#
#
import curses
import json
from pathlib import Path

class Check():
    _filename = None

    def __init__(self, filename=None):
        if not filename:
            self._filename = str(
                Path(__file__).resolve().parent / 'check.json' 
            )
        else:
            self._filename = filename

    def loads(self):
        with open(self._filename) as f:
            return json.load(f)

    def dumps(self, data):
        with open(self._filename, 'w') as json_file:
            json.dump(data, json_file)
