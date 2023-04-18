import pyodbc
import configparser

class CornMoistDB:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.connection = self.connect()

    def connect(self):
        server = self.config['MSSQL']['server']
        database = self.config['MSSQL']['database']
        username = self.config['MSSQL']['username']
        password = self.config['MSSQL']['password']
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        return pyodbc.connect(connection_string)

    def create_database(self, db_name):
        cursor = self.connection.cursor()
        cursor.execute(f'CREATE DATABASE {db_name}')
        self.connection.commit()

    def create_table(self, table_name, columns):
        cursor = self.connection.cursor()
        columns_string = ', '.join(columns)
        cursor.execute(f'CREATE TABLE {table_name} ({columns_string})')
        self.connection.commit()

    def select_data(self, table_name, condition=None):
        cursor = self.connection.cursor()
        if condition:
            query = f'SELECT * FROM {table_name} WHERE {condition}'
        else:
            query = f'SELECT * FROM {table_name}'
        cursor.execute(query)
        return cursor.fetchall()

    def drop_table(self, table_name):
        cursor = self.connection.cursor()
        cursor.execute(f'DROP TABLE {table_name}')
        self.connection.commit()

    def update_table(self, table_name, updates, condition=None):
        cursor = self.connection.cursor()
        updates_string = ', '.join(updates)
        if condition:
            query = f'UPDATE {table_name} SET {updates_string} WHERE {condition}'
        else:
            query = f'UPDATE {table_name} SET {updates_string}'
        cursor.execute(query)
        self.connection.commit()

    def insert_into_table(self, table_name, columns=None, values=None):
        cursor = self.connection.cursor()
        if columns is None:
            columns = ['insLot', 'material', 'batch', 'plant', 'count', 'min_value', 'max_value', 'mean_value', 'stddev_value']
        columns_string = ', '.join(columns)
        values_string = ', '.join(f"'{value}'" for value in values)
        cursor.execute(f'INSERT INTO {table_name} ({columns_string}) VALUES ({values_string})')
        self.connection.commit()

    def truncate_table(self, table_name):
        cursor = self.connection.cursor()
        cursor.execute(f'TRUNCATE TABLE {table_name}')
        self.connection.commit()

    def close_connection(self):
        self.connection.close()