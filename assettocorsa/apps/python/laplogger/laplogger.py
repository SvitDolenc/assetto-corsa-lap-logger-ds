import sys
import ac
import acsys
import os
import json
import urllib.request
# -----------------------------------------
# Constants
# -----------------------------------------

# The name of the custom HUD window displayed when this app is active.
APP_NAME = "Lap Logger"
# Because the script is run from the context of the main .exe we need to point to provide a relative path to this script.
LOG_DIR = "apps/python/laplogger/logs"

LAP_LOG_DIR = "apps/python/laplogger/laplogs"

API_URL = "https://webhook.site/b844bb26-1c29-4d39-8c5c-c3a1527af193"


# -----------------------------------------
# Variables
# -----------------------------------------

active = False

appWindow = None
logFile = None

lblLapCount = None
lblBestLap = None
lblLastLap = None
lblCurrentTime = None

lapCount = 0
bestLap = 0
lastLap = 0

lastLapInvalidated = False

username = ""

# -----------------------------------------
# Asseto Corsa Events
# -----------------------------------------

def acMain(ac_version):

	log("Starting {}".format(APP_NAME))

	global appWindow
	appWindow = ac.newApp(APP_NAME)
	ac.setSize(appWindow, 400, 250)

	# TODO Get this working
	#ac.addOnAppActivatedListener(appWindow, onAppActivated)
	#ac.addOnAppDismissedListener(appWindow, onAppDismissed)

	global lblLapCount
	lblLapCount = ac.addLabel(appWindow, "")
	ac.setPosition(lblLapCount, 3, 30)

	global lblBestLap
	lblBestLap = ac.addLabel(appWindow, "")
	ac.setPosition(lblBestLap, 3, 60)

	global lblLastLap
	lblLastLap = ac.addLabel(appWindow, "")
	ac.setPosition(lblLastLap, 3, 90)

	global lblCurrentTime
	lblCurrentTime = ac.addLabel(appWindow, "")
	ac.setPosition(lblCurrentTime, 3, 120)


	global button
	button = ac.addButton(appWindow, "Submit best lap")
	ac.setPosition(button, 3, 150)
	ac.setSize(button, 150, 50)

	ac.addOnClickedListener(button, sendLapData)

	global submitedLap
	submitedLap = ac.addLabel(appWindow, "")
	ac.setPosition(submitedLap, 3, 200)

	openLog()

	return APP_NAME


def acUpdate(deltaT):

	# if (not active):
		# return

	updateState()
	refreshUI()

def acShutdown():
	# TODO Save lap logs
	closeLog()


# -----------------------------------------
# Helper Functions
# -----------------------------------------

def log(message, level = "INFO"):
	'''Logs a message to the py_log with the (optional) specified level tag.'''
	ac.log("laplogger [{}]: {}".format(level, message))

def getFormattedLapTime(lapTime):
	'''Returns a lap time string formatted for display.'''

	if (not lapTime > 0):
		return "--:--:--"

	minutes = int(lapTime/1000/60)
	seconds = int((lapTime/1000)%60)
	millis = lapTime - (int((lapTime/1000))*1000)

	return "{}:{:02d}:{:03d}".format(minutes, seconds, millis)

def updateState():
	'''Updates the state of all variables required for logging.'''

	global lastLapInvalidated

	# Not working
	if ac.getCarState(0, acsys.CS.LapInvalidated) != 0:
		lastLapInvalidated = True

	global lapCount
	currentLap = ac.getCarState(0, acsys.CS.LapCount)
	if (lapCount < currentLap):
		lapCount = currentLap
		writeLogEntry()

		lastLapInvalidated = False


def refreshUI():
	'''Updates the state of the UI to reflect the latest data.'''

	global lblLapCount, lapCount
	ac.setText(lblLapCount, "Laps: {}".format(lapCount))

	global lblBestLap, bestLap
	bestLap = ac.getCarState(0, acsys.CS.BestLap)
	ac.setText(lblBestLap, "Best: {}".format(getFormattedLapTime(bestLap)))

	global lblLastLap, lastLap
	lastLap = ac.getCarState(0, acsys.CS.LastLap)
	ac.setText(lblLastLap, "Last: {}".format(getFormattedLapTime(lastLap)))

	global lblCurrentTime
	ac.setText(lblCurrentTime, "Time: {}".format(getFormattedLapTime(ac.getCarState(0, acsys.CS.LapTime))))

	# TODO
	# Personal best
	# Graph


# -----------------------------------------
# Logging
# -----------------------------------------

def openLog():

	# Create a log name based on the curent vehicle-track combination
	LOG_NAME = "{}-{}-{}.acl".format(ac.getCarName(0), ac.getTrackName(0), ac.getTrackConfiguration(0))

	# TODO If no track configration is available, write "default"
	# TODO Condider creating a spacer between log entries from different sessions.

	if not os.path.exists(LOG_DIR):
		os.mkdir(LOG_DIR)

	shouldInit = not os.path.exists("{}/{}".format(LOG_DIR, LOG_NAME))

	global logFile
	logFile = open("{}/{}".format(LOG_DIR, LOG_NAME), "a+")

	if shouldInit:
		initLog()

def openLapLog():
	LAP_LOG_NAME = "{}-{}-{}.json".format(ac.getCarName(0), ac.getTrackName(0), ac.getTrackConfiguration(0))
	
	if not os.path.exists(LAP_LOG_DIR):
			os.mkdir(LAP_LOG_DIR)

	global LaplogFile
	LaplogFile = open("{}/{}".format(LAP_LOG_DIR, LAP_LOG_NAME), "a+")


def initLog():
	'''Initialises the log file with important information regarding this log.'''
	carNameLine =		"car: {}".format(ac.getCarName(0))
	trackNameLine =		"track: {}".format(ac.getTrackName(0))
	trackConfigLine =	"config: {}".format(ac.getTrackConfiguration(0))

	logFile.write("{}\n{}\n{}\n\n".format(carNameLine, trackNameLine, trackConfigLine))

def writeLogEntry():
	'''Writes a new log entry to the log using the current state information.'''
	global logFile
	global user
	lapData = {
		"lap" : lapCount,
		"time" : ac.getCarState(0, acsys.CS.LastLap),
		"invalidated" : lastLapInvalidated,
		"splits" : ac.getLastSplits(0),
	}

	#runLogUploader(lapData)
	# Run logger uploader
	#
	logFile.write("{}\n".format(lapData))


def sendLapData(one,two):
    global bestLap, LaplogFile, bestLap
    #openLapLog()
    lapData = {
		"car" : ac.getCarName(0),
		"track" : ac.getTrackName(0),
		"config" : ac.getTrackConfiguration(0),
		"lap" : lapCount,
		"bestLapTime" : bestLap,
	}
    send(lapData)

def send(item):
		global submitedLap, bestLap
		request = urllib.request.Request(
            url=API_URL,
            data=json.dumps(item).encode('ascii'),
            method='POST',
            headers={"Content-Type": "application/json"}
        )
		with urllib.request.urlopen(request) as transaction:
			if transaction.status != 200:
				log("Failed to send lap data to server", "ERROR")
			ac.setText(submitedLap, "Time submited: {}".format(getFormattedLapTime(bestLap)))


def closeLog():
	global logFile
	logFile.close()

# -----------------------------------------
# Event Handlers
# -----------------------------------------

def onAppDismissed():
	ac.console("LapLogger Dismissed")
	active = False
	log("Dismissed")

def onAppActivated():
	ac.console("LapLogger Activated")
	active = True
	log("Activated")
