import re
import subprocess
import time
import typing

from PIL import Image, ImageDraw, ImageFont


BASE_IMAGE = "/home/signage/raspi-signage/assets/logo.png"
FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
OUTPUT_TO = "/var/tmp/wait-screen.png"


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
