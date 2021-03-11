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
from curses import textpad
from window import Window
from color_code import ColorCode
from success import SuccessWindow
from curses.textpad import Textbox

class TextBox(Window):
    _text = None

    def __init__(self,window, h, w, y, x):
        super().__init__(window)
        self.h = h
        self.w = w
        self.x = x
        self.y = y

    def create_textbox(self, color_code):
        is_valid = False
        while(not is_valid):
            new_win = curses.newwin(self.h, self.w, self.y, self.x)
            text = Textbox(new_win, insert_mode=False)
            data = text.edit()

            if data.strip() == "1.1.1.1":
                is_valid = True
            else:
                col_code_attr = ColorCode().get_color_pair(3)
                self.on_attr(col_code_attr)
                self._window.addstr(self.y + 3,3 ,f"Error: Invalid hostname {data.strip()}")
                self.off_attr(col_code_attr)
                self._window.refresh()

        self._window.clear()
        win = SuccessWindow(self._window)
        win.create_default_window(2)
        win.create_window(color_code=2,data=data)


