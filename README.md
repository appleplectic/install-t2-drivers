# install-t2-drivers

A Python script that installs the T2 Linux drivers for you.

See https://wiki.t2linux.org/ for how to get WiFi files, install drivers, view state of Linux on T2 Macs, etc.

Need help? The Discord is a great place to start: https://discord.gg/wAyMNZrmHR

Permalink: https://tinyurl.com/install-t2

## Requirements
- Python 3.7+
- os, re, sys, shutil, subprocess, argparse (included with Python)
- pygit2
- requests
- wget

Install dependencies:
```
#Debian
sudo apt-get install python3 python3-pip -y
#Arch
sudo pacman -S python3 python3-pip

pip3 install -r requirements.txt
```

## To-do

TBD: Offline mode

TBD: Auto select kernel


## Credits

T2 Linux Wiki for the overall how-to - https://wiki.t2linux.org (https://github.com/t2linux/wiki/)

kevineinarsson for the audio files - https://gist.github.com/kevineinarsson/8e5e92664f97508277fefef1b8015fba

jamlam for the patched kernels - https://github.com/jamlam/mbp-16.1-linux-wifi

aunali1 for the BCE modules - https://github.com/aunali1/apple-bce-arch

T2Linux for the Touchbar and ALB modules - https://github.com/t2linux/apple-ib-drv

The Linux on T2 Macs Discord: https://discord.gg/wAyMNZrmHR
