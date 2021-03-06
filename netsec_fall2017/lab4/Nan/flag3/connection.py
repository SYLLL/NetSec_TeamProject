import playground
import asyncio
import lab3_protocol
import logging



class app(asyncio.Protocol):
    def __init__(self):
        self.transport=None
    def connection_made(self,transport):
        self.transport = transport
        self.close()
    def close(self):
        self.transport.close()
    def data_received(self,data):
        self.close()




if __name__=='__main__':
    loop = asyncio.get_event_loop()
    coro = playground.getConnector("plcs").create_playground_connection(app(),"20174.1.1337.3",1)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()

