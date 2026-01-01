#!/bin/bash
set -e

# Create live user with a home directory and default shell
if [ ! -d /home/live-user ]; then
    useradd -m -p "" -g users -G "adm,audio,floppy,log,lp,network,optical,power,rfkill,scanner,storage,sys,users,video,wheel" -s /usr/bin/zsh liveuser 
fi

# Set a password for liveuser
echo "liveuser:liveuser" | chpasswd

# Enable the wheel group for sudo access
echo "%wheel ALL=(ALL) ALL" | sudo tee /etc/sudoers.d/wheel
sudo chmod 440 /etc/sudoers.d/wheel
echo "liveuser ALL=(ALL:ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/liveuser
sudo chmod 440 /etc/sudoers.d/liveuser

# Enable display manager & network manager
systemctl enable --now sddm
systemctl enable --now NetworkManager
