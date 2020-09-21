from socket import *
import os
import sys
import struct
import time
import select
import binascii
ICMP_ECHO_REQUEST = 8
count = 0

def checksum(s):      
    csum = 0     
    countTo = (len(s) / 2) * 2          
    count = 0      
    while count < countTo:         
        thisVal = s[count+1] * 256 + s[count]                
        csum = csum + thisVal                 
        csum = csum & 0xffffffff                 
        count = count + 2      
    if countTo < len(s):         
        csum = csum + ord(s[len(s) - 1])         
        csum = csum & 0xffffffff               
    csum = (csum >> 16) + (csum & 0xffff)     
    csum = csum + (csum >> 16)     
    answer = ~csum     
    answer = answer & 0xffff        
    answer = answer >> 8 | (answer << 8 & 0xff00)         
    return answer  

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        #Fill in start
        #Fetch the ICMP header from the IP packet
        icmpHeader = recPacket[20:28] 
        icmpType, code, checksum, packet_id, sequence = struct.unpack("bbHHh", icmpHeader) #Unpacking packet header for sequence 
        #Windows uses a fixed identifier, which varies between Windows versions, and a sequence number that is only reset at boot time.
        length = len(recPacket) - 20    #Length of ICMP Header
        ipheader = struct.unpack('!BBHHHBBH4s4s' , recPacket[:20]) #Returns Unpacked values for IP Header
        ttl = ipheader[5] 
        address = inet_ntoa(ipheader[8]) #Convert to string format
    
        if type != 8 and packet_id == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            rtt = (timeReceived - timeSent) * 1000
            return 'Pinging {} bytes from {}: ICMP-Sequence={} TTL={} RTT={:.2f} ms'.format(length, address, sequence, ttl, rtt)
        
        #Fill in end
        timeLeft = timeLeft - howLongInSelect
        
        if timeLeft <= 0:
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum.
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
    #Convert 16-bit integers from host to network byte order.
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
    #Both LISTS and TUPLES consist of a number of objects
    #which can be referenced by their position number within the object

def doOnePing(destAddr, timeout):         
    icmp = getprotobyname("icmp") 
    #Create Socket here
    mySocket = socket(AF_INET, SOCK_RAW, icmp) 

    myID = os.getpid() & 0xFFFF  #Return the current process i     
    sendOnePing(mySocket, destAddr, myID) 
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)          

    mySocket.close()         
    return delay  

def ping(host, timeout=1):

        dest = gethostbyname(host)
        print ("\nPinging " + "'"+host+"'" + ", " + dest + " using Python " + str(count) + " times:\n")
        #Send ping requests to a server separated by approximately one second
        for i in range(0,count):
            delay = doOnePing(dest, timeout)
            print (delay)
            time.sleep(1)# one second

count= int(input('\nNo of times to Ping : '))
ping("google.com")  #North America Google.com
ping("www.marutisuzuki.com") #Asia Indian Car Manufacturer Website
ping("www.mercedes-benz.com.br") #South America Mercedez-Benz Brazil Website
ping("carwow.co.uk") #Europe Car Review Website UK