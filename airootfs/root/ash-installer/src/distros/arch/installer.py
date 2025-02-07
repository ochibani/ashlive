#!/usr/bin/env python3

import os
import subprocess as sp
import sys
from src.installer_core import * # NOQA
from setup import args, distro

#   1. Define variables
is_format_btrfs = True # REVIEW temporary
KERNEL = "" # options: https://wiki.archlinux.org/title/kernel e.g. "-xanmod"
packages = f"base linux{KERNEL} btrfs-progs sudo grub dhcpcd networkmanager nano \
linux-firmware python3 python-anytree paru vim fakeroot debugedit reflector" # os-prober bash tmux arch-install-scripts
#if not is_ash_bundle:
#    packages +=  " python3 python-anytree"
if is_efi:
    packages += " efibootmgr"
if is_luks:
    packages += " cryptsetup" # REVIEW
super_group = "wheel"
v = "" # GRUB version number in /boot/grubN

def main():
    #   Pre bootstrap
    pre_bootstrap()

    #   Mount-points for chrooting
    ashos_mounts()

    #   2. Bootstrap and install packages in chroot
    #if KERNEL not in ("-hardened", "-lts", "-zen"): # AUR required
       # sp.call(f'{installer_dir}/src/distros/{distro}/aur/aurutils.sh', shell=True)
    while True:
        try:
            strap()
        except sp.CalledProcessError as e:
            print(e)
            if not yes_no("F: Failed to strap package(s). Retry?"):
                unmounts("failed") # user declined
                sys.exit("F: Install failed!")
        else: # success
            break

    #   Go inside chroot
    os.system("cp /root/ash-git.pkg.tar.zst /mnt/var/cache/pacman/pkg/")
    cur_dir_code = chroot_in("/mnt")

    #   3. Package manager database and config files
    #os.system("cp -r /var/lib/pacman/. /usr/share/ash/db/") # removed /mnt/XYZ from both paths and below
    #os.system("sed -i 's|[#?]DBPath.*$|DBPath       = /usr/share/ash/db/|g' /etc/pacman.conf")
    os.system(f"sed -i 's|HoldPkg.*$|HoldPkg      = {packages}|g' /etc/pacman.conf")

    #   4. Update hostname, hosts, locales and timezone, hosts
    os.system(f"echo {hostname} > /etc/hostname")
    os.system(f"echo 127.0.0.1 {hostname} {distro} >> /etc/hosts")
    #os.system(f"{SUDO} chroot /mnt {SUDO} localedef -v -c -i en_US -f UTF-8 en_US.UTF-8")
    os.system("sed -i 's|^#en_US.UTF-8|en_US.UTF-8|g' /etc/locale.gen")
    os.system("locale-gen")
    os.system("echo 'LANG=en_US.UTF-8' > /etc/locale.conf")
    os.system(f"ln -sf /usr/share/zoneinfo/{tz} /etc/localtime") # removed /mnt/XYZ from both paths (and from all lines above)
    os.system("/sbin/hwclock --systohc")
    os.system("useradd -m -s /bin/bash aur")
    os.system("echo 'aur ALL=(ALL:ALL) NOPASSWD: ALL' >> /etc/sudoers")
    os.system("su aur -c 'paru -Sy rc-local --noconfirm'")
    install_ash = os.system("pacman -U '/var/cache/pacman/pkg/ash-git.pkg.tar.zst' --noconfirm")
    if install_ash != 0:
        sys.exit(1)

    #   Post bootstrap
    post_bootstrap(super_group)

    #   5. Services (init, network, etc.)
    #os.system("/usr/lib/systemd/system-generators/systemd-fstab-generator /run/systemd/generator '' ''") # REVIEW recommended as fstab changed. "systemctl daemon-reload"
    os.system("systemctl daemon-reload")
    os.system("systemctl enable NetworkManager")

    #   6. Boot and EFI
    initram_update()
    grub_ash(v)

    #   BTRFS snapshots
    deploy_base_snapshot()

    #   Copy boot and etc: deployed snapshot <---> common
    deploy_to_common()

    #   Unmount everything and finish
    chroot_out(cur_dir_code)
    #if is_ash_bundle:
    #    bundler()
    unmounts()

    clear()
    print("Installation complete!")
    print("You can reboot now :)")

def initram_update(): # REVIEW removed "{SUDO}" from all lines below
    if is_luks:
        os.system("dd bs=512 count=4 if=/dev/random of=/etc/crypto_keyfile.bin iflag=fullblock") # removed /mnt/XYZ from output (and from lines below)
        os.system("chmod 000 /etc/crypto_keyfile.bin") # Changed from 600 as even root doesn't need access
        os.system(f"cryptsetup luksAddKey {args[1]} /etc/crypto_keyfile.bin")
        os.system("sed -i -e '/^HOOKS/ s/filesystems/encrypt filesystems/' \
                        -e 's|^FILES=(|FILES=(/etc/crypto_keyfile.bin|' /etc/mkinitcpio.conf")
    if is_format_btrfs: # REVIEW temporary
        os.system(f"sed -i 's|^MODULES=(|MODULES=(btrfs|' /etc/mkinitcpio.conf") # TODO if array not empty, needs to be "btrfs "
    if is_luks or is_format_btrfs: # REVIEW mkinitcpio needed to run without these conditions too?
        os.system(f"mkinitcpio -p linux{KERNEL}")

def strap():
    sp.check_call(f"pacstrap /mnt --needed {packages}", shell=True)

main()

