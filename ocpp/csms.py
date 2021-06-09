import asyncio
import logging

import route as route
import websockets
from datetime import datetime

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.v16 import call

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    @on('BootNotification')
    async def on_boot_notification(self, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status= "Accepted"
        )
    #my business logic
    @on('Heartbeat')
    async def on_heartbeat(self):
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        )

    @on('Authorize')
    async def on_authorize(self, **kwargs): #add **kwargs
        #check here if customer is on list??? Can i do this using sim? Maybes should avoid
        return call_result.AuthorizePayload(
            id_tag_info= {
        "expiryDate": "msdfg",
        "parentIdTag": "Mustang",
        "status": "Accepted"
})

    @on("StartTransaction")
    async def on_start_transaction(self, **kwargs):
        #checks here i.e is authroized? / is already started?
        return call_result.StartTransactionPayload(
            transaction_id = 2, # adjust number based on how many transactions there have been
            id_tag_info= {
        "expiryDate": "msdfg",
        "parentIdTag": "Mustang",
        "status": "Accepted"
})

    @on("StopTransaction")
    async def on_stop_transaction(self, **kwargs):
        #check here if I can stop? Make sure it is started in first place
        return call_result.StopTransactionPayload(
            id_tag_info={
                "expiryDate": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
                "parentIdTag": "Mustang",
                "status": "Accepted"}
        )

    @on("MeterValues")
    async def on_meter_values(self, **kwargs):
        #do something with meter values here
        return call_result.MeterValuesPayload()

    @on("StatusNotification")
    async def on_status_notification(self, **kwargs):
        return call_result.StatusNotificationPayload()

    @on("DataTransfer")
    async def on_data_transfer(self, **kwargs):
        return call_result.DataTransferPayload(
            #this works both ways, charge point is asking for csms status
            status= 'Accepted', # the CSMS' status
            data = 'Some data here??'
        )

async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers[
            'Sec-WebSocket-Protocol']
    except KeyError:
        logging.info("Client hasn't requested any Subprotocol. "
                 "Closing Connection")
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()

    charge_point_id = path.strip('/')
    cp = ChargePoint(charge_point_id, websocket)
    try:
        await cp.start()
        print('awaited')

    except Exception as e: print(e)
    print('Disconnected ' + cp.id)



async def main():
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp1.6']
    )
    logging.info("WebSocket Server Started")

    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())