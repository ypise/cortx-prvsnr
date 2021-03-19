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
import config
from curses import textpad
from color_code import ColorCode

class Window:
    _max_h = None
    _max_w = None
    _window = None
    _stdscr = None

    def __init__(self, window):
        self._max_h, self._max_w = window.getmaxyx()
        self._window = window
        self._stdscr = window
        self._window.border()

    def enable_keypad(self):
        self._window.keypad(1)

    def get_max_height(self):
        return self._max_h

    def get_max_width(self):
        return self._max_w

    def on_attr(self, attr):
        self._window.attron(attr)

    def off_attr(self, attr):
        self._window.attroff(attr)

    def create_default_window(self, color_code):
        col_code_attr = ColorCode().get_color_pair(color_code)
        self.on_attr(col_code_attr)
        header_window = curses.newwin( self._max_h // 5, self._max_w - 1, 1, 1)
        header_window.border()
        #textpad.rectangle(self._window, 1,1, self._max_h // 2 - 2, self._max_w //2 - 2)
        h , w = header_window.getmaxyx()
        header_window.addstr(h // 2 , w // 2 - len(config.tittle)//2 ,f"{config.tittle}")
        header_window.refresh()
        #self._window.hline(6,2,"_",self._max_w - 4)
        #self._window.addstr(self._max_h-1, 0, " Key Commands : q - to quit " ,curses.color_pair(color_code) )
        self.off_attr(col_code_attr)
        curses.napms(2000)

    def create_window(self, **kwargs):
        pass

