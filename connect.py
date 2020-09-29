'''
    connect.py

    Establishes a connection from FS2020 to the FltPlan Go app.
'''
import socket
import logging
import sys
import threading
from math import *

from SimConnect import *
from SimConnect.Enum import *

XPLANE_PORT = 49002
REFRESH_TIME = 0.5

RUNNING = True

print("")
print("--- MSFS 2020 -> FltPlan Go ---")

receivers = []
numIPs = len(sys.argv)-1
if numIPs == 0:
    sys.exit("Must specify the IP address of the FltPlan Go app!")
else:
    for i in range(numIPs):
        addr = sys.argv[i+1]
        receivers.append((addr, XPLANE_PORT))
        print("Connecting to " + addr + "...")

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.info("START")

# connect to MSFS
sm = SimConnect()
aq = AircraftRequests(sm, _time=0)

def fatalError(msg):
    print(msg)
    RUNNING = False
    sm.exit()

# Create the UDP socket to communicate with FltPlan Go
try:
    fpgSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error as msg:
    fatalError(msg)

def sendToFltplan(msg):
    packet = bytes(msg,'utf-8')
    for dest in receivers:
        try:
            fpgSock.sendto(packet, dest)
        except socket.error as msg:
            fatalError(msg)

def numFormat(num):
    return str(round(num,5))

def outsideRange(val, small, big):
    return (val < small) or (val > big)

# Key, minimum range, maximum range
simVarKeys = [
    ['PLANE_LATITUDE',-90,90],
    ['PLANE_LONGITUDE',-180,180],
    ['PLANE_ALTITUDE',-1360, 99999],
    ['PLANE_HEADING_DEGREES_TRUE',-6.283185,6.283185],
    ['GROUND_VELOCITY',0,800],
    ['PLANE_PITCH_DEGREES',-6.283185,6.283185],
    ['PLANE_BANK_DEGREES',-6.283185,6.283185] ]

simvars = {}
for k in simVarKeys:
    key, minRange, maxRange = k[0],k[1],k[2]
    sv = aq.find(key)
    if sv != None:
        sv.cachedVal = 0
        sv.minRange = minRange
        sv.maxRange = maxRange
        simvars[key] = sv
    else:
        fatalError("Can't access sim variable: " + key)

def getSimvar(key):
    sv = simvars[key]
    try:
        val = sv.value
    except:
        fatalError("Can't refresh sim variable: " + key)
    if outsideRange(val, sv.minRange, sv.maxRange):
        # if failed to update, use previously cached value
        val = sv.cachedVal
    sv.cachedVal = val
    return val

def queueTimer(t):
    if RUNNING and not sm.quit:
        vT = threading.Timer(t, refreshVars)
        vT.start()
        return vT
    return None

def refreshVars():
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

    # Continue to refresh if still running
    if queueTimer(REFRESH_TIME) == None:
        sm.exit()

# Start refreshing on a thread
queueTimer(REFRESH_TIME)
if RUNNING:
    input("Press Return to stop.")
RUNNING = False