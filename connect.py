'''
    connect.py

    Establishes a connection from FS2020 to the FltPlan Go app.
'''
import socket
import logging
import sys
from time import sleep
from math import degrees

from SimConnect import *
from SimConnect.Enum import *

XPLANE_PORT = 49002

print("")
print("--- MSFS 2020 -> FltPlan Go ---")

if len(sys.argv) == 1:
    sys.exit("Must specify the IP address of the FltPlan Go app!")
else:
    ipAddr = sys.argv[1]
    FLTPLAN_ADDR = (ipAddr, XPLANE_PORT)

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.info("START")

# connect to MSFS
sm = SimConnect()
aq = AircraftRequests(sm)

# Create the UDP socket to communicate with FltPlan Go
try:
    fpgSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error as msg:
    print(msg)
    sys.exit()

def sendToFltplan(msg):
    try:
        fpgSock.sendto(bytes(msg,'utf-8'), FLTPLAN_ADDR)
    except socket.error as msg:
        print(msg)
        sys.exit()

def numFormat(num):
    return str(round(num,5))

def getSimvar(key):
    return aq.PositionandSpeedData.get(key)

while not sm.quit:
    # Get crucial simvars via SimConnect
    lat = getSimvar('PLANE_LATITUDE')
    lon = getSimvar('PLANE_LONGITUDE')
    alt = getSimvar('PLANE_ALTITUDE')
    hdg = getSimvar('PLANE_HEADING_DEGREES_TRUE')
    spd = getSimvar('GROUND_VELOCITY')
    pitch = getSimvar('PLANE_PITCH_DEGREES')
    bank = getSimvar('PLANE_BANK_DEGREES')
    
    # Perform unit conversions to X-Plane standard
    alt = alt * 0.3048      # feet -> meters
    hdg = degrees(hdg)      # radians -> degrees
    spd = spd / 1.945       # knots -> m/s
    pitch = degrees(pitch)
    bank = degrees(bank)

    # Send pseudo-NMEA sentences masquerading as X-Plane
    #b'XGPS1,-73.878280,40.782172,2.2004,122.2988,0.0692'
    gpsMsg = "XGPS1," + numFormat(lon) + "," + numFormat(lat) + "," + numFormat(alt) + "," + numFormat(hdg) + "," + numFormat(spd)
    #b'XATT1,122.3,-6.1,0.3,-0.0014,0.0629,-0.0003,-0.0,0.1,-0.0,-0.02,1.86,0.21'
    attMsg = "XATT1," + numFormat(hdg) + "," + numFormat(pitch) + "," + numFormat(bank) + ",0,0,0,0,0,0,0,0,0"
    
    sendToFltplan(gpsMsg)
    sendToFltplan(attMsg)

    sleep(0.5)

sm.exit()