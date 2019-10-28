import mysql.connector
from mysql.connector import errorcode, Error
_verbose = False
_debug = False
class MySQLClient ():
    def __init__(self,host,port,db,user,password):
        if (_debug):
            print (">>Entering MySQLClient::__init__(", host,port,db,user,password,")")
        self.MySQL = mysql.connector
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        self.query = ''
        self.query_args = ''
        self.query_cursor = ''
        if (_debug):
            print ("<<Leaving MySQLClient::__init__()")
    def connect(self):
        if (_debug):
            print (">>Entering MySQLClient::connect()")
        try:
            self.MySQL =  mysql.connector.connect(host=self.host, port = self.port, database = self.db, user = self.user, password= self.password)
            if (self.MySQL.is_connected() and (_debug or _verbose)):
                print('writing to database')
 
        except Error as e:
            print(e)
        if (_debug):
            print ("<<Leaving MySQLClient::connect()")
    def close(self):
        if (_debug):
            print (">>Entering MySQLClient::close()")
        self.MySQL.close()
        if (_debug):
            print ("<<Leaving MySQLClient::close()")

    def insert(self,table,args):
        
        if (_debug):
            print (">>Entering MySQLClient::insert(",table,args ,")")

        col_str =""
        values = ()
        temp_str=""
        
        for arg in args:
            col_str = col_str + str(arg[0]) + ', '
            temp_str = temp_str + '%s, '
            values = values + (arg[1],)

        col_str = col_str.rstrip(', ')
        temp_str = temp_str.rstrip(', ')
        self.query = "INSERT INTO " + table + " (" + col_str + ") VALUES (" + temp_str + ")"

        self.query_args = (values)
        
        try:
            self.query_cursor = self.MySQL.cursor()
            self.query_cursor.execute(self.query,self.query_args)
            self.MySQL.commit()
        except Error as error:
            print(error)
        finally:
            self.query_cursor.close()
        if (_debug):
            print ("<<Leaving MySQLClient::insert()")
            
    #def new_db(self,
    def stored_procedure(self,procedure_name,args):
        if (_debug):
            print (">>Entering MySQLClient::stored_procedure(" + procedure + ", " + args + ")")   
       
        try:
            self.query_cursor = self.MySQL.cursor()
            self.query_cursor.callproc(procedure_name,args)
            if (_debug or _verbose):
                for result in self.query_cursor.stored_results():
                    print(result.fetchall())
        except Error as error:
            print(error)
        finally:
            self.query_cursor.close()
        if (_debug):
            print ("<<Leaving MySQLClient::stored_procedure()")
            
    def new_table(self,table_string):
        if (_debug):
            print (">>Entering MySQLClient::new_table(" + table_string + ")")   
        self.query = "CREATE TABLE IF NOT EXISTS " + table_string
        try:
            self.query_cursor = self.MySQL.cursor()
            self.query_cursor.execute(self.query)
        except Error as error:
            print(error)
        finally:
            self.query_cursor.close()
        if (_debug):
            print ("<<Leaving MySQLClient::insert()")


