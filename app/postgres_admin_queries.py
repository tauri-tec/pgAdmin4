
"""
Postgres specific stuff goes here in case we ever want to write something else.
"""


#http://www.linuxscrew.com/2009/07/03/postgresql-show-tables-show-databases-show-columns/

def get_databases(connection):
    return sorted(connection.execute('select datname as dbname from pg_database').fetchall())