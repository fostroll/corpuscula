# -*- coding: utf-8 -*-
# Corpuscula project: Items Dictionary
#
# Copyright (C) 2019-present by Sergei Ternovykh
# License: BSD, see LICENSE for details
"""
Loader for csv-files with names, surnames and patronyms to the Items database.
"""
import csv
import os

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
###
import sys
sys.path.append(os.path.join(SCRIPT_PATH, '..'))
###
from corpuscula import Items


def load_names_db(names_csv, n_db, p_db, s_db,
                  n_thresh=None, p_thresh=None, s_thresh=None):
    """Load databases *n_db*, *p_db* and *s_db* with names, patronyms and
    surnames respectively from *names_csv* file

    Struct of the resulting db:
        'name'|'patronym'|'surname':
            'count': <count:int>
            'gender': 'F|M|FM|-'
            'F': <count:int>
            'M': <count:int>
            'F': <count:int>
            '-': <count:int>

    :param n_thresh: ignore name if it is met in *names_csv* less than this
                     value
    :param p_thresh: ignore patronym if it is met in *names_csv* less than this
                     value
    :param s_thresh: ignore surname if it is met in *names_csv* less than this
                     value
    """
    names, patronyms, surnames = {}, {}, {}
    # 'names.csv' contains csv strings (delimiter is semicolon) with names,
    # patronyms and surnames of some Russian persons
    with open(names_csv, mode='rt', encoding='utf-8-sig') as f:
        lines = list(csv.reader(f, delimiter=';', quotechar='"'))
        for i, line in enumerate(lines):
            try:
                name, patronym, surname = line[:3]
            except ValueError as e:
                print('ERROR in line {}: {}'.format(i, line))
                raise e
            name = name.strip()
            patronym = patronym.strip()
            surname = surname.strip()

            gender = '-'
            if patronym.endswith('вна') or patronym.endswith('чна') \
                                        or patronym.endswith('кызы'):
                gender = 'F'
            elif patronym.endswith('вич') or patronym.endswith('ьич') \
                                          or patronym.endswith('оглы'):
                gender = 'M'
            else:
                # ignore persons with non-Russian and non-Turkish style names
                continue

            if gender == '-':
                if len(surname) >= 5 and (surname.endswith('ова')
                                       or surname.endswith('ева')):
                    gender = 'F'
                elif len(surname) >= 4 and (surname.endswith('ов')
                                         or surname.endswith('ев')):
                    gender = 'M'

            ####
            names[name][gender] = \
                names.setdefault(name, {}).get(gender, 0) + 1
            patronyms[patronym][gender] = \
                patronyms.setdefault(patronym, {}).get(gender, 0) + 1
            surnames[surname][gender] = \
                surnames.setdefault(surname, {}).get(gender, 0) + 1

        for items, thresh in zip([names, patronyms, surnames],
                                 [n_thresh, p_thresh, s_thresh]):
            del_items = []
            for item, feats in items.items():
                gender, count = '-', 0
                if 'F' in feats:
                    if thresh and feats['F'] < thresh:
                        del feats['F']
                        pass
                    else:
                        gender = 'F'
                        count = feats['F']
                if 'M' in feats:
                    if thresh and feats['M'] < thresh:
                        del feats['M']
                        pass
                    else:
                        gender = 'FM' if gender == 'F' else 'M'
                        count += feats['M']
                if '-' in feats:
                    if gender in ['F', 'M']:
                        feats[gender] += feats['-']
                        count += feats['-']
                        del feats['-']
                    elif gender == '-':
                        if thresh and feats['-'] < thresh:
                            del feats['-']
                        else:
                            count += feats['-']
                if count != 0:
                    feats['gender'] = gender
                    feats['count'] = count
                else:
                    del_items.append(item)
            for item in del_items:
                del items[item]

        for line in lines:
            name, patronym, surname = line[:3]
            name = name.strip()
            patronym = patronym.strip()
            surname = surname.strip()

            if patronym not in patronyms:
                continue

            n_gender = names[name]['gender'] if name in names else 'X'
            p_gender = patronyms[patronym]['gender'] \
                           if patronym in patronyms else 'X'
            s_gender = surnames[surname]['gender'] \
                           if surname in surnames else 'X'

            gender = 'F' if 'F' in [n_gender, p_gender, s_gender] \
                        and 'M' not in [n_gender, p_gender, s_gender] else \
                     'M' if 'M' in [n_gender, p_gender, s_gender] \
                        and 'F' not in [n_gender, p_gender, s_gender] else \
                     '-'
            if gender != '-':
                if n_gender == '-':
                    names[name]['gender'] = gender
                    names[name][gender] = names[name]['count']
                if p_gender == '-':
                    patronyms[patronym]['gender'] = gender
                    patronyms[patronym][gender] = patronyms[patronym]['count']
                if s_gender == '-':
                    surnames[surname]['gender'] = gender
                    surnames[surname][gender] = surnames[surname]['count']
            elif '-' in [n_gender, p_gender, s_gender]:
                print(name, patronym, surname, 'gender?')

    n_db.load(names, 'name')
    p_db.load(patronyms, 'patronym')
    s_db.load(surnames, 'surname')
    print('{} names, {} patronyms, {} surnames'
              .format(len(names), len(patronyms), len(surnames)))


if __name__ == '__main__':
    n_db, s_db = Items(), Items()
    load_names_db(os.path.join(SCRIPT_PATH, '../data/names.csv'),
                  n_db=n_db, p_db=n_db, s_db=s_db,
                  n_thresh=5, p_thresh=5, s_thresh=3)
    n_db.backup_to(os.path.join(SCRIPT_PATH, '../names.pickle'))
    s_db.backup_to(os.path.join(SCRIPT_PATH, '../surnames.pickle'))
