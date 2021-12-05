# install-t2-drivers

**WARNING: UNSTABLE.** Currently undergoing rigorous testing. **USE AT YOUR OWN RISK!**

A Python script that installs the T2 Linux drivers for you.

See https://wiki.t2linux.org/ for how to get WiFi files, install drivers, view state of Linux on T2 Macs, etc.

Need help? The Discord is a great place to start: https://discord.gg/wAyMNZrmHR

Permalink: https://tinyurl.com/install-t2



## Requirements
- Python 3.7+
- os, re, sys, shutil, subprocess, argparse (usually included with Python)
- pygit2
- requests
- wget

Install `python3` and `python3-pygit2`, `python3-requests`, and `python3-wget` with your package manager. You could also use `python3-pip`:

```
sudo pip3 install -r requirements.txt
```


## Stability

- Arch Linux & Arch-based distros: **BETA**
- Debian & Debian-based distros: **UNSTABLE**
- Fedora & Fedora-based distros: **EXTREMELY UNSTABLE**


## To-Do

- Test Debian-based distros (IN PROGRESS)
- Test Arch-based distros (IN PROGRESS)
- Test Fedora-based distros (LATER)
- Eopkg support (LATER)


## Notes

- Manjaro has some weird dependency issues with PyGit2 - try changing to Manjaro's unstable branch


## Credits

T2 Linux Wiki for the overall how-to - https://wiki.t2linux.org (https://github.com/t2linux/wiki/)

kevineinarsson for the audio files - https://gist.github.com/kevineinarsson/8e5e92664f97508277fefef1b8015fba

jamlam for the patched kernels - https://github.com/jamlam/mbp-16.1-linux-wifi

aunali1 for the BCE modules - https://github.com/aunali1/apple-bce-arch

T2Linux for the Touchbar and ALB modules - https://github.com/t2linux/apple-ib-drv

The Linux on T2 Macs Discord: https://discord.gg/wAyMNZrmHR
