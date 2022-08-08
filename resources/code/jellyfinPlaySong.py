#!/usr/bin/python3
import miniaudio
import time
import os

tmpDir = "/dev/shm/tmpassistant/"
jellyfinurl, jellyfinauth, userid = "url", "auth", "uid"
headers = {"X-Emby-Token": jellyfinauth,}


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

def getSongDetails(userid,itemid):
  songInfo = [[],["Name", "Album Artist", "Album", "Release Date (in silly YYYY-MM-DD format)", "Favourite?", "Genre", "Play Count", "FileType", "Bitrate", "Bit depth", "Item ID", "Album Art ID"]]

  # Send get request to AlbumArtists API endpoint on the Jellyfin server with authentication
  get = requests.get(jellyfinurl+"/Users/"+userid+"/Items/" + itemid, headers = headers)
  song = json.loads(get.text)
  # add the values to a list
  songInfo[0].append(song["Name"])
  songInfo[0].append(song["AlbumArtist"])
  songInfo[0].append(song["Album"])
  songInfo[0].append(song["PremiereDate"].split("-"))

  # Remove Extraneous Info From Date Field
  songInfo[0][3][2] = songInfo[0][3][2][:2]

  songInfo[0].append(song["UserData"]["IsFavorite"])
  songInfo[0].append(song["GenreItems"][0]["Name"])
  songInfo[0].append(song["UserData"]["PlayCount"])
  songInfo[0].append(song["MediaStreams"][0]["Codec"])
  songInfo[0].append(song["MediaStreams"][0]["BitRate"])
  songInfo[0].append(song["MediaStreams"][0]["BitDepth"])
  songInfo[0].append(song["Id"])
  songInfo[0].append(song["AlbumPrimaryImageTag"])
  return songInfo
  
  
stream = miniaudio.stream_file(tmpDir + "currentMedia")
device = miniaudio.PlaybackDevice()
device.start(stream)
itemid = open(tmpDir + "jellyfinPlay", "r").read()

songInfo = getSongDetails(userid,itemid)
songInfoFile = open(tmpDir + "songInfoFile", "w")
songInfoFile.write(str(songInfo[0]))
                  
#Get duration with very long line of code
duration = int(miniaudio.flac_get_info((open(tmpDir + "currentMedia", "rb")).read()).duration)

progress = 0

while True:
  if os.path.exists(tmpDir + "jellyfinStop"):
    device.close()
    os.remove(tmpDir + "jellyfinStop")
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
    os.remove(tmpDir + "songInfoFile")
    break
  time.sleep(1)
  if not os.path.exists(tmpDir + "jellyfinIsPaused"):
    progress += 1
