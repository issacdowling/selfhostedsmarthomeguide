#!/usr/bin/python3
import miniaudio
import time
import os

tmpDir = "/dev/shm/tmpassistant/"

if os.path.exists(tmpDir + "jellyfinStop"):
  os.remove(tmpDir + "jellyfinStop")
if os.path.exists(tmpDir + "jellyfinPause"):
  os.remove(tmpDir + "jellyfinPause")
if os.path.exists(tmpDir + "jellyfinResume"):
  os.remove(tmpDir + "jellyfinResume")
if os.path.exists(tmpDir + "jellyfinIsPaused"):
  os.remove(tmpDir + "jellyfinIsPaused")


stream = miniaudio.stream_file(tmpDir + "currentMedia")
device = miniaudio.PlaybackDevice()
device.start(stream)

#Get duration with very long line of code
duration = int(miniaudio.flac_get_info((open("currentMedia", "rb")).read()).duration)

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
    break
  time.sleep(1)
  if not os.path.exists(tmpDir + "jellyfinIsPaused"):
    progress += 1
