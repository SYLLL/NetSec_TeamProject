import asyncio
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING
from Peep_Packets import PEEP_Packet
from random import randint

from playground.network.common import StackingTransport,StackingProtocol,StackingProtocolFactory

class PEEP_Server(asyncio.protocols):
    def __init__(self):
        self.transport= None

    def connection_made(self, transport):
        self.transport = transport
        self._deserializer = PacketType.Deserializer()

    def data_received(self, data):

        self._deserializer.update(data)

    def connection_lost(self, exc=None):
        self.transport = None
        print("connection has lost!")


class PEEP_Server_Passthrough2(StackingProtocol):
    def __init__(self):
     #   super.__init__()
        self.transport=None

    def connection_made(self, transport):
        print("Client: start a connection")
        self.transport = transport
        htransport = StackingTransport(self.transport)
        self.higherProtocol().connection_made(htransport)

    def data_received(self, data):
        print("Client :data received")
        self.higherProtocol().data_received(data)

    def connection_lost(self, exc=None):
        print("Client : connection lost")
        self.higherProtocol().connection_lost()
        self.transport = None


class PEEP_Server_Passthrough1(StackingProtocol):
    def __init__(self):
        self.received=0
        self.transport=None
        #self._Deserializer = PacketType.Deserializer()
        self.state=0
       # super.__init__()

    def connection_made(self,transport):
        self.transport=transport
        self._Deserializer=PacketType.Deserializer()
        peername = transport.get_extra_info('peername')
        print('server(prepare)-->client(prepare):Connection from {}'.format(peername))
        self.higherProtocol().connection_made(StackingTransport(transport))

    def data_received(self,data):
        self._Deserializer=PacketType.Deserializer()
        self._Deserializer.update(data)
        for pkt in self._Deserializer.nextPackets():
            self.handle_packets(pkt)
        self.higherProtocol().data_received(data)


    def handle_packets(self,pkt):
        if isinstance(pkt,PEEP_Packet):
            typenum = pkt.Type
            if typenum == 0:
                print('server side: received SYN')
                self.handle_syn(pkt)
            elif typenum == 2:
                print('server side: received ACK')
                self.handle_ack(pkt)
            elif typenum == 3:
                print('server side: received RIP')
                self.handle_rip(pkt)
            elif typenum == 4:
                print('server side: received RIPACK')
                self.handle_ripack(pkt)
            else:
                print('server side: received UNKNOWN TYPE')
        else:
            print('server side:This packet is not the correct type')
    def handle_syn(self,pkt):
        if pkt.Checksum==0:
            print('server side: checksum of SYN is correct')
            pktback=PEEP_Packet()
            pktback.Acknowledgement=pkt.SequenceNumber+1
            pktback.SequenceNumber = randint(0,100)
            pktback.Type=1
            pktback.Checksum=0
            self.transport.write(pktback.__serialize__())
            self.state+=1
            print('server side: sent SYNACK')
        else:
            print('server side: checksum of SYN is incorrect')
            pktback=PEEP_Packet()
            pktback.Type=5
            pktback.Checksum=0
            self.transport.write(pktback.__serialize__())
            print('server side: sent RST')
            # clear buffer
            self.transport.close()

    def handle_ack(self,pkt):
        if pkt.Checksum==0:
            print('server side: checksum of ACK is correct')
            #send data
            #self.higherProtocol().data_received(data)
            self.state+=1

        else:
            print('server side: checksum of ACK is incorrect')
            pktback=PEEP_Packet()
            pktback.Type=5
            pktback.Checksum=0
            self.transport.write(pktback.__serialize__())
            self.transport.close()
            print('server side: sent RST')

    def handle_rip(self,pkt):
        if pkt.Checksum==0:
            print('server side: checksum of RIP is correct')
            pktback=PEEP_Packet()
            pktback.Acknowledgement=pkt.SequenceNumber+1
            pktback.Type=4
            pktback.Checksum=0
            self.transport.write(pktback.__serialize__())
            print('server side: sent RIPACK')
            # Sending remaining packets back
            pktback2=PEEP_Packet()
            pktback2.Acknowledgement=pkt.SequenceNumber+1
            pktback2.Type=3
            pktback2.Checksum=0
            pktback2.SequenceNumber=randint(0,100)
            self.transport.write(pktback2.__serialize__())
            print('server side: sent RIP')
        else:
            print('server side: checksum of RIP is incorrect')
            pktback=PEEP_Packet()
            pktback.Type=5
            pktback.Checksum=0
            self.transport.write(pktback.__serialize__())
            self.transport.close()
            prnt('server side: sent RST')

    def handle_ripack(self,pkt):
        if pkt.Checksum==0:
            print('server side: checksum of RIPACK is correct')
            self.transport.close()
        else:
            print('server side: checksum of RIPACK is incorrect')
            self.transport.close()

