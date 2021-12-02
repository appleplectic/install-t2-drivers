#!/bin/bash python3
# -*- coding: utf-8 -*-
#install-t2.py


# This is a script that installs necessary drivers for the MacBook Pro 16,1
# Copyright (C) 2021 appleplectic
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.


# Big thanks to:
# T2 Linux Wiki for the overall how-to - https://wiki.t2linux.org (https://github.com/t2linux/wiki/)
# kevineinarsson for the audio files - https://gist.github.com/kevineinarsson/8e5e92664f97508277fefef1b8015fba
# jamlam for the patched kernels - https://github.com/jamlam/mbp-16.1-linux-wifi
# aunali1 for the BCE modules - https://github.com/aunali1/apple-bce-arch
# T2Linux for the Touchbar and ALB modules - https://github.com/t2linux/apple-ib-drv
#
# The Linux on T2 Macs Discord: https://discord.gg/wAyMNZrmHR

# This script is soley for bundling these together for an easy-to-install way.

# Modules used:
# os, re, sys, shutil, subprocess, argparse (usually part of Python)
# PyGit2 + dependencies
# Requests + dependencies
# Wget + dependencies

# This script only works on T2 Macs

# TO-DO:
# After release: Download wifi firmware online
# IN PROGRESS: Change /etc/default/grub for the user
# After release: Offline mode
# After release: Auto select kernel
# After release: Fedora support
# TBD: Auto-detect arch-based or debian-based

#====START CODE====


import argparse
import os
import shutil
import subprocess
import sys

import pygit2
import requests
import wget



def check_compatibility():

    if sys.version_info < (3,7,0):
        raise EnvironmentError("Must be using Python 3.7+")
    if os.geteuid() != 0:
        raise EnvironmentError('Script must be run with root privileges.')

    try:
        requests.get('https://www.google.com/').status_code
    except:
        raise ConnectionRefusedError('This device does not appear to have an internet connection. Please connect Ethernet, then try again.')



def install_wifi(model_id:str, wifi_id:str, filepaths:list):

    #Renaming & moving files to /lib/firmware/brcm
    for file in filepaths:
        if file.endswith('.trx'):
            shutil.copy(file, f'/lib/firmware/brcm/brcmfmac{wifi_id}-pcie.bin'.replace('//', '/'))
        elif file.endswith('.clmb'):
            shutil.copy(file, f'/lib/firmware/brcm/brcmfmac{wifi_id}-pcie.clm_blob'.replace('//', '/'))
        elif file.endswith('.txt'):
            shutil.copy(file, f'/lib/firmware/brcm/brcmfmac{wifi_id}-pcie.Apple Inc.-{model_id}.txt'.replace('//', '/'))



def install_kernel(distro:str, ver:str):

    if ver == 'bigsur':
        if distro == 'arch':
            jsonreq = requests.get("https://api.github.com/repos/jamlam/mbp-16.1-linux-wifi/releases/latest").json()
            download_urls = []
            for dic in jsonreq['assets']:
                download_urls.append(dic['browser_download_url'])
            for url in download_urls:
                filename = wget.download(url)
                subprocess.run(['pacman', '-U {filename}'])
        elif distro == 'debian':
            # Have to use 5.13.15 and not 5.13.19
            jsonreq = requests.get("https://api.github.com/repos/marcosfad/mbp-ubuntu-kernel/releases/49398102").json()
            download_urls = []
            for dic in jsonreq['assets']:
                download_urls.append(dic['browser_download_url'])
            for url in download_urls:
                filename = wget.download(url)
                subprocess.run(['apt-get', 'install', f'./filename', '-y'])
    elif ver == 'mojave':
        if distro == 'arch':
            jsonreq = requests.get("https://api.github.com/repos/aunali1/linux-mbp-arch/releases/latest").json()
            download_urls = []
            for dic in jsonreq['assets']:
                download_urls.append(dic['browser_download_url'])
            for url in download_urls:
                filename = wget.download(url)
                subprocess.run(['pacman', f'-U {filename}'])
        elif distro == 'debian':
            # Have to use 5.13.15 and not 5.13.19
            jsonreq = requests.get("https://api.github.com/repos/marcosfad/mbp-ubuntu-kernel/releases/49397674").json()
            download_urls = []
            for dic in jsonreq['assets']:
                download_urls.append(dic['browser_download_url'])
            for url in download_urls:
                filename = wget.download(url)
                subprocess.run(['apt-get', 'install', f'./{filename}', '-y'])



def install_bce(distro:str):

    if distro == 'arch':
        subprocess.run(['pacman', '-S dkms'])
        jsonreq = requests.get('https://api.github.com/repos/aunali1/apple-bce-arch/releases/latest').json()
        download_urls = []
        for dic in jsonreq['assets']:
            download_urls.append(dic['browser_download_url'])
        for url in download_urls:
            if not url.endswith('pkg.tar.zst') or not 'apple-bce-dkms-git' in url:
                continue
            filename = wget(url)
        subprocess.run(['pacman', f'-U {filename}'])
    elif distro == 'debian':
        subprocess.run(['apt-get', 'install', 'dkms', '-y'])
        pygit2.clone_repository('https://github.com/t2linux/apple-bce-drv', '/usr/src/apple-bce-r183.c884d9c')
        with open('/usr/src/apple-bce-r183.c884d9c/dkms.conf', 'w', encoding='utf-8') as conf:
            conf.write('''PACKAGE_NAME="apple-bce"
PACKAGE_VERSION="r183.c884d9c"
MAKE[0]="make KVERSION=$kernelver"
CLEAN="make clean"
BUILT_MODULE_NAME[0]="apple-bce"
DEST_MODULE_LOCATION[0]="/kernel/drivers/misc"
AUTOINSTALL="yes"
''')
        for kernel in os.listdir('/var/lib/initramfs-tools'):
            subprocess.run(['dkms', 'install', '-m apple-bce', '-v r183.c884d9c', f'-k {kernel}'])



def install_ib(distro:str, tb_config_num:str, backlight:bool):

    if distro == 'arch':
        subprocess.run(['pacman', '-S dkms'])
    elif distro == 'debian':
        subprocess.run(['apt-get', 'install', 'dkms', '-y'])

    os.mkdir('/usr/src/apple-ibridge-0.1')

    if backlight:
        pygit2.clone_repository('https://github.com/Redecorating/apple-ib-drv', '/usr/src/apple-ibridge-0.1')
    else:
        pygit2.clone_repository('https://github.com/t2linux/apple-ib-drv', '/usr/src/apple-ibridge-0.1')

    for kernel in os.listdir('/var/lib/initramfs-tools'):
        subprocess.run(['dkms', 'install', '-m apple-ibridge', '-v 0.1', f'-k {kernel}'])

    subprocess.run(['modprobe', 'apple_bce'])
    subprocess.run('modprobe', 'apple_ib_tb')
    subprocess.run(['modprobe', 'apple_ib_als'])

    with open('/etc/modules-load.d/t2.conf', 'w', encoding='utf-8') as t2conf:
        t2conf.write('apple-bce\napple-ib-tb\napple-ib-als\nbrcmfmac')

    if distro == 'debian':
        with open('/etc/modprobe.d/apple-touchbar.conf', 'w', encoding='utf-8') as tbconf:
            tbconf.write(f'options apple-ib-tb fnmode={tb_config_num}')
    else:
        with open('/etc/modprobe.d/apple-tb.conf', 'w', encoding='utf-8') as tbconf:
            tbconf.write(f'options apple-ib-tb fnmode={tb_config_num}')

    with open('/lib/systemd/system-sleep/rmmod_tb.sh', 'w', encoding='utf-8') as rmmodtb:
        rmmodtb.write(
'''#!/bin/sh
if [ "${1}" = "pre" ]; then
  modprobe -r apple_ib_tb
  modprobe -r hid_apple
elif [ "${1}" = "post" ]; then
  modprobe hid_apple
  modprobe apple_ib_tb
fi''')

    os.chmod('/lib/systemd/system-sleep/rmmod_tb.sh', 755)
    os.chown('/lib/systemd/system-sleep/rmmod_tb.sh', 0, 0)



def install_audiofix(model_id):

    home = os.path.expanduser('~')

    if model_id == 'MacBookPro16,1':
        jsonreq = requests.get('https://api.github.com/gists/8e5e92664f97508277fefef1b8015fba').json()
        if os.path.isdir('/usr/share/alsa/cards/') and os.path.isdir('/usr/share/pulseaudio/alsa-mixer/profile-sets/') and os.path.isdir('/usr/lib/udev/rules.d/') and os.path.isdir(home + '/.config/pulse/'):
            # PulseAudio
            for key in jsonreq['files'].keys():
                url = jsonreq['files'][key]['raw_url']
                if 'README' in url:
                    continue
                fname = wget.download(url)
                if fname == 'AppleT2.conf':
                    shutil.move(fname, '/usr/share/alsa/cards/')
                elif fname == 'apple-t2.conf':
                    shutil.move(fname, '/usr/share/pulseaudio/alsa-mixer/profile-sets/')
                elif fname == '91-pulseaudio-custom.rules':
                    shutil.move(fname, '/usr/lib/udev/rules.d/')
                elif fname == 'default.pa':
                    shutil.move(fname, home + '/.config/pulse/')
                elif fname == 'daemon.conf':
                    shutil.move(fname, home + '/.config/pulse/')
        elif os.path.isdir('/usr/share/alsa/cards/') and os.path.isdir('/usr/share/alsa-card-profile/mixer/profile-sets/') and os.path.isdir('/usr/lib/udev/rules.d/') and os.path.isdir(home + '/.config/pulse/'):
            # PipeWire
            for key in jsonreq['files'].keys():
                url = jsonreq['files'][key]['raw_url']
                if 'README' in url:
                    continue
                fname = wget.download(url)
                if fname == 'AppleT2.conf':
                    shutil.move(fname, '/usr/share/alsa/cards/')
                elif fname == 'apple-t2.conf':
                    shutil.move(fname, '/usr/share/alsa-card-profile/mixer/profile-sets/')
                elif fname == '91-pulseaudio-custom.rules':
                    os.remove('91-pulseaudio-custom.rules')
                    wget.download('https://raw.githubusercontent.com/appleplectic/T2-Misc/main/91-pulseaudio-custom.rules')
                    shutil.move(fname, '/usr/lib/udev/rules.d/')
                elif fname == 'default.pa':
                    shutil.move(fname, home + '/.config/pulse/')
                elif fname == 'daemon.conf':
                    shutil.move(fname, home + '/.config/pulse/')
        else:
            print('Please install PulseAudio or PipeWire and Alsa first.')

    elif model_id == 'MacBookAir9,1':
        jsonreq = requests.get('https://api.github.com/gists/8b670ae29e0b7be2b73887f3f37a057b').json()
        if os.path.isdir('/usr/share/alsa/cards/') and os.path.isdir('/usr/share/pulseaudio/alsa-mixer/profile-sets/') and os.path.isdir('/usr/lib/udev/rules.d/'):
            # PulseAudio
            for key in jsonreq['files'].keys():
                url = jsonreq['files'][key]['raw_url']
                if 'README' in url:
                    continue
                fname = wget.download(url)
                if fname == 'AppleT2.conf':
                    shutil.move(fname, '/usr/share/alsa/cards/')
                elif fname == 'apple-t2.conf':
                    shutil.move(fname, '/usr/share/pulseaudio/alsa-mixer/profile-sets/')
                elif fname == '91-pulseaudio-custom.rules':
                    shutil.move(fname, '/usr/lib/udev/rules.d/')

        elif os.path.isdir('/usr/share/alsa/cards/') and os.path.isdir('/usr/share/alsa-card-profile/mixer/profile-sets/') and os.path.isdir('/usr/lib/udev/rules.d/'):
            # PipeWire
            for key in jsonreq['files'].keys():
                url = jsonreq['files'][key]['raw_url']
                if 'README' in url:
                    continue
                fname = wget.download(url)
                if fname == 'AppleT2.conf':
                    shutil.move(fname, '/usr/share/alsa/cards/')
                elif fname == 'apple-t2.conf':
                    shutil.move(fname, '/usr/share/alsa-card-profile/mixer/profile-sets/')
                elif fname == '91-pulseaudio-custom.rules':
                    os.remove('91-pulseaudio-custom.rules')
                    wget.download('https://raw.githubusercontent.com/appleplectic/T2-Misc/main/91-pulseaudio-custom.rules')
                    shutil.move(fname, '/usr/lib/udev/rules.d/')

    else:
        jsonreq = requests.get('https://api.github.com/gists/c357291e4e5c18894bea10665dcebffb').json()
        if os.path.isdir('/usr/share/alsa/cards/') and os.path.isdir('/usr/share/pulseaudio/alsa-mixer/profile-sets/') and os.path.isdir('/usr/lib/udev/rules.d/'):
            # PulseAudio
            for key in jsonreq['files'].keys():
                url = jsonreq['files'][key]['raw_url']
                if 'README' in url:
                    continue
                fname = wget.download(url)
                if fname == 'AppleT2.conf':
                    shutil.move(fname, '/usr/share/alsa/cards/')
                elif fname == 'apple-t2.conf':
                    shutil.move(fname, '/usr/share/pulseaudio/alsa-mixer/profile-sets/')
                elif fname == '91-pulseaudio-custom.rules':
                    shutil.move(fname, '/usr/lib/udev/rules.d/')

        elif os.path.isdir('/usr/share/alsa/cards/') and os.path.isdir('/usr/share/alsa-card-profile/mixer/profile-sets/') and os.path.isdir('/usr/lib/udev/rules.d/'):
            # PipeWire
            for key in jsonreq['files'].keys():
                url = jsonreq['files'][key]['raw_url']
                if 'README' in url:
                    continue
                fname = wget.download(url)
                if fname == 'AppleT2.conf':
                    shutil.move(fname, '/usr/share/alsa/cards/')
                elif fname == 'apple-t2.conf':
                    shutil.move(fname, '/usr/share/alsa-card-profile/mixer/profile-sets/')
                elif fname == '91-pulseaudio-custom.rules':
                    os.remove('91-pulseaudio-custom.rules')
                    wget.download('https://raw.githubusercontent.com/appleplectic/T2-Misc/main/91-pulseaudio-custom.rules')
                    shutil.move(fname, '/usr/lib/udev/rules.d/')



if __name__ == '__main__':

    print('This script installs T2 drivers on your Mac.')

    # Check if the script can be run on this machine
    check_compatibility()

    with open('/sys/devices/virtual/dmi/id/product_name', 'r', encoding='utf-8') as productname:
        model_id = productname.read().strip().strip('\n')

    # chdir to /tmp
    os.mkdir('/tmp/install-t2')
    os.chdir('/tmp/install-t2')


    # ArgParse
    DESC = 'Script to install drivers for T2 Macs.\nInstalls patched kernel, WiFi drivers, BCE drivers (for keyboard/touchpad), iBridge (touchbar), and Audio drivers.\nNeed help? See https://wiki.t2linux.org or https://discord.gg/fsaU8nbaRT!'
    parser = argparse.ArgumentParser(description=DESC)

    bceaudio = parser.add_argument_group('bce/audio')
    bceaudio.add_argument('-b', '--no-bce', action='store_true', help='Don\'t install the BCE drivers')
    bceaudio.add_argument('-a', '--no-audio', action='store_true', help='Don\'t install the Audio configs')

    wifi = parser.add_argument_group('wifi')
    wifi.add_argument('-w', '--no-wifi', action='store_true', help='Don\'t install the WiFi firmware')
    wifi.add_argument('-c', '--wifi-chipset', help='WiFi chipset number (i.e. 4364); see https://wiki.t2linux.org/guides/wifi/', default=None)
    wifi.add_argument('-f', '--filepaths', help='Absolute filepaths to the 3 WiFi firmware files (.trx, .clmb, & .txt), seperated by semicolons', default=None)

    ibridge = parser.add_argument_group('ibridge')
    ibridge.add_argument('-i', '--no-ibridge', help='Don\'t install iBridge drivers.')
    ibridge.add_argument('-n', '--ib-num', help='Configuration number for Touchbar (see: https://wiki.t2linux.org/guides/dkms/#module-configuration)', default='2')
    ibridge.add_argument('--backlight', action='store_true', help='Install the Backlight drivers. WARNING: UNSTABLE & ONLY FOR 16,1')

    kernels = parser.add_argument_group('kernels')
    kernels.add_argument('--mojave', action='store_true', help='Install the Mojave-patched WiFi kernel')
    kernels.add_argument('--bigsur', action='store_true', help='Install the Big Sur-patched WiFi kernel')
    parser.add_argument('-k', '--no-kernel', action='store_true', help='Don\'t install the custom kernel')

    distros = parser.add_argument_group('distributions')
    distros.add_argument('-arch', action='store_true', help='Arch Linux-based distros (Manjaro, Endeavour, etc.)')
    distros.add_argument('-deb', action='store_true', help='Debian-based distros (Ubuntu, Mint, MX, etc.)')

    parsed = parser.parse_args()

    if not parsed.deb and not parsed.arch:
        parser.error('a distribution must be specified')

    if not parsed.mojave and not parsed.bigsur and not parsed.no_kernel:
        parser.error('a kernel version, or no kernel install, must be specified')

    if (parsed.wifi_chipset is None or parsed.filepaths is None) and not parsed.no_wifi:
        parser.error('a wifi chipset and wifi files, or no wifi, should be specified')

    if parsed.deb:
        DISTRO = 'debian'
    elif parsed.arch:
        DISTRO = 'arch'


    wifi_id = parsed.wifi_chipset


    if not parsed.no_wifi:
        # Getting filepaths for the Wifi firmware files, and formatting them
        fps = parsed.filepaths
        fps = fps.strip(';').strip().split(';')
        escaped = []
        for file in fps:
            escapedf = file.strip().replace(' ', '\ ').replace(r'\\',r'\b'.replace('b',''))
            escaped.append(escapedf)
        for file in escaped:
            if not file.endswith('.trx') or not file.endswith('.clmb') or not file.endswith('.txt'):
                parser.error('invalid WiFi files - bad file extentions')

            if not os.path.isfile(file):
                parser.error('invalid WiFi filepaths - do not exist')

        install_wifi(model_id, wifi_id, escaped)


    # Patched Kernel install
    if parsed.bigsur:
        install_kernel(DISTRO, ver='bigsur')
    elif parsed.mojave:
        install_kernel(DISTRO, ver='mojave')

    # BCE DKMS
    if not parsed.no_bce:
        install_bce(DISTRO)

    # iBridge DKMS
    if not parsed.no_ibridge:
        if parsed.backlight:
            install_ib(DISTRO, parsed.ib_num, backlight=True)
        else:
            install_ib(DISTRO, parsed.ib_num, backlight=False)

    # Audio
    if not parsed.no_audio:
        install_audiofix(model_id)


    print('Script is complete!')

#====END CODE====
