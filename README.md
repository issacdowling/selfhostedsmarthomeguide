# SelfhostedVoiceAssistantGuide
### This is not done yet. In-progress.

## What's needed
Raspberry Pi 4

Micro SD Card >=16GB (or other boot device, USB drives work too)

FOR TESTING ONLY

USB Mic

3.5mm Speakers

# Setting Up the Pi

### Download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/), and install/run it.

Choose OS, then **Raspberry Pi OS (other)**

![Other](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/otherOS.png)

then **Raspberry Pi OS 64-bit lite**

![64-bit-lite](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/lite64.png)

### Now, click the settings icon in the bottom right corner.

* Set hostname to whatever you want to call it. I chose assistant-main-node
* Enable SSH 
* Set username and password
* Configure Wifi if you're going to use it instead of ethernet. Ethernet is more stable, but Wifi allows for more freedom in positioning.
* Scroll down, save.

![Settings page](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/settings.png)

### Choose your boot device (what you'll be keeping in the Pi, typically a MicroSD card)
![Boot device list](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/selectboot.png)

### And finally, press write, and wait for it to finish.
![Writing Media](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/writingprogress.png)

# Booting and initial install
Assuming you have a Micro-HDMI cable, you can turn on the Pi without anything inserted to ensure it boots fine. You'll likely get a screen like this.
![Boot with no device](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/bootnodevice.png)

But if - like most people - you don't own a Micro HDMI cable, that's alright. We can run *headlessly* (without a display)

### Regardless of whether you'll be connecting a keyboard and monitor to the Pi or not, make sure it's off, then insert your boot drive, and plug it in. Then, wait for one of two things:

If you've got a display connected, wait until there's a line with your username in green at the bottom of the screen, like this.
![Linux bootup scene](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/withdisplaybootup.png)

If you don't have a display connected, go to a computer on the same network as your Pi (so, if you didn't set up Wifi, connect an ethernet cable). Then, search terminal, same on Linux, Windows 11, or MacOS. On Windows 10, search cmd. Now, type ```ssh yourusername@yourhostname.local```, and replace 'yourusername' with your username, and 'yourhostname' with the hostname you typed in the settings page. At first, it'll likely error out, since the Pi isn't done booting yet, but you can press the up arrow and enter to run the command again. You know you've succeeded once you see this page.
![SSH fingerprint question](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/fingerprint.png)

Type yes, enter, then type your password (which won't show up onscreen as a security measure, but it *is* still going through). 

### From here, we can run commands.

First, run
```
sudo apt update && sudo apt upgrade -y
```
to get up to date

### Now, set a static local IP

In your terminal, type ```ip route | grep default```. Then, note down three things: the first IP, the network device, and the second IP. The IPs will likely be 192.168.x.x, but may be different. In the image, I've highlighted these things in yellow so you know where to look.

![my private IP for the Pi](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/ipdefault.png)

Now, run
```
sudo nano /etc/dhcpcd.conf
```
and navigate down to the bottom line using the arrow keys, then press enter a few times to add some lines. You should get to here:

![dhcpcd](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/dhcpcd.png)

Then, paste this in:

```
interface
static ip_address=/24
static routers=
static domain_name_servers=1.1.1.1
```

Next to interface, add a space, then the network device (either **eth0** or **wlan0**). Now, for static ip_address, type the second IP before the */24*. Finally, add the first IP from earlier directly after **static routers=**. Then, press CTRL+X, then Y, then Enter, to save and exit. Finally, run ```sudo reboot``` to restart. Your SSH will disconnect, and you can just keep trying to reconnect until it works to check if you're booted.


# Installing things
Run
```
curl -sSL https://get.docker.com | sh
sudo apt-get install -y uidmap libffi-dev libssl-dev python3 python3-pip python3-dev
dockerd-rootless-setuptool.sh install
sudo pip3 install docker-compose
```
to install docker and docker compose. This may take a while

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
        ports:
            - '12101:12101'
        volumes:
            - '$HOME/.config/rhasspy/profiles:/profiles'
            - '/etc/localtime:/etc/localtime:ro'
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
![Install complete](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/donedocker.png)

# Initally setting up rhasspy
In a browser on the same network as your Pi, go to this site, changing 'yourhostname' to your hostname.
```
http://yourhostname.local:12101
```
Your browser *should* complain that this site is not secure. If it was a site on the internet, you wouldn't want to access it, however it's just local, so we can tell the browser that we want to continue.
![https issue](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/httpsonly.png)

### And now you'll be here!
![Rhasspy main page](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/rhasspyhome.png)

# Testing things

Then, go to the settings page using the left-side menu. Go through each service, and - for now - just select the default from the dropdown menu. Then, press the save settings button below the list, and restart. Once restarted, go to the top of the page, and press download. After that's done, things should look like this.

![Settings page with defaults selected](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/settingdefault.png)

## Testing audio output
### Plug something in using the Pi's 3.5mm jack.

To test audio output, go back to the home page, and type something into the 'speak' box, and see if it comes out of your speakers. 

![AudioTest](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/audiotest.png)

It will likely sound quite bad, but should work.

## Testing audio input
### Plug a USB microphone into a USB port

To test audio input, press 'Wake Up' on the home page, and say "What time is it?". If it hears you, you'll get a response, and the UI will update to show this:

![AudioInputWorks](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/audioinputworks.png)

If there's no response, try relaunching rhasspy, by going back to your terminal, and typing
```
sudo docker-compose up -d --force-recreate
```
This may get your mic detected if it wasn't before.

# Some improvements
## TTS
I reccommend going back to the settings page, switching your Text To Speech to Larynx, and choosing a voice you think sounds good. Southern-english-female is - at this point in writing - my chosen voice, since higher-pitched voices will work better for voice assistants due to them often using small speakers with little bass response. Low Quality is perfectly fine, as you'll see when you test it. Though, speaking of testing, trying Larynx was somewhat awkward in the settings page for the first minute-or-so of restarting after selecting a new voice, so don't be alarmed if this happens to you. Remember to save your settings and restart afterwards.

![TTSsettings](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/Texttospeech.png)

## Wake word
In the settings page, click the green "Wake Word" dropdown, and type a wakeword for testing. This is what you'll say to activate the assistant. Make sure it has quite a few syllables so it's easy to recognise. Then, record yourself saying it in three different ways, and maybe even another person to be safe. Then, press save, and restart.

![wakewordsettings](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/Wakeword.png)

# Making it smart
## Setting up Homeassistant
### If you've already got a homassistant instance, scroll down until we start entering URLs
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

![hass onboarding](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/hassonboarding.png)

Just type a name, username, and make a password, and press 'Create Account'

![hass make account](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/hassmakeaccoun.png)

Now, give your home a name and location, (plus elevation, if you'd like)

![hass name home](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/hassnamehome.png)

And choose which data to *opt-in* for. These are all disabled by default, however I'd ask that you consider turning on anything you're comfortable with, since it can help the devs.

![hass opt in](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/hassoptin.png)

Finally for the onboarding, just press finish! This page shows any services that homeassistant automatically found, but we'll set things up later.

![hass auto find](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/hassautofind.png)

Now, you should be on the main homeassistant page. Click your name in the bottom right, then scroll down to long-lived tokens.

![llat](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/llat.png)

Create one, name it whatever you'd like, and save it for a minute.

Go back to your rhasspy tab, then settings, scroll down to intent handler, and select local command.

![local intent handler](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/localcommandintents.png)

Then, press the green dropdown, and set the program to ```/profiles/intentHandler```

Now, you can press save and restart.

## It gets difficult.

Now, we have to learn stuff, and edit yaml files. 


### Our example will be getting the assistant to return the time.




### Trying it

With any luck, once things are restarted, you can go to rhasspy's web UI, click the wake button, say out loud **"What time is it?**, and it should respond with the current time.

## Actually controlling devices

### Alright, how do we make it control things?

Go to your terminal (still SSH'd into the Pi), and type 
```
sudo nano ~/hass/config/configuration.yaml
```

By default, your configuration.yaml should look like this:

![default config.yaml](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/defaultyaml.png)

Go right to the top of the file, and look for the line ```default_config:```. Go one line below it, and add exactly:
```
api:
```
Then, CTRL+X, Y, ENTER.

So you know, there are more ways to accomplish things. I'll be describing the methods I use, but if there's a better method, please feel free to share, I'd appreciate it.

First, we need a thing to control. This isn't a homeassistant tutorial, but if you've got any WLED devices, they should automatically appear in the devices section to be configured like this:

![Autoadd1](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/Autoadd1.png)
![Autoadd2](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/Autoadd2.png)
![Autoadd3](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/Autoadd3.png)

To check the device name, go to settings, then entities in Homeassistant. Then, click on the device you're intending to control. Note down the name at the bottom.

![Wled device in entities](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/wledentities.png)

Now, go back to your automations file, by running ```sudo nano ~/hass/config/automations.yaml```, and paste this blank template a few lines below the previous one.

```
- alias: "GUI Name"
  trigger:
  - event_data: {}
    platform: event
    event_type: rhasspy_NameInRhasspy
  action:
     - service:
       data:
         entity_id: "{{trigger.event.data.entity}}"
```

So, edit this using what we learned before. The alias for me will be **"Turn On Specific Light"**. The event type will be the same but without spaces, **"rhasspy_TurnOnSpecificLight"**. I don't want it to say anything in response, so I'll make the payload empty. I'm keeping it here in the example for you to use for other things, though. Then, next to the service with nothing next to it, we'll choose what we want to do. In my case, I'm turning a WLED device (a light) on, so I'll add **"light.turn_on"**, but **"homeassistant.turn_on"** would work too, and is how you'd interact with other devices. For further reading, [go here for the documentation](https://www.home-assistant.io/docs/scripts/service-calls/)

Normally, we'd put something else in **"entity_id:"**, however we'll use Rhasspy to send this data, so we can specify it with our voice. Now you've got something which looks mildly similar to this:

![Done WLED example](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/donewledexample.png)

go to Homeassistant's developer tools, then YAML, and then reload automations.

![reload automations](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/reloadautomations.png)

Now, head back to Rhasspy. Then, on the left, go to the sentences section. Add some lines after any other text, then add - inside square brackets - the event type from earlier. So, in my case, ```TurnOnSpecificLight```. Then, below it, add what you want to say. I want to turn on the door light by saying **"turn on the door light"**. After writing that, add brackets around the text which represents your device *(so, in my case, the words 'door light')*, then add some curly brackets next to it. Type inside them: ```entity:```, then the name of your device within homeassistant which we checked earlier. For me, that's ```light.wled_door```. Repeat this for your other lights if following my example, and you should end up with something like this.

![specificlighton](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/turnonspecificlight.png)

Then, using what you've learned, you could add the option to turn it off.

![Turning off in automations yaml](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/turnoffspecificlightsyaml.png)
![Turning off in automations rhasspy](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/turnoffspecificlightsrhasspy.png)

Now, save and retrain, then go to rhasspy's web UI, wake it up, and ask it one of your sentences. Ideally, it works.

## Sending Extra Data
Alright, but I don't *just* want **on** or **off**, I want to tell my lights to be a certain colour.

Before we do that, lets improve the scalability of our previous light control setup. The way I did it previously was easier to explain, especially for small setups, but this works better in the long term.

Click the circular "slots" tab,

![slot tab](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/slottab.png)

then make a new slot called lights. Within regular brackets, put the name you'd like to speak. If there are multiple, such as "Bed LEDS" and "Bedside LEDs", separate them with a pipe symbol (|). Then, immediately after the brackets, add a colon (:), and **without adding a space**, add the entity id from homeassistant. Here's what mine looks like with two lights.

![Light slot](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/lightslot.png)

Then, head back to your sentences section, and remove what you've already got. If you want to use my setup, paste this in:
```
[SetSpecificLightPower]
light_name = ($lights){entity}
light_state = (on | off){state}
(set | turn) <light_state> [the] <light_name>
(set | turn) [the] <light_name> <light_state>
```
What's within the top square brackets is what homeassistant will recognise when checking what event is being sent. Then, we set two variables. light_name equals what's in our lights slot (we know we're talking about a slot because of the $), and light_state can be on or off. Again, **or** is represented by a pipe (|). [The next bit was taught to me by a post on the rhasspy community page. Credit to them for this config!](https://community.rhasspy.org/t/access-from-home-assistant-the-raw-value-in-slots-array/3497) Then, we make some sentences. I made two, so I can say things in different orders. The first would allow me to say **"Turn on the bedside light"**, and the second allows **"Turn the bedside light on"**. Arrow brackets reference variables, regular brackets reference groups of words, square brackets reference optional words, and curly brackets reference the name that the sent data will have in the JSON file that Rhasspy sends to homeassistant. When saving, remember to allow training.


### But we also need to update our homeassistant automations.

So, while SSH'd into the pi, run
```
sudo nano ~/hass/config/automations.yaml
```
Then, just remove the old config, and paste this instead:
```
- alias: "Turn on/off specific light"
  trigger:
  - event_data: {}
    platform: event
    event_type: rhasspy_SetSpecificLightPower
  action:
     - service: rest_command.tts
       data:
         payload: ""
     - service: light.turn_{{trigger.event.data.state}}
       data:
         entity_id: "{{trigger.event.data.entity}}"
```
If you changed what's within the square brackets, change what's after ```rhasspy_```. Otherwise, things should just work. If you'd like your assistant to respond verbally, you can add things within the parenthesis next to ```payload:```. Now, like we did earlier, go to homeassistant's dev tools, YAML, and reload automations. Now, you should be able to ask it to turn on the lights as before, but in a way that's much better for the future.

And, now it's easy to add colours. Go back to your slots, add a new one called ```colours``` (the British spelling), and paste this:
```
(aqua | aquamarine | beige | black | blue | brown | chocolate | coral | crimson | cyan | firebrick | forest green | gold | gray | green | greenyellow | hot pink | indigo | khaki | lavender | light blue | light coral | light cyan | light green | light pink | light salmon | light yellow | lime | lime green | magenta | maroon | navy | olive | orange | orchid | pink | purple | red | salmon | tomato | violet | white | yellow){colour}
```
It actually supports all colours in [this list](https://www.w3.org/TR/css-color-3/#svg-color), so if I omitted your favourite colour, you can add it as long as it's in the page on that link.

![Colour slot](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/colourslotcorrected.png)

Then, go to your sentences, and duplicate your power control section. Change Power to Colour (or apply your own naming convention), and change ```light_state``` to ```light_colour```, and change ```on | off``` to ```$colours```. Remember to also change light_state in the actual sentence too, along with correcting the layout of the sentence so it makes sense when you say it. In the end, I've got this:

![Colour sentence](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/coloursentencecorrection.png)

Finally, go back to your terminal with automations.yaml open, and paste this below your power config:
```
- alias: "Set specific light colour"
  trigger:
  - event_data: {}
    platform: event
    event_type: rhasspy_SetSpecificLightColour
  action:
     - service: rest_command.tts
       data:
         payload: ""
     - service: light.turn_on
       data:
         entity_id: "{{trigger.event.data.entity}}"
         color_name: "{{trigger.event.data.colour}}"
```

All you should need to change is the event_type if you decided to name things differently. Save and exit (CTRL+X, Y, ENTER), then reload your automations in homeassistant, and things should work.




## Wake word
To wake things without using the web UI, you *could* set a custom word using Rhasspy Raven, however I had trouble with being recognised. I just went into porcupine's dropdown, pressed refresh, and selected one from the list, and I'd suggest you do the same. Save and restart, and it should work.

# Credit
[Rhasspy Documentation](https://rhasspy.readthedocs.io)
[Homeassistant Documentation](https://www.home-assistant.io/docs/)
