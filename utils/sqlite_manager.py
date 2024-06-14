import sqlite3
from typing import List, Tuple
from datetime import datetime
import os
import sys

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

class SQLiteManager:
    def __init__(self, db_name):
        self.db_name = os.path.join(BUNDLE_DIR, db_name)
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS Deliverymen (id TEXT PRIMARY KEY, farmax_id INTEGER, name TEXT)")
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS Deliveries (id TEXT, farmax_id INTEGER PRIMARY KEY, deliveryman_id TEXT, done INTEGER, created_at TEXT)")
            print("Connected to SQLite")
        except sqlite3.Error as e:
            print("Error connecting to SQLite database:", e)

    def saveDeliverymen(self, deliverymen: List[Tuple[str, int, str]]):
        query = "INSERT OR REPLACE INTO Deliverymen (id, farmax_id, name) VALUES (?, ?, ?)"
        self.cursor.executemany(query, deliverymen)
        self.conn.commit()

    def areDeliverymenUpToDate(self, deliverymen_ids: List[str]):
        query = "SELECT * FROM Deliverymen WHERE id IN ({})".format(','.join(['?'] * len(deliverymen_ids)))
        self.cursor.execute(query, [deliverymanId for deliverymanId in deliverymen_ids])
        results = self.cursor.fetchall()
 
        if len(deliverymen_ids) != len(results):
            return False  # Different number of deliverymen
        
        # Sort both lists for consistent comparison
        deliverymen_ids.sort()
        results.sort()
        
        # Check if all attributes are equal
        for i in range(len(deliverymen_ids)):
            if deliverymen_ids[i] != results[i][0]:
                return False  # Attributes don't match
        
        return True  # All deliverymen are up to date
    
    def filterDeliveriesNotAdded(self, farmax_deliveries_ids: List[str]):
        """
        Filters deliveries from Farmax that are not added to SQLite
        """
        query = "SELECT * FROM Deliveries WHERE farmax_id IN ({})".format(','.join(['?'] * len(farmax_deliveries_ids)))
        self.cursor.execute(query, [deliveryId for deliveryId in farmax_deliveries_ids])
        results = self.cursor.fetchall()
        resultIDs = [result["farmax_id"] for result in results]

        return filter(lambda farmaxDeliveryId: farmaxDeliveryId not in resultIDs, farmax_deliveries_ids)

    def create_table(self, table_name, columns):
        try:
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
            print(f"Table '{table_name}' created successfully")
        except sqlite3.Error as e:
            print("Error creating table:", e)

    def insert_data(self, table_name, data):
        try:
            self.cursor.execute(f"INSERT INTO {table_name} VALUES ({','.join(['?']*len(data))})", data)
            self.conn.commit()
            print("Data inserted successfully")
        except sqlite3.Error as e:
            print("Error inserting data:", e)

    def get_data(self, table_name):
        try:
            query = f"SELECT * FROM {table_name}"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            return data
        except sqlite3.Error as e:
            print("Error fetching data from table:", e)
            return []
        
    def get_data_in(self, table_name, column, inside: list, additional_conditions=list()):
        try:
            conditions = ' AND '.join([f"{condition[0]} = ?" for condition in additional_conditions])
            query = f"SELECT * FROM {table_name} WHERE {column} IN ({", ".join("?" * len(inside))}) {conditions}"
            self.cursor.execute(query, list(inside) + list([condition[1] for condition in additional_conditions]))
            data = self.cursor.fetchall()
            return data
        except Exception as e:
            print("Error fetching data from table:", e)
            return []
        
    def get_data_where_multi(self, table_name, conditions, not_null=list(), is_null=list()):
        try:
            placeholders = ' AND '.join([f"{condition[0]} = ?" for condition in conditions])
            if len(not_null) > 0:
                placeholders = placeholders + ' AND ' + ' AND '.join([f"{not_null_value} IS NOT NULL" for not_null_value in not_null])
            if len(is_null) > 0:
                placeholders = placeholders + ' AND ' + ' AND '.join([f"{null_value} IS NULL" for null_value in is_null])
            values = [condition[1] for condition in conditions]
            query = f"SELECT * FROM {table_name} WHERE {placeholders}"
            self.cursor.execute(query, values)
            data = self.cursor.fetchall()
            return data
        except sqlite3.Error as e:
            print("Error fetching data from table:", e)
            return []

    def get_data_where(self, table_name, column_name, values):
        try:
            placeholders = ', '.join(['?' for _ in values])
            query = f"SELECT * FROM {table_name} WHERE {column_name} IN ({placeholders})"
            self.cursor.execute(query, values)
            data = self.cursor.fetchone()
            return data
        except sqlite3.Error as e:
            print("Error fetching data from table:", e)
            return []

    def has_data(self, table_name, column_name, values):
        try:
            # Execute a SELECT query to check if the data exists
            query = f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} = ?"
            results = []
            for value in values:
                self.cursor.execute(query, (value,))
                count = self.cursor.fetchone()[0]
                results.append(count > 0)

            return results
        except sqlite3.Error as e:
            print("Error checking data existence:", e)
            return [False] * len(values)

    def update_data(self, table_name, set_values, where_condition):
        try:
            # Construct SET clause for UPDATE query
            set_clause = ', '.join([f"{value[0]} = ?" for value in set_values])

            # Construct WHERE clause for UPDATE query
            where_clause = ' AND '.join([f"{condition[0]} = ?" for condition in where_condition])

            # Execute the UPDATE query
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            self.cursor.execute(query, list(value[1] for value in set_values) + list(condition[1] for condition in where_condition))
            self.conn.commit()

            print("Data updated successfully")
        except sqlite3.Error as e:
            self.conn.rollback()
            print("Error updating data:", e)

    def getLatestSale(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"SELECT * FROM Deliveries ORDER BY created_at DESC LIMIT 1")
        result = self.cursor.fetchone()
        return result
    
    def delete_where(self, table_name, conditions):
        try:
            # Construct WHERE clause for UPDATE query
            where_clause = ' AND '.join([f"{condition[0]} = ?" for condition in conditions])
            query = f"DELETE FROM {table_name} WHERE {where_clause}"
            self.cursor.execute(query, list(condition[1] for condition in conditions))
            self.conn.commit()
        except Exception as e:
            print("Error deleting data from table:", e)

    def close_connection(self):
        if self.conn:
            self.conn.close()
            print("SQLite connection closed")
        else:
            print("No SQLite connection to close")
