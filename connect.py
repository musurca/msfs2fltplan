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
UPDATE_RATE = 5     # in Hz
REFRESH_TIME = 1 / UPDATE_RATE

# List of addresses on the network that will receive updates
receivers = []

# The network socket
fpgSock = None

# Will send an XGPS message when this equals 0
shouldUpdatePos = 0

# Sim var key, minimum range, maximum range
simVarKeys = [
    ['PLANE_LATITUDE',-90,90],
    ['PLANE_LONGITUDE',-180,180],
    ['PLANE_ALTITUDE',-1360, 99999],
    ['PLANE_HEADING_DEGREES_TRUE',-6.283185,6.283185],
    ['GROUND_VELOCITY',0,800],
    ['PLANE_PITCH_DEGREES',-6.283185,6.283185],
    ['PLANE_BANK_DEGREES',-6.283185,6.283185] ]

# List of registered simvars
simvars = {}

def fatalError(msg):
    print(msg)
    RUNNING = False
    sm.exit()

def sendToFltplan(msg):
    packet = bytes(msg,'utf-8')
    for dest in receivers:
        try:
            fpgSock.sendto(packet, dest)
        except socket.error as msg:
            fatalError(msg)

def numFormat(num,r=5):
    return str(round(num,r))

def outsideRange(val, small, big):
    return (val < small) or (val > big)

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

def nextUpdate():
    global RUNNING

    if RUNNING and not sm.quit:
        vT = threading.Timer(REFRESH_TIME, refreshVars)
        vT.start()
        return vT
    return None

def refreshVars():
    global shouldUpdatePos

    # Get crucial simvars via SimConnect
    if shouldUpdatePos == 0:
        lat = getSimvar('PLANE_LATITUDE')
        lon = getSimvar('PLANE_LONGITUDE')
        alt = getSimvar('PLANE_ALTITUDE') * 0.3048          # ft ASL -> MSL

    hdg = degrees( getSimvar('PLANE_HEADING_DEGREES_TRUE') )
    pitch = -degrees( getSimvar('PLANE_PITCH_DEGREES') )    # X-Plane flips the sign
    bank = -degrees( getSimvar('PLANE_BANK_DEGREES') )      
    spd = getSimvar('GROUND_VELOCITY') / 1.945              # knots -> m/s

    # Send pseudo-NMEA sentences masquerading as X-Plane.
    # X-Plane uses a modified version of the ForeFlight protocol: 
    # https://www.foreflight.com/support/network-gps/

    #b'XGPS1,-73.878280,40.782172,2.2004,122.2988,0.0692'
    if shouldUpdatePos == 0:
        # XGPS messages sent once per second
        sendToFltplan( "XGPS1," + numFormat(lon) + "," + numFormat(lat) + "," + numFormat(alt,2) + "," + numFormat(hdg,2) + "," + numFormat(spd,2) )

    #b'XATT1,122.3,-6.1,0.3,-0.0014,0.0629,-0.0003,-0.0,0.1,-0.0,-0.02,1.86,0.21'
    # XATT messages sent at the current update rate (per protocol, anywhere from 4-10 Hz)
    sendToFltplan( "XATT1," + numFormat(hdg,2) + "," + numFormat(pitch,2) + "," + numFormat(bank,2) + ",0,0,0," + numFormat(-spd,2)+","+numFormat(pitch,2)+",0,0,0,0" )

    shouldUpdatePos = ( shouldUpdatePos + 1 ) % UPDATE_RATE

    # Continue to refresh if still running
    if nextUpdate() == None:
        sm.exit()

# Program begins here
RUNNING = True

print("")
print("--- FltPlan Go Connect for MSFS 2020 ---")

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

# Create the UDP socket to communicate with FltPlan Go
try:
    fpgSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error as msg:
    fatalError(msg)

# Register simvars for updates
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

# Start refreshing on a thread
nextUpdate()
if RUNNING:
    input("Press Return to stop.\n")

# Flag the thread to stop when done
RUNNING = False