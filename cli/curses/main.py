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
from main_menu import MainMenu
from color_code import ColorCode

def main(stdscr):
    screen = curses.initscr()
    curses.curs_set(0)
    cod = ColorCode()
    cod.create_color_pair(curses.COLOR_BLACK, curses.COLOR_WHITE)
    cod.create_color_pair(curses.COLOR_GREEN,curses.COLOR_BLACK)
    cod.create_color_pair(curses.COLOR_RED,curses.COLOR_BLACK)
    wind = MainMenu(stdscr)
    wind.create_default_window(2)
    wind.create_window(color_code=2,menu_code=0)
    wind.process_input()

curses.wrapper(main)

