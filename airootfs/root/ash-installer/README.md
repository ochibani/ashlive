# ash-installer
Experimental installer for [AshOS](https://github.com/ashos/ashos).


# Partition and format drive
* If installing on a BIOS system, use a dos (MBR) partition table.
* On EFI you can use GPT.
* The EFI partition has to be formatted to FAT32 before running the installer (```mkfs.fat -F32 /dev/<part>```).


```
lsblk  # Find your drive name
cfdisk /dev/*** # Format drive, make sure to add an EFI partition, if using BIOS leave 2M free space before first partition
mkfs.btrfs /dev/*** # Create a btrfs filesystem, don't skip this step!
```


# Run installer
```
python3 setup.py /dev/<root_partition> /dev/<drive> [/dev/<efi part>] [distro_id] ["distro_name"]# Skip the EFI partition if installing in BIOS mode
```

