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
from window import Window
from color_code import ColorCode
from text_box import TextBox
from success import SuccessWindow

class StaticNetworkWindow(Window):


    def create_window(self, **kwargs):
        color_code = kwargs['color_code']
        self._parent = kwargs['component']
        col_code_attr = ColorCode().get_color_pair(color_code)
        self.create_menu_head()

        x = self.get_max_width() // 2
        y = self.get_max_height() // 2 - 1
        self.enable_keypad()


        self.on_attr(col_code_attr)
        self._window.addstr(y,3 ,f"Please enter ip for this machine ")
        self.off_attr(col_code_attr)
        data1 = TextBox(self._window, 1, 16, y+3, 3).create_textbox(color_code, kwargs['component'])
        self._window.clear()
        
        self.create_menu_head()
        self.on_attr(col_code_attr)
        self._window.addstr(y,3 ,f"Please enter netmask for this machine ")
        self.off_attr(col_code_attr)
        data2 = TextBox(self._window, 1, 16, y+3, 3).create_textbox(color_code, 2)
        self._window.clear()

        self.create_menu_head()
        self.on_attr(col_code_attr)
        self._window.addstr(y,3 ,f"Please enter gateway for this machine ")
        self.off_attr(col_code_attr)
        data3 = TextBox(self._window, 1, 16, y+3, 3).create_textbox(color_code, 3)
        self._window.clear()

        data = data1 + data2 + data3
        win = SuccessWindow(self._window)
        win.create_window(color_code=2,data=f"{' '.join(self._parent)} : {data}")


