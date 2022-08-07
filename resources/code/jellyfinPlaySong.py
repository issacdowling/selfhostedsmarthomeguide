import miniaudio
import time
import os

stream = miniaudio.stream_file("/dev/shm/tmpassistant/currentMedia")
device = miniaudio.PlaybackDevice()
device.start(stream)

#Get duration with very long line of code
duration = int(miniaudio.flac_get_info((open("currentMedia", "rb")).read()).duration) 

progress = 0

while True:
  if os.path.exists("/dev/shm/tmpassistant/jellyfinStop"):
    device.close()
    os.remove("/dev/shm/tmpassistant/jellyfinStop")
    break
  if os.path.exists("/dev/shm/tmpassistant/jellyfinPause"):
    device.stop()
    os.remove("/dev/shm/tmpassistant/jellyfinPause")
  if os.path.exists("/dev/shm/tmpassistant/jellyfinResume"):
    device.start(stream)
    os.remove("/dev/shm/tmpassistant/jellyfinResume")
  if progress >= duration:
    device.close()
    break
  time.sleep(1)
  progress += 1
