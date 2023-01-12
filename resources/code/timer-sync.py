import asyncio
import websockets
import json
from time import sleep
from subprocess import call
import os

webserver_url = 'ws://localhost:4762/timer'
working_dir = "/dev/shm/tmpassistant/"
timer_info_file = working_dir + "timer_sync_info.json"
timer_stop_file = working_dir + "timer_stop"
timer_start_file = working_dir + "timer_start"
timer_finished_audio = "/home/assistant-main-node/sync-conveniences/timerchime.wav"

source = "Blueberry"

async def get_timer_info():
    async with websockets.connect(webserver_url) as websocket:
        #Blank timer stats initialise at start
        timer = {"remaining_length" : 0, "dismissed" : True}
        #Constantly running loop, do everything within all of the time
        while True:
            #If stop file exists, send websocket message to stop the timer and delete the file
            if os.path.exists(timer_stop_file):
                os.remove(timer_stop_file)
                await websocket.send(json.dumps({"stop" : "please"}))
            #If start file exists, send websocket message with the info from the start file
            if os.path.exists(timer_start_file):
                start_info = json.load(open(timer_start_file, 'r'))
                os.remove(timer_start_file)
                start_info_dict = {"length" : start_info["length"], "source" : source}
                await websocket.send(json.dumps(start_info_dict))

            #Store the state of the previous message, but don't fail if no message came through on this loop
            try:
                #Wait for a message from websocket for a second, timeout WITHOUT FAILING otherwise
                timer = json.loads(await asyncio.wait_for(websocket.recv(), 0.3))
            except:
                pass
            #Save timer info to external file
            timer_file = open(timer_info_file, 'w')
            timer_file.write(json.dumps(timer))
            timer_file.close()
            #If timer is at 0, but not dismissed, play sound.
            if timer["remaining_length"] == 0:
                if timer["dismissed"] == False:
                    call(["aplay", timer_finished_audio])

# This allows the script to reconnect if the websocket is not open. Tries every 2 seconds if not open.
while True:
    try:
        asyncio.run(get_timer_info())
    except OSError:
        sleep(2)