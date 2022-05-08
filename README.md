# SelfhostedVoiceAssistantGuide
### This is not done yet. In-progress.

## What's needed
Raspberry Pi 4

Micro SD Card - >=16GB (or other boot device, USB drives work too)

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

![Settings page with defaults selected](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/settingspagedefault.png)

## Testing audio output
### Plug something in using the Pi's 3.5mm jack.

To test audio output, go back to the home page, and type something into the 'speak' box, and see if it comes out of your speakers. 

![AudioTest](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/audiotest.png)

It will likely sound quite bad, but should work.

## Testing audio input
### Plug a USB microphone into a USB port

To test audio input, press 'Wake Up' on the home page, and say "What time is it?". If it hears you, you'll get a response.

If there's no response, try relaunching rhasspy, by going back to your terminal, and typing
```
docker-compose up -d --force-recreate
```
This may get your mic detected if it wasn't before.



# Credit
[Rhasspy Documentation](https://rhasspy.readthedocs.io)
