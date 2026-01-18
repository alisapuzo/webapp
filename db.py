import click
import os
import sqlite3
from flask import current_app, g

#Stellt eine Verbindung zur Datenbank her
def get_db_con(pragma_foreign_keys = True):
    if 'db_con' not in g:
        g.db_con = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db_con.row_factory = sqlite3.Row
        if pragma_foreign_keys:
            g.db_con.execute('PRAGMA foreign_keys = ON;') 
            #Mit PRAGMA foreign_keys = ON; weisen wir SQLite an, 
            # Fremdschlüsselbeschränkungen zu erzwingen, die standardmäßig deaktiviert sind
    return g.db_con

#Schließt die Datenbankverbindung
def close_db_con(e=None):
    db_con = g.pop('db_con', None)
    if db_con is not None:
        db_con.close()


@click.command('init-db')
def init_db():
    try:
        os.makedirs(current_app.instance_path)
    except OSError:
        pass
    db_con = get_db_con()
    with current_app.open_resource('sql/drop_tables.sql') as f:
        db_con.executescript(f.read().decode('utf8'))
    with current_app.open_resource('sql/create_tables.sql') as f:
        db_con.executescript(f.read().decode('utf8'))
    click.echo('Database has been initialized.')        


def insert_sample():
    db_con = get_db_con()
    with current_app.open_resource('sql/insert_sample.sql') as f:
        db_con.executescript(f.read().decode('utf8'))