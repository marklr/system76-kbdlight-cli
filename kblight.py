#!/bin/env python3
import sys

import plac
import webcolors
import os

_COLOR_FILTERS = {
    '#': '',
    '(': '',
    ')': '',
}

LIGHT_CONTROLS = {
    'left': '/sys/class/leds/system76::kbd_backlight/color_left',
    'center': '/sys/class/leds/system76::kbd_backlight/color_center',
    'right': '/sys/class/leds/system76::kbd_backlight/color_right',
}

def check_light_controls():
    for light, fpath in LIGHT_CONTROLS.items():
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Light path {fpath} for light {light} does not exist")


def parse_color(color):
    c = str(color).lower().strip()
    for k, v in _COLOR_FILTERS.items():
        c = c.replace(k, v)

    hex = None
    try:
        hc = '#' + c if not c.startswith('#') else c
        rgb = webcolors.hex_to_rgb(hc)
        if rgb:
            return hc.upper()
    except Exception:
        # probably not a hex already
        pass

    try:
        hex = webcolors.name_to_hex(c)
    except Exception:
        pass

    if '%' in c:
        try:
            hex = webcolors.rgb_percent_to_hex((int(x.strip()) for x in c.split(',')))
        except Exception:
            pass
    else:
        try:
            hex = webcolors.rgb_to_hex((int(x.strip()) for x in c.split(',')))
        except Exception:
            pass

    return hex


def set_light(name, hex):
    if name not in LIGHT_CONTROLS:
        raise NotImplementedError(f"Cannot control light {name}")

    print(f"[+] Setting light {name} to {hex}", file=sys.stdout)

    with open(LIGHT_CONTROLS[name], 'w') as f:
        f.write(hex.upper().replace('#', '') + "\n")

def main(color: ("color choice (rgb triplet/color name/hex)", 'positional'),
         light: ("light to set (right/left/center/all)", 'option', 'l')='all'):
    check_light_controls()
    hex = parse_color(color)

    if not hex:
        print(f"[-] Unrecognized color {color}", file=sys.stderr)
        return os.EX_NOINPUT

    print(f"[*] Parsed color {color} to hex {hex}", file=sys.stdout)
    for light_ in filter(lambda x: light == x or light == 'all', LIGHT_CONTROLS.keys()):
        set_light(light_, hex)

if __name__ == '__main__':
    plac.call(main)
