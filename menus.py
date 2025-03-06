# menus.py
# This file implements a menus class
"""
Menus Abstraction:
- init
menus: dict
- add menu (menu_name, menu_items)
menu_items format: csv of menu spreadsheet for the week
- get menu (sunday of the week date)
- get all menus

"""


class Menus:
    def __init__(self):
        self.menus = {}

    def add_menu(self, week_start_date, menu_items):
        self.menus[week_start_date] = menu_items

    def get_menu(self, week_start_date):
        return self.menus[week_start_date]

    def get_latest_menu(self):
        if not self.menus:
            return "No menus available"
        return self.menus[max(self.menus.keys())]

    def get_all_menus(self):
        return self.menus
