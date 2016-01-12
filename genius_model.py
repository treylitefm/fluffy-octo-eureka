import sqlite3

class Model:
    """Class handling select and insert operations for scraper"""
    db = None
    db_name = None

    def __init__(self, name):
        self.db_name = name
        self.db = sqlite3.connect(name)

    def insert(self, table, **kwargs):
        query_keys = '(' + ','.join(kwargs.keys())
        query_keys += 'created_on,updated_on)'

        query_values = ','.join(map(lambda val: '\''+val+'\'', kwargs.values()))
        query_values += ',datetime(\'now\',\'-5 hour\'),datetime(\'now\',\'-5 hour\')'

        where_conditions = ''
        
        for key,value in kwargs.iteritems():
            print key,value
            where_conditions += key + '=' + '\'' + value + '\' AND '

        where_conditions = where_conditions[:where_conditions.rfind('\'')+1]


        query = 'INSERT INTO '+\
                table+' '+\
                query_keys+' '+\
                'SELECT '+\
                query_values+' '+\
                'WHERE NOT EXISTS('+\
                'SELECT 1 FROM '+\
                table+' '+\
                'WHERE '+\
                where_conditions+\
                ');'

        query = query.encode('utf-8')
        #print query
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
