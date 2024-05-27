from PyQt5.QtCore import QThread, pyqtSignal
from utils.sqlite_manager import SQLiteManager
from utils.farmax import Farmax
from utils.velide import Velide
from utils.logger import Logger
import asyncio
from datetime import datetime, timedelta
import sys
import os

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

DB_NAME = os.path.join(BUNDLE_DIR, "resources", "vel2farmax.db")

class IntegrationWorker(QThread):
    end = pyqtSignal()

    def __init__(self, farmax_conn: Farmax, velide: Velide, logger: Logger):
        super().__init__()
        self.farmax_conn = farmax_conn
        self.velide = velide
        self.logger = logger

    def run(self):
        self.sqlite = SQLiteManager(DB_NAME)
        self.sqlite.connect()

        latest_sale = self.sqlite.getLatestSale()
        latest_sale_created_at = None if latest_sale is None else datetime.fromisoformat(latest_sale[4])

        current_date = datetime.now()
        # Set the time to midnight (00:00:00)
        start_of_day = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        search_after_time = start_of_day if latest_sale is None or latest_sale_created_at < start_of_day else latest_sale_created_at

        changes = self.farmax_conn.fetchChangesAfterTime(search_after_time)

        asyncio.run(self.handleInsertChanges(changes))
        asyncio.run(self.handleDeleteChanges(changes))
        asyncio.run(self.handleRouteStarts())
        asyncio.run(self.handleRouteEnds())

        self.sqlite.close_connection()
        self.sqlite = None
        self.end.emit()

    async def handleInsertChanges(self, changes):
        insert_changes = tuple(change for change in changes if change[2] == "INSERT")
        if len(insert_changes) == 0:
            return

        # Not all "insert changes" should be added, since some are already in route or concluded
        deliveries_to_insert = self.farmax_conn.fetchDeliveriesByIds(tuple(change[1] for change in insert_changes))
        if len(deliveries_to_insert) == 0:
            return
        # Format data to send to Velide
        sales_info_to_insert = self.farmax_conn.getSalesInfo(deliveries_to_insert)

        # Add deliveries to velide
        for sale_info in sales_info_to_insert:
            vel_delivery = await self.velide.addDelivery(sale_info)
            self.sqlite.insert_data("Deliveries", (vel_delivery["id"], sale_info["cd_venda"], None, 0, datetime.now().isoformat()))
            self.logger.info(f"Nova entrega adicionada ao Velide: {vel_delivery["location"]["properties"]["name"] if vel_delivery["location"]["properties"]["name"] is not None else "Endereço Indefinido"}")
    
    async def handleDeleteChanges(self, changes):
        delete_changes = tuple(change for change in changes if change[2] == "DELETE")
        if len(delete_changes) == 0:
            return

        # TODO: Check if it is not done
        deliveries_to_delete = self.sqlite.get_data_in("Deliveries", "farmax_id", [change[1] for change in delete_changes])
        if len(deliveries_to_delete) == 0:
            return
        
        # Delete deliveries in Velide
        for delivery_to_delete in deliveries_to_delete:
            if delivery_to_delete[2] is not None:
                self.logger.error(f"Entrega excluída no Farmax não pode ser removida no Velide porque está em rota (Venda {delivery_to_delete[1]}).")
                self.sqlite.delete_where("Deliveries", [("farmax_id", delivery_to_delete[1])])
                continue

            vel_delivery = await self.velide.deleteDelivery(delivery_to_delete[0])
            if not vel_delivery:
                continue

            self.sqlite.delete_where("Deliveries", [("id", vel_delivery["id"])])
            self.logger.info(f"Entrega deletada: {vel_delivery["location"]["properties"]["name"] if vel_delivery["location"]["properties"]["name"] is not None else "Endereço Indefinido"}")

    async def handleRouteStarts(self):
        current_date = datetime.now()
        day_before = current_date - timedelta(hours=24)
        deliveries = await self.velide.getDeliveries(day_before.timestamp(), current_date.timestamp())
        deliveries_in_route = [delivery for delivery in deliveries 
                               if "route" in delivery 
                               and delivery["route"] is not None
                               and (
                                   ("endedAt" in delivery and delivery["endedAt"] is None) 
                                   or not "endedAt" in delivery
                                ) 
                               and "deliverymanId" in delivery["route"]
                               and delivery["route"]["deliverymanId"] is not None]
        
        deliveries_from_integration_not_in_route = self.sqlite.get_data_where_multi("Deliveries", [("done", 0)], is_null=["deliveryman_id"])

        # Used for logging new route.
        new_deliverymen_in_route = list()

        for delivery in deliveries_from_integration_not_in_route:
            delivery_from_velide = next((vel_delivery for vel_delivery in deliveries_in_route if vel_delivery["id"] == delivery[0]), None)
            if delivery_from_velide is not None:
                cd_venda = delivery[1]
                left_at = datetime.fromtimestamp(delivery_from_velide["route"]["startedAt"] / 1000.0)
                deliveryman = self.sqlite.get_data_where("Deliverymen", "id", (delivery_from_velide["route"]["deliverymanId"],))
                cd_entregador = deliveryman[1]

                # Updates data in Farmax
                self.farmax_conn.updateDeliveryAsInRoute(cd_venda, cd_entregador, left_at.time())
                # Updates data locally in SQLite 
                self.sqlite.update_data("Deliveries", (("deliveryman_id", deliveryman[0]),), (("farmax_id", cd_venda),))

                # Used for logging only
                if deliveryman[2] not in [new_deliveryman_in_route[0] for new_deliveryman_in_route in new_deliverymen_in_route]:
                    new_deliverymen_in_route.append((deliveryman[2], (delivery_from_velide,)))
                else:
                    for i, (name, deliveries) in enumerate(new_deliverymen_in_route):
                        if name == deliveryman[2]:
                            new_deliverymen_in_route[i] = (name, (*deliveries, delivery_from_velide))
        
        for deliveryman in new_deliverymen_in_route:
            deliveries_names = [delivery["location"]["properties"]["name"] if delivery["location"]["properties"]["name"] is not None else "Endereço Indefinido" for delivery in deliveryman[1]]
            self.logger.info(f"Rota iniciada para {deliveryman[0]} contendo as entregas: {", ".join(deliveries_names)}")

    async def handleRouteEnds(self):
        current_date = datetime.now()
        day_before = current_date - timedelta(hours=24)
        deliveries = await self.velide.getDeliveries(day_before.timestamp(), current_date.timestamp())
        deliveries_done = [delivery for delivery in deliveries 
                               if "endedAt" in delivery 
                               and delivery["endedAt"] is not None]
        
        deliveries_from_integration_in_route = self.sqlite.get_data_where_multi("Deliveries", (("done", 0),), not_null=["deliveryman_id"])

        # Used for logging the deliverymen names
        new_route_ended = list()

        for delivery in deliveries_from_integration_in_route:
            delivery_from_velide = next((vel_delivery for vel_delivery in deliveries_done if vel_delivery["id"] == delivery[0]), None)
            if delivery_from_velide is not None:
                cd_venda = delivery[1]
                arrived_at = datetime.fromtimestamp(delivery_from_velide["endedAt"] / 1000.0)
                # Updates data in Farmax
                self.farmax_conn.updateDeliveryAsDone(cd_venda, arrived_at.time())
                # Updates data locally in SQLite 
                self.sqlite.update_data("Deliveries", (("done", 1),), (("farmax_id", cd_venda),))

                deliveryman = self.sqlite.get_data_where("Deliverymen", "id", (delivery_from_velide["route"]["deliverymanId"],))

                # Used for logging only
                if deliveryman[2] not in new_route_ended:
                    new_route_ended.append(deliveryman[2])

        for deliveryman in new_route_ended:
            self.logger.info(f"O entregador {deliveryman} retornou para loja.")
