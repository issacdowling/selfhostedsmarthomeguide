# SelfhostedVoiceAssistantGuide
### This is not done yet. In-progress.

## What's needed
Raspberry Pi 4

Micro SD Card (or other boot device, USB drives work too)

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
```
Then, press CTRL+X, Y, Enter, to save and exit. After which, you can just run
```
sudo docker-compose up -d
```
to begin installing. This, again, may take a while. You'll know it's done once you see this:
![Install complete](https://github.com/IssacDowling/SelfhostedVoiceAssistantGuide/blob/main/images/donedocker.png)

# Credit
[Rhasspy Documentation](https://rhasspy.readthedocs.io)
