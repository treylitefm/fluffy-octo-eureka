import sqlite3

class Model:
    """Class handling select and insert operations for scraper"""
    db = None
    db_name = None

    def __init__(self, name):
        self.db_name = name
        self.db = sqlite3.connect(name)

    def insert(self, table, **kwargs):
        query_keys = '('
        query_values = '('

        for key,value in kwargs.iteritems():
            query_keys += key+','
            query_values += '\''+value+'\','

        query_keys += 'created_on,updated_on)'
        query_values += 'datetime(\'now\',\'-5 hour\'),datetime(\'now\',\'-5 hour\'));'

        query = 'INSERT INTO '+\
                table+' '+\
                query_keys+' '+\
                'VALUES '+\
                query_values 

        print query
        id = str(self.db.execute(query).lastrowid)
        self.db.commit()
        return id
    '''
    def select(self, table, limit=None, **kwargs):
        return 'not yet implemented'
        query = ''
        print "Table:", table
        print "Limit:", limit

        query += ' limit '+limit+';' if limit else ';'
   '''
