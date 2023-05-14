# SelfhostedSmartHomeGuide
### This is not done yet. In-progress. You assume all responsibility for if *anything* goes wrong for *any reason*.

# Table of Contents
[**Prerequisites**](README.md#prerequisites)

[**Setting up the Pi**](README.md#setting-up-the-pi)

[**Initally setting up Rhasspy**](README.md#initally-setting-up-rhasspy)

[**Making it smart**](README.md#making-it-smart)

[**Adding features (skills)**](README.md#features)

[Controlling Lights](README.md#controlling-devices)

[Basic maths](README.md#doing-basic-maths)

[Setting timers](README.md#setting-timers)

[Generic "Stop" function](README.md#generic-stop-function)

[Getting the weather](README.md#the-weather)

[Getting the time](README.md#getting-the-time-but-better)

[Getting the date](README.md#getting-the-date)

[Giving greetings](README.md#giving-greetings)

[Using as bluetooth speaker](README.md#bluetooth-audio-streaming-highly-imperfect)

[Adding natural and varied responses](README.md#natural-and-varied-responses)

[Jellyfin Music Support (beta)](README.md#jellyfin-music-support)

[Volume Controls](README.md#volume-control)

[Finding the days until a date](README.md#finding-days-until)

[Converting Units](README.md#converting-units)

# Prerequisites

## *What's this?*
A project that aims to make a self-hosted smart speaker with a reasonable amount of functionality, speed, and ease of use once complete. It won't be perfect, but it'll work. We'll use [Rhasspy](https://rhasspy.readthedocs.io/en/latest/)  to tie together all of the separate bits we need to assemble an assistant (TTS, STT, Wake Word, etc), and [Homeassistant](https://www.home-assistant.io/docs/) to interface with any smart devices. Our equivalent of an Alexa Skill would be an Intent, and whenever Rhasspy recognises one of these, it'll be passed along to a Python script to be handled. This means we can do anything Python can do, assuming we've got the patience to program it.

## What's needed
* Raspberry Pi 4

* Micro SD Card >=16GB (or other boot device, USB drives work too)

===BELOW IS FOR TESTING ONLY===

* USB Mic

* 3.5mm Speakers

# Setting Up the Pi

## Flashing the OS

### Download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/), and install/run it.

Choose OS, then **Raspberry Pi OS (other)**

![Other](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/otherOS.png)

then **Raspberry Pi OS 64-bit lite**

![64-bit-lite](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/lite64.png)

### Now, click the settings icon in the bottom right corner.

* Set hostname to whatever you want to call it. I chose assistant1
* Enable SSH with a password
* Set username and password
* Configure Wifi if you're going to use it instead of ethernet. Ethernet is more stable, but Wifi allows for more freedom in positioning.
* Scroll down, save.

![Settings page](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/settings.png)

### Choose your boot device (what you'll be keeping in the Pi, typically a MicroSD card)
![Boot device list](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/selectboot.png)

### And finally, press write, and wait for it to finish.

![Writing Media](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/writingprogress.png)

## Booting and initial install
Assuming you have a Micro-HDMI cable, you can turn on the Pi without anything inserted to ensure it boots fine. You'll likely get a screen like this.

![Boot with no device](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/bootnodevice.png)

But if - like most people - you don't own a Micro HDMI cable, that's alright. We can run *headlessly* (without a display)

### Regardless of whether you'll be connecting a keyboard and monitor to the Pi or not, make sure it's off, then insert your boot drive, and plug it in. Then, wait for one of two things:

If you've got a display connected, wait until there's a line with your username in green at the bottom of the screen, like this.

![Linux bootup scene](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/withdisplaybootup.png)

If you don't have a display connected, go to a computer on the same network as your Pi (so, if you didn't set up Wifi, connect an ethernet cable). Then, run **"terminal"** (same on Linux, Windows 11, or MacOS, but on Windows 10, run cmd). Now, type `ssh yourusername@yourhostname.local`, and replace 'yourusername' with your Pi username, and 'yourhostname' with the hostname you typed in the settings page. At first, it'll likely error out, since the Pi isn't done booting yet, but you can press the up arrow and enter to run the command again. You know you've succeeded once you see this page.
![SSH fingerprint question](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/fingerprint.png)

Type yes, enter, then type your password (which won't show up onscreen as a security measure, but it *is* still going through). 

### From here, we can run commands.

First, run
```
sudo apt update && sudo apt upgrade -y
``` 
to get up to date

### Now, set a static local IP

In your terminal, type `ip route | grep default`. Then, note down three things: the first IP, the network device, and the second IP. The IPs will likely be 192.168.x.x, but may be different. In the image, I've highlighted these things in yellow so you know where to look.

![my private IP for the Pi](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/ipdefault.png)

Now, run
```
sudo nano /etc/dhcpcd.conf
```
and navigate down to the bottom line using the arrow keys, then press enter a few times to add some lines. You should get to here:

![dhcpcd](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/dhcpcd.png)

Then, paste this in:

```
interface
static ip_address=/24
static routers=
static domain_name_servers=1.1.1.1
```

Next to interface, add a space, then the network device (either **eth0** or **wlan0**). Now, for static ip_address, type the second IP before the */24*. Finally, add the first IP from earlier directly after **static routers=**. Then, press CTRL+X, then Y, then Enter, to save and exit. Finally, run `sudo reboot` to restart. Your SSH will disconnect, and you can just keep trying to reconnect until it works to check if you're booted.

## Optimisations

### We can make our pi run better, and use less power on things we're not using.

#### Running better

The Pi can be overclocked. Run this:
```
sudo nano /boot/config.txt
```
then go down to where it says **"#uncomment to overclock the arm"**

![default boot config](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/defaultarmover.png)

Remove the **#** from the line beginning `#arm_freq`, and change the number to 1750. Add another line below the **"#uncomment to overclock the arm"** bit, and copy this in:
```
over_voltage=2
```
Then, if you're not going to be using the HDMI ports, below the `#arm_freq` line, paste this:
```
gpu_freq=0
```

If you want to put in the effort **and extra cooling**, you can tune this for better performance at the cost of more heat, however the above config should be doable by practically all Pi 4s, and remain at safe temperatures. I do **over_voltage=4**, **arm_freq=2000**, and have not had any cooling or stability issues despite running the Pi bare.

#### Using less energy

Now, to disable all LEDs on the board, go down to the section starting with `**[pi4]**` and paste what's below:
```
# Disable the power LED
dtparam=pwr_led_trigger=none
dtparam=pwr_led_activelow=off
# Disable the Activity LED
dtparam=act_led_trigger=none
dtparam=act_led_activelow=off
# Disable ethernet LEDs
dtparam=eth_led0=4
dtparam=eth_led1=4
```

And, if you're not using the GPU, you can also add `gpu_mem=16` to the **"[all]"** section above. It likely won't affect anything though. Something that will help power consumption is the line `**dtoverlay=disable-bt**`. If you're not using wifi either, you can duplicate that line and change **bt** to **wifi**. However, if you intend on using this like a regular smart-speaker (including the ability to play music as a bluetooth speaker, and not needing to run an ethernet cable to it), I suggest leaving both Wifi and bluetooth enabled.

You can now do CTRL+X, Y, ENTER, to save and exit, then run `sudo reboot` to restart your pi. Once you're back, continue with the next section.

# Installing things

First, run
```
sudo apt-get install python3-venv git -y
cd
git clone https://github.com/rhasspy/rhasspy3
cd rhasspy3
git reset --hard 11e8d3016d323a2ab1756dc68b4ba8a9f75f22a6
```

(right now, that `git reset` command is to peg the version of Rhasspy3 to a specific version while it's in heavy development and incomplete)

to install dependencies, which will then allow the installation of rhasspy in a folder in the home directory.

Now, we're gonna configure Rhasspy. Most of this is almost directly taken from Rhasspy's own docs.

```
nano config/configuration.yaml
```

# Configuring things

Paste in the following for the different things that need configuring:

**Microphone**
After the `-D`, you've got to add something. Run `arecord -L`, then find your microphone. In my case, it began with `plughw:`, so I copied that to go after the `-D`, e.g: `-D plughw:CARD=CameraB409241`. When you're done, CTRL+X, Y, ENTER, to save.
```
programs:
  mic:
    arecord:
      command: |
        arecord -q -r 16000 -c 1 -f S16_LE -t raw -D
      adapter: |
        mic_adapter_raw.py --rate 16000 --width 2 --channels 1

pipelines:
  default:
    mic:
      name: arecord
```

**Voice Activity Detection**

Run this to install the program used to detect when you're speaking:
```
mkdir -p config/programs/vad/
cp -R programs/vad/silero config/programs/vad/
config/programs/vad/silero/script/setup
```

Then go back into your config:
```
nano config/configuration.yaml
```
And paste (below the whole `mic:` section) the silero configs:
```
  vad:
    silero:
      command: |
        script/speech_prob "share/silero_vad.onnx"
      adapter: |
        vad_adapter_raw.py --rate 16000 --width 2 --channels 1 --samples-per-chunk 512
```
and then below the other `mic:` section in `pipelines:`
```
    vad:
      name: silero
```

**Speech To Text**

First, install `faster-whisper`, our speech to text engine:
```
mkdir -p config/programs/asr/
cp -R programs/asr/faster-whisper config/programs/asr/
config/programs/asr/faster-whisper/script/setup
config/programs/asr/faster-whisper/script/download.py tiny-int8
```

Then, add this below the whole `vad:` section:
```
  asr:
    faster-whisper:
      command: |
        script/wav2text "${data_dir}/tiny-int8" "{wav_file}"
      adapter: |
        asr_adapter_wav2text.py
    faster-whisper.client:
      command: |
        client_unix_socket.py var/run/faster-whisper.socket

servers:
  asr:
    faster-whisper:
      command: |
        script/server --language "en" "${data_dir}/tiny-int8"
```
And do the same below `vad:` within the `pipelines:` section:
```
    asr:
      name: faster-whisper.client
```

**Wake Word**
Run
```
mkdir -p config/programs/wake/
cp -R programs/wake/porcupine1 config/programs/wake/
config/programs/wake/porcupine1/script/setup
```

Then go back to the configs, and add this to the programs section below `asr:`:
```
  wake:
    porcupine1:
      command: |
        .venv/bin/python3 bin/porcupine_stream.py --model "${model}"
      template_args:
        model: "blueberry_raspberry-pi.ppn"
```

Then this in the `pipelines:`
```
    wake:
      name: porcupine1
```
If you're not on a pi, change `raspberry-pi` to `linux`, and you can look at your installed models with a `config/programs/wake/porcupine1/script/list_models`

**Intent handler**

In your config, add this in the `programs:` below `wake:`, and replace `assistant1` with your chosen username.
```
  handle:
    intent_handler:
      command: |
        /home/assistant1/rhasspy3/.venv/bin/python3 bin/intent_handler.py
      adapter: |
        handle_adapter_text.py
```

and in `pipelines:`
```
    handle:
      name: intent_handler
```

**Text To Speech**

Run
```
mkdir -p config/programs/tts/
cp -R programs/tts/piper config/programs/tts/
config/programs/tts/piper/script/setup.py
```

I don't want to use the default en-gb voice. If you want the default for British English, run this:
```
config/programs/tts/piper/script/download.py en-gb
```
Obviously, you can change en-gb for other regions. If you know of a different voice you want, you can run `nano config/programs/tts/piper/script/download.py` and change the voice selected for your region, _then_ run that previous command. I choose `en-gb-southern_english_female-low`.

Now, add this to your config in `programs:`, and change `model:` to the one you've got:
```
  tts:
    piper:
      command: |
        bin/piper --model "${model}" --output_file -
      adapter: |
        tts_adapter_text2wav.py
      template_args:
        model: "${data_dir}/en-gb-southern_english_female-low.onnx"
    piper.client:
      command: |
        client_unix_socket.py var/run/piper.socket
  snd:
    aplay:
      command: |
        aplay -q -r 22050 -f S16_LE -c 1 -t raw
      adapter: |
        snd_adapter_raw.py --rate 22050 --width 2 --channels 1
```

and this to `servers:` (again, change the model to the one you want)
```
  tts:
    piper:
      command: |
        script/server "${model}"
      template_args:
        model: "${data_dir}/en-gb-southern_english_female-low.onnx"
```

and this to `pipelines:`
```
    tts:
      name: piper.client
    snd:
      name: aplay
```

**HTTP SERVER**

Just run:
```
script/setup_http_server
```

To set up the server for later.

# Running:
In one terminal:
```
script/http_server --debug --server asr faster-whisper --server tts piperer
```

In another:
```
curl -X POST 'localhost:13331/pipeline/run'
```

# Intent Handler

To make a template for your intent handler:
```
mkdir -p config/programs/handle/intent_handler/bin/
touch config/programs/handle/intent_handler/bin/intent_handler.py
chmod +x config/programs/handle/intent_handler/bin/intent_handler.py
nano config/programs/handle/intent_handler/bin/intent_handler.py
```

Then paste this in:

```
import re
import random
import sys
import os

# Set responses
agreeResponse = ("Okay, ", "Alright, ", "Will do. ", "Got it, ", "Sure, ")
currentlyResponse = ("Right now it's ", "It's ", "Currently it's ", "At the moment it's ", "Presently, it's >
morningResponse = (" in the morning", " AM")
eveningResponse = (" in the afternoon", " in the evening", " PM")


text = sys.stdin.read().strip().lower()
words = [re.sub(r"\W", "", word) for word in text.split()]
raw_words = text.split()

#Create temp file path
tmp_file_path = "/dev/shm/tmpassistant/"
if not os.path.exists(tmp_file_path):
  os.makedirs(tmp_file_path)
```
CTRL+X, Y, ENTER to save and exit.

## The structure of queries

Lots of nested ifs. 

I separate things into different categories. For example, this wonderful line:
```
elif ("what" in words) or ("whats" in words) or ("tell" in words):
```
checks if you're asking a question. Other things might be commands. Within those, I check for words said. For example, when checking the time, I check for a question including the word time, and then whether it includes a place. If it doesn't, it just says the local time, but if it does, you can get the time somewhere else. It's like a little decision tree.

Keep in mind, we're working with lowercase words with all special characters removed. It would be possible to grab the raw version with capitalisation and punctuation, but that's not what this decision tree is using. (e.g, `what's` is invalid and will never show up, so we must use `whats` instead, even if it's frustrating grammar-wise)

I would also eventually like to check for politeness to have the assistant respond with manners, and other fun things.

## Bluetooth Audio Streaming
You can use an Echo or Google Home as a bluetooth speaker, why not this?

First, run this to install all of the (originally difficult for me to find) dependencies

```
sudo apt-get install -y libdbus-glib-1-2 libdbus-glib-1-dev python3-gi python3-gst-1.0 pulseaudio-module-bluetooth python3-pip gstreamer1.0-plugins gstreamer1.0-alsa
pip3 install dbus-python
```

Then, paste this into your terminal
```
sudo hostnamectl --pretty set-hostname ""
```
and put what you want the speaker to appear as within the quotes. So, if you put "Issac Bedroom Speaker", it would appear to your phone like this:
![Issac Bedroom Speaker in Bluetooth settings](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/issacbedroomspeaker.png)

In the end, I picked Blueberry.

Then, run 
```
sudo nano /etc/bluetooth/main.conf
```
and go to the `#DiscoverableTimeout` line. Remove the #, and set it to `DiscoverableTimeout = 30`

and add:
`Class = 0x000414` to the top of the config.

Then `CTRL+X, Y, ENTER` to save and exit.

Next, run this to download the script that makes your Pi visible as a bluetooth speaker
```
mkdir -p ~/rhasspy3/resources/code
cd ~/rhasspy3/resources/code
curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/new/resources/code/bt-audio.py
chmod +x bt-audio.py
cd ~/rhasspy3
```

Then, into the intenthandler, we'll add this function:
```
def bluetooth_pairing():
  # Spawn detached (background, unrelated to this python script) process for bluetooth audio. Very annoying to find right command, had to rant here.
  p = subprocess.Popen(['/home/assistant1/rhasspy3/resources/code/bt-audio.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  print(random.choice(agreeResponse) + " I'll turn on bluetooth pairing")
```

Also, at the top, add this (`import subprocess`) to import what's necessary.

Then `sudo reboot now` to reboot.

This is decision tree with just this:
```
# If the user is asking for bluetooth pairing
if ("bluetooth" in words) and (("turn" in words) or ("on" in words) or ("pairing" in words)):
  bluetooth_pairing()
```

If you **unpair** (not just disconnect) your phone, you won't be able to reconnect. To fix that, open the terminal, run `bluetoothctl`, then type `remove `, press tab, and it'll either fill something in, or give you a list of options. If it fills something in, just press enter and you're done. If you've got a list, type the first letter of one, press tab, then enter, and do that for each item in the list.

### Optimal.

## Getting the time

I added
```
from datetime import datetime
```
and this function:

```
def say_time():
  now = datetime.now()
  if now.strftime('%p') == "PM":
    apm = random.choice(eveningResponse)
  else:
    apm = random.choice(morningResponse)
  if now.strftime('%M') == 00:
    speech("Its " + now.strftime('%I') + " " + apm)
  else:
    print(random.choice(currentlyResponse) + now.strftime('%I') + " " + now.strftime('%M') + " " + apm)
```

This will be called if you ask a question including the time, but not a place (I'll properly add support for asking the time in different places later).

It sets whether we're in the morning or evening, and then says the current time followed by whether that's AM or PM, using info from datetime.

This is the decision tree with only this included:
```
# If user is asking for information
elif ("what" in words) or ("whats" in words) or ("tell" in words):
  # If asking for the time
  if "time" in words:
    # If asking for the time in a place
    if [place for place in places if place in words]:
      print("I don't know the time in chicago") # Placeholder
    # If just generally asking for the time
    else:
      say_time()
```

## The weather
What if I want it to tell me the weather?

First, go to [openweathermap](https://openweathermap.org/) and sign up for a free account. Then, check your email for an API key. It's important to do this first, since they key will take a little bit to properly activate. 

In the intent handler, I added this function:
```
def get_weather():
  opnwthrurl = "https://api.openweathermap.org/data/2.5/weather?"
  opnwthrauth = "YOURAUTHKEY"
  opnwthrlat, opnwthrlon = "LAT" , "LONG"
  opnwthrunits = "metric"
  weather = requests.get(opnwthrurl+"lat="+opnwthrlat+"&lon="+opnwthrlon+"&units="+opnwthrunits+"&appid="+opnwthrauth).json()
  currentTemp = weather["main"]["temp"]
  currentDesc = weather["weather"][0]["description"]
  speech("It's currently " + str(round(currentTemp)) + " degrees and " + currentDesc)
```

I also had to `import requests` then `pip install requests`, but within the venv created earlier. To do this, run `~/rhasspy3/.venv/bin/pip install requests`. Any other pip install should be done with this pip too.


Change **YOURAUTHKEY** to your api key from openweathermap, and **LAT** / **LONG** to your current latitude and longitude. They don't have to be exactly on your location, but you can use a tool [like this](https://www.latlong.net/) to get the numbers for your general area.

Then, save and exit, and ask your assistant **"What's the weather"**, and it should tell you the current temperature, along with two words to describe it, like **Clear Sky** or **Scattered Clouds**.


This is the decision tree with only this:
```
# If user is asking for information
elif ("what" in words) or ("whats" in words) or ("tell" in words):
  # If asking for the weather
  elif ("weather" in words) or ("temperature" in words) or ("heat" in words) or ("hot" in words) or ("cold" in words):
    ## If asking for the weather in a place
    if ("in" in words) or ("at" in words):
      print("I don't know the weather in chicago")
    ## If asking for the weather in general
    else:
      get_weather()
```

## Getting the date

Add this elif statement:

```
def get_date():
  months = [" January ", " February ", " March ", " April ", " May ", " June ", " July ", " August ", " September ", " October ", " November ", " December "]
  weekdays = [" Monday ", " Tuesday ", " Wednesday ", " Thursday ", " Friday ", " Saturday ", " Sunday "]
  dayNum = datetime.now().day
  month = months[(datetime.now().month)-1]
  weekday = weekdays[datetime.today().weekday()]
  print(random.choice(currentlyResponse) + weekday + "the " + str(dayNum) + " of" + month)
```

We get a number for the day of the month, day of week, and month (so, Jan is 1, Dec is 12), then convert these to words using lists. Then, we speak a sentence which puts it all together.

Ensure `from datetime import datetime` is present (it should be from earlier though).

Here is the decision tree with just this:
```
# If user is asking for information
elif ("what" in words) or ("whats" in words) or ("tell" in words):
  # If the user is asking for the date
  elif ("date" in words) or ("today" in words) or ("day" in words):
    get_date()
```

## Giving greetings

This is **part of the Rhasspy-provided example script,** however it's a feature nonetheless. 

In your Rhasspy sentences section, add this:
```
[Greet]
Hello
Hi
Good (morning | afternoon | evening)
```
and remember to save and retrain.

It should work immediately, since it was part of the example we pasted in earlier, however we'll look at the code anyway.

```
def generic_greet():
  replies = ["Hi!", "Hello!", "Hey there!", "Greetings.", "Hola.", "Good day."]
  print(random.choice(replies))
```

If the intent is **"Greet"**, we make a list of items, each of which is a string. In this case, they're just different ways of greeting the user. Then, we randomly pick one of the items and say t. If you want to add extra things to say, just add a string to the list. 

I at some point intend to make it aware of the time so it can correct you if you mistakenly say **Good Morning** in the **Evening** (or vice versa).

This is the decision tree with just this:
```
#If user is generically saying hi
elif ("hi" in words) or ("hello" in words) or ("hey" in words):
  generic_greet()
```

## Volume control
Setting my speaker any below 65% is entirely inaudible, so we'll add support for setting **your own** "boundaries" for volume. In my case, I'd want "0%" to actually mean 65%. This obviously isn't necessary for everyone, and shouldn't be for me in the future either, but is useful for those dealing with separate amps and stuff.

First, we'll get the sound file we need into the right place.

```
mkdir -p ~/rhasspy3/resources/sounds/
cd ~/rhasspy3/resources/sounds/
sudo curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/sounds/stoplistening.wav
mv stoplistening.wav volume_change.wav
cd ~/rhasspy3
```

and then this to your intentHandler:
```
def set_volume(percentage):
  audioDevice = "Master"
  minBound, maxBound = 65, 100
  percentage = int(minBound+int((percentage)*((maxBound-minBound)/100)))
  subprocess.call(["amixer", "sset", audioDevice, str(percentage) + "%"], stdout=subprocess.DEVNULL)
  subprocess.call(["aplay", "/home/assistant1/rhasspy3/resources/sounds/volume_change.wav"], stdout=subprocess.DEVNULL)
```

You'll also need to add `import subprocess` to the top of the intent handler.

This *might* just work immediately for you, however if not, it's likely the audio device that's wrong. We can find the right one like this.Just run `amixer`, and you'll see a list of devices (or just one, like me for now). We just care about finding the name of the right one. 

![Amixer devices](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/amixer-devices.png)

Here, that's `Headphone`.  If yours is different, just change it in the python script.

This is the decision tree with only this section:
```
# If the user is telling something to happen
elif ("set" in words) or ("said" in words) or ("make" in words): # "said" since "set" is sometimes misheard)
  ## If the user is setting the volume
  if ("volume" in words) or ("speakers" in words):
    #Find the percentage, send that over to the set_volume function.
    for word in raw_words:
      if "%" in word:
        # Get the index of the percentage value, then get that from the filtered words for just the numerical value.
        # Convert it to int, then call function
        set_volume(int(words[raw_words.index(word)]))
```

# Smart Home controls

For all of this, make sure `import requests` is at the top of your intent handler.

Also, do `~/rhasspy3/.venv/bin/pip install colour`, which will let us turn human colours into rgb values more easily.

## WLED

#### This section is for controlling WLED Lights:

(for now at least), I've not made a function for this. Here's an example of the decision tree with just this, using two lights.:

```
# If the user wants to control lights
elif ("light" in words) or ("lights" in words):
  if ("door" in words):
    if ("on" in words):
      requests.post("http://IP/win&T=1")
      print(random.choice(agreeResponse) + " I'll turn on the door light")
    elif ("off" in words):
      requests.post("http://IP/win&T=0")
      print(random.choice(agreeResponse) + " I'll turn off the door light")
    #elif ADD COLOUR CHECKING HERE:
    else:
      for word in raw_words:
        if "%" in word:
          # Get the index of the percentage value, then get that from the filtered words for just the numerical value.
          # Convert it to int, then call function
          requests.post("http://IP/win&A=" +  str(int(int(words[raw_words.index(word)])*2.55)) )
          print(random.choice(agreeResponse) + " I'll set the door light to " + word)
  elif ("bed" in words) or ("bedside" in words):
    if ("on" in words):
      requests.post("http://IP/win&T=1")
      print(random.choice(agreeResponse) + " I'll turn on the bedside light")
    elif ("off" in words):
      requests.post("http://IP/win&T=0")
      print(random.choice(agreeResponse) + " I'll turn off the bedside light")
    #elif ADD COLOUR CHECKING HERE:
    else:
      for word in raw_words:
        if "%" in word:
          # Get the index of the percentage value, then get that from the filtered words for just the numerical value.
          # Convert it to int, then call function
          requests.post("http://IP/win&A=" +  str(int(int(words[raw_words.index(word)])*2.55)) )
          print(random.choice(agreeResponse) + " I'll set the bedside light to " + word)

```

## Jellyfin Music Support
We can talk to the Jellyfin API to get music from a server, and integrate it with our speech-to-text so that all artists, songs, and albums are recognised.

#### Also, authenticating in a way that makes sense will come one day.

But that's not how things are right now, so the setup is weird, but it works.

### Downloading an index of your library.

Jellyfin's API supports search, but voice recognition isn't perfect, and Jellyfin's search doesn't seem to be fuzzy at all, so I'll have to search a local index instead.

Run this:

```
mkdir -p ~/rhasspy3/jellyfin/
cd ~/rhasspy3/jellyfin/
curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/code/create-jf-slots.py
sudo nano create-jf-slots.py
```

Next, change the contents of `jellyfinurl` to the address that you access your jellyfin server from. It should appear just like it does in your browser, including **https://** and (if applicable) the `:portnumber` at the end.

Then, go to your Jellyfin server's web client, then click the profile icon in the top right, dashboard, then API keys on the left bar. Add one, pick whatever name you want, and copy that key to your `jellyfinauth` variable. 

Next, press F12 to open your browser's dev tools, click the network tab, and enter `userid` into the search bar, then refresh the page. Hopefully you'll see something like this:

![Firefox dev tools showing URL with userid](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/devtoolsuserid.png)

Right click one of the options, copy the URL, then paste it into your address bar. Copy out the value for `userid` (remembering not to include the `&` symbol which will be at the end, and paste it into the `userid` section in the python script.

Then, save and exit by doing CTRL+X, Y, ENTER.

Now, you can just run `python create-jf-slots.py`.

### Getting the songs to play

In this section, we'll add to the intentHandler, allowing it to grab the IDs of the songs you want to play, and shuffle them if necessary.
 
Firstly, run `~/rhasspy3/.venv/bin/pip install thefuzz python-Levenshtein python3-mpv` to install the library we'll be using for searching.

Then, paste this elif statement at the end of the intenthandler:
```
def JellyfinPlay():
  # Set Variables
  jellyfinurl, jellyfinauth, userid = "https://", "", ""
  headers = {"X-Emby-Token": jellyfinauth,}
  songsList = []
  ps, itemid, q = o["slots"]["ps"], o["slots"]["itemid"], o["slots"]["q"]
  # Check if song currently playing. Stop it if True
  if os.path.exists(currentMediaPath):
    jellyfinStop = open(jellyfinStopFilePath, "w")
    jellyfinStop.close()
    time.sleep(1)

  # If not just an individual song, get the list of songs and their info. 
  if not q == "song":
    if itemid == "favourites":
      get = requests.get(jellyfinurl+"/Users/"+userid+"/Items?Recursive=true&Filters=IsFavorite&IncludeItemTypes=Audio", headers = headers)
    else:
      get = requests.get(jellyfinurl+"/Users/"+userid+"/Items?Recursive=true&IncludeItemTypes=Audio&parentId=" + itemid, headers = headers)
    receivedJson = json.loads(get.text)
    songs = receivedJson["Items"]
  # If individual song, just get one song's info
  else:
    get = requests.get(jellyfinurl+"/Users/"+userid+"/Items/" + itemid, headers = headers)
    songs = [json.loads(get.text)]

  for song in songs:
    songsList.append({"Name": song["Name"], "Id" : song["Id"]})

  # If user asked for shuffle (ps stands for play/shuffle), shuffle.
  if ps == "shuffle":
    random.shuffle(songsList)

  #Initialise song to zero, and begin loop for every song in the list
  songPos = 0
  for song in songsList:
    if os.path.exists(jellyfinStopFilePath):
      break
    currentSong = open(currentMediaPath, "w")
    currentSong.write("2")
    currentSong.close()
    jellyfinPlay = open(jellyfinPlayFilePath, "w")
    jellyfinPlay.write(songsList[songPos]["Id"])
    jellyfinPlay.close()
    # Loop which only stops once currentMedia deleted (which signifies the end of the song). After this, increment song and loop back.
    while os.path.exists(currentMediaPath):
      if os.path.exists(jellyfinStopFilePath):
        break
    songPos += 1
```
Remember to add the server URL, auth, and userid.

Also, at the top of your intent handler, ensure you've got the follwing:
```                                            
from thefuzz import fuzz
from thefuzz import process
import os
```

You'll need to go into your Jellyfin profile and disable audio playback with transcoding, or the API breaks for some reason.

This script first checks if a song is currently playing, and stops if so. Then, if you're not asking for an individual song, it checks if you asked for favourites. If you did, it loads your favourites into a list. If you didn't, it will try to load all songs within the requested album/playlist/artist into the list instead. If you just asked for one song, we load that into the list instead. Then, we shuffle if necessary, and initialise a loop, where the song is downloaded, the playback script (which we will soon create) is requested to start, and this loop only restarts once the previous song is done.

### To add playback support

Now, we'll make another script. Just like with bluetooth support, we can't run everything in the docker container, so we'll be making a system service that is *activated* by the intentHandler.

First, install miniaudio using pip

```
sudo apt install python3-mpv
```

Now, make the playback script@
```
cd ~/rhasspy3/jellyfin/
curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/code/jellyfinPlay.py
sudo chmod +x jellyfinPlay.py
sudo nano ~/assistant/jellyfinPlay.py
```

And remember to add the URL, authtoken, and user id to the variables at the top, then CTRL+X, Y, Enter to save.

This script handles playback (including pausing, stopping, and resuming), as well as getting info for the currently playing song incase we want it for later.


### Getting currently playing song
Although probably not the most useful while playing a single song, we'll add this feature now so we have it later.

In the code previously added, we're already storing a lot of info about the currently playing song in RAM. All we need is to specify a way of accessing it. Although for future use (potentially in a UI? not sure) we've got lots of info available (release date, file format, bitrate, etc), all I want is the name and artist. I want to say "what song is this?" - or something similar - and for the assistant to respond: "This is <songname> by <artistname>"
    
The file with this info is called "songInfoFile".
    
First, we'll add this sentence to Rhasspy:
```
[JFGetPlayingMediaName]
what song [is] [(this | playing | on)]
whats the name of [this] song
whats currently playing
whats playing right now
```
Then, we can add this elif statement to the intentHandler:
```
elif intent == "JFGetPlayingMediaName":
  if not os.path.exists(currentMediaPath):
    speech("No songs are playing")
  song_info = eval(open(songInfoFilePath, 'r').read())
  speech("This is " + song_info["Name"] + " by " + song_info["AlbumArtist"])
```
    
And add this to our ```# Set Paths``` section
```
songInfoFilePath = tmpDir+"songInfoFile"
```
    
It'll now read that file (which was created by the playback script, grabbing the info from your Jellyfin server using the ID of the song), separate out the name and artist, then say them in a sentence.

#### Adding ability to skip.
    
Add this sentence:
```
[JellyfinSkipSong]
(skip | next) [the] (song | track | music)
```

Then, we'll add this elif statement, which makes a skip file. It'll work like the stop file used to, except it ***won't*** tell our song-queue to stop too:
```
elif intent == "JellyfinSkipSong":
  if not os.path.exists(currentMediaPath):
    speech("No songs are playing")
  jellyfinSkipSong = open(workingDir + "tmp/jellyfinSkipSong", "w")
  jellyfinSkipSong.close()
```

And now, you should be able to skip song.

This works because we're basically simulating the song having finished, but not also stopping the queue program.


## Setting timers
Unlike when I originally wrote this, I now have a system for handling syncing timers with Blueberry and other devices. If you don't care, this'll work standalone, you don't need to mess with anything, but if you're interested, [here's the link with more details](https://gitlab.com/issacdowling/selfhosted-synced-stuff).

First, we'll add things to our intenthandler. 

Go to the top, add a section called `# Set Paths`, and below it, add: 
```
stop_timer_path = tmpDir + "timer_stop"
start_timer_path = tmpDir + "timer_start"
timer_info_path = tmpDir + "timer_sync_info.json"
```

Then, add the following elif statements.
```
elif intent == "start_timer":
  length = int(o["slots"]["time"])
  unit = o["slots"]["unit"]

  # Tell user that timer is set.
  speech("Alright, I'll set a " + str(length) + " " + unit + " timer")

  #Convert spoken time into seconds if applicable
  if unit == "minute":
    length = (length*60)

  #Write the length info to start file.
  start_timer_json = {"length" : length}
  with open(start_timer_path, "w") as start_timer:
    start_timer.write(json.dumps(start_timer_json))

elif intent == "stop_timer":
  with open(stop_timer_path, "w"):
      pass
  speech(random.choice(agreeResponse) + "i'll stop the timer")

elif intent == "timer_remaining":
  timer = json.load(open(timer_info_path, 'r'))
  #If timer already running, tell user the details
  if timer["remaining_length"] > 0:
    if timer["remaining_length"]-3 >= 60:
      speech("Your timer has " + str(math.trunc((timer["remaining_length"]-3)/60)) + " minutes and " + str((timer["remaining_length"] % 60) - 3) + " seconds left")
    else:
      speech("Your timer has " + str(timer["remaining_length"]-3) + " seconds left")
  #If timer going off, tell user, fix it.
  elif timer["dismissed"] == False:
    with open(stop_timer_path, "w"):
      pass
    speech("You've got a timer going off. I'll dismiss it.")
  else:
    speech("You've got no timers running")

```

In your Rhasspy sentences, you'll want to add these (remember to save and train):
```
[start_timer]
(set | make | start) a (1..60){time} (second | minute){unit} timer

[stop_timer]
stop [the] (timer | alarm)

[timer_remaining]
how long left on timer
what is [the] timer [at | on]
```

#### Now that those are added, we'll get the server and notifier set up.

Run this to download the necessary files and put them in the right place:
```
sudo apt-get install -y nodejs npm
sudo pip install websockets
mkdir ~/sync-conveniences
cd ~/sync-conveniences
curl -O https://gitlab.com/issacdowling/selfhosted-synced-stuff/-/raw/main/webserver.mjs
curl -O https://gitlab.com/issacdowling/selfhosted-synced-stuff/-/raw/main/timer.py
curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/sounds/timerchime.wav
curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/code/timer-sync.py
npm install ws## Setting timers
Unlike when I originally wrote this, I now have a system for handling syncing timers with Blueberry and other devices. If you don't care, this'll work standalone, you don't need to mess with anything, but if you're interested, [here's the link with more details](https://gitlab.com/issacdowling/selfhosted-synced-stuff).

First, we'll add things to our intenthandler. 

Go to the top, add a section called `# Set Paths`, and below it, add: 
```
stop_timer_path = tmpDir + "timer_stop"
start_timer_path = tmpDir + "timer_start"
timer_info_path = tmpDir + "timer_sync_info.json"
```

Then, add the following elif statements.
```
elif intent == "start_timer":
  length = int(o["slots"]["time"])
  unit = o["slots"]["unit"]

  # Tell user that timer is set.
  speech("Alright, I'll set a " + str(length) + " " + unit + " timer")

  #Convert spoken time into seconds if applicable
  if unit == "minute":
    length = (length*60)

  #Write the length info to start file.
  start_timer_json = {"length" : length}
  with open(start_timer_path, "w") as start_timer:
    start_timer.write(json.dumps(start_timer_json))

elif intent == "stop_timer":
  with open(stop_timer_path, "w"):
      pass
  speech(random.choice(agreeResponse) + "i'll stop the timer")

elif intent == "timer_remaining":
  timer = json.load(open(timer_info_path, 'r'))
  #If timer already running, tell user the details
  if timer["remaining_length"] > 0:
    if timer["remaining_length"]-3 >= 60:
      speech("Your timer has " + str(math.trunc((timer["remaining_length"]-3)/60)) + " minutes and " + str((timer["remaining_length"] % 60) - 3) + " seconds left")
    else:
      speech("Your timer has " + str(timer["remaining_length"]-3) + " seconds left")
  #If timer going off, tell user, fix it.
  elif timer["dismissed"] == False:
    with open(stop_timer_path, "w"):
      pass
    speech("You've got a timer going off. I'll dismiss it.")
  else:
    speech("You've got no timers running")

```

In your Rhasspy sentences, you'll want to add these (remember to save and train):
```
[start_timer]
(set | make | start) a (1..60){time} (second | minute){unit} timer

[stop_timer]
stop [the] (timer | alarm)

[timer_remaining]## Setting timers
Unlike when I originally wrote this, I now have a system for handling syncing timers with Blueberry and other devices. If you don't care, this'll work standalone, you don't need to mess with anything, but if you're interested, [here's the link with more details](https://gitlab.com/issacdowling/selfhosted-synced-stuff).

First, we'll add things to our intenthandler. 

Go to the top, add a section called `# Set Paths`, and below it, add: 
```
stop_timer_path = tmpDir + "timer_stop"
start_timer_path = tmpDir + "timer_start"
timer_info_path = tmpDir + "timer_sync_info.json"
```

Then, add the following elif statements.
```
elif intent == "start_timer":
  length = int(o["slots"]["time"])
  unit = o["slots"]["unit"]

  # Tell user that timer is set.
  speech("Alright, I'll set a " + str(length) + " " + unit + " timer")

  #Convert spoken time into seconds if applicable
  if unit == "minute":
    length = (length*60)

  #Write the length info to start file.
  start_timer_json = {"length" : length}
  with open(start_timer_path, "w") as start_timer:
    start_timer.write(json.dumps(start_timer_json))

elif intent == "stop_timer":
  with open(stop_timer_path, "w"):
      pass
  speech(random.choice(agreeResponse) + "i'll stop the timer")

elif intent == "timer_remaining":
  timer = json.load(open(timer_info_path, 'r'))
  #If timer already running, tell user the details
  if timer["remaining_length"] > 0:
    if timer["remaining_length"]-3 >= 60:
      speech("Your timer has " + str(math.trunc((timer["remaining_length"]-3)/60)) + " minutes and " + str((timer["remaining_length"] % 60) - 3) + " seconds left")
    else:
      speech("Your timer has " + str(timer["remaining_length"]-3) + " seconds left")
  #If timer going off, tell user, fix it.
  elif timer["dismissed"] == False:
    with open(stop_timer_path, "w"):
      pass
    speech("You've got a timer going off. I'll dismiss it.")
  else:
    speech("You've got no timers running")

```

In your Rhasspy sentences, you'll want to add these (remember to save and train):
```
[start_timer]
(set | make | start) a (1..60){time} (second | minute){unit} timer

[stop_timer]
stop [the] (timer | alarm)

[timer_remaining]
how long left on timer
what is [the] timer [at | on]
```

#### Now that those are added, we'll get the server and notifier set up.

Run this to download the necessary files and put them in the right place:
```
sudo apt-get install -y nodejs npm
sudo pip install websockets
mkdir ~/sync-conveniences
cd ~/sync-conveniences
curl -O https://gitlab.com/issacdowling/selfhosted-synced-stuff/-/raw/main/webserver.mjs
curl -O https://gitlab.com/issacdowling/selfhosted-synced-stuff/-/raw/main/timer.py
curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/sounds/timerchime.wav
curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/code/timer-sync.py
npm install ws
sudo systemctl --force --full edit start-sync-webserver.service
```
and pasting:
```                                        
[Unit]
Description=Start sync conveniences webserver       
After=multi-user.target

[Service]
ExecStart=/usr/bin/node /home/assistant-main-node/sync-conveniences/webserver.mjs

[Install]
WantedBy=multi-user.target

```
Change `assistant-main-node` to your username in that file if it's different.

Then do:
```
sudo systemctl --force --full edit start-sync-timer.service
```
and paste:
```
[Unit]
Description=Start sync conveniences timer       
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/assistant-main-node/sync-conveniences/timer.py

[Install]
WantedBy=multi-user.target
```

Then do:
```
sudo systemctl --force --full edit start-sync-timersync.service
```
and paste:
```
[Unit]
Description=Start sync conveniences timer-sync    
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/assistant-main-node/sync-conveniences/timer-sync.py

[Install]
WantedBy=multi-user.target
```

Modify the timer-sync file
```
sudo nano ~/sync-conveniences/timer-sync.py
sudo nano ~/sync-conveniences/timer.py
sudo nano ~/sync-conveniences/webserver.mjs
```
Change working_directory to `/dev/shm/tmpassistant/` for all of those text files.

In timer_finished_audio, change the username if it's not the same as mine! Same goes if you want a different audio file.

Now we'll make it all executable and enable it:
```
sudo systemctl enable start-sync-webserver.service --now
sudo systemctl enable start-sync-timer.service --now
sudo systemctl enable start-sync-timersync.service --now
```

And now you should be done. You can ask for a timer, ask how long's left, or stop it, as well as accessing it from other devices [if you set that up.](https://gitlab.com/issacdowling/selfhosted-synced-stuff)

START_TIMER, STOP_TIMER, and TIMER_FILE.JSON are handled by the timer.py file itself. TIMER_START, TIMER_STOP, and TIMER_SYNC_INFO.JSON are handled by the sync handler, and are what should be used.

## Generic stop function
In the future, we might have other things that we'd like to stop, such as music playback, which is why I made the "timer stop" it's own separate thing. I'd still like to be able to just say "stop", so we'll add another intent which just stops everything. 

First, we'll add the sentence, since it's the most basic part. Go to your rhasspy web UI, sentences, and paste this:
```
[generic_stop]
stop
```
Wonderful.

Now, we'll add this code to the end of our intentHandler, which says that - if we're not specifically told ***what***  we're stopping - we'll stop everything:
```
elif intent == "generic_stop":
  stop = requests.post(webserver_url + "/timer_stop").text
```
As you can see, we're just stopping the timer right now, but the point of this intent is that we'll add anything else that can be stopped here too. This'll be mentioned in the relevant sections. For now, you can save and exit.

#### Now that those are added, we'll get the server and notifier set up.

Run this to download the necessary files and put them in the right place:
```
sudo apt-get install -y nodejs npm
sudo pip install websockets
mkdir ~/sync-conveniences
cd ~/sync-conveniences
curl -O https://gitlab.com/issacdowling/selfhosted-synced-stuff/-/raw/main/webserver.mjs
curl -O https://gitlab.com/issacdowling/selfhosted-synced-stuff/-/raw/main/timer.py
curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/sounds/timerchime.wav
curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/code/timer-sync.py
npm install ws
sudo systemctl --force --full edit start-sync-webserver.service
```
and pasting:
```                                        
[Unit]
Description=Start sync conveniences webserver       
After=multi-user.target

[Service]
ExecStart=/usr/bin/node /home/assistant-main-node/sync-conveniences/webserver.mjs

[Install]
WantedBy=multi-user.target

```
Change `assistant-main-node` to your username in that file if it's different.

Then do:
```
sudo systemctl --force --full edit start-sync-timer.service
```
and paste:
```
[Unit]
Description=Start sync conveniences timer       
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/assistant-main-node/sync-conveniences/timer.py

[Install]
WantedBy=multi-user.target
```

Then do:
```
sudo systemctl --force --full edit start-sync-timersync.service
```
and paste:
```
[Unit]
Description=Start sync conveniences timer-sync    
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/assistant-main-node/sync-conveniences/timer-sync.py

[Install]
WantedBy=multi-user.target
```

Modify the timer-sync file
```
sudo nano ~/sync-conveniences/timer-sync.py
sudo nano ~/sync-conveniences/timer.py
sudo nano ~/sync-conveniences/webserver.mjs
```
Change working_directory to `/dev/shm/tmpassistant/` for all of those text files.

In timer_finished_audio, change the username if it's not the same as mine! Same goes if you want a different audio file.

Now we'll make it all executable and enable it:
```
sudo systemctl enable start-sync-webserver.service --now
sudo systemctl enable start-sync-timer.service --now
sudo systemctl enable start-sync-timersync.service --now
```

And now you should be done. You can ask for a timer, ask how long's left, or stop it, as well as accessing it from other devices [if you set that up.](https://gitlab.com/issacdowling/selfhosted-synced-stuff)

START_TIMER, STOP_TIMER, and TIMER_FILE.JSON are handled by the timer.py file itself. TIMER_START, TIMER_STOP, and TIMER_SYNC_INFO.JSON are handled by the sync handler, and are what should be used.

## Generic stop function
In the future, we might have other things that we'd like to stop, such as music playback, which is why I made the "timer stop" it's own separate thing. I'd still like to be able to just say "stop", so we'll add another intent which just stops everything. 

First, we'll add the sentence, since it's the most basic part. Go to your rhasspy web UI, sentences, and paste this:
```
[generic_stop]
stop
```
Wonderful.

Now, we'll add this code to the end of our intentHandler, which says that - if we're not specifically told ***what***  we're stopping - we'll stop everything:
```
elif intent == "generic_stop":
  stop = requests.post(webserver_url + "/timer_stop").text
```
As you can see, we're just stopping the timer right now, but the point of this intent is that we'll add anything else that can be stopped here too. This'll be mentioned in the relevant sections. For now, you can save and exit.
and pasting:
```                                        
[Unit]
Description=Start sync conveniences webserver       
After=multi-user.target
## Setting timers
Unlike when I originally wrote this, I now have a system for handling syncing timers with Blueberry and other devices. If you don't care, this'll work standalone, you don't need to mess with anything, but if you're interested, [here's the link with more details](https://gitlab.com/issacdowling/selfhosted-synced-stuff).

First, we'll add things to our intenthandler. 

Go to the top, add a section called `# Set Paths`, and below it, add: 
```
stop_timer_path = tmpDir + "timer_stop"
start_timer_path = tmpDir + "timer_start"
timer_info_path = tmpDir + "timer_sync_info.json"
```

Then, add the following elif statements.
```
elif intent == "start_timer":
  length = int(o["slots"]["time"])
  unit = o["slots"]["unit"]

  # Tell user that timer is set.
  speech("Alright, I'll set a " + str(length) + " " + unit + " timer")

  #Convert spoken time into seconds if applicable
  if unit == "minute":
    length = (length*60)

  #Write the length info to start file.
  start_timer_json = {"length" : length}
  with open(start_timer_path, "w") as start_timer:
    start_timer.write(json.dumps(start_timer_json))

elif intent == "stop_timer":
  with open(stop_timer_path, "w"):
      pass
  speech(random.choice(agreeResponse) + "i'll stop the timer")

elif intent == "timer_remaining":
  timer = json.load(open(timer_info_path, 'r'))
  #If timer already running, tell user the details
  if timer["remaining_length"] > 0:
    if timer["remaining_length"]-3 >= 60:
      speech("Your timer has " + str(math.trunc((timer["remaining_length"]-3)/60)) + " minutes and " + str((timer["remaining_length"] % 60) - 3) + " seconds left")
    else:
      speech("Your timer has " + str(timer["remaining_length"]-3) + " seconds left")
  #If timer going off, tell user, fix it.
  elif timer["dismissed"] == False:
    with open(stop_timer_path, "w"):
      pass
    speech("You've got a timer going off. I'll dismiss it.")
  else:
    speech("You've got no timers running")

```

In your Rhasspy sentences, you'll want to add these (remember to save and train):
```
[start_timer]
(set | make | start) a (1..60){time} (second | minute){unit} timer

[stop_timer]
stop [the] (timer | alarm)

[timer_remaining]
how long left on timer
what is [the] timer [at | on]
```

#### Now that those are added, we'll get the server and notifier set up.

Run this to download the necessary files and put them in the right place:
```
sudo apt-get install -y nodejs npm
sudo pip install websockets
mkdir ~/sync-conveniences
cd ~/sync-conveniences
curl -O https://gitlab.com/issacdowling/selfhosted-synced-stuff/-/raw/main/webserver.mjs
curl -O https://gitlab.com/issacdowling/selfhosted-synced-stuff/-/raw/main/timer.py
curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/sounds/timerchime.wav
curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/code/timer-sync.py
npm install ws
sudo systemctl --force --full edit start-sync-webserver.service
```
and pasting:
```                                        
[Unit]
Description=Start sync conveniences webserver       
After=multi-user.target

[Service]
ExecStart=/usr/bin/node /home/assistant-main-node/sync-conveniences/webserver.mjs

[Install]
WantedBy=multi-user.target

```
Change `assistant-main-node` to your username in that file if it's different.

Then do:
```
sudo systemctl --force --full edit start-sync-timer.service
```
and paste:
```
[Unit]
Description=Start sync conveniences timer       
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/assistant-main-node/sync-conveniences/timer.py

[Install]
WantedBy=multi-user.target
```

Then do:
```
sudo systemctl --force --full edit start-sync-timersync.service
```
and paste:
```
[Unit]
Description=Start sync conveniences timer-sync    
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/assistant-main-node/sync-conveniences/timer-sync.py

[Install]
WantedBy=multi-user.target
```

Modify the timer-sync file
```
sudo nano ~/sync-conveniences/timer-sync.py
sudo nano ~/sync-conveniences/timer.py
sudo nano ~/sync-conveniences/webserver.mjs
```
Change working_directory to `/dev/shm/tmpassistant/` for all of those text files.

In timer_finished_audio, change the username if it's not the same as mine! Same goes if you want a different audio file.

Now we'll make it all executable and enable it:
```
sudo systemctl enable start-sync-webserver.service --now
sudo systemctl enable start-sync-timer.service --now
sudo systemctl enable start-sync-timersync.service --now
```

And now you should be done. You can ask for a timer, ask how long's left, or stop it, as well as accessing it from other devices [if you set that up.](https://gitlab.com/issacdowling/selfhosted-synced-stuff)

START_TIMER, STOP_TIMER, and TIMER_FILE.JSON are handled by the timer.py file itself. TIMER_START, TIMER_STOP, and TIMER_SYNC_INFO.JSON are handled by the sync handler, and are what should be used.

## Generic stop function
In the future, we might have other things that we'd like to stop, such as music playback, which is why I made the "timer stop" it's own separate thing. I'd still like to be able to just say "stop", so we'll add another intent which just stops everything. 

First, we'll add the sentence, since it's the most basic part. Go to your rhasspy web UI, sentences, and paste this:
```
[generic_stop]
stop
```
Wonderful.

Now, we'll add this code to the end of our intentHandler, which says that - if we're not specifically told ***what***  we're stopping - we'll stop everything:
```
elif intent == "generic_stop":
  stop = requests.post(webserver_url + "/timer_stop").text
```
As you can see, we're just stopping the timer right now, but the point of this intent is that we'll add anything else that can be stopped here too. This'll be mentioned in the relevant sections. For now, you can save and exit.
WantedBy=multi-user.target

```
Change `assistant-main-node` to your username in that file if it's different.

Then do:
```
sudo systemctl --force --full edit start-sync-timer.service
```
and paste:
```
[Unit]
Description=Start sync conveniences timer       
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/assistant-main-node/sync-conveniences/timer.py

[Install]
WantedBy=multi-user.target
```

Then do:
```
sudo systemctl --force --full edit start-sync-timersync.service
```
and paste:
```
[Unit]
Description=Start sync conveniences timer-sync    
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/assistant-main-node/sync-conveniences/timer-sync.py

[Install]
WantedBy=multi-user.target
```

Modify the timer-sync file
```
sudo nano ~/sync-conveniences/timer-sync.py
sudo nano ~/sync-conveniences/timer.py
sudo nano ~/sync-conveniences/webserver.mjs
```
Change working_directory to `/dev/shm/tmpassistant/` for all of those text files.

In timer_finished_audio, change the username if it's not the same as mine! Same goes if you want a different audio file.

Now we'll make it all executable and enable it:
```
sudo systemctl enable start-sync-webserver.service --now
sudo systemctl enable start-sync-timer.service --now
sudo systemctl enable start-sync-timersync.service --now
```

And now you should be done. You can ask for a timer, ask how long's left, or stop it, as well as accessing it from other devices [if you set that up.](https://gitlab.com/issacdowling/selfhosted-synced-stuff)

START_TIMER, STOP_TIMER, and TIMER_FILE.JSON are handled by the timer.py file itself. TIMER_START, TIMER_STOP, and TIMER_SYNC_INFO.JSON are handled by the sync handler, and are what should be used.

## Generic stop function
In the future, we might have other things that we'd like to stop, such as music playback, which is why I made the "timer stop" it's own separate thing. I'd still like to be able to just say "stop", so we'll add another intent which just stops everything. 

First, we'll add the sentence, since it's the most basic part. Go to your rhasspy web UI, sentences, and paste this:
```
[generic_stop]
stop
```
Wonderful.

Now, we'll add this code to the end of our intentHandler, which says that - if we're not specifically told ***what***  we're stopping - we'll stop everything:
```
elif intent == "generic_stop":
  stop = requests.post(webserver_url + "/timer_stop").text
```
As you can see, we're just stopping the timer right now, but the point of this intent is that we'll add anything else that can be stopped here too. This'll be mentioned in the relevant sections. For now, you can save and exit.

## Finding days until
If you want to be able to find the days until (or since) a date, this is the code for you.

Add the Rhasspy sentence:
```
[get_days_until]
how (many days | long) until [the] ($day_of_month_words){day} [of ($month_numbers){month}] [(1900..2100){year}]
```
Go to your slots section, and add a new one called `day_of_month_words`, paste this and *save*:
```
first:1
second:2
third:3
fourth:4
fifth:5
sixth:6
seventh:7
eighth:8
ninth:9
tenth:10
eleventh:11
twelfth:12
thirteenth:13
fourteenth:14
fifteenth:15
sixteenth:16
seventeenth:17
eighteenth:18
nineteenth:19
twentieth:20
(twenty first):21
(twenty second):22
(twenty third):23
(twenty fourth):24
(twenty fifth):25
(twenty sixth):26
(twenty seventh):27
(twenty eighth):28
(twenty ninth):29
thirtieth:30
(thirty first):31
```
Then, add another called `month_numbers`, since Rhasspy's built-in one outputs words, but we want numbers:
```
January:1
February:2
March:3
April:4
May:5
June:6
July:7
August:8
September:9
October:10
November:11
December:12
```
Finally, add this elif statement to your intenthandler:
```
elif intent == "get_days_until":
  day = int(o["slots"]["day"])
  try:
    month = int(o["slots"]["month"])
    no_month = False
  except:
    no_month = True
  try:
    year = int(o["slots"]["year"])
    no_year = False
  except:
    no_year = True

  current_date = datetime.now()

  if no_year == True:
      if no_month == True:
        until_date = current_date.replace(day=day)
      else:
          until_date = current_date.replace(day=day, month=month)
  else:   
    until_date = current_date.replace(day=day, month=month, year=year)

  if (until_date - current_date).days < 0:
    until = False
    phrase = "Since then, there have been " + str((until_date - current_date).days) + " days"
  else:
    until = True
    phrase = "There are " + str((until_date - current_date).days) + " days until that date"

  speech(phrase)
```

## Converting units

First, add a slot file called "units", and paste this in:
```
kilometres
metres
centimetres
millimetres

miles
feet
inches
yards


tons
(kilograms | kilos):kilograms
grams

ounces
pounds
stones


litres
millilitres
centilitres

fluid ounces
```
I've separated the "types" of units (length, mass, volume) with two lines, and the metric / imperial units by one line. These are all of the units that I thought of immediately that could be useful, but if you ever need anything else, you could just add it here.


Now, go to the sentences section, and paste this:
```
[UnitConversion]
unit = ($units)
(whats | convert) (1..1000){number} <unit>{unit1} (to | in) <unit>{unit2}
```

All that's left is the awkward bit, coding the conversions. To simplify things, we'll be converting into an intermediary unit. So, rather than having to separately code the conversions between kilograms and tons, then grams and ounces, etc for every unit of mass, we can instead just turn every unit1 into kilograms, then go from kilograms to unit2.

The code isn't nice, and it's massive. It works though. Paste this elif statement into your intentHandler:
```
elif intent == "UnitConversion":
    number, unit1, unit2 = float(o["slots"]["number"]), o["slots"]["unit1"], o["slots"]["unit2"]
# Length
    if unit1 == "metres":
        toBeConverted = number
    elif unit1 == "kilometres":
        toBeConverted = number*1000
    elif unit1 == "centimetres":
        toBeConverted = number/100
    elif unit1 == "millimetres":
        toBeConverted = number/1000
    elif unit1 == "miles":
        toBeConverted = number*1609.344
    elif unit1 == "feet":
        toBeConverted = number*0.3048
    elif unit1 == "inches":
        toBeConverted = number*0.0254
    elif unit1 == "yards":
        toBeConverted = number*0.9144

# Mass
    elif unit1 == "kilograms":
        toBeConverted = number
    elif unit1 == "tons":
        toBeConverted = number*1000
    elif unit1 == "grams":
        toBeConverted = number/1000
    elif unit1 == "ounces":
        toBeConverted = number*0.02834
    elif unit1 == "pounds":
        toBeConverted = number*0.4535
    elif unit1 == "stones":
        toBeConverted = number*6.35029

# Volume
    elif unit1 == "litres":
        toBeConverted = number
    elif unit1 == "millilitres":
        toBeConverted = number/1000
    elif unit1 == "centilitres":
        toBeConverted = number/100
    elif unit1 == "fluid ounces":
        toBeConverted = number*0.02841

# Doing the conversion
    if unit2 == "kilometres":
        finalValue = toBeConverted/1000
    elif unit2 == "metres":
        finalValue = toBeConverted
    elif unit2 == "centimetres":
        finalValue = toBeConverted*100
    elif unit2 == "millimetres":
        finalValue = toBeConverted*1000
    elif unit2 == "miles":
        finalValue = toBeConverted/1609.344
    elif unit2 == "feet":
        finalValue = toBeConverted*3.28084
    elif unit2 == "inches":
        finalValue = toBeConverted*39.37
    elif unit2 == "yards":
        finalValue = toBeConverted*1.093613

    elif unit2 == "tons":
        finalValue = toBeConverted/1000
    elif unit2 == "kilograms":
        finalValue = toBeConverted
    elif unit2 == "grams":
        finalValue = toBeConverted*1000
    elif unit2 == "ounces":
        finalValue = toBeConverted*35.27396
    elif unit2 == "pounds":
        finalValue = toBeConverted*2.2046
    elif unit2 == "stones":
        finalValue = toBeConverted*0.15747

    elif unit2 == "litres":
        finalValue = toBeConverted
    elif unit2 == "millilitres":
        finalValue = toBeConverted*1000
    elif unit2 == "centilitres":
        finalValue = toBeConverted*100
    elif unit2 == "fluid ounces":
        finalValue = toBeConverted*35.195

    speech(str(number) + " " + unit1 + " is " + str(round(finalValue,3)).replace("." , " point ") + " " + unit2)
```

## Doing basic maths

What if we want to ask the assistant to perform calculations? I'll explain the basic multiplication, subtraction, and addition stuff, and if you want to make it better, you should be able to figure it out from what you learn here.

In the intenthandler, I added this function
```
def do_maths(operator, num1, num2):
  operator, num1, num2 = o["slots"]["operator"], o["slots"]["num1"], o["slots"]["num2"]
  if operator == "*":
    operator = " times "
    calcResult = str(num1*num2)
  elif operator == "+":
    operator = " add "
    calcResult = str(num1+num2)
  elif operator == "-":
    operator = " minus "
    calcResult = str(num1-num2)
  elif operator == "/":
    operator = " over "
    calcResult = str(num1/num2)
  if num1 == 9 and num2 == 10 and operator == " add ":
    speech("9 plus 10 is 21")
  else:
    speech(str(num1) + operator + str(num2) + " is " + calcResult.replace("." , " point "))
```

TESTING BIT=======
  # If asking for a mathematical operation
  elif ("plus" in words) or ("add" in words) or ("+" in words) or ("minus" in words) or ("take" in words) or ("-" in >
    #Extract numbers from statement
    numbers = []
    for word in words:
      if word.isdigit():
        numbers.append(int(word))
    #If there are 2 numbers
    if len(numbers) == 2:
      if (word == "plus") or (word == "add") or (word == "+"):
        print(str(numbers[0]) + " plus " + str(numbers[1]) + " equals " + str(numbers[0] + numbers[1]))
      elif (word == "minus") or (word == "take") or (word == "-"):
        print(str(numbers[0]) + " minus " + str(numbers[1]) + " equals " + str(numers[0] - numbers[1]))
==================

Basically, we make variables for the operator and both numbers from the incoming JSON, then just perform the operation, speaking the result. Once you've saved and exited, it should just work. Keep in mind, you've got to say your numbers quite quickly. Once your sentence is perceived to be complete, it will stop listening, even if you're still speaking. This means that if you say - for example - **"twenty seven"** too slowly, it may cut you off before you've said seven. This is why it was important to change your STT settings earlier, increasing `silence after` time.

# Making it smart
## Setting up Homeassistant
### If you've already got a homassistant instance, scroll down until we need our access tokens.
To set up homeassistant, first we need a docker-compose file, just like what we had for rhasspy.
So, run:
```
mkdir ~/hass
cd ~/hass
nano docker-compose.yml
```
And paste in:
```
version: '3'
services:
  homeassistant:
    container_name: homeassistant
    image: "ghcr.io/home-assistant/home-assistant:stable"
    volumes:
      - ./config:/config
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    privileged: true
    network_mode: host
```
Then, press CTRL+X, Y, Enter, to save and exit. After which, run
```
sudo docker-compose up -d
```
Once that's done, go to a browser on another machine on your network, and go to this URL: (or your already existing server's URL)
```
http://yourhostname.local:8123
```
Replacing 'yourhostname' with your hostname. It should look like this: (after the same security prompt as before)

![hass onboarding](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/hassonboarding.png)

Just type a name, username, and make a password, and press 'Create Account'

![hass make account](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/hassmakeaccoun.png)

Now, give your home a name and location, (plus elevation, if you'd like)

![hass name home](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/hassnamehome.png)

And choose which data to *opt-in* for. These are all disabled by default, however I'd ask that you consider turning on anything you're comfortable with, since it can help the devs.

![hass opt in](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/hassoptin.png)

Finally for the onboarding, just press finish! This page shows any services that homeassistant automatically found, but we'll set things up later.

![hass auto find](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/hassautofind.png)

Now, you should be on the main homeassistant page. Click your name in the bottom left, then scroll down to long-lived tokens.

![llat](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/llat.png)

Create one, name it whatever you'd like, and save it for a minute.

Go back to your rhasspy tab, then settings, scroll down to intent handler, and select local command.

![local intent handler](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/localcommandintents.png)

Then, press the green dropdown, and set the program to `/profiles/intentHandler`

Now, you can press save and restart.

While it's restarting, run this:
```
sudo nano ~/assistant/profiles/intentHandler
```
Then, paste this in [(we're building from the Rhasspy example)](https://github.com/synesthesiam/rhasspy/blob/master/bin/mock-commands/handle.py):
```
#!/usr/bin/env python

import sys
import json
import random
from datetime import datetime
import requests

def speech(text):
  print(json.dumps({"speech" : {"text" : text}}))

# Set paths
workingDir = "/profiles/"
tmpDir = workingDir + "tmp/"

# Set Homeassistant URL
hassurl = "http://YOUR-PI-IP:8123"
hassauth = ""
hassheaders = {"Authorization": "Bearer " + hassauth, "content-type": "application/json",}

# get json from stdin and load into python dict
o = json.loads(sys.stdin.read())

intent = o["intent"]["name"]

if intent == "GetTime":
    now = datetime.datetime.now()
    speech("It's %s %d %s." % (now.strftime('%H'), now.minute, now.strftime('%p')))

elif intent == "Greet":
    replies = ['Hi!', 'Hello!', 'Hey there!', 'Greetings.']
    speech(random.choice(replies))
```
Now, add your Pi's IP to the hassurl section, (and also in the request.post statement), and add your auth token to the hassauth section.

CTRL+X, Y, ENTER.

Then, run
```
sudo chmod +x ~/assistant/profiles/intentHandler
```
which will allow the script to be executed.

Now, go to rhasspy's web UI, click the wake button, and say out loud, "What time is it?". It should respond with the current time. If not, give it about 20 seconds, the TTS may be doing first-time setup.

Go to your terminal (still SSH'd into the Pi), and type 
```
sudo nano ~/hass/config/configuration.yaml
```

Go right to the top of the file, and look for the line `default_config:`. Go one line below it, and add exactly:
```
api:
```

Also, I highly recommend going some lines below, and pasting this, which will prevent homeassistant from taking up lots of space on your (presumably quite limited) Pi storage, and reduce disk usage, prolonging life:
```
# Remove history to save space
recorder:
  auto_purge:
  purge_keep_days: 14
  commit_interval: 30
```
Then, CTRL+X, Y, ENTER.

You can also run `sudo docker restart homeassistant` now too.

#### For all sections where there's lots of iteration and changing of code (e.g - Controlling smart lights, setting timers), you can choose to skip to the end of them for a finished code block that you can paste right into your intentHandler if you'd like. However, if you would like to understand how each bit works, you can pay attention to the whole section

# Features

## Controlling devices

So you know, there are more ways to accomplish things. I'll be describing the methods I use, but if there's a better method, please feel free to share, I'd appreciate it.

### First, we need a thing to control. 

This isn't a homeassistant tutorial, but if you've got any WLED devices, they should automatically appear in the devices section to be configured like this:

![Autoadd1](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/Autoadd1.png)
![Autoadd2](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/Autoadd2.png)
![Autoadd3](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/Autoadd3.png)

To check the device name, go to settings, then entities in Homeassistant. Then, click on the device you're intending to control. Note down the name at the bottom.

![Wled device in entities](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/wledentities.png)

Back in Rhasspy, click the circular "slots" tab,

![slot tab](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/slottab.png)

then make a new slot called lights. Within regular brackets, put the name you'd like to speak. If there are multiple, such as "Bed LEDS" and "Bedside LEDs", separate them with a pipe symbol (|). Then, immediately after the brackets, add a colon (:), and **without adding a space**, add the entity id from homeassistant. Here's what mine looks like with two lights.

![Light slot](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/lightslot.png)

Then, MAKE SURE YOU PRESS SAVE, and head back to your sentences section, remove what you've already got. If you want to use my setup, paste this in:
```
[SetSpecificLightPower]
light_name = ($lights){entity}
light_state = (on | off){state}
(set | turn) <light_state> [the] <light_name>
(set | turn) [the] <light_name> <light_state>
```
What's within the top square brackets is what the intent handler will recognise when checking what event is being sent. Then, we set two variables. light_name equals what's in our lights slot (we know we're talking about a slot because of the $), and light_state can be on or off. Again, **or** is represented by a pipe (|). [The next bit was taught to me by a post on the rhasspy community page. Credit to them for this config!](https://community.rhasspy.org/t/access-from-home-assistant-the-raw-value-in-slots-array/3497) Then, we make some sentences. I made two, so I can say things in different orders. The first would allow me to say **"Turn on the bedside light"**, and the second allows **"Turn the bedside light on"**. Arrow brackets reference variables, regular brackets reference groups of words, square brackets reference optional words, and curly brackets reference the name that the sent data will have in the JSON file that Rhasspy sends to homeassistant. When saving, remember to allow training.

While SSH'd into the pi, run
```
sudo nano ~/assistant/profiles/intentHandler
```
And paste this below the last elif statement:
```
elif intent == "SetSpecificLightPower":
    entity = o["slots"]["entity"]
    state = o["slots"]["state"]
    requests.post(hassurl+"/api/services/light/turn_"+state, headers = hassheaders, json = {"entity_id": entity})
    speech("Alright, I'll turn it " + state )
```

Anything within `speech()` will be spoken. 

### Now, we'll learn how to add colour.

Go back to your slots, add a new one called ```colours``` (the British spelling), and paste this:
```
(aqua | aquamarine | beige | black | blue | brown | chocolate | coral | crimson | cyan | firebrick | forest green | gold | gray | green | hot pink | indigo | khaki | lavender | light blue | light coral | light cyan | light green | light pink | light salmon | light yellow | lime | lime green | magenta | maroon | navy | olive | orange | orchid | pink | purple | red | salmon | tomato | violet | white | yellow)
```
It actually supports all colours in [this list](https://www.w3.org/TR/css-color-3/#svg-color), so if I omitted your favourite colour, you can add it as long as it's in the page on that link. MAKE SURE WHENEVER YOU ADD SLOTS OR SENTENCES, YOU SAVE THEM.

![Colour slot](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/colourslotcorrected.png)

Then, in your sentences section, add this:
```
[SetSpecificLightColour]
light_name = ($lights){entity}
light_colour = ($colours){colour}
(set | turn | make) [the] <light_name> <light_colour>
```

Then, run:
```
sudo nano ~/assistant/profiles/intentHandler
```
We'll paste another elif block, very similar to our last:
```
elif intent == "SetSpecificLightColour":
    entity = o["slots"]["entity"]
    colour = o["slots"]["colour"]
    requests.post(hassurl+"/api/services/light/turn_on", headers = hassheaders, json = {"entity_id": entity, "color_name" : colour})
    speech("Alright, I'll make it " + colour )
```
Once you've saved an exited, it should work immediately. 

### Adding brightness settings

It would be nice to be able to control brightness, but we can't yet, so let's add it.

First, go back into your intentHandler file:
```
sudo nano ~/assistant/profiles/intentHandler
```
And add this elif statement, just like the colour one:
```
elif intent == "SetSpecificLightBrightness":
    entity = o["slots"]["entity"]
    brightness = o["slots"]["brightness"]
    requests.post(hassurl+"/api/services/light/turn_on", headers = hassheaders, json = {"entity_id": entity, "brightness_pct" : brightness})
    speech("Alright, I'll make it " + str(brightness) + " percent")
```
You can probably see how things work now, based on how little has changed from the version of that code which modifies colour instead.

Go to rhasspy's web ui at `yourip:12101`, then click sentences on the left, and add this:

```
[SetSpecificLightBrightness]
light_name = ($lights){entity}
(set | turn | make) [the] <light_name> [to] (1..100){brightness} percent [brightness]
```

Save and retrain rhasspy, and things should work.

### Finished code blocks (remember to still change any needed variables if applicable)

#### Changing light power
Code
```
elif intent == "SetSpecificLightPower":
  entity, state = o["slots"]["entity"], o["slots"]["state"]
  requests.post(hassurl+"/api/events/assistant_"+intent, headers = hassheaders, json = {"entity": entity,"state": state})
  speech("Alright, I'll turn it " + state )
```
Sentence
```
[SetSpecificLightPower]
light_name = ($lights){entity}
light_state = (on | off){state}
(set | turn) <light_state> [the] <light_name>
(set | turn) [the] <light_name> <light_state>
```

#### Changing light colour
Code
```
elif intent == "SetSpecificLightColour":
  entity, colour = o["slots"]["entity"], o["slots"]["colour"]
  requests.post(hassurl+"/api/events/assistant_"+intent, headers = hassheaders, json = {"entity": entity,"colour": colour})
  speech("Alright, I'll make it " + colour )
```
Sentence
```
[SetSpecificLightColour]
light_name = ($lights){entity}
light_colour = ($colours){colour}
(set | turn | make) [the] <light_name> <light_colour>
```
#### Changing light brightness
Code
```
elif intent == "SetSpecificLightBrightness":
  entity, brightness = o["slots"]["entity"], o["slots"]["brightness"]
  requests.post(hassurl+"/api/events/assistant_"+intent, headers = hassheaders, json = {"entity": entity,"brightness": brightness})
  speech("Alright, I'll make it " + str(brightness) + " percent")
```
Sentence
```
[SetSpecificLightBrightness]
light_name = ($lights){entity}
(set | turn | make) [the] <light_name> [to] (1..100){brightness} percent [brightness]
```

# Resources
There's a folder called resources in this git repo. It contains any files of mine (or somebody else's, if they're ok with it) that you might want. Any API keys or related stuff in code will be blocked out, however they're otherwise unmodified.








# Extras
[Rhasspy Documentation](https://rhasspy.readthedocs.io)

[Homeassistant Documentation](https://www.home-assistant.io/docs/)
