"""The World Today: 25 November 2026 in one image.

A pure standard-library Python program that draws a newspaper front
page summarising the world news of Wednesday 25 November 2026 and
writes it as a deterministic PNG to /output/entry.png (or to the
directory named by MAKEFUN_OUTPUT_DIR when that variable is set).

Stories carried, each reported on 25 November by at least two outlets:
two oil tankers struck naval mines and caught fire in the Strait of
Hormuz, Iran's Revolutionary Guard said; China launched Shenzhou-24
carrying Pakistani pilot Muhammad Zeeshan Ali, the first foreigner to
board the Tiangong space station; Colombian forces stormed a Cartagena
supermarket after a 17-hour siege and freed all 20 hostages, one
captor killed; a Brooklyn jury convicted Huawei of conspiracy to steal
trade secrets and bank fraud; Australia and the Solomon Islands signed
a treaty making Australia the primary security partner. The ticker
adds the leaked Rosstat death toll near 500,000, the Houthi drone
strike on a Riyadh tower, North Korea expelling the Swiss envoy and
the Dow closing above 50,000.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (176, 42, 30)
BLUE = (29, 78, 121)
GREY = (96, 96, 96)
LIGHT = (226, 219, 198)
GREEN = (58, 128, 62)
GOLD = (198, 146, 32)
TEAL = (28, 110, 110)
SKY = (18, 52, 96)
ORANGE = (224, 122, 32)
SEA = (16, 68, 110)


# A 5x7 bitmap font. Each glyph is seven rows of five bits.
FONT = {
    "A": (14, 17, 17, 31, 17, 17, 17), "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14), "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31), "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15), "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14), "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17), "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17), "N": (17, 17, 25, 21, 19, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14), "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13), "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30), "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14), "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17), "X": (17, 10, 4, 4, 4, 10, 17),
    "Y": (17, 10, 4, 4, 4, 4, 4), "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14), "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 2, 4, 8, 31), "3": (14, 17, 1, 6, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2), "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14), "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14), "9": (14, 17, 17, 15, 1, 2, 12),
    ".": (0, 0, 0, 0, 0, 12, 12), ",": (0, 0, 0, 0, 12, 4, 8),
    "'": (4, 4, 8, 0, 0, 0, 0), '"': (10, 10, 10, 0, 0, 0, 0),
    "-": (0, 0, 0, 31, 0, 0, 0), ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8), "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 2, 4, 0, 4), "/": (1, 1, 2, 4, 8, 16, 16),
    "(": (2, 4, 8, 8, 8, 4, 2), ")": (8, 4, 2, 2, 2, 4, 8),
    "$": (4, 15, 20, 14, 5, 30, 4), "%": (24, 25, 2, 4, 8, 19, 3),
    "+": (0, 4, 4, 31, 4, 4, 0), "&": (12, 18, 20, 8, 21, 18, 13),
    " ": (0, 0, 0, 0, 0, 0, 0),
}


class Canvas:
    """A tiny RGB framebuffer with just enough drawing for a page."""

    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(colour * (width * height))

    def set(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            off = (y * self.width + x) * 3
            self.pixels[off:off + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, colour)

    def frame(self, x, y, w, h, colour, thick=3):
        self.rect(x, y, w, thick, colour)
        self.rect(x, y + h - thick, w, thick, colour)
        self.rect(x, y, thick, h, colour)
        self.rect(x + w - thick, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour, thick=2):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            self.rect(x - thick // 2, y - thick // 2, thick, thick, colour)

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, colour)

    def text(self, x, y, s, scale, colour):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, colour)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return max(len(s) - 1, 0) * 6 * scale + 5 * scale if s else 0

    def centred(self, y, s, scale, colour):
        x = (self.width - self.text_width(s, scale)) // 2
        self.text(x, y, s, scale, colour)

    def wrapped(self, x, y, s, scale, colour, max_width, leading=None):
        if leading is None:
            leading = 9 * scale
        words = s.split()
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if self.text_width(trial, scale) <= max_width:
                line = trial
            else:
                self.text(x, y, line, scale, colour)
                y += leading
                line = word
        if line:
            self.text(x, y, line, scale, colour)
            y += leading
        return y


def draw_hormuz(cv, x, y, w, h):
    """Lead picture: two tankers burning in the Strait of Hormuz."""
    cv.rect(x, y, w, h, SKY)
    cv.disc(x + 880, y + 42, 26, GOLD)
    cv.rect(x, y + 110, w, h - 110, SEA)
    for wx in range(x + 20, x + w - 20, 60):
        cv.rect(wx, y + 128, 34, 4, LIGHT)
    # Tanker one, left.
    cv.rect(x + 90, y + 138, 300, 34, INK)
    cv.rect(x + 90, y + 118, 300, 20, RED)
    cv.rect(x + 150, y + 96, 26, 22, PAPER)
    cv.rect(x + 300, y + 96, 26, 22, PAPER)
    # Flames over tanker one.
    cv.rect(x + 170, y + 66, 26, 30, ORANGE)
    cv.rect(x + 178, y + 52, 10, 16, GOLD)
    cv.rect(x + 230, y + 78, 20, 18, ORANGE)
    cv.disc(x + 200, y + 44, 16, GREY)
    cv.disc(x + 240, y + 30, 12, GREY)
    # Tanker two, right.
    cv.rect(x + 560, y + 138, 300, 34, INK)
    cv.rect(x + 560, y + 118, 300, 20, RED)
    cv.rect(x + 620, y + 96, 26, 22, PAPER)
    cv.rect(x + 770, y + 96, 26, 22, PAPER)
    cv.rect(x + 660, y + 70, 26, 26, ORANGE)
    cv.rect(x + 668, y + 56, 10, 16, GOLD)
    cv.rect(x + 720, y + 80, 20, 16, ORANGE)
    cv.disc(x + 690, y + 46, 16, GREY)
    cv.disc(x + 730, y + 32, 12, GREY)
    cv.text(x + 18, y + h - 30, "TWO TANKERS HIT MINES, IRAN SAYS", 2, PAPER)


def draw_rocket(cv, x, y):
    cv.rect(x + 22, y + 6, 16, 34, PAPER)
    cv.rect(x + 26, y + 0, 8, 8, RED)
    cv.rect(x + 14, y + 30, 8, 12, RED)
    cv.rect(x + 38, y + 30, 8, 12, RED)
    cv.rect(x + 24, y + 42, 12, 10, ORANGE)
    cv.rect(x + 27, y + 42, 6, 10, GOLD)
    cv.disc(x + 6, y + 8, 3, PAPER)
    cv.disc(x + 54, y + 20, 3, PAPER)


def draw_store(cv, x, y):
    cv.rect(x + 4, y + 30, 54, 30, INK)
    cv.rect(x + 8, y + 20, 46, 10, RED)
    cv.rect(x + 22, y + 40, 18, 20, PAPER)


def draw_columns(cv, x, y):
    cv.rect(x + 6, y + 34, 50, 6, INK)
    cv.rect(x + 10, y + 40, 42, 4, INK)
    for i in range(4):
        cv.rect(x + 12 + i * 11, y + 20, 5, 14, INK)
    cv.disc(x + 31, y + 14, 10, INK)
    cv.rect(x + 29, y + 0, 4, 6, INK)


def draw_island(cv, x, y):
    cv.rect(x + 4, y + 40, 54, 14, GREEN)
    cv.rect(x + 6, y + 54, 50, 6, SEA)
    cv.line(x + 31, y + 6, x + 31, y + 40, INK, 3)
    cv.rect(x + 31, y + 6, 22, 12, BLUE)
    cv.rect(x + 31, y + 18, 22, 4, PAPER)


def story(cv, x, y, w, icon, kicker, headline, body):
    cv.text(x, y, kicker, 2, RED)
    y += 22
    y = cv.wrapped(x, y, headline, 2, INK, w, leading=18)
    y += 4
    icon(cv, x, y)
    y = cv.wrapped(x + 72, y, body, 2, INK, w - 72, leading=18)
    return y


def write_png(path, cv):
    raw = b""
    for yy in range(cv.height):
        raw += b"\x00"
        raw += bytes(cv.pixels[yy * cv.width * 3:(yy + 1) * cv.width * 3])
    data = zlib.compress(raw, 9)

    def chunk(kind, payload):
        out = struct.pack(">I", len(payload)) + kind + payload
        out += struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.width, cv.height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", data)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


def main():
    cv = Canvas(WIDTH, HEIGHT, PAPER)
    cv.frame(8, 8, WIDTH - 16, HEIGHT - 16, INK, 4)
    cv.centred(28, "THE WORLD TODAY", 5, INK)
    cv.centred(78, "WEDNESDAY 25 NOVEMBER 2026", 2, GREY)
    cv.rect(32, 104, WIDTH - 64, 3, INK)
    y = cv.wrapped(32, 120, "TANKERS ABLAZE IN THE STRAIT OF HORMUZ", 3, INK,
                   WIDTH - 64, leading=28)
    draw_hormuz(cv, 32, y + 8, WIDTH - 64, 210)
    y = y + 226
    y = cv.wrapped(32, y, "IRAN'S REVOLUTIONARY GUARD SAID TWO OIL TANKERS STRUCK "
                   "NAVAL MINES AND CAUGHT FIRE IN THE STRAIT OF HORMUZ ON "
                   "WEDNESDAY, AFTER THE VESSELS TOOK AN UNAUTHORISED ROUTE. "
                   "THE STRAIT CARRIES A FIFTH OF THE WORLD'S OIL.",
                   2, INK, WIDTH - 64, leading=18)
    cv.rect(32, y + 6, WIDTH - 64, 3, INK)
    top = y + 18
    end1 = story(cv, 32, top, 464, draw_rocket, "SPACE",
                 "SHENZHOU-24 REACHES TIANGONG",
                 "CHINA LAUNCHED SHENZHOU-24 ON WEDNESDAY, CARRYING PAKISTANI "
                 "PILOT MUHAMMAD ZEESHAN ALI, THE FIRST FOREIGNER TO BOARD THE "
                 "TIANGONG SPACE STATION. THE CREW DOCKED IN 3.5 HOURS.")
    end2 = story(cv, 528, top, 464, draw_store, "COLOMBIA",
                 "ALL 20 HOSTAGES FREED IN CARTAGENA",
                 "FORCES STORMED AN EXITO SUPERMARKET AFTER A 17-HOUR SIEGE, "
                 "RESCUING ALL 20 HOSTAGES. ONE CAPTOR WAS KILLED. TEN PEOPLE "
                 "HAD BEEN FREED EARLIER.")
    mid = max(end1, end2)
    cv.rect(32, mid + 8, WIDTH - 64, 3, INK)
    top2 = mid + 20
    end3 = story(cv, 32, top2, 464, draw_columns, "TECH",
                 "HUAWEI FOUND GUILTY IN NEW YORK",
                 "A BROOKLYN JURY CONVICTED HUAWEI OF CONSPIRACY TO STEAL "
                 "TRADE SECRETS AND BANK FRAUD. THE COURT ACQUITTED IT OF THE "
                 "RACKETEERING CHARGE.")
    end4 = story(cv, 528, top2, 464, draw_island, "PACIFIC",
                 "SOLOMONS SIGN PACT WITH AUSTRALIA",
                 "AUSTRALIA AND THE SOLOMON ISLANDS SIGNED A TREATY IN "
                 "CANBERRA MAKING AUSTRALIA THE PRIMARY SECURITY PARTNER. NO "
                 "FOREIGN BASE MAY BE BUILT ON SOLOMONS SOIL.")
    bottom = max(end3, end4)
    cv.rect(32, bottom + 8, WIDTH - 64, 3, INK)
    y = cv.wrapped(32, bottom + 18, "ROSSTAT LEAK: NEARLY 500,000 RUSSIAN DEAD + "
                   "HOUTHI DRONE HITS RIYADH TOWER, 11 HURT + NORTH KOREA EXPELS "
                   "SWISS ENVOY + DOW CLOSES ABOVE 50,000",
                   2, GREY, WIDTH - 64, leading=18)
    cv.rect(32, y + 6, WIDTH - 64, 3, INK)
    cv.text(32, y + 18, "IN BRIEF", 2, RED)
    y = cv.wrapped(32, y + 40, "SUDAN: RSF DRONE STRIKES KILL 19 CIVILIANS, "
                   "RIGHTS GROUP SAYS. GAZA: ISRAEL KILLS HAMAS SECURITY CHIEF "
                   "ABUELOUF IN STRIKE. CLIMATE: POPE LEO WARNS COP31 FAILED "
                   "TO REACH A DEAL.",
                   2, INK, WIDTH - 64, leading=18)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"), cv)


if __name__ == "__main__":
    main()
