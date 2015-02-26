
"""
Postgres specific stuff goes here in case we ever want to write something else.
"""


#http://www.linuxscrew.com/2009/07/03/postgresql-show-tables-show-databases-show-columns/

def get_databases(connection):
    return sorted(connection.execute('select datname as dbname from pg_database').fetchall())

def index_cache_hitrate(connection):
   #% of times your indicies are loaded from ram.
   return connection.execute('''SELECT
     sum(idx_blks_read) as idx_read,
       sum(idx_blks_hit)  as idx_hit,
         (sum(idx_blks_hit) - sum(idx_blks_read)) / sum(idx_blks_hit) as ratio
         FROM
           pg_statio_user_indexes;''').fetchall()

def index_hitrates_per_table(connection):
    #info on index usage on tables
    return connection.execute('''SELECT
  relname, seq_scan, idx_scan, seq_tup_read, idx_tup_fetch,
    100 * idx_scan / (seq_scan + idx_scan) percent_of_times_index_used,
      n_live_tup rows_in_table
      FROM
        pg_stat_user_tables
        WHERE
            seq_scan + idx_scan > 0
            ORDER BY
              seq_scan desc;''').fetchall()



############# PG STAT STATEMENTS SPECIFIC QUERIES ####################

def check_query_cache_hitrates(connection):
    return connection.execute('''SELECT query, calls, total_time, rows, 100.0 * shared_blks_hit /
               nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
          FROM pg_stat_statements ORDER BY total_time DESC LIMIT 5;''').fetchall()


def check_queries_that_use_lots_of_time(connection):
    return connection.execute('''select *, total_time/calls as avg_time from pg_stat_statements
                                 where calls > 100 order by  total_time desc;''').fetchall()

def check_queries_that_have_high_average_time(connection):
    return connection.execute('''select *, total_time/calls as avg_time from pg_stat_statements
                                 where calls > 100 order by  avg_time desc;''')