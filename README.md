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

* Set hostname to whatever you want to call it. I chose assistant-main-node
* Enable SSH 
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

## Installing things
Run
```
curl -sSL https://get.docker.com | sh
sudo apt-get install -y uidmap libffi-dev libssl-dev python3 python3-pip python3-dev
sudo pip3 install docker-compose
sudo gpasswd -a $USER docker
```
to install docker and docker compose. This may take a while.

Then run

Then, to install rhasspy, run
```
mkdir assistant
cd assistant
nano docker-compose.yml
```
and paste in the following. This will be much easier if being run from another PC through SSH, since indentation must be exactly correct.
```
version: '3.3'
services:
    rhasspy:
        container_name: rhasspy
        ports:
            - '12101:12101'
            - '12183:12183'
        volumes:
            - './profiles:/profiles'
            - '/etc/localtime:/etc/localtime:ro'
            - '/dev/shm/tmpassistant:/profiles/tmp'

        devices:
            - '/dev/snd:/dev/snd'
        image: rhasspy/rhasspy
        command: --user-profiles /profiles --profile en
        restart: unless-stopped
```
Then, press CTRL+X, Y, Enter, to save and exit. After which, you can just run
```
sudo docker-compose up -d
```
to begin installing. This, again, may take a while. You'll know it's done once you see this:
![Install complete](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/donedocker.png)

# Initally setting up rhasspy
In a browser on the same network as your Pi, go to this site, changing 'your-ip' to your pi's IP we set before (hostname can work too, but sometimes it causes issues).
```
http://your-ip.local:12101
```
Your browser *should* complain that this site is not secure. If it was a site on the internet, you wouldn't want to access it, however it's just local, so we can tell the browser that we want to continue.

![https issue](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/httpsonly.png)

### And now you'll be here!
![Rhasspy main page](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/rhasspyhome.png)

Then, go to the settings page using the left-side menu. Go through each service, and - for now - just select the default from the dropdown menu. Then, press the save settings button below the list, and restart. Once restarted, go to the top of the page, and press download. After that's done, things should look like this.

![Settings page with defaults selected](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/settingdefault.png)

## Testing things

### Testing audio output
#### Plug something in using the Pi's 3.5mm jack.

To test audio output, go back to the home page, and type something into the 'speak' box, and see if it comes out of your speakers. 

![AudioTest](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/audiotest.png)

It will likely sound quite bad, but should work.

### Testing audio input
#### Plug a USB microphone into a USB port

To test audio input, press 'Wake Up' on the home page, and say "What time is it?". If it hears you, you'll get a response, and the UI will update to show this:

![AudioInputWorks](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/audioinputworks.png)

If there's no response, try relaunching rhasspy. This may get your mic detected if it wasn't before, and can be done by running:
```
sudo docker restart rhasspy
```

## Some improvements
### TTS
I reccommend going back to the settings page, switching your **Text To Speech** to `Larynx`, pressing refresh, and choosing a voice you think sounds good. **Southern-english-female** is - at this point in writing - my chosen voice, since higher-pitched voices will work better for voice assistants due to them often using small speakers with little bass response, and I believe it to be the most natural sounding. **Low Quality Vocoder** is perfectly fine, as you'll see when you test it, and is necesary for fast responses on a Pi. Though, **Larynx takes around 15 seconds to initialise each time you reboot, and doesn't do this automatically,** meaning the first question you ask will be highly delayed. 

### Remember to save your settings and restart afterwards.

![TTSsettings](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/Texttospeech.png)

### Wake word
To wake things without using the web UI, you *could* set a custom word using **Rhasspy Raven,** however I had trouble with being recognised. Instead, I use **Porcupine**. I just went into porcupine's dropdown, pressed refresh, and selected one from the list, and I'd suggest you do the same. I also increased the sensitivity to **0.75** so it can pick me up when I'm quieter. I suggest you do your own experimentation with this to find the best balance between false positives and false negatives. Save and restart, and it should work.

![Wakeword settings](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/Wakewordsetting.png)

### STT
In your speech to text settings, I highly recommend going to the bottom, and changing `silence after` to one second, which gives you some time to pause during speech during a potentially valid sentence. For example, if I say **"What's ten plus one hundred and twenty... seven"**, there's a decent chance that it'll cut me off before I say the 7, since 120 is also a valid word.

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
import datetime
import requests

def speech(text):
  requests.post("http://YOUR-PI-IP:12101/api/text-to-speech", headers = {"content-type": "text/plain"}, data = text)

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
sudo nano ~/hass/config/automations.yaml
```
Then, paste this in some empty space (remove square brackets if there):
```
- alias: "Turn on/off specific light"
  trigger:
  - event_data: {}
    platform: event
    event_type: assistant_SetSpecificLightPower
  action:
     - service: light.turn_{{trigger.event.data.state}}
       data:
         entity_id: "{{trigger.event.data.entity}}"
```
If you changed what's within the square brackets in the sentence section, change what's after `assistant_` to match. Otherwise, things should just work. Now, go to homeassistant's dev tools, YAML, and reload automations. 

Now, run:
```
sudo nano ~/assistant/profiles/intentHandler
```
And paste this below the last elif statement:
```
elif intent == "SetSpecificLightPower":
    entity = o["slots"]["entity"]
    state = o["slots"]["state"]
    requests.post(hassurl+"/api/events/assistant_"+intent, headers = hassheaders, json = {"entity": entity,"state": state})
    speech("Alright, I'll turn it " + state )
```

Anything within `speech()` will be spoken. 

### Now, we'll learn how to add colour.

Go back to your slots, add a new one called ```colours``` (the British spelling), and paste this:
```
(aqua | aquamarine | beige | black | blue | brown | chocolate | coral | crimson | cyan | firebrick | forest green | gold | gray | green | hot pink | indigo | khaki | lavender | light blue | light coral | light cyan | light green | light pink | light salmon | light yellow | lime | lime green | magenta | maroon | navy | olive | orange | orchid | pink | purple | red | salmon | tomato | violet | white | yellow)
```
It actually supports all colours in [this list](https://www.w3.org/TR/css-color-3/#svg-color), so if I omitted your favourite colour, you can add it as long as it's in the page on that link.

![Colour slot](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/colourslotcorrected.png)

Then, in your sentences section, add this:
```
[SetSpecificLightColour]
light_name = ($lights){entity}
light_colour = ($colours){colour}
(set | turn | make) [the] <light_name> <light_colour>
```

Finally, go back to your terminal with automations.yaml open, and paste this below your power config:
```
- alias: "Set specific light colour"
  trigger:
  - event_data: {}
    platform: event
    event_type: assistant_SetSpecificLightColour
  action:
     - service: light.turn_on
       data:
         entity_id: "{{trigger.event.data.entity}}"
         color_name: "{{trigger.event.data.colour}}"
```

All you should need to change is the event_type if you decided to name things differently. Save and exit (CTRL+X, Y, ENTER), then reload your automations in homeassistant. 

Then, run:
```
sudo nano ~/assistant/profiles/intentHandler
```
We'll paste another elif block, very similar to our last:
```
elif intent == "SetSpecificLightColour":
    entity = o["slots"]["entity"]
    colour = o["slots"]["colour"]
    requests.post(hassurl+"/api/events/assistant_"+intent, headers = hassheaders, json = {"entity": entity,"colour": colour})
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
    requests.post(hassurl+"/api/events/assistant_"+intent, headers = hassheaders, json = {"entity": entity,"brightness": brightness})
    speech("Alright, I'll make it " + str(brightness) + " percent")
```
You can probably see how things work now, based on how little has changed from the version of that code which modifies colour instead.

Now, go to your automations.yaml file:
```
sudo nano ~/hass/config/automations.yaml
```
and at the bottom, paste this:
```
- alias: "Set specific light brightness"
  trigger:
  - event_data: {}
    platform: event
    event_type: assistant_SetSpecificLightBrightness
  action:
     - service: light.turn_on
       data:
         entity_id: "{{trigger.event.data.entity}}"
         brightness_pct: "{{trigger.event.data.brightness}}"
```

All that's left is to reload your automations.yaml (if you don't remember, that's **developer tools --> yaml --> reload automations**) and add your Rhasspy sentences.

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

## Doing basic maths

What if we want to ask the assistant to perform calculations? I'll explain the basic multiplication, subtraction, and addition stuff, and if you want to make it better, you should be able to figure it out from what you learn here.

First, go back to the slots section in the left menu.

![slot tab](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/slottab.png)

Then, we'll define our operations. Make a new slot called **"operations"**, then paste this in:
```
(add | plus):+
(times | multiplied by):*
(minus | subtract | take | take away):-
(divided by | over):/
```
If you'd like to be able to call a certain operation with another word, just add it within the brackets, along with a pipe (|) symbol to separate it from the other words. Save this.

Now, go to the sentences tab, and add a [DoMaths] section. Paste in what's below:
```
[DoMaths]
operator = ($operators){operator}
what is (-1000..1000){num1} <operator> (-1000..1000){num2}
```
This lets us perform those three operations on two numbers between -1000 and 1000. You can increase the range by changing the numbers at either end of the two dots (**".."**), but I was concerned that the assistant may find it harder to tell exactly what number you're saying as the range of numbers increases, so 1000 seemed an alright compromise.

Finally, head over to the intentHandler by running:
```
sudo nano ~/assistant/profiles/intentHandler
```
And paste this below the last elif section:
```
elif intent == "DoMaths":
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


Basically, we make variables for the operator and both numbers from the incoming JSON, then just perform the operation, speaking the result. Once you've saved and exited, it should just work. Keep in mind, you've got to say your numbers quite quickly. Once your sentence is perceived to be complete, it will stop listening, even if you're still speaking. This means that if you say - for example - **"twenty seven"** too slowly, it may cut you off before you've said seven. This is why it was important to change your STT settings earlier, increasing `silence after` time.

## Setting timers
What if you want to set a timer? It's not a super complex one, you can only pick minutes **or** seconds, meaning you couldn't ask for a 2 minute and 17 second timer, but it works well enough.

Go to your sentences section, and add this:
```
[DoTimer]
(set | make | start) a (1..60){time} (second | minute){unit} timer
```
Remember to save and train.

Then, go to the intentHandler script (`sudo nano ~/assistant/profiles/intentHandler`) and paste this below the last elif statement:

```
elif intent == "DoTimer":
  number, unit = o["slots"]["time"], o["slots"]["unit"]
  speech("Alright, i'll set a " + str(number) + " " + unit + " timer")
  if unit == "second":
    timerLength = number-1
  elif unit == "minute":
    timerLength = (number*60)-1
  while timerLength:
    time.sleep(1)
    timerLength -=1
  speech("Timer complete")
```
It receives a number between 1-60, and the unit (whether you said "Seconds" or "Minutes"). It then sets a variable to the correct number of seconds, either by taking 1 away from the number you said, or multiplying it by 60, then still removing one. Afterwards, it just runs a timer, and will speak once it's complete. You can still run other voice commands while the timer is running.

### But that's not a great way of announcing the completion of a timer

We want a sound. Let's get one. If you've got something on your computer (a .wav file), you can copy it over to the Pi by running the first section ON YOUR PC, NOT THE PI's SSH SESSION(and if you've not got one yet, you can find one at the bottom of this section)
:

```
scp pathtoyourfile piusername@pihostname:/home/assistant-main-node/
```
Then, on the pi, you can do
```
sudo cp /home/assistant-main-node/yourfile.wav ~/assistant/profiles
```

Replace pathtoyourfile with the path to your wav file. Replace piusername with the username you picked for your Pi. Replace hostname with the hostname you picked for your Pi. If you're using the same file structure and docker compose files as me, you can keep the rest of the command the same. When you press enter, it'll ask for your Pi's password. This copies your file to the Pi over ssh. If you choose another method to get the file to the Pi, that's fine, just make sure it's in a directory accessible from the docker container, which is why I chose the profiles folder. I made my own sounds (which can be found in the resources folder of this guide), however I don't use them, and might repurpose them - they were just two notes played on a digital keyboard. The sound I actually ended up using was [a royalty free one which reminded me of an aeroplane announcement system.](https://soundbible.com/1598-Electronic-Chime.html) I trimmed the empty bits off of that sound, [and reuploaded it if you'd like to use it too.](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/blob/main/resources/sounds/timerchime.wav)

Now, go to the top of your intentHandler script, and add `from subprocess import call`.

And on another line, add 
```
import os
import time
```

Then, go back down to your DoTimer section, and add these lines right to the top of the elif statement (ensure indentation matches the rest of the code):
```
timerFinishedAudio = workingDir+"yourfile.wav"
if os.path.exists(stopTimerFilePath):
    os.remove(stopTimerFilePath)
```
We'll be looping a small piece of audio until we detect a file that tells us to stop, which will be made when we say the voice command **"stop"**. This bit of code was necessary to make sure the file isn't already there incase the user was detected to be saying **"stop"** while a sound wasn't going off. Remember again to replace **"yourfile.wav"** with the name of your file.

Now, you can replace the `speech("Timer complete")` line with this:
```
while not os.path.exists(stopTimerFilePath):
  call(["aplay", timerFinishedAudio])
if os.path.exists(stopTimerFilePath):
  os.remove(stopTimerFilePath)
```

If you were now to ask for a timer, it would finish by infinitely repeating whatever your sound is. We can fix this by making a new elif statement below:
```
elif intent == "StopTimer":
  stopTimerFile = open(stopTimerFilePath, 'w')
  stopTimerFile.close()
```

Now, go to the top of the file, and paste this:
```
# Set paths
workingDir = "/profiles/"
stopTimerFilePath = workingDir+"tmp/"+"stopTimerFile"
```

If you're using a different file structure, you can change the data inside the workingDir variable. In this case, we're actually saving things to memory to cut down on drive access. Remember to save and exit (CTRL+X, Y, ENTER)

Now, go to your rhasspy sentences section, and make a new section that looks like this:
```
[StopTimerSound]
stop [the] (alarm)
```
Remember to save and retrain Rhasspy once done. Now, you should be able to ask for a quick one second timer, then while the audio is looping, ask it to stop the alarm. Once the current loop is over, it will finish. **Once we've completed the timer section, there'll be a section about adding a generic "stop" function that applies to everything. If you want to be able to stop the timer by just saying "stop", you can go there now if you'd like.**

### Some notes about the audio
Due to it finishing the current audio loop before stopping, I suggest having a simple sub-5 second sound. Anything long will take a very long time to stop after you ask it to. It's not ideal, but it works, and even this solution took me hours to figure out. I just used an [electronic chime licensed under the Public Domain.](https://soundbible.com/1598-Electronic-Chime.html) Though, there was quite a bit of empty space at the end of that audio file, so I've trimmed it, [and uploaded it here.](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/blob/main/resources/sounds/timerchime.wav)

### Check Timer Progress While Running
Ideally, you could ask the assistant how far along the timer is. Let's make that.

First, add a variable to the top of your intentHandler in the `# Set paths` section called timerLeftPath, and set it to `workingDir+"tmp/"+"timerLeft"`. Then, within your `while timerLength` loop, add this to the bottom (ensure indentation stays correct):
```
timerLeft = open(timerLeftPath, "w")
timerLeft.write(str(timerLength))
```

Then, at the bottom of your **DoTimer** intent, duplicate your already existing section which deletes your stopfile, and change `stopFilePath` to `timerLeftPath`. It should look like this:
```
if os.path.exists(timerLeftPath):
  os.remove(timerLeftPath)
```
Now we've got a file that contains the number of seconds remaining, and it'll delete itself once the timer is done.

Go to the bottom of your intentHandler, and paste this:
```
elif intent == "TimerRemaining":
  if os.path.exists(timerLeftPath):
    timerRemainingNumber = int(open(timerLeftPath, "r").read()) - 3
    if timerRemainingNumber >= 60:
      speech("There are " + str(math.trunc(timerRemainingNumber/60)) + " minutes and " + str(timerRemainingNumber % 60) + " seconds left")
    else:
      speech("There are " + str(timerRemainingNumber) + " seconds left")
  else:
    speech("You've got no timers set")
```
This checks if the file exists, and if it does, checks whether the time remaining should be measured in minutes (number is > 60) or seconds (number is < 60). Then, if minutes are needed, we divide the number of seconds by 60, then truncate (remove **but not round** the decimals) it, as well as telling us the number of seconds by finding the remainder when dividing by 60. If just seconds are needed, we only need to speak the number we've gotten from the file. Also, since I expect the words to be spoken 3-ish seconds after reading the value, I remove 3 from the number we get at the start.

In here, we use the **math** library, so you'll want to go to the top of your file, and add ```import math``` too.

Now, in rhasspy's sentences tab, you just need to add this:
```
[TimerRemaining]
how long left on timer
what is [the] timer [at]
```
The broken English is intentional, since our speech-to-text system will turn whatever you say into the *closest* sentence possible, so having a shorter sentence that misses words is alright, and I believe *(with no tested evidence)* that it could speed things up.

### Cancelling a timer

But what if you decide that you don't want your timer anymore? (or, more likely, STT picks up the wrong number)

We'll use the stop file for this too. If you ask it to stop before the timer's done, it'll cancel. 

Within the `while timerLength` section, at the end of it, add this, which will stop the timer if it detects the cancel file:

```
if os.path.exists(stopTimerFilePath):
  speech("Timer cancelled")
  break
```

We'll now be working within the `while not os.path.exists(stopTimerFilePath)` section.

At the same level of indentation as the `call aplay` line, right at the top, add:
```
if os.path.exists(stopTimerFilePath):
  break
else:
```
Then, correct your `call aplay` line to be at the right level of indentation.

Now, add a new elif statement for making the cancelFile:

And remember, if you don't like *anything at all* about how I handle things, **you can change it**. All of the code is free for you to make exactly how you like it, even for things as basic as how you phrase sentences. You don't need to follow everything verbatim, but you can, it's up to you.

### Adding validation to the `stopTimer` section

Now that we can know whether a timer's running (because of the timerLeft file), let's also use it to help the stopTimer bit.
```
elif intent == "StopTimerSound":
  if os.path.exists(timerLeftPath):
    stopTimerSoundFile = open(stopTimerSoundFilePath, "w")
    stopTimerSoundFile.close()
  else:
    speech("You've got no timers set")
```

Change it to the above code, and if you try to stop a timer that's not running, it'll tell you.

### The end result
This timer section was massive. My code at the end of it looks like this:
```
elif intent == "DoTimer":
  number, unit = o["slots"]["time"], o["slots"]["unit"]
  speech("Alright, i'll set a " + str(number) + " " + unit + " timer")
  timerFinishedAudio = workingDir+"timerchime.wav"
  if os.path.exists(stopTimerFilePath):
    os.remove(stopTimerFilePath)
  if unit == "second":
    timerLength = number-1
  elif unit == "minute":
    timerLength = (number*60)-1
  while timerLength:
    time.sleep(1)
    timerLength -=1
    timerLeft = open(timerLeftPath, "w")
    timerLeft.write(str(timerLength))
    if os.path.exists(stopTimerFilePath):
      speech("Timer cancelled")
      break
  while not os.path.exists(stopTimerFilePath):
    if os.path.exists(stopTimerFilePath):
      break
    else:
      call(["aplay", timerFinishedAudio])
  if os.path.exists(stopTimerFilePath):
    os.remove(stopTimerFilePath)
  if os.path.exists(timerLeftPath):
    os.remove(timerLeftPath)
```
Here's the StopTimerSound section:
```
elif intent == "StopTimer":
  if os.path.exists(timerLeftPath):
    stopTimerFile = open(stopTimerFilePath, "w")
    stopTimerFile.close()
  else:
    speech("You've got no timers set")
```

And here's the TimerRemaining section:
```
elif intent == "TimerRemaining":
  if os.path.exists(timerLeftPath):
    timerRemainingNumber = int(open(timerLeftPath, "r").read()) - 3
    if timerRemainingNumber >= 60:
      speech("There are " + str(math.trunc(timerRemainingNumber/60)) + " minutes and " + str(timerRemainingNumber % 60) + " seconds left")
    else:
      speech("There are " + str(timerRemainingNumber) + " seconds left")
  else:
    speech("You've got no timers set")
```

## Generic stop function
In the future, we might have other things that we'd like to stop, such as music playback, which is why I made the "timer stop" it's own separate thing. I'd still like to be able to just say "stop", so we'll add another intent which just stops everything. 

First, we'll add the sentence, since it's the most basic part. Go to your rhasspy web UI, sentences, and paste this:
```
[GenericStop]
stop
```
Wonderful.

Now, we'll add this code to the end of our intentHandler, which says that - if we're not specifically told ***what***  we're stopping - we'll stop everything:
```
elif intent == "GenericStop":
  open(stopTimerFilePath, "w")
```
As you can see, we're just stopping the timer right now, but the point of this intent is that we'll add anything else that can be stopped here too. This'll be mentioned in the relevant sections. For now, you can save and exit.

## The weather
What if I want it to tell me the weather?

First, go to [openweathermap](https://openweathermap.org/) and sign up for a free account. Then, check your email for an API key. It's important to do this first, since they key will take a little bit to properly activate. Then, you can go to your rhasspy sentences tab, and add this:
```
[GetWeather]
(what's | tell me) the (weather | temperature)
how (hot | cold | warm ) is it [today | right now]
```
If you want to customise the way you speak to it, you can do it from here. Remember to save and train.

Then, go to your intent handler, and below the last elif statement, paste this:
```
elif intent == "GetWeather":
  opnwthrurl = "https://api.openweathermap.org/data/2.5/weather?"
  opnwthrauth = "YOURAUTHKEY"
  opnwthrlat, opnwthrlon = "LAT" , "LONG"
  opnwthrunits = "metric"
  weather = requests.get(opnwthrurl+"lat="+opnwthrlat+"&lon="+opnwthrlon+"&units="+opnwthrunits+"&appid="+opnwthrauth).json()
  currentTemp = weather["main"]["temp"]
  currentDesc = weather["weather"][0]["description"]
  speech("It's currently " + str(round(currentTemp)) + " degrees and " + currentDesc)
```
Change **YOURAUTHKEY** to your api key from openweathermap, and **LAT** / **LONG** to your current latitude and longitude. They don't have to be exactly on your location, but you can use a tool [like this](https://www.latlong.net/) to get the numbers for your general area.

Then, save and exit, and ask your assistant **"What's the weather"**, and it should tell you the current temperature, along with two words to describe it, like **Clear Sky** or **Scattered Clouds**.

## Getting the time (but better)

### The examples provided by Rhasspy can already do this...

but we can do it better. It normally responds in 24-hour (at least, it does for me, though my system is set to 24-hour), which is great for reading the time, but not for speaking it. Also, despite technically telling our assistant to say whether it's AM or PM, it sends the strings "am" and "pm", meaning that they're pronounced very awkwardly. To fix this, you can replace the GetTime intent near the top of the intentHandler with this:

```
if intent == "GetTime":
    now = datetime.datetime.now()
    if now.strftime('%p') == "PM":
        apm = "peey em"
    else:
        apm = "ey em"
    if now.strftime('%M') == 00:
        speech("Its " + now.strftime('%I') + " " + apm)
    else:
        speech("Its " + now.strftime('%I') + " " + now.strftime('%M') + " " + apm)
```
Basically, we check whether it's AM or PM, and get the 12-hour time, and then just format it in a nice way for speech. It's really simple.

I know that **"Its"** should have an apostrophe to represent a contraction, and it annoys me too, a lot, however I'm trying to avoid extra symbols when necessary.

Then, at the top of your python file, paste this:

```
from datetime import datetime
```

Because of the interesitng methods of writing AM ("ey em") and PM ("peey em"), this might not sound right if you use a different TTS voice to me. However, on the southern english female voice for larynx, they sound much better than the deault, and it now speaks in 12-hour.

Also, I earlier asked you to remove all of the predone sentences in rhasspy, which would include the GetTime ones. Here's what to add to your sentences:
```
[GetTime]
what's [the] time
tell [me the] time
what time [is it]
```

## Getting the date

Add this elif statement:

```
elif intent == "GetDate":
    months = [" January ", " February ", " March ", " April ", " May ", " June ", " July ", " August ", " September ", " October ", " November ", " December "]
    weekdays = [" Monday ", " Tuesday ", " Wednesday ", " Thursday ", " Friday ", " Saturday ", " Sunday "]
    dayNum = datetime.now().day
    month = months[(datetime.now().month)-1]
    weekday = weekdays[datetime.today().weekday()]
    speech(random.choice(currentlyResponse) + weekday + "the " + str(dayNum) + " of" + month)
```

We get a number for the day of the month, day of week, and month (so, Jan is 1, Dec is 12), then convert these to words using lists. Then, we speak a sentence which puts it all together.

Go to your Rhasspy sentences section, and add this:
```
[GetDate]
what date [is it]
whats [the] date
tell me [the] date
whats today
```
Save and retrain, and it should work.

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
elif intent == "Greet":
    replies = ['Hi!', 'Hello!', 'Hey there!', 'Greetings.']
    speech(random.choice(replies))
```

If the intent is **"Greet"**, we make a list of items, each of which is a string. In this case, they're just different ways of greeting the user. Then, we randomly pick one of the items and say t. If you want to add extra things to say, just add a string to the list. 

I at some point intend to make it aware of the time so it can correct you if you mistakenly say **Good Morning** in the **Evening** (or vice versa).

## Bluetooth Audio Streaming
You can use an Echo or Google Home as a bluetooth speaker, why not this?

First, run this to install all of the (originally difficult for me to find) dependencies

```
sudo apt-get install libdbus-glib-1-2 libdbus-glib-1-dev python3-gi python3-gst-1.0
sudo pip install dbus-python
```

Then, paste this into your terminal
```
sudo hostnamectl --pretty set-hostname ""
```
and put what you want the speaker to appear as within the quotes. So, if you put "Issac Bedroom Speaker", it would appear to your phone like this:
![Issac Bedroom Speaker in Bluetooth settings](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/issacbedroomspeaker.png)

Then, run 
```
sudo nano /etc/bluetooth/main.conf
```
and go to the `#DiscoverableTimeout` line. Remove the #, and set it to `DiscoverableTimeout = 30`

Then `CTRL+X, Y, ENTER` to save and exit.

Now, run `sudo reboot now` to reboot and apply these changes.

Once you're back in, run this to download the script that makes your Pi visible as a bluetooth speaker
```
cd ~/assistant/
sudo curl -O https://raw.githubusercontent.com/elwint/bt-audio/master/bt-audio.py
```

Now, run this to install some dependencies and begin editing your intentHandler:
```
sudo apt install pulseaudio-module-bluetooth
sudo nano ~/assistant/profiles/intentHandler
```

and go to near the bottom, where you'll add another elif statement:
```
elif intent == "BluetoothPairing":
    bleutoothFile = open(bluetoothFilePath, "w") 
    time.sleep(0.1)
    bluetoothFile.close()
    os.remove(bluetoothFilePath)
    speech("Turning on bluetooth pairing")
```

Then, go to the `# Set paths` section at the top, and add 
```
bluetoothFilePath = workingDir+"tmp/"+"bluetoothFile"
```
Save and exit.

Then run this to create a new system service (which will handle the bt-audio script)
```
sudo nano /etc/systemd/system/speakerbluetoothpair.service
```
and paste in
```
[Unit]
Description=Starts bluetooth pairing script

[Service]
Type=oneshot
ExecStart=/home/assistant-main-node/assistant/bt-audio.py
```
(replace assistant-main-node with your username if different).

Save and exit.

Then, make practically the same thing by running:
```
sudo nano /etc/systemd/system/speakerbluetoothpairstop.service
```
and pasting:
```
[Unit]
Description=Stops bluetooth pairing script after 30s

[Service]
Type=oneshot
ExecStart=/home/assistant-main-node/assistant/stop-bluetooth-pairing.sh
```
(replace assistant-main-node with your username if different). This 2nd service just kills that previous service once it's not needed anymore.

Then, we'll make two more services, which handle *enabling* the previous two. 
```
sudo nano /etc/systemd/system/speakerbluetoothpair.path
```
And paste in:
```
[Unit]
Description=Checks for bluetooth pairing file from rhasspy to start pairing

[Path]
PathExists=/dev/shm/tmpassistant/bluetoothFile

[Install]
WantedBy=multi-user.target
```

And again, for the second, run
```
sudo nano /etc/systemd/system/speakerbluetoothpairstop.path
```
And paste in:
```
[Unit]
Description=Checks for bluetooth pairing file from rhasspy to stop pairing

[Path]
PathExists=/dev/shm/tmpassistant/bluetoothFile

[Install]
WantedBy=multi-user.target
```


CTRL+X+Y to save and exit.

Now, let's make the script which is used to stop the first service:
```
sudo nano ~/assistant/stop-bluetooth-pairing.sh
```
and add
```
#!/bin/sh
sleep 30
systemctl stop speakerbluetoothpair.service
systemctl reset-failed speakerbluetoothpair.service
```

And finally run this to add permissions and enable services: 
```
sudo chmod +x ~/assistant/stop-bluetooth-pairing.sh
sudo chmod +x ~/assistant/bt-audio.py
sudo systemctl enable speakerbluetoothpair.path --now
sudo systemctl enable speakerbluetoothpairstop.path --now
```

Then, go to your rhasspy sentences section, and paste this at the bottom:
```
[BluetoothPairing]
turn on bluetooth [pairing]
```

Then `sudo reboot now` to reboot.


**It's a mess, but it works.**

Except for if you re-pair your phone. It likely won't let you re-pair.

To fix that, there's no elegant solution right now. Open the terminal, run `bluetoothctl`, then type `remove `, press tab, and it'll either fill something in, or give you a list of options. If it fills something in, just press enter and you're done. If you've got a list, type the first letter of one, press tab, then enter, and do that for each item in the list.

### Optimal.

## Natural and varied responses

Right now, the assistant will always respond in the same way to a given request. This is easy to program, but not very natural, and we can make it better.

If you were paying attention to the **greetings** section, you'll probably understand how we'll implement this. All we need is a list of potential appropriate phrases, and then we pick a random one to speak each time.

First, we need to figure out what we want it to say, and which possible situations they're appropriate for. For example, after turning on a light, it would make sense to preface "I'll turn it on" with **Ok / Alright / Will do / Got it / Sure**, but it wouldn't make sense to have that same list of words when answering a maths question.

So, get into your intentHandler:
```
sudo nano ~/assistant/profiles/intentHandler
```
and go to just below your `# Set paths` section.

Add a new section called `# Set responses`. Then, add your responses below - here's how you would add the example from before:
```
agreeResponse = ["Okay, ", "Alright, ", "Will do. ", "Got it, ", "Sure, "] 
```
In this case, I want a small pause after the phrase, so I've added a comma and a space within the quotes for all of them, and used a comma after the parenthesis to separate each one. 

Now, I can go down to the `SetSpecificLight` sections, and change this:
```
speech("Alright, I'll make it " + colour)
```
to this (doing the same change for all light sections):
```
speech(random.choice(agreeResponse) + "I'll make it " + colour)
```
All we've actually done is make it pick a random string from the list we made instead of just saying **"Alright, "**. If we just saved and exited here, it would work.

### But we can add it to other situations, like the time and weather

Back in the `# Set responses` section, I've added this line:
```
currentlyResponse = ["Right now it's ", "Its ", "Currently its ", "At the moment its "]
```
Then, in the `GetTime` and `GetWeather` sections, we can replace the `"Its "` with
```
random.choice(currentlyResponse)
```

I've also added it to the timer section, so I've replaced this:
```
speech("Alright, I'll set a " + str(number) + " " + unit + " timer")
```
with this:
```
speech(random.choice(agreeResponse) + "I'll set a " + str(number) + " " + unit + " timer")
```


### We could also implement different options for individual responses. 

For example, when cancelling a timer, I could add:
```
timerCancelResponse = ["Timer cancelled", "Cancelling timer", "I'll cancel the timer"]
```
and then just set it to pick one of those:
```
speech(random.choice(timerCancelResponse))
```

### Or different ways of saying AM / PM

We can add `morningResponse = [" in the morning", " ey em"]` and then `eveningResponse = [" in the afternoon", " in the evening", " peey em"]`

**(remember from the timer bit, AM and PM are spelt weirdly so that they're spoken correctly with my TTS choice. They might need changing for whatever voice you choose personally)**

Now, we go down to the `if intent == "GetTime":` section, and make the a/pm variable sections with:
```
apm = random.choice(eveningResponse)
```
then the next one is
```
apm = random.choice(morningResponse)
```
and now your time announcements should be a bit more varied than before.

The way we're doing this is really simple and flexible, but makes the responses less repetitive. I like it.

## Jellyfin Music Support
We can talk to the Jellyfin API to get music from a server, and integrate it with our speech-to-text so that all artists, songs, and albums are recognised.

Progress made on this integration happens [here](https://gitlab.com/issacdowling/jellypy).

#### Here is a reminder to myself to make this into a slots program eventually so that it's even more hands-off.

#### Also, authenticating in a way that makes sense will come one day.

But that's not how things are right now, so the setup is weird, but it works.

### Making the slot files

Firstly, we'll make our slots. This is how the voice assistant will understand what words are valid, and luckily, is automated.

Automated once you've added the info from your Jellyfin server manually. So, on your Pi, run this:

```
cd ~/assistant/profiles/en/slots/
sudo nano create-jf-slots.py
```

Now, go to [this link](https://gitlab.com/issacdowling/jellypy/-/raw/main/main.py), CTRL+A to select everything, and paste it into that text editor we opened.

Next, change the contents of `jellyfinurl` to the address that you access your jellyfin server from. It should appear just like it does in your browser, including **https://** and (if applicable) the `:portnumber` at the end.

Then, go to your Jellyfin server's web client, then click the profile icon in the top right, dashboard, then API keys on the left bar. Add one, pick whatever name you want, and copy that key to your `jellyfinauth` variable. 

Next, press F12 to open your browser's dev tools, click the network tab, and enter `userid` into the search bar, then refresh the page. Hopefully you'll see something like this:

![Firefox dev tools showing URL with userid](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/devtoolsuserid.png)

Right click one of the options, copy the URL, then paste it into your address bar. Copy out the value for `userid` (remembering not to include the `&` symbol which will be at the end, and paste it into the `userid` section in the python script.

Finally, go right to the bottom of the script, add some empty lines, and type `genMusicSlots()`. 

Then, save and exit by doing CTRL+X, Y, ENTER.

Now, you can just run `sudo python create-jf-slots.py`. We need `sudo` because otherwise it won't have permissions to create its files.

### Playing individual songs

For now, we'll be adding functionality to play any specific song. Shuffling artists or albums will come later on.

### Test your sentences
Assuming you haven't modified any names in the python script, you should just be able to go to your sentences section, and paste this at the bottom:

```
[JellyfinPlaySong]
songs = ($songs){itemid}
play [the] song <songs>
```

Remember to save and train. Speaking of, with my example slots files with approximately 10,000 songs, 1000 albums, and 100 artists, my time-to-train on a Pi 4 went from 16 seconds to 51, so don't worry if it takes longer than you're used to to train.

But now, while on the main page, ask it to play any song, artist, or album in your library. To simplify things for the voice recognition - for once we add artists and albums - I've set it so you need to say "the *song* songname", or "the *artist* artistname*. You might have some conflicts with pronunciations of certain things with interesting names (like having to say "twenty-four K magic" for the album *24K Magic* because it doesn't understand that K means karat) , but you can correct these in Rhasspy's UI if they bother you.

### Downloading the media

Firstly, we want to be able to download the media that's requested, since I don't understand how to stream it normally. Due to this, go to your `# Set paths` section, and add this:
```
currentMediaPath = workingDir+"tmp/"+"currentMedia"
jellyfinPlayFilePath = workingDir+"tmp/"+"jellyfinPlay"
```
Also, add this elif statement:

```
elif intent == "JellyfinPlaySong":
  if os.path.exists(currentMediaPath):
    exit("Already playing")
  itemid = o["slots"]["itemid"]
  jellyfinurl, jellyfinauth = "https://", ""
  headers = {"X-Emby-Token": jellyfinauth,}

  # Send get request to Item Download API endpoint on the Jellyfin server with authentication
  get = requests.get(jellyfinurl+"/Items/"+itemid+"/Download", headers = headers)
  # If request successful, save file
  if get.status_code == 200:
    currentSong = open(currentMediaPath, "wb")
    currentSong.write(get.content)
    currentSong.close()
    jellyfinPlay = open(jellyfinPlayFilePath, "w")
    jellyfinPlay.write(itemid)
    jellyfinPlay.close()
```

Just as before, add your jellyfin server URL and auth token to the variables.

This script uses the ID of the song (located within the slots file) to download it from the Jellyfin server, and then (assuming the download was successful), write it to a file, and then make another file which willl be detected by a playback script to tell it to begin.

### To add playback support


Now, we'll make another script. Just like with bluetooth support, we can't run everything in the docker container, so we'll be making a system service that is *activated* by the intentHandler.

First, install miniaudio using pip

```
sudo pip install miniaudio
```

Then, make a systemd service which checks for the file made by the intenthandler by running this:
```
sudo nano /etc/systemd/system/jellyfinSongPlay.path
```
then paste:
```
[Unit]
Description=Checks for jellyfin play file, and activates the service which runs script which handles playback

[Path]
PathExists=/dev/shm/tmpassistant/jellyfinPlay

[Service]
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
Save and exit, then run:
```
sudo nano /etc/systemd/system/jellyfinSongPlay.service
```
and paste:
```
[Unit]
Description=Activates script which handles playback for jellyfin song

[Service]
Type=oneshot
ExecStart=/home/assistant-main-node/assistant/jellyfinPlaySong.py

[Install]
WantedBy=multi-user.target
```
Now make that script by running:
```
cd ~/assistant/
curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/code/jellyfinPlaySong.py
sudo chmod +x jellyfinPlaySong.py
sudo nano ~/assistant/jellyfinPlaySong.py
```

And remember to add the URL, authtoken, and user id to the variables at the top, then CTRL+X, Y, Enter to save.

This script handles playback (including pausing, stopping, and resuming), as well as getting info for the currently playing song incase we want it for later.

### Now enable it all
Run
```
sudo systemctl enable jellyfinSongPlay.path --now
sudo chmod +x ~/assistant/jellyfinPlaySong.py
```

### Pause, stop, and resume

First, go to the Rhasspy web UI, sentences, and add this:
```
[JellyfinPlaybackCtrl]
(stop | pause | unpause | continue | resume){playback} [the] (song | music)
```

Now, add this to the bottom of your intentHandler:
```
elif intent == "JellyfinPlaybackCtrl":
  if not os.path.exists(currentMediaPath):
    speech("No songs are playing")
  playback = o["slots"]["playback"]
  if playback == "continue" or playback == "resume" or playback == "unpause":
    jellyfinResume = open(jellyfinResumeFilePath, "w")
    jellyfinResume.close()
  if playback == "pause":
    jellyfinPause = open(jellyfinPauseFilePath, "w")
    jellyfinPause.close()
  if playback == "stop":
    jellyfinStop = open(jellyfinStopFilePath, "w")
    jellyfinStop.close()
```

This bit of code makes a file to represent you wanting to *play*, *pause*, or *resume* the music, which is then detected and handled by the playback script.

#### And, you can add `open(jellyfinStopFilePath, "w")` to your "GenericStop" intent too.

Then, in your `# Set paths` section, add these:
```
jellyfinResumeFilePath = workingDir+"tmp/"+"jellyfinResume"
jellyfinStopFilePath = workingDir+"tmp/"+"jellyfinStop"
jellyfinPauseFilePath = workingDir+"tmp/"+"jellyfinPause"
```
Now, you should be able to ask for any song, then tell it to pause, stop, or resume after pausing.

I also suggest changing the if statement at the start of the `jellyfinPlaySong` section. Instead of exiting if we've already got something playing, we'll just *stop* what's already playing so we can continue.

So, replace this:
```
if os.path.exists(currentMediaPath):
  exit("Already playing")
```
with this:
```
if os.path.exists(currentMediaPath):
  jellyfinStop = open(jellyfinStopFilePath, "w")
  jellyfinStop.close()
  time.sleep(2)
```

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
  songInfoFile = open(songInfoFilePath, "r").read()[1:-1].replace("'","").split(",")
  songName, songArtist = songInfoFile[0], songInfoFile[1]
  speech("This is " + songName + " by " + songArtist)
```
    
And add this to our ```# Set Paths``` section
```
songInfoFilePath = workingDir+"tmp/"+"songInfoFile"
```
    
It'll now read that file (which was created by the playback script, grabbing the info from your Jellyfin server using the ID of the song), separate out the name and artist, then say them in a sentence.


### Playing a queue of songs.

Now, we've got a fairly competent way to play, stop, pause, and resume individual songs from your library, but what about whole albums or artists?

First, add these sentences:
```
[JellyfinPlayQueue]
albums = ($albums){itemid}
albumartists = ($albumartists){itemid}
favourites = (favourites){itemid}
playlists = ($playlists){itemid}
(play | shuffle){ps} my <favourites>
(play | shuffle){ps} the album <albums>
(play | shuffle){ps} the artist <albumartists>
(play | shuffle){ps} the playlist <playlists>
```

Then, paste this elif statement at the end of the intenthandler:
```
elif intent == "JellyfinPlayQueue":
  if os.path.exists(currentMediaPath):
    jellyfinStop = open(jellyfinStopFilePath, "w")
    jellyfinStop.close()
    time.sleep(1)
  jellyfinurl, jellyfinauth = "", ""
  headers = {"X-Emby-Token": jellyfinauth,}
  songsList = [[],[]]
  ps, itemid = o["slots"]["ps"], o["slots"]["itemid"]
  userid = ""
  if itemid == "favourites":
    get = requests.get(jellyfinurl+"/Users/"+userid+"/Items?Recursive=true&Filters=IsFavorite&IncludeItemTypes=Audio", headers = headers)
  else:
    get = requests.get(jellyfinurl+"/Users/"+userid+"/Items?Recursive=true&IncludeItemTypes=Audio&parentId=" + itemid, headers = headers)
  receivedJson = json.loads(get.text)
  songs = receivedJson["Items"]
  for song in songs:
    songsList[0].append(song["Name"])
    songsList[1].append(song["Id"])
  if ps == "shuffle":
    tmpShuffle = list(zip(songsList[0],songsList[1]))
    random.shuffle(tmpShuffle)
    songsList[0], songsList[1] = zip(*tmpShuffle)
    songsList[0], songsList[1] = list(songsList[0]), list(songsList[1])
  songPos = 0
  for song in songsList[0]:
    if os.path.exists(jellyfinStopFilePath):
        break
    # Send get request to Item Download API endpoint on the Jellyfin server with authentication
    get = requests.get(jellyfinurl+"/Items/"+songsList[1][songPos]+"/Download", headers = headers)
    # If request successful, save file
    if get.status_code == 200:
        currentSong = open(currentMediaPath, "wb")
        currentSong.write(get.content)
        currentSong.close()
        jellyfinPlay = open(jellyfinPlayFilePath, "w")
        jellyfinPlay.write(songsList[1][songPos])
        jellyfinPlay.close()
    while os.path.exists(currentMediaPath):
      if os.path.exists(jellyfinStopFilePath):
        break
    songPos += 1
```
Remember to add the server URL, auth, and userid.

This script gets each audio file that's *under* a certain item (say, a playlist), and saves their IDs and Names to a list (and, if requested, it then shuffles them). Then, we handle things similarly to with individual songs, except in a `for loop`, which sends a new request to the playback script for each song.

Now, go to the jellyfinPlaySong file:
```
sudo nano ~/assistant/jellyfinPlaySong.py
```
and add this to the end (now it matters that we clean up after playback is finished):
```
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
```

We can now play or shuffle a big queue of songs, however we have no ability to skip.
    
#### Adding ability to skip.
    
Add this sentence:
```
[JellyfinSkipSong]
(skip | next) [the] (song | track | music)
```

Then, we'll add this elif statement, which makes a skip file. It'll work like the stop file used to, except it ***won't*** tell our song-queue to stop too:
```
elif intent == "JellyfinSkipSong":
  open(workingDir + "tmp/jellyfinSkipSong", "w") 
```

Now, we'll edit the jellyfinPlaySong file again:
```
sudo nano ~/assistant/jellyfinPlaySong.py
```
and add this to both the start and end:
```
elif intent == "JellyfinSkipSong":
  if not os.path.exists(currentMediaPath):
    speech("No songs are playing")
  jellyfinSkipSong = open(workingDir + "tmp/jellyfinSkipSong", "w")
  jellyfinSkipSong.close()
```

Then, modify your ```if os.path.exists(tmpDir + "jellyfinStop"):``` line and add (before the colon :)
```
or os.path.exists(tmpDir + "jellyfinSkipSong")
```
    
And now, you should be able to skip song.

This works because we're basically simulating the song having finished, but not also stopping the queue program.
    
## Volume control
For now, this is more complex than I'd like (if you're in my situation), however definitely workable. With the tools we've got, setting my speaker any below 65% is entirely inaudible, so we'll add support for setting **your own** "boundaries" for volume. In my case, I'd want "0%" to actually mean 65%. This obviously isn't necessary for everyone, and shouldn't be for me in the future either.
    
After doing some looking, I couldn't change the volume of audio from the host OS, since Rhasspy's docker container has separate access to audio devices. But that's fine, because our python script runs within that docker container, so we can just call `amixer` and politely ask for a volume change.
    
So, add this to your sentences:
```
[ChangeVolume]
(set | change) [the] volume [to] (0..100){percentage} [percent]
```
and then this to your intentHandler:
```
elif intent == "ChangeVolume":
  audioDevice = "Headphone"
  percentage = o["slots"]["percentage"]
  minBound, maxBound = 0, 100
  percentage = int(minBound+(percentage*((maxBound-minBound)/100)))
  call(["amixer", "sset", audioDevice, str(percentage) + "%"])
  call(["aplay", "/profiles/testSound.wav"])
```
This *might* just work immediately for you, however if not, it's likely the audio device that's wrong. We can find the right one like this.
    
First, run this:
```
docker exec -it rhasspy bash
```
You're now inside Rhasspy.
    
From here, just run `amixer`, and you'll see a list of devices (or just one, like me for now). We just care about finding the name of the right one. 

![Amixer devices](https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/images/amixer-devices.png)

Here, that's `Headphone`.  If yours is different, just change it in the python script (and if you think you're stuck inside Rhasspy, you can leave it by running `exit`)
    
### Setting custom boundaries
    
Sometimes, we want custom minimum/maximum audio levels. If you do, all we need to do is change the numbers on this line:
```
minBound, maxBound = 0, 100
```

So, if I have a minBound of 60 and a maxBound of 80, then ask for 50% volume, it'll give me 70% "real" volume. This won't be useful for everyone, but I needed it, and it works.

### Adding a confirmation sound.

You might want to be given a general idea for how loud you've set your volume. This is as simple as adding one line to the end of this section:
```
call(["aplay", "/profiles/yourfile.wav"])
```
In my case, I'll be repurposing the sounds that I made which were originally intended for the "start/stop listening" sounds. If you want to use them, run this:
```
cd ~/assistant/profiles
sudo curl -O https://gitlab.com/issacdowling/selfhostedsmarthomeguide/-/raw/main/resources/sounds/stoplistening.wav
sudo mv stoplistening.wav testSound.wav
```
and obviously change that line to be
```
call(["aplay", "/profiles/testSound.wav"])
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


# Resources
There's a folder called resources in this git repo. It contains any files of mine (or somebody else's, if they're ok with it) that you might want. Any API keys or related stuff in code will be blocked out, however they're otherwise unmodified.








# Extras
[Rhasspy Documentation](https://rhasspy.readthedocs.io)

[Homeassistant Documentation](https://www.home-assistant.io/docs/)
