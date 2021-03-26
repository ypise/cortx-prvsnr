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

    data = {'Ip': '10.10.10.10',
            'Netmask': '1.255.255.255',
            'Gateway': '198.162.0.1'}

    def submit_button(self, x, y, menu, selected_rows):
        buttons = {
           "Submit": x + 15,
           "Cancel": x + 5
        }
        selected_button = None
        if selected_rows == len(menu):
            selected_button = "Submit"
        elif selected_rows == len(menu) + 1:
            selected_button = "Cancel"
        for button in buttons.keys():
            if selected_button == button:
                cod = ColorCode.get_color_pair(1)
                self.on_attr(cod)
                self._window.addstr(y + 1,buttons[button] ,button)
                self.off_attr(cod)
            else:
                self._window.addstr(y + 1,buttons[button] ,button)


    def create_window(self, **kwargs):
        color_code = kwargs['color_code']
        self._parent = kwargs['component']

        if 'selected' not in kwargs:
            selected_rows = 0
        else:
            selected_rows = kwargs['selected']

        if 'edit' not in kwargs:
            edit = False
        else:
            edit = kwargs['edit']

        self._window.border()
        col_code_attr = ColorCode.get_color_pair(color_code)
        self.create_menu_head()

        x = self.get_max_width() // 2
        y = self.get_max_height() // 3 - 1
        self.enable_keypad()

        self.on_attr(col_code_attr)
        self._window.addstr(y,3 ,f"Please enter ip for this machine ")
        self.off_attr(col_code_attr)

        values = list(self.data.keys())
        x = 6

        for idx, row in enumerate(values):
            y = self.get_max_height()  // 3 - len(values)//2 + (idx+1)*2
            #self._window.hline(y+1 , 15 ,"_",16)
            if not (idx == selected_rows):
                self._window.addstr(y,x ,f"{values[idx]}:")
                self._window.addstr(y,14 ,f" {self.data[values[idx]]}")
 
        y = self.get_max_height()  // 3 - len(values)//2 + (len(values) + 1)*2

        self.submit_button(x, y, values, selected_rows)
   #     if selected_rows == len(values):
   #         cod = ColorCode.get_color_pair(1)
   #         self.on_attr(cod)
   #         self._window.addstr(y + 1,x + 15 ,"Submit ")
   #         self.off_attr(cod)
   #     else:
            #cod = ColorCode.get_color_pair(1) 
            #self.on_attr(cod)      
   #         self._window.addstr(y + 1,x + 15 ,"Submit ")
            #self.off_attr(cod)

        if selected_rows <len(values):
           y = self.get_max_height()  // 3 - len(values)//2 + (selected_rows + 1)*2

           self.on_attr(col_code_attr)
           self._window.addstr(y,x-3 ,">> ")
           self._window.addstr(y,x ,f"{values[selected_rows]}:")
           if edit:
               data2 = TextBox(self._window, 1, 16, y , x + 10, self.get_max_height() // 4).create_textbox(color_code, self.data[values[selected_rows]])
               self.data[values[selected_rows]] = data2
           else:
              self._window.addstr(y,14 ,f" {self.data[values[selected_rows]]}")
           self.off_attr(col_code_attr)

    def process_input(self, color_code):
        current_row = 0
        values = list(self.data.keys())
        while 1:
           key = self._window.getch()
           self._window.clear()
           if key == curses.KEY_UP and current_row > 0:
               current_row = current_row - 1
           elif key == curses.KEY_DOWN and  current_row < len(values):
               current_row = current_row + 1
           elif current_row == len(values) and key == curses.KEY_LEFT:
               current_row = current_row + 1
           elif current_row == len(values) + 1 and key == curses.KEY_RIGHT:
               current_row = current_row - 1
           elif key == 113:
               return
           elif key == curses.KEY_ENTER or key in (10, 13):
               if current_row < 3 and current_row >= 0:
                    self._window.clear()
                    self.create_window(color_code=color_code, selected=current_row, component=self._parent,edit=True)
                    self._window.refresh() 
               elif current_row == len(values):
                    win = SuccessWindow(self._window)
                    win.create_window(color_code=2,data=f"Network data : {str(self.data)}")
                    break
               else:
                    break

           self._window.clear()
           self.create_window(color_code=color_code, selected=current_row, component=self._parent)
           self._window.refresh()
