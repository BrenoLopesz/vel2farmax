import fdb
from datetime import datetime

class Farmax:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.farmax_conn = None
        
        self.SEQUENCE_NAME = "DELIVERYLOG_ID_AUTOINCREMENT"
        self.LOG_TABLE_NAME = "DELIVERYLOG"
        self.INCREMENT_TRIGGER_NAME = "TRG_DELIVERY_LOGID_INCREMENT"
        self.ADD_DELIVERY_TRIGGER_NAME = "TRG_ADD_DELIVERY"

    def connect(self):
        try:
            # Connect to the Firebird database
            self.farmax_conn = fdb.connect(
                dsn=self.host + ':' + self.database,
                user=self.user,
                password=self.password
            )

            self.initialSetup()
        except Exception as e:
            print("Error connecting to database:", e)

    def initialSetup(self):
        """
        Add neccessary triggers to track new or deleted deliveries on Farmax.
        """
        if not self.farmax_conn:
            print("Not connected to the database.")
            return

        try: 
            cur = self.farmax_conn.cursor()
            # Create sequence if not exists
            if not self.checkIfSequenceExists(self.SEQUENCE_NAME): 
                cur.execute(f"CREATE SEQUENCE {self.SEQUENCE_NAME}")

            # Create log table if not exists
            if not self.checkIfTableExists(self.LOG_TABLE_NAME): 
                cur.execute(f"CREATE TABLE {self.LOG_TABLE_NAME} ( Id INTEGER PRIMARY KEY, CD_VENDA DOUBLE PRECISION, Action VARCHAR(20), LogDate TIMESTAMP )")

            # Create a trigger to update sequence, if not exists
            if not self.checkIfTriggerExists(self.INCREMENT_TRIGGER_NAME): 
                cur.execute(f"""CREATE TRIGGER {self.INCREMENT_TRIGGER_NAME} FOR {self.LOG_TABLE_NAME}
                            ACTIVE BEFORE INSERT POSITION 0
                            AS
                            BEGIN
                                NEW.Id = next value for {self.SEQUENCE_NAME};
                            END""")
            
            # Create trigger for 'ENTREGAS', and insert to log, if not exists
            if not self.checkIfTriggerExists(self.ADD_DELIVERY_TRIGGER_NAME): 
                cur.execute(f"""CREATE TRIGGER {self.ADD_DELIVERY_TRIGGER_NAME}
                                FOR ENTREGAS
                                ACTIVE AFTER INSERT OR UPDATE OR DELETE
                            AS
                            BEGIN
                                IF (INSERTING) THEN
                                    INSERT INTO {self.LOG_TABLE_NAME} (CD_VENDA, Action, LogDate)
                                    VALUES (NEW.CD_VENDA, 'INSERT', CURRENT_TIMESTAMP);
                                ELSE IF (UPDATING) THEN
                                    INSERT INTO {self.LOG_TABLE_NAME} (CD_VENDA, Action, LogDate)
                                    VALUES (NEW.CD_VENDA, 'UPDATE', CURRENT_TIMESTAMP);
                                ELSE IF (DELETING) THEN
                                    INSERT INTO {self.LOG_TABLE_NAME} (CD_VENDA, Action, LogDate)
                                    VALUES (OLD.CD_VENDA, 'DELETE', CURRENT_TIMESTAMP);
                            END""")
                
            self.farmax_conn.commit()
            cur.close()

        except Exception as e:
            print("Error on initial Farmax database setup.", e)

    def fetchDeliverymen(self):
        if not self.farmax_conn:
            print("Not connected to the database.")
            return

        try:
            cur = self.farmax_conn.cursor()
            cur.execute("SELECT CD_VENDEDOR, NOME FROM VENDEDORES WHERE TIPO_FUNCIONARIO='E' ORDER BY NOME")
            rows = cur.fetchall()
            for row in rows:
                print(row)
            cur.close()
            return rows
        except Exception as e:
            print("Error fetching deliverymen:", e)

    def fetchChangesAfterTime(self, date_time):
        """
        Get changes after given time
        """
        if not self.farmax_conn:
            print("Not connected to the database.")
            return []

        try:
            cur = self.farmax_conn.cursor()
            cur.execute(f"SELECT * FROM {self.LOG_TABLE_NAME} WHERE LOGDATE > ?", (date_time,))
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print("Error fetching changes:", e)
            return []

    def fetchDeliveriesByIds(self, cd_vendas):
        """
        Get deliveries by id, that aren't in route
        """
        if not self.farmax_conn:
            print("Not connected to the database.")
            return []

        try:
            cur = self.farmax_conn.cursor()
            cur.execute(f"SELECT CD_VENDA, NOME, HORA_SAIDA FROM ENTREGAS WHERE STATUS = 'S' AND CD_VENDA IN ({",".join("?" * len(cd_vendas))}) ORDER BY CD_VENDA DESC", cd_vendas)
            rows = cur.fetchall()

            return rows
        except Exception as e:
            print("Error fetching deliveries:", e)
            return []
        
    def getSalesInfo(self, deliveries):
        cur = self.farmax_conn.cursor()

        cur.execute(f"""SELECT V1.CD_VENDA, V1.HORA, V1.TEMPENDERECO, V1.TEMPREFERENCIA
                        FROM VENDAS V1
                        JOIN (
                            SELECT CD_VENDA, MIN(CD_PRODUTO) AS first_sale
                            FROM VENDAS
                            WHERE CD_VENDA IN ({",".join("?" * len(deliveries))})
                            GROUP BY CD_VENDA
                        ) V2 ON V1.CD_VENDA = V2.CD_VENDA AND V1.CD_PRODUTO = V2.first_sale ORDER BY CD_VENDA DESC;
                        """, tuple(map(lambda delivery: delivery[0], deliveries)))

        # Prevents having duplicated sales with same 'CD_VENDA'
        sales = filter_repeated_values(cur.fetchall())

        # Close cursor and connection
        cur.close()

        sales_info = []
        for i, sale in enumerate(sales):
            sale_info = {}
            sale_info["cd_venda"] = sale[0]
            sale_info["created_at"] = sale[1]
            sale_info["address"] = sale[2]
            sale_info["reference"] = sale[3]
            sale_info["name"] = deliveries[i][1]
            sale_info["route_started_at"] = deliveries[i][2]
            sales_info.append(sale_info)
        
        return sales_info
    
    def updateDeliveryAsInRoute(self, cd_venda, cd_entregador, left_at):
        cursor = self.farmax_conn.cursor()
        cursor.execute("UPDATE ENTREGAS SET CD_ENTREGADOR = ?, HORA_SAIDA = ?, STATUS = 'R' WHERE CD_VENDA = ?", (float(cd_entregador), left_at, float(cd_venda)))
        self.farmax_conn.commit()
    
    def updateDeliveryAsDone(self, cd_venda, ended_at):
        cursor = self.farmax_conn.cursor()
        cursor.execute("UPDATE ENTREGAS SET HORA_CHEGADA = ?, STATUS = 'V' WHERE CD_VENDA = ?", (ended_at, float(cd_venda)))
        cursor.execute("UPDATE VENDAS SET CONCLUIDO = 'S', STATUS = 'V', HORAFINAL = ? WHERE CD_VENDA = ?", (ended_at, float(cd_venda)))
        self.farmax_conn.commit()
    
    def checkIfSequenceExists(self, sequence_name):
        cursor = self.farmax_conn.cursor()
        cursor.execute("SELECT * FROM RDB$GENERATORS WHERE RDB$GENERATOR_NAME = ?", (sequence_name,))
        return cursor.fetchone() is not None
    
    def checkIfTableExists(self, table_name):
        cursor = self.farmax_conn.cursor()
        cursor.execute("SELECT * FROM RDB$RELATIONS WHERE RDB$RELATION_NAME = ? AND RDB$VIEW_BLR IS NULL", (table_name,))
        return cursor.fetchone() is not None
    
    def checkIfTriggerExists(self, trigger_name):
        cursor = self.farmax_conn.cursor()
        cursor.execute("SELECT * FROM RDB$TRIGGERS WHERE RDB$TRIGGER_NAME = ?", (trigger_name,))
        return cursor.fetchone() is not None

    def close_connection(self):
        if self.farmax_conn:
            self.farmax_conn.close()
            self.farmax_conn = None

def filter_repeated_values(array):
    unique_values = {}
    filtered_array = []
    for tup in array:
        first_value = tup[0]
        if first_value not in unique_values:
            unique_values[first_value] = True
            filtered_array.append(tup)
    return filtered_array