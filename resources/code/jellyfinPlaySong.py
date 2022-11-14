#!/usr/bin/python3
import time
import os
import requests
import json
import mpv

def getSongDetails(userid,itemid):
  # Send get request to AlbumArtists API endpoint on the Jellyfin server with authentication
  get = requests.get(jellyfinurl+"/Users/"+userid+"/Items/" + itemid, headers = headers)
  song = json.loads(get.text)
  # add the values to a list
  songInfo = {"Name" : song["Name"], "AlbumArtist" : song["AlbumArtist"]}
  return songInfo

tmpDir = "/dev/shm/tmpassistant/"
jellyfinurl, jellyfinauth, userid, deviceid, playsessionid = "https://", "", "", "123", "323235546"

itemid = open(tmpDir + "jellyfinPlay", "r").read()

if os.path.exists(tmpDir + "jellyfinStop"):
  os.remove(tmpDir + "jellyfinStop")
if os.path.exists(tmpDir + "jellyfinPause"):
  os.remove(tmpDir + "jellyfinPause")
if os.path.exists(tmpDir + "jellyfinResume"):
  os.remove(tmpDir + "jellyfinResume")
if os.path.exists(tmpDir + "jellyfinSkipSong"):
  os.remove(tmpDir + "jellyfinSkipSong")
if os.path.exists(tmpDir + "jellyfinPlay"):
  os.remove(tmpDir + "jellyfinPlay")

player = mpv.MPV()
player.play(jellyfinurl + '/Audio/' + itemid + '/universal?UserId=' + userid + '&DeviceId=' + deviceid + '&MaxStreamingBitrate=140000000&api_key=' + jellyfinauth + '&PlaySessionId=' + playsessionid + '&StartTimeTicks=0')

time.sleep(2)

while player.percent_pos < 100:
  if os.path.exists(tmpDir + "jellyfinStop") or os.path.exists(tmpDir + "jellyfinSkipSong"):
    player.quit()
    break
  if os.path.exists(tmpDir + "jellyfinPause"):
    player.pause = True
    os.remove(tmpDir + "jellyfinPause")
  if os.path.exists(tmpDir + "jellyfinResume"):
    player.pause = False
    os.remove(tmpDir + "jellyfinResume")
  time.sleep(1)

if os.path.exists(tmpDir + "jellyfinStop"):
  os.remove(tmpDir + "jellyfinStop")
if os.path.exists(tmpDir + "jellyfinPause"):
  os.remove(tmpDir + "jellyfinPause")
if os.path.exists(tmpDir + "jellyfinResume"):
  os.remove(tmpDir + "jellyfinResume")
if os.path.exists(tmpDir + "songInfoFile"):
  os.remove(tmpDir + "songInfoFile")
if os.path.exists(tmpDir + "currentMedia"):
  os.remove(tmpDir + "currentMedia")
if os.path.exists(tmpDir + "jellyfinSkipSong"):
  os.remove(tmpDir + "jellyfinSkipSong")
