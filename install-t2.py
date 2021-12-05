#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# install-t2.py

# WARNING: EXTREMELY UNSTABLE

# This is a script that installs necessary drivers for the MacBook Pro 16,1
# Copyright (C) 2021 Appleplectic
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

# This script is soley for bundling these together for an easy-to-install way - I do not own any of these repos.

# Modules used:
# os, sys, shutil, subprocess, argparse (usually part of Python)
# pygit2 + dependencies
# requests + dependencies
# wget + dependencies



import argparse
import os
import re
import shutil
import subprocess
import sys

from urllib.error import HTTPError

import pygit2
import requests
import wget



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
                subprocess.call(f'pacman -U {filename} --noconfirm', shell=True)
        elif distro == 'debian':
            # Have to use 5.13.15 and not 5.13.19
            jsonreq = requests.get("https://api.github.com/repos/marcosfad/mbp-ubuntu-kernel/releases/49398102").json()
            download_urls = []
            for dic in jsonreq['assets']:
                download_urls.append(dic['browser_download_url'])
            for url in download_urls:
                filename = wget.download(url)
                subprocess.call(f'apt-get install ./{filename} -y', shell=True)
        elif distro == 'fedora':
            # Have to use mbp16 one
            jsonreq = requests.get('https://api.github.com/repos/mikeeq/mbp-fedora-kernel/releases/43328558').json()
            download_urls = []
            for dic in jsonreq['assets']:
                download_urls.append(dic['browser_download_url'])
            for url in download_urls:
                if 'packages.zip' in url or 'sha256' in url:
                    continue
                filename = wget.download(url)
                subprocess.call(f'rpm -i {filename}', shell=True)

    elif ver == 'mojave':
        if distro == 'arch':
            jsonreq = requests.get("https://api.github.com/repos/aunali1/linux-mbp-arch/releases/latest").json()
            download_urls = []
            for dic in jsonreq['assets']:
                download_urls.append(dic['browser_download_url'])
            for url in download_urls:
                filename = wget.download(url)
                subprocess.call(f'pacman -U {filename} --noconfirm', shell=True)
        elif distro == 'debian':
            # Have to use 5.13.15 and not 5.13.19
            jsonreq = requests.get("https://api.github.com/repos/marcosfad/mbp-ubuntu-kernel/releases/49397674").json()
            download_urls = []
            for dic in jsonreq['assets']:
                download_urls.append(dic['browser_download_url'])
            for url in download_urls:
                filename = wget.download(url)
                subprocess.call(f'apt-get install ./{filename} -y', shell=True)
        elif distro == 'fedora':
            jsonreq = requests.get('https://api.github.com/repos/mikeeq/mbp-fedora-kernel/releases/latest').json()
            download_urls = []
            for dic in jsonreq['assets']:
                download_urls.append(dic['browser_download_url'])
            for url in download_urls:
                if 'packages.zip' in url or 'sha256' in url:
                    continue
                filename = wget.download(url)
                subprocess.call(f'rpm -i {filename}')

    with open('/etc/fstab', 'a') as fstab:
        fstab.write('\nefivarfs /sys/firmware/efi/efivars efivarfs ro,remount 0 0')



def install_bce(distro:str):

    if distro == 'arch':
        subprocess.call('pacman -S dkms --noconfirm --needed', shell=True)
        jsonreq = requests.get('https://api.github.com/repos/aunali1/apple-bce-arch/releases/latest').json()
        download_urls = []
        for dic in jsonreq['assets']:
            download_urls.append(dic['browser_download_url'])
        for url in download_urls:
            if not url.endswith('pkg.tar.zst') or not 'apple-bce-dkms-git' in url:
                continue
            filename = wget.download(url)
        subprocess.call(f'pacman -U {filename} --noconfirm', shell=True)
    elif distro == 'debian' or distro == 'fedora':
        if distro == 'debian':
            subprocess.call('apt-get install dkms -y', shell=True)
        else:
            subprocess.call('dnf install dkms -y', shell=True)

        pygit2.clone_repository('https://github.com/t2linux/apple-bce-drv', '/usr/src/apple-bce-r183.c884d9c')
        with open('/usr/src/apple-bce-r183.c884d9c/dkms.conf', 'w', encoding='utf-8') as conf:
            conf.write('''PACKAGE_NAME="apple-bce"
PACKAGE_VERSION="r183.c884d9c"
MAKE[0]="make KVERSION=$kernelver"
CLEAN="make clean"
BUILT_MODULE_NAME[0]="apple-bce"
DEST_MODULE_LOCATION[0]="/kernel/drivers/misc"
AUTOINSTALL="yes"''')
        vmlinuz = []
        for file in os.listdir('/boot'):
            if 'vmlinuz-' in file:
                vmlinuz.append(file)
        kernels = []
        for file in vmlinuz:
            file = file.replace('vmlinuz-', '')
            kernels.append(file)
        for kernel in kernels:
            subprocess.call(f'dkms install -m apple-bce -v r183.c884d9c -k {kernel}', shell=True)



def install_ib(distro:str, tb_config_num:str, backlight:bool):

    if distro == 'arch':
        subprocess.call('pacman -S dkms --noconfirm --needed', shell=True)
    elif distro == 'debian':
        subprocess.call('apt-get install dkms -y', shell=True)
    elif distro == 'fedora':
        subprocess.call('dnf install dkms -y', shell=True)

    try:
        os.mkdir('/usr/src/apple-ibridge-0.1')
    except FileExistsError:
        shutil.rmtree('/usr/src/apple-ibridge-0.1')
        os.mkdir('/usr/src/apple-ibridge-0.1')

    if backlight:
        pygit2.clone_repository('https://github.com/Redecorating/apple-ib-drv', '/usr/src/apple-ibridge-0.1')
    else:
        pygit2.clone_repository('https://github.com/t2linux/apple-ib-drv', '/usr/src/apple-ibridge-0.1')

    vmlinuz = []
    for file in os.listdir('/boot'):
        if 'vmlinuz-' in file:
            vmlinuz.append(file)
    kernels = []
    for file in vmlinuz:
        file = file.replace('vmlinuz-', '')
        kernels.append(file)
    for kernel in kernels:
        subprocess.call(f'dkms install -m apple-ibridge -v 0.1 -k {kernel}', shell=True)

    subprocess.call('modprobe apple_bce', shell=True)
    subprocess.call('modprobe apple_ib_tb', shell=True)
    subprocess.call('modprobe apple_ib_als', shell=True)

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



def install_audiofix(model_id:str, stereo:bool):

    home = os.path.expanduser('~')

    if model_id == 'MacBookPro16,1':
        if stereo:
            jsonreq = requests.get('https://api.github.com/gists/67d23a7c7aa1ee51edcb3eb60cd6a893').json()
        else:
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
            print('Please install PulseAudio or PipeWire first.')

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
            print('Please install PulseAudio or PipeWire first.')

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
        else:
            print('Please install PulseAudio or PipeWire first.')




if __name__ == '__main__':

    if sys.version_info < (3,7,0):
        raise EnvironmentError("Must be using Python 3.7+")

    try:
        requests.get('https://www.google.com/').status_code
    except:
        raise ConnectionRefusedError('This device does not appear to have an internet connection. Please connect Ethernet, then try again.') from None

    with open('/sys/devices/virtual/dmi/id/product_name', 'r', encoding='utf-8') as productname:
        model_id = productname.read().strip('\n').strip()


    unparsed = subprocess.check_output('lspci -d \'14e4:*\'', shell=True).decode('utf-8')
    try:
        lspci = re.search(r'BCM(\d{4})', unparsed).group(1)
    except AttributeError:
        lspci = None
        print('Failed to parse lspci. Make sure to fill out wifi chipset or filepaths.')

    # ArgParse
    DESC = 'Script to install drivers for T2 Macs.\nInstalls patched kernel, WiFi drivers, BCE drivers (for keyboard/touchpad), iBridge (touchbar), and Audio drivers.\nNeed help? See https://wiki.t2linux.org or https://discord.gg/fsaU8nbaRT!'
    parser = argparse.ArgumentParser(description=DESC)

    bceaudio = parser.add_argument_group('bce/audio')
    bceaudio.add_argument('--no-bce', action='store_true', help='Don\'t install the BCE drivers')
    bceaudio.add_argument('--no-audio', action='store_true', help='Don\'t install the Audio configs')
    bceaudio.add_argument('--stereo', action='store_true', help='Install stereo configurations instead of regular ones for better sounding 16,1 audio')

    wifi = parser.add_argument_group('wifi')
    wifi.add_argument('--no-wifi', action='store_true', help='Don\'t install the WiFi firmware')
    wifi.add_argument('--wifi-chipset', help='WiFi chipset number (i.e. 4364); see https://wiki.t2linux.org/guides/wifi/. Default tries to parse lspci', default=lspci)
    wifi.add_argument('--filepaths', help='Absolute filepaths to the 3 WiFi firmware files (.trx, .clmb, & .txt), seperated by semicolons', default=None)
    wifi.add_argument('--ioreg', help='`ioreg -l | grep RequestedFiles` output (in one line) from macOS - tries to use this to download files online', default=None)

    ibridge = parser.add_argument_group('ibridge')
    ibridge.add_argument('--no-ibridge', help='Don\'t install iBridge drivers.')
    ibridge.add_argument('--ib-num', help='Configuration number for Touchbar (see: https://wiki.t2linux.org/guides/dkms/#module-configuration)', default='2')
    ibridge.add_argument('--backlight', action='store_true', help='Install the Backlight drivers. WARNILE & ONLY FOR 16,1')

    kernels = parser.add_argument_group('kernels')
    kernels.add_argument('--mojave', action='store_true', help='Install the Mojave-patched WiFi kernel')
    kernels.add_argument('--bigsur', action='store_true', help='Install the Big Sur-patched WiFi kernel')
    kernels.add_argument('--no-kernel', action='store_true', help='Don\'t install the custom kernel')

    parsed = parser.parse_args()

    # Check if script is run with root
    if os.geteuid() != 0:
        raise EnvironmentError('Script must be run with root privileges.')

    # chdir to /tmp
    try:
        os.mkdir('/tmp/install-t2')
    except FileExistsError:
        shutil.rmtree('/tmp/install-t2')
        os.mkdir('/tmp/install-t2')
    os.chdir('/tmp/install-t2')

    if os.path.isfile('/usr/bin/apt-get'):
        DISTRO = 'debian'
    elif os.path.isfile('/usr/bin/pacman'):
        DISTRO = 'arch'
    elif os.path.isfile('/usr/bin/dnf'):
        DISTRO = 'fedora'
    else:
        parser.error('either this distribution is not supported, or the script failed to parse the package manager')

    if not parsed.mojave and not parsed.bigsur and not parsed.no_kernel:
        parser.error('a kernel version, or no kernel install, must be specified')

    if (parsed.wifi_chipset is None or (parsed.filepaths is None and parsed.ioreg is None)) and not parsed.no_wifi:
        parser.error('either failed to parse the wifi chipset, or filepaths or ioreg were not specified')

    wifi_id = parsed.wifi_chipset

    if DISTRO == 'debian':
        subprocess.call('apt-get update', shell=True)
    elif DISTRO == 'arch':
        subprocess.call('pacman -Sy --noconfirm', shell=True)
    elif DISTRO == 'fedora':
        subprocess.call('dnf check-update -y', shell=True)


    if not parsed.no_wifi:
        # Getting filepaths for the Wifi firmware files, and formatting them
        if parsed.filepaths is not None:
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

        elif parsed.ioreg is not None:
            research = re.search(r'"Firmware"="(.*?)"(.*?)"Regulatory"="(.*?)"(.*?)"NVRAM"="(.*?)"', parsed.ioreg)
            filelist = []
            filelist.append(research.group(1))
            filelist.append(research.group(3))
            filelist.append(research.group(5))
            filepaths = []
            for file in filelist:
                try:
                    fname = wget.download('https://raw.githubusercontent.com/AdityaGarg8/macOS-Big-Sur-WiFi-Firmware/main/' + file)
                except HTTPError:
                    try:
                        fname = wget.download('https://packages.aunali1.com/apple/wifi-fw/18G2022/' + file)
                    except HTTPError:
                        raise FileNotFoundError(f'Failed to download WiFi file {file}. It may not be in the archives.') from None
                filepaths.append(os.getcwd() + '/' + fname)
            install_wifi(model_id, wifi_id, filepaths)



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
        install_audiofix(model_id, parsed.stereo)


    print('Script is complete!')
