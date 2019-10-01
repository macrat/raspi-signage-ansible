import re
import subprocess
import time
import typing

from PIL import Image, ImageDraw, ImageFont
import qrcode


BASE_IMAGE = "/home/signage/initial-screen/initial-screen-base.png"
FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
OUTPUT_TO = "/var/tmp/initial-screen.png"
HOSTAPD_CONF = "/etc/hostapd/hostapd.conf"

CONSOLE_URL = "http://example.com:8080"


def get_addresses() -> typing.List[typing.Tuple[str, str]]:
    result = subprocess.run(
        ["ip", "-f", "inet", "-o", "addr", "show"], capture_output=True
    )

    return sorted(
        [
            (m.group(1), m.group(2))
            for m in (
                re.match(r"\d+:\s+(\w+)\s+inet\s+(\d{1,3}(?:\.\d{1,3}){3}/\d+) ", line)
                for line in result.stdout.decode("utf8").splitlines()
            )
            if m is not None and not m.group(2).startswith("127.")
        ],
        key=lambda x: x[0],
    )


def get_wifi_info() -> typing.Tuple[str, str]:
    ssid = ""
    password = ""
    for line in open(HOSTAPD_CONF):
        m = re.match(r"^ssid=(?P<ssid>.*)|wpa_passphrase=(?P<password>.*)$", line)
        if m:
            if m.group("ssid"):
                ssid = m.group("ssid")
            if m.group("password"):
                password = m.group("password")

    return ssid, password


def generate(
    addresses: typing.List[typing.Tuple[str, str]],
    base: str = BASE_IMAGE,
    font: str = FONT_FILE,
    output: str = OUTPUT_TO,
) -> None:
    img = Image.open(base)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(font, 24)

    longest_if = max(len(x[0]) for x in addresses)

    for i, (interface, address) in enumerate(addresses):
        if_ = " " * (longest_if - len(interface)) + interface
        draw.text((20, i * 40), f"{if_}: {address}", font=font, fill=(64, 64, 64, 255))

    qr = qrcode.QRCode(border=0)
    ssid, password = get_wifi_info()
    qr.add_data(f"WIFI:T:WPA;S:{ssid};P:{password};;")
    qr.make()
    img.paste(
        qr.make_image(fill_color="black", back_color="white").resize((230, 230)),
        (180, 500),
        qr.make_image(fill_color="white", back_color="black")
        .resize((230, 230))
        .convert("L"),
    )
    draw.text((170, 740), f"{ssid} / {password}", font=font, fill=(64, 64, 64, 255))

    qr = qrcode.QRCode(border=0)
    qr.add_data(CONSOLE_URL)
    qr.make()
    img.paste(
        qr.make_image(fill_color="black", back_color="white").resize((230, 230)),
        (768 - 160, 500),
        qr.make_image(fill_color="white", back_color="black")
        .resize((230, 230))
        .convert("L"),
    )

    img.save(output)


def main() -> typing.NoReturn:
    addresses = get_addresses()

    generate(addresses)

    while True:
        time.sleep(10)

        new = get_addresses()

        if len(addresses) != len(new):
            generate(addresses)
            continue

        for x, y in zip(addresses, new):
            if x != y:
                generate(addresses)
                break


if __name__ == "__main__":
    main()
