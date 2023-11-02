# cruise_patch.py
#
# Author: Mykola1453
#
# Patches CruiseShipTycoon.exe to support widescreen resolutions,
# replacing the default '1280x960' resolution.
#
# MIT License
#
# Copyright (c) 2023 Mykola1453
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import shutil
import struct
import zlib
import sys
import os
import re

# Functions
def calculate_crc(file_path):
    crc = 0
    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            crc = zlib.crc32(chunk, crc)
    crc = crc & 0xFFFFFFFF
    return crc

def replace_bytes(content, search, replace):
    search_bytes = bytes.fromhex(search)
    replace_bytes = bytes.fromhex(replace)
    return content.replace(search_bytes, replace_bytes)

def get_res_le(res=False, letterbox=False, menu=False):
    tested_resolutions = {
        "1024x768": (1024, 768),
        "1280x720": (1280, 720),
        "1280x800": (1280, 800),
        "1280x960": (1280, 960),
        "1360x768": (1360, 768),
        "1366x768": (1366, 768),
        "1440x1080": (1440, 1080),
        "1600x900": (1600, 900),
        "1920x1080": (1920, 1080),
        "1920x1440": (1920, 1440),
        "2560x1440": (2560, 1440),
        "3840x2160": (3840, 2160)
    }

    if res:
        print("Using custom resolution")
        nums = res.split('x')
        if len(nums) == 2:
            width = int(nums[0])
            height = int(nums[1])
    else:
        # Using resolution of current display
        if os.name == 'nt':
            import ctypes

            user32 = ctypes.windll.user32
            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)
        else:
            try:
                import pyautogui

                # Get the screen resolution using pyautogui
                width, height = pyautogui.size()
            except:
                print("Install pyautogui to detect screen size: pip install pyautogui")

    if letterbox:
        width = (4 * height) / 3
        width = round(width)

        if (width == 960 and height == 720) or \
                (width == 1067 and height == 800) or \
                (width == 1200 and height == 900):
            # These 4:3 resolutions make the game render in 640x480,
            # using 1024x768
            width = 1024
            height = 768
        elif (width == 2880 and height == 2160):
            # The same as above
            # using 1920x1440
            width = 1920
            height = 1440
    if not menu:
        print(f"Changing resolution to {width}x{height}")

        if wide_menu_arg:
            print(f"Changing menu resolution to {width}x{height}")
            print("Menu will likely get cropped!")
    else:
        print(f"Changing menu resolution to {width}x{height}")

    if height == 2160:
        print(" NOTE: While the game can be displayed in 4K resolution,")
        print(" it will also crash a few times, probably due to engine limitation.")
        print(" Can't really promise a stable gameplay, but worth a try.")
        print(" If the game still doesn't launch in 4K after a few tries, or if 4K just doesn't work,")
        print(" feel free to restore backup and patch again, setting resolution to 2560x1440 or lower.")

    # Check if the actual resolution matches any of the tested resolutions
    matching_resolution = False
    for resolution, (expected_width, expected_height) in tested_resolutions.items():
        if (width == expected_width and height == expected_height):
            matching_resolution = True
            break

    if not matching_resolution:
        print(f" NOTE: {width}x{height} resolution was not tested, it might or might not work.")

    return width, height


def restore_backup():
    if os.path.isfile(f"{cruise_path}.bak"):
        directory = os.path.dirname(cruise_path)
        if directory:
            settings_path = f"{directory}/settings.dat"
        else:
            settings_path = "settings.dat"

        if os.path.isfile(settings_path):
            print("Resetting settings")
            os.remove(settings_path)

        print(f"Restoring backup")
        shutil.copy(f"{cruise_path}.bak", cruise_path)
    else:
        print(f"No backup is found")


# Command line arguments
arguments = sys.argv
cruise_path = False
res_arg = False
restore_arg = False
wide_menu_arg = False
letterbox_arg = False
help_arg = False
for arg in arguments:
    if arg.endswith('.exe'):
        cruise_path = arg
    elif re.match(r'\d+x\d+', arg):
        res_arg = arg
    elif arg == "--restore" or arg == "-r":
        restore_arg = True
    elif arg == "--wide_menu" or arg == "-w":
        wide_menu_arg = True
    elif arg == "--letterbox" or arg == "-l":
        letterbox_arg = True
    elif arg == "--help" or arg == "-h":
        help_arg = True

if not cruise_path:
    cruise_path = 'CruiseShipTycoon.exe'

if not os.path.isfile(cruise_path):
    print("File is not found!")

if not help_arg and not restore_arg:
    # Checking CRC of exe file
    calculated_crc = calculate_crc(cruise_path)

    tested_versions = [
        1142252342,  # v1.0.0.1
        3759243516  # v1.0.0.1 + Patch 3
    ]

    if calculated_crc in tested_versions:
        # Notice if game version is not the latest
        if calculated_crc == 1142252342:
            print(" FYI: this is not the latest version of the game")
            print(" Not that it matters, this patch will work as is.")
            print(" But if you wish, look for Patch 3 of the game,")
            print(" and patch again after updating.")

        # Create a backup of the original file
        print(f"Making a backup")
        shutil.copy(cruise_path, f"{cruise_path}.bak")

        print("Patching the game")
        # Open the file for reading in binary mode
        with open(cruise_path, 'rb') as cruise:
            # Read the contents of the file
            cruise_content = cruise.read()
        
        # Getting the resolution and converting the resolution to hexadecimal (little endian)
        width, height = get_res_le(res_arg, letterbox_arg)

        width_le = struct.pack('<I', width).hex()
        height_le = struct.pack('<I', height).hex()

        if wide_menu_arg:
            menu_width_le, menu_height_le = width_le, height_le
        else:
            menu_width, menu_height = get_res_le(res_arg, True, True)
            menu_width_le = struct.pack('<I', menu_width).hex()
            menu_height_le = struct.pack('<I', menu_height).hex()

        # Main Menu resolution
        if calculated_crc == tested_versions[0]:
            cruise_content = replace_bytes(cruise_content, "20030000C744243858020000",
                                        f"{menu_width_le}C7442438{menu_height_le}")
        elif calculated_crc == tested_versions[1]:
            cruise_content = replace_bytes(cruise_content, "20030000C744243458020000",
                                        f"{menu_width_le}C7442434{menu_height_le}")

        # In-game resolution
        if calculated_crc == tested_versions[0]:
            cruise_content = replace_bytes(cruise_content, "00050000E8DCF80100C74030C0030000",
                                        f"{width_le}E8DCF80100C74030{height_le}")
        elif calculated_crc == tested_versions[1]:
            cruise_content = replace_bytes(cruise_content, "00050000E80AE50100C74030C0030000",
                                        f"{width_le}E80AE50100C74030{height_le}")

        # HUD fix
        # Hex value below, 68 01, corresponds to 360 and is tied to height of 960.
        # Namely, it's height - 600
        # We need to correct it for the HUD to be placed right
        print("Fixing HUD")
        fix_height = height - 600

        # Convert fix value to little-endian hexadecimal value
        fix_h_le = struct.pack('<I', fix_height).hex()

        cruise_content = replace_bytes(cruise_content, "BD68010000C7", f"BD{fix_h_le}C7")
        cruise_content = replace_bytes(cruise_content, "000500007509BD68010000", f"{width_le}7509BD{fix_h_le}")

        # Save the modified content to a new file
        with open(cruise_path, 'wb') as cruise:
            cruise.write(cruise_content)

        print("File has been patched successfully")
        print("Don't forget to set game resolution to 1280x960 in options!")
    else:
        print(f"Wrong file! Didn't recognize CRC: {calculated_crc}")
        # restore_backup()
elif restore_arg:
    restore_backup()
else:
    help_msg = """
    This is a patch that replaces the default 1280x960 (4:3) resolution with a widescreen one, and fixes the game's HUD to accommodate the new resolution.
    Run it in the root of the game to set the resolution to your screen's resolution.
    Menu resolution and in-game resolution can have different value, so resolution of the menu is in 4:3 aspect ratio to avoid parts of the menu being cropped.
    (On Linux, you'll need to have pyautogui pip package to detect your screen resolution, otherwise you can define it manually, as explained below)\n
    Patch accepts the following arguments:
    "path/to/the/game.exe" defines path to the game's exe (not needed if the patch is already in the game folder)
    (width)x(height) sets custom resolution
    --wide_menu (-w) sets menu resolution to be widescreen too, but the menu can get partially cropped
    --letterbox (-l) sets that 4:3 resolution which is the closest to the defined widescreen resolution
    --restore (-r) if backup file is present, restores the game exe's backup and deletes user settings
    --help (-h) prints help message
    """
    print(help_msg)