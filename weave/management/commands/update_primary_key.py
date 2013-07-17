# -*- coding: utf-8 -*-
# code is in the public domain
#
# Based on:
# http://djangosnippets.org/snippets/2691/
# myapp/management/commands/update_primary_key.py
u'''

Management command to update a primary key and update all child-tables with a foreign key to this table.

Does use django's db introspection feature. Tables don't need to have django ORM models.

Usage: manage.py update_primary_key table_name column_name value_old value_new
'''
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.transaction import commit_on_success

table_list=None
def get_table_list(cursor):
    global table_list
    if not table_list:
        table_list=connection.introspection.get_table_list(cursor)
    return table_list

relations={} # Cache
def get_relations(cursor, table_name):
    rels=relations.get(table_name)
    if rels is None:
        rels=connection.introspection.get_relations(cursor, table_name)
        relations[table_name]=rels
    return rels

def get_back_relations(cursor, table_name):
    backs=[]
    relations_back={}
    for ref_table in get_table_list(cursor):
        ref_relations=get_relations(cursor, ref_table)
        for ref_col_idx, ref_relation in ref_relations.items():
            to_col=ref_relation[0]
            to_table=ref_relation[1]
            if to_table!=table_name:
                continue
            # Found a reference to table_name
            backs=relations_back.get(to_col)
            if not backs:
                backs=[]
                relations_back[to_col]=backs
            backs.append((ref_col_idx, ref_table))
    return (backs, relations_back)

class Command(BaseCommand):
    args = 'table_name column_name value_old value_new'
    help = 'Update a primary key and update all child-tables with a foreign key to this table.'
    @commit_on_success
    def handle(self, *args, **options):
        rootLogger = logging.getLogger('')
        rootLogger.setLevel(logging.INFO)
        if len(args)!=4:
            raise CommandError('Need args: %s' % self.args)
        table_name, column_name, value_old, value_new = args
        cursor=connection.cursor()
        descr=connection.introspection.get_table_description(cursor, table_name)
        for idx, col in enumerate(descr):
            if col.name==column_name:
                break
        else:
            raise CommandError('Column %r not in table %r' % (column_name, table_name))
        backs, relations_back = get_back_relations(cursor, table_name)

        if relations_back.has_key(idx):
            relations_all = relations_back[idx]
            #Find if there are any relations for the relations themselves. This case is mainly to support model inheritance
            for rel in relations_back[idx][:]:
                _backs, _relations_back = get_back_relations(cursor, rel[1])
                if _relations_back.has_key(rel[0]):
                    relations_all += _relations_back[rel[0]]
        else:
            relations_all = []

        sql='select count(*) from "%s" where "%s" = %%s' % (table_name, column_name)
        cursor.execute(sql, [value_old])
        count=cursor.fetchone()[0]
        sql=sql % value_old
        if count==0:
            raise CommandError('No row found: %s' % sql)
        if count>1:
            raise CommandError('More than one row found???: %s' % sql)
        def execute(sql, args):
            logging.info('%s %s' % (sql, args))
            cursor.execute(sql, args)
        execute('update "%s" set "%s" = %%s where "%s" = %%s' % (table_name, column_name, column_name), [value_new, value_old])
        for col_idx, ref_table in relations_all:
            cursor.execute('update "%s" set "%s" = %%s where "%s" = %%s' % (table_name, column_name, column_name), [value_new, value_old])
            ref_descr=connection.introspection.get_table_description(cursor, ref_table)
            ref_col=ref_descr[col_idx]
            execute('update "%s" set "%s" = %%s where "%s" = %%s' % (ref_table, ref_col.name, ref_col.name), [value_new, value_old])
