# AshLive
Custom archiso profile to create AshOS installation ISO.

# Build the iso
Add [chaotic-aur](https://aur.chaotic.cx/docs) repository
```
pacman -S archiso
cp -r ashlive/ash-repo /tmp
mkarchiso -v -r -w /path/to/work_dir -o /path/to/out_dir /path/to/ashlive/
example: mkarchiso -v -r -w /tmp/ashliveiso-tmp -o ~/out_dir ~/ashlive
```
