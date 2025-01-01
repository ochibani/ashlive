# AshLive
Custom archiso profile to create AshOS installation ISO.

# Build the iso
Add [chaotic-aur](https://aur.chaotic.cx/docs) repository
```
pacman -S archiso
mkarchiso -v -w /path/to/work_dir -o /path/to/out_dir /path/to/ashlive/
```
