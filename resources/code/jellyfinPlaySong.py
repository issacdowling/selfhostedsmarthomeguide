#!/usr/bin/python3
import miniaudio
import time
import os
import requests
import json

def getSongDetails(userid,itemid):
  songInfo = [[],["Name", "Album Artist"]]
  # Send get request to AlbumArtists API endpoint on the Jellyfin server with authentication
  get = requests.get(jellyfinurl+"/Users/"+userid+"/Items/" + itemid, headers = headers)
  song = json.loads(get.text)
  # add the values to a list
  songInfo[0].append(song["Name"])
  songInfo[0].append(song["AlbumArtist"])
  return songInfo

tmpDir = "/dev/shm/tmpassistant/"
jellyfinurl, jellyfinauth, userid = "https://", "auth", "userid"
headers = {"X-Emby-Token": jellyfinauth,}

if not os.path.exists(tmpDir + "currentMedia"):
  exit("No media to play")

if os.path.exists(tmpDir + "songInfoFile"):
  os.remove(tmpDir + "songInfoFile")
itemid = open(tmpDir + "jellyfinPlay", "r").read()
songInfo = getSongDetails(userid,itemid)
songInfoFile = open(tmpDir + "songInfoFile", "w")
songInfoFile.write(str(songInfo[0]))
songInfoFile.close()

if os.path.exists(tmpDir + "jellyfinStop"):
  os.remove(tmpDir + "jellyfinStop")
if os.path.exists(tmpDir + "jellyfinPause"):
  os.remove(tmpDir + "jellyfinPause")
if os.path.exists(tmpDir + "jellyfinResume"):
  os.remove(tmpDir + "jellyfinResume")
if os.path.exists(tmpDir + "jellyfinIsPaused"):
  os.remove(tmpDir + "jellyfinIsPaused")
if os.path.exists(tmpDir + "jellyfinSkipSong"):
  os.remove(tmpDir + "jellyfinSkipSong")
if os.path.exists(tmpDir + "jellyfinPlay"):
  os.remove(tmpDir + "jellyfinPlay")

try:
  stream = miniaudio.stream_file(tmpDir + "currentMedia")
  # Attempt to get duration for all 4 supported file types. If ALL fail, log it.
  try:
    duration = int(miniaudio.flac_get_info((open(tmpDir + "currentMedia", "rb")).read()).duration)
  except:
    try:
      duration = int(miniaudio.mp3_get_info((open(tmpDir + "currentMedia", "rb")).read()).duration)
    except:
      try:
        duration = int(miniaudio.wav_get_info((open(tmpDir + "currentMedia", "rb")).read()).duration)
      except:
        try:
          duration = int(miniaudio.vorbis_get_info((open(tmpDir + "currentMedia", "rb")).read()).duration)
        except:
          print("Unable to get duration info")
except:
  print("Error parsing currentMedia")

try:
  device = miniaudio.PlaybackDevice()
  device.start(stream)
except:
  print("Erorr starting playback with miniaudio")
  duration = -1

progress = 0

while True:
  if os.path.exists(tmpDir + "jellyfinStop") or os.path.exists(tmpDir + "jellyfinSkipSong"):
    device.close()
    break
  if os.path.exists(tmpDir + "jellyfinPause"):
    device.stop()
    os.remove(tmpDir + "jellyfinPause")
    open(tmpDir + "jellyfinIsPaused", "w")
  if os.path.exists(tmpDir + "jellyfinResume"):
    device.start(stream)
    os.remove(tmpDir + "jellyfinResume")
    os.remove(tmpDir + "jellyfinIsPaused")
  if progress >= duration:
    device.close()
    break
  time.sleep(1)
  if not os.path.exists(tmpDir + "jellyfinIsPaused"):
    progress += 1

if os.path.exists(tmpDir + "jellyfinStop"):
  os.remove(tmpDir + "jellyfinStop")
if os.path.exists(tmpDir + "jellyfinPause"):
  os.remove(tmpDir + "jellyfinPause")
if os.path.exists(tmpDir + "jellyfinResume"):
  os.remove(tmpDir + "jellyfinResume")
if os.path.exists(tmpDir + "jellyfinIsPaused"):
  os.remove(tmpDir + "jellyfinIsPaused")
if os.path.exists(tmpDir + "songInfoFile"):
  os.remove(tmpDir + "songInfoFile")
if os.path.exists(tmpDir + "currentMedia"):
  os.remove(tmpDir + "currentMedia")
if os.path.exists(tmpDir + "jellyfinSkipSong"):
  os.remove(tmpDir + "jellyfinSkipSong")
