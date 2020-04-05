# -*- coding: utf-8 -*-
# Corpuscula project: Items Dictionary
#
# Copyright (C) 2019-present by Sergei Ternovykh
# License: BSD, see LICENSE for details
"""
Just a simple wrapper to store some structured data. For example (see lower),
to store dictionary of names.
"""
from copy import deepcopy
import pickle
import sys

from .utils import LOG_FILE


class Items:

    def __init__(self, restore_from=None, backup_to=None):
        """
        :param restore_from: path to backup file to load from
        :type restore_from: str
        :param backup_to: path to backup file to save to
        :type backup_to: str
        :param log_file: stream for info messages
        :type file
        """
        self._items = {}  # {item_class: {}}

        if restore_from:
            self.restore_from(restore_from)
        if backup_to:
            self.backup_to(backup_to)

    def backup(self):
        """Get current state"""
        return self._items

    def backup_to(self, file_path):
        """Store current state to file"""
        with open(file_path, 'wb') as f:
            pickle.dump(self.backup(), f, 2)

    def restore(self, o):
        """Restore current state from backup object"""
        self._items = o

    def restore_from(self, file_path):
        """Restore current state from file"""
        with open(file_path, 'rb') as f:
            self.restore(pickle.load(f))

    def isempty(self, item_class=None):
        """Check if current state is not contain any information"""
        return not self._items.get(item_class)

    def get(self, item_class=None, item=None, copy=True):
        """Return a value of some *item* of some class. If item is None, return
        all items of the class.

        :param copy: if True, return a copy of the object (default). Elsewise,
                     return the object itself
        """
        assert item_class in self._items, 'ERROR: Item class does not exist'
        res = self._items[item_class]
        if item:
            res = res.get(item.lower() if isinstance(item, str) else item)
        return deepcopy(res) if copy else res

    def item_isknown(self, item, item_class):
        return self._items.get(item_class, {}).get(
            item.lower() if isinstance(item, str) else item
        ) is not None

    def load(self, items, item_class=None, update=False, encoding='utf-8-sig',
             log_file=LOG_FILE):
        """Load a list of *items* of some class.

        :param items: {item: {attr: val}}, [item], set(item)
        :type items: dict|list|set
        :param item_class: some identificator to designate the list given 
                           (e.g.: 'surname')
        :param update: if a list of the given class is already exists, append
                       or update it
        """
        assert self.isempty(item_class) or update, 'ERROR: Item class is ' \
            'already exists. Use update=True to append or update it'
        if not isinstance(items, dict):
            items = dict.fromkeys(items, {})
        old_len = None if self.isempty(item_class) else len(self._items[item_class])
        items_ = {}
        for item, props in items.items():
            props[None] = item
            items_[item.lower() if isinstance(item, str) else item] = props
        self._items.setdefault(item_class, {}).update(items_)
        print('Loaded {} items{} ({})'
                  .format(len(items_),
                          ' to class {}'
                              .format(item_class) if item_class else '',
                          'new' if old_len is None else
                          '{} new, {} total'
                              .format(old_len, len(self._items[item_class]))),
              file=log_file)

    def derive(self, derivator, item_class, proto_class=None, update=False):
        """Make a new class of items derived from some already existing class.

        :param derivator: method that make a new class
        :type derivator: callable
        :param item_class: identificator for a new class
        :param proto_class: identificator of the existing class
        :param update: if a list of the given class is already exists, append
                       or update it
        """
        assert self._isempty(item_class) or update, 'ERROR: Item class is ' \
            'already exists. Use update=True to append or update it'
        items = derivator(self.items[item_class])
        self._items.setdefault(item_class, set()).update(items)
        print('Created {} items of class {} (total: {})'
                  .format(len(items), item_class,
                          len(self._items[item_class])),
              file=log_file)


if __name__ == '__main__':
    import csv
    it = Items()
    names, patronyms, surnames = {}, {}, {}
    # 'names.txt' contains csv strings (delimiter is semicolon) with names,
    # patronyms and surnames of some Russian persons
    with open('names.txt', mode='rt', encoding='utf-8-sig') as f:
        lines = list(csv.reader(f, delimiter=';', quotechar='"'))
        for i, line in enumerate(lines):
            try:
                name, patronym, surname, isactive = line
            except ValueError as e:
                print('ERROR in line {}: {}'.format(i, line))
                raise e
            name = name.strip()
            patronym = patronym.strip()
            surname = surname.strip()
            isactive = isactive == 't'

            gender = '-'
            if patronym.endswith('вна') or patronym.endswith('чна'):
                gender = 'F'
            elif patronym.endswith('вич') or patronym.endswith('ьич'):
                gender = 'M'
            else:
                # ignore persons with non-Russian-style names
                continue

            if gender == '-':
                if len(surname) >= 5 and (surname.endswith('ова')
                                       or surname.endswith('ева')):
                    gender = 'F'
                elif len(surname) >= 4 and (surname.endswith('ов')
                                         or surname.endswith('ев')):
                    gender = 'M'

            ####
            if name in names:
                cur_gender = names[name]['gender']
                if cur_gender == '-':
                    names[name]['gender'] = gender
                elif gender != '-' and cur_gender != 'FM' \
                 and gender != cur_gender:
                    print(name, patronym, surname,
                          'name gender changed!', cur_gender, gender)
                    names[name]['gender'] = 'FM'
            else:
                names[name] = {'gender': gender, 'count': 0}
            if isactive:
                names[name]['count'] += 1

            ####
            if patronym:
                if patronym in patronyms:
                    cur_gender = patronyms[patronym]['gender']
                    if cur_gender == '-':
                        patronyms[patronym]['gender'] = gender
                    elif gender != '-' and cur_gender != 'FM' \
                     and gender != cur_gender:
                        print(name, patronym, surname,
                              'patronym gender changed!', cur_gender, gender)
                        patronyms[patronym]['gender'] = 'FM'
                else:
                    patronyms[patronym] = {'gender': gender, 'count': 0}
                if isactive:
                    patronyms[patronym]['count'] += 1

            ####
            if surname in surnames:
                cur_gender = surnames[surname]['gender']
                if cur_gender == '-':
                    surnames[surname]['gender'] = gender
                elif gender != '-' and cur_gender != 'FM' \
                 and gender != cur_gender:
                    #print(name, patronym, surname,
                    #      'surname gender changed!', gender, cur_gender)
                    surnames[surname]['gender'] = 'FM'
            else:
                surnames[surname] = {'gender': gender, 'count': 0}
            if isactive:
                surnames[surname]['count'] += 1

        for name, patronym, surname, isactive in lines:
            name = name.strip()
            patronym = patronym.strip()
            surname = surname.strip()

            if patronym not in patronyms:
                continue

            n_gender = names[name]['gender']
            p_gender = patronyms[patronym]['gender']
            s_gender = surnames[surname]['gender']

            gender = 'F' if 'F' in [n_gender, p_gender, s_gender] \
                        and 'M' not in [n_gender, p_gender, s_gender] else \
                     'M' if 'M' in [n_gender, p_gender, s_gender] \
                        and 'F' not in [n_gender, p_gender, s_gender] else \
                     '-'
            if gender:
                if n_gender == '-':
                    names[name]['gender'] = gender
                if p_gender == '-':
                    patronyms[patronym]['gender'] = gender
                if s_gender == '-':
                    surnames[surname]['gender'] = gender
            elif '-' in [n_gender, p_gender, s_gender]:
                print(name, patronym, surname, 'gender?')

    it.load(names, 'name')
    it.load(patronyms, 'patronym')
    it.load(surnames, 'surname')
    it.backup_to('items.pickle')
    print('{} names, {} patronyms, {} surnames'
              .format(len(names), len(patronyms), len(surnames)))
