"""Wednesday 25 November 2026, drawn as one front page.

This program needs nothing but the Python standard library. It paints
a newspaper page for Wednesday 25 November 2026 and saves it as a
1024 by 1024 PNG. The output path is /output/entry.png unless the
MAKEFUN_OUTPUT_DIR environment variable names another folder, and
running it twice gives byte-identical files.

The front page leads with the two tankers burning in the Strait of
Hormuz. Below it, four shorter stories: Shenzhou-24 docking at
Tiangong with the first foreign visitor aboard, the end of the
Cartagena supermarket siege, the Huawei verdict in New York, and the
Australia-Solomon Islands security treaty. A ticker and an In Brief
column carry the Rosstat toll, the Riyadh tower strike, the Swiss
envoy's expulsion from Pyongyang and the Dow's record close.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PALETTE = {
    "paper": (247, 243, 232),
    "ink": (26, 26, 26),
    "red": (176, 42, 30),
    "grey": (96, 96, 96),
    "sand": (226, 219, 198),
    "gold": (198, 146, 32),
    "teal": (28, 110, 110),
    "night": (18, 52, 96),
    "flame": (224, 122, 32),
    "sea": (16, 68, 110),
    "leaf": (58, 128, 62),
    "navy": (29, 78, 121),
}

# Five-wide, seven-tall letterforms. "#" is ink, "." is empty.
GLYPHS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##...", "##..#", "...#.", "..#..", ".#...", "#.###", "...##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


class Sheet:
    """An RGB pixel grid with the few marks a front page needs."""

    def __init__(self, width, height, base):
        self.width = width
        self.height = height
        self.buf = bytearray(base * (width * height))

    def px(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            at = (y * self.width + x) * 3
            self.buf[at:at + 3] = bytes(colour)

    def box(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, colour)

    def border(self, x, y, w, h, colour, t=3):
        self.box(x, y, w, t, colour)
        self.box(x, y + h - t, w, t, colour)
        self.box(x, y, t, h, colour)
        self.box(x + w - t, y, t, h, colour)

    def seg(self, x0, y0, x1, y1, colour, t=2):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i // n
            y = y0 + (y1 - y0) * i // n
            self.box(x - t // 2, y - t // 2, t, t, colour)

    def dot(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.px(xx, yy, colour)

    def glyph(self, x, y, text, scale, colour):
        pen = x
        for ch in text.upper():
            rows = GLYPHS.get(ch, GLYPHS[" "])
            for r, row in enumerate(rows):
                for c, mark in enumerate(row):
                    if mark == "#":
                        self.box(pen + c * scale, y + r * scale,
                                 scale, scale, colour)
            pen += 6 * scale
        return pen

    def measure(self, text, scale):
        if not text:
            return 0
        return (len(text) * 6 - 1) * scale

    def center(self, y, text, scale, colour):
        x = (self.width - self.measure(text, scale)) // 2
        self.glyph(x, y, text, scale, colour)

    def para(self, x, y, text, scale, colour, width, gap=None):
        if gap is None:
            gap = 9 * scale
        words = text.split()
        line = ""
        for word in words:
            nxt = word if not line else line + " " + word
            if self.measure(nxt, scale) <= width:
                line = nxt
            else:
                self.glyph(x, y, line, scale, colour)
                y += gap
                line = word
        if line:
            self.glyph(x, y, line, scale, colour)
            y += gap
        return y


def tanker(sh, x, y):
    """One burning tanker: hull, deck, cabins, flame and smoke."""
    sh.box(x, y + 138, 300, 34, PALETTE["ink"])
    sh.box(x, y + 118, 300, 20, PALETTE["red"])
    sh.box(x + 60, y + 96, 26, 22, PALETTE["paper"])
    sh.box(x + 210, y + 96, 26, 22, PALETTE["paper"])
    sh.box(x + 80, y + 66, 26, 30, PALETTE["flame"])
    sh.box(x + 88, y + 52, 10, 16, PALETTE["gold"])
    sh.box(x + 140, y + 78, 20, 18, PALETTE["flame"])
    sh.dot(x + 110, y + 44, 16, PALETTE["grey"])
    sh.dot(x + 150, y + 30, 12, PALETTE["grey"])


def hormuz_scene(sh, x, y, w, h):
    """Lead picture: two tankers on fire under a low sun."""
    sh.box(x, y, w, h, PALETTE["night"])
    sh.dot(x + 880, y + 42, 26, PALETTE["gold"])
    sh.box(x, y + 110, w, h - 110, PALETTE["sea"])
    for wx in range(x + 20, x + w - 20, 60):
        sh.box(wx, y + 128, 34, 4, PALETTE["paper"])
    tanker(sh, x + 90, y)
    tanker(sh, x + 560, y)
    sh.glyph(x + 18, y + h - 30, "TWO TANKERS HIT MINES, IRAN SAYS",
             2, PALETTE["paper"])


def rocket_mark(sh, x, y):
    sh.box(x + 22, y + 8, 16, 32, PALETTE["ink"])
    sh.box(x + 26, y + 2, 8, 8, PALETTE["red"])
    sh.box(x + 26, y + 14, 8, 12, PALETTE["paper"])
    sh.box(x + 14, y + 32, 8, 12, PALETTE["red"])
    sh.box(x + 38, y + 32, 8, 12, PALETTE["red"])
    sh.box(x + 24, y + 44, 12, 10, PALETTE["flame"])
    sh.box(x + 27, y + 44, 6, 10, PALETTE["gold"])
    sh.dot(x + 6, y + 10, 3, PALETTE["gold"])
    sh.dot(x + 54, y + 22, 3, PALETTE["gold"])


def store_mark(sh, x, y):
    sh.box(x + 4, y + 32, 54, 28, PALETTE["ink"])
    sh.box(x + 8, y + 22, 46, 10, PALETTE["red"])
    sh.box(x + 22, y + 42, 18, 18, PALETTE["paper"])


def court_mark(sh, x, y):
    sh.box(x + 6, y + 36, 50, 6, PALETTE["ink"])
    sh.box(x + 10, y + 42, 42, 4, PALETTE["ink"])
    for i in range(4):
        sh.box(x + 12 + i * 11, y + 22, 5, 14, PALETTE["ink"])
    sh.dot(x + 31, y + 16, 10, PALETTE["ink"])
    sh.box(x + 29, y + 2, 4, 6, PALETTE["ink"])


def island_mark(sh, x, y):
    sh.box(x + 4, y + 42, 54, 14, PALETTE["leaf"])
    sh.box(x + 6, y + 56, 50, 6, PALETTE["sea"])
    sh.seg(x + 31, y + 8, x + 31, y + 42, PALETTE["ink"], 3)
    sh.box(x + 31, y + 8, 22, 12, PALETTE["navy"])
    sh.box(x + 31, y + 20, 22, 4, PALETTE["paper"])


GRID = [
    ("SPACE", "SHENZHOU-24 DOCKS AT TIANGONG",
     "CHINA'S SHENZHOU-24 LIFTED OFF ON WEDNESDAY WITH PAKISTANI PILOT "
     "MUHAMMAD ZEESHAN ALI ABOARD, THE FIRST FOREIGN VISITOR TO THE "
     "TIANGONG STATION. DOCKING TOOK 3.5 HOURS.", rocket_mark),
    ("COLOMBIA", "CARTAGENA SIEGE ENDS: 20 FREE",
     "TROOPS STORMED AN EXITO STORE IN CARTAGENA AFTER A 17-HOUR "
     "STANDOFF AND FREED THE LAST 20 HOSTAGES. ONE GUNMAN WAS KILLED; "
     "TEN MORE HAD BEEN RELEASED EARLIER.", store_mark),
    ("TECH", "HUAWEI GUILTY IN NEW YORK",
     "A NEW YORK JURY FOUND HUAWEI GUILTY OF PLOTTING TO STEAL TRADE "
     "SECRETS AND OF BANK FRAUD, BUT CLEARED THE COMPANY OF "
     "RACKETEERING.", court_mark),
    ("PACIFIC", "SOLOMONS PACT WITH AUSTRALIA",
     "CANBERRA AND HONIARA SIGNED A TREATY NAMING AUSTRALIA THE "
     "SOLOMONS' MAIN SECURITY PARTNER AND BARRING ANY FOREIGN BASE ON "
     "ITS SOIL.", island_mark),
]


def grid_story(sh, x, y, w, mark, kicker, headline, body):
    sh.glyph(x, y, kicker, 2, PALETTE["red"])
    y += 22
    y = sh.para(x, y, headline, 2, PALETTE["ink"], w, gap=18)
    y += 4
    mark(sh, x, y)
    y = sh.para(x + 72, y, body, 2, PALETTE["ink"], w - 72, gap=18)
    return y


def save_png(path, sh):
    rows = b""
    for yy in range(sh.height):
        rows += b"\x00"
        rows += bytes(sh.buf[yy * sh.width * 3:(yy + 1) * sh.width * 3])
    blob = zlib.compress(rows, 9)

    def piece(kind, payload):
        out = struct.pack(">I", len(payload)) + kind + payload
        out += struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)
        return out

    head = struct.pack(">IIBBBBB", sh.width, sh.height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += piece(b"IHDR", head)
    png += piece(b"IDAT", blob)
    png += piece(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


def main():
    sh = Sheet(W, H, PALETTE["paper"])
    sh.border(8, 8, W - 16, H - 16, PALETTE["ink"], 4)
    sh.center(28, "THE WORLD TODAY", 5, PALETTE["ink"])
    sh.center(78, "WEDNESDAY 25 NOVEMBER 2026", 2, PALETTE["grey"])
    sh.box(32, 104, W - 64, 3, PALETTE["ink"])
    y = sh.para(32, 120, "TANKERS ABLAZE IN THE STRAIT OF HORMUZ",
                3, PALETTE["ink"], W - 64, gap=28)
    hormuz_scene(sh, 32, y + 8, W - 64, 210)
    y = y + 226
    y = sh.para(32, y, "IRAN'S REVOLUTIONARY GUARD SAID TWO TANKERS HIT "
                "NAVAL MINES AND BURST INTO FLAMES IN THE STRAIT OF HORMUZ "
                "ON WEDNESDAY AFTER SAILING AN UNAUTHORISED ROUTE. A FIFTH "
                "OF THE WORLD'S OIL PASSES THROUGH THE STRAIT.",
                2, PALETTE["ink"], W - 64, gap=18)
    sh.box(32, y + 6, W - 64, 3, PALETTE["ink"])
    top = y + 18
    first = []
    for i in range(2):
        kicker, headline, body, mark = GRID[i]
        first.append(grid_story(sh, 32 + i * 496, top, 464, mark,
                                kicker, headline, body))
    mid = max(first)
    sh.box(32, mid + 8, W - 64, 3, PALETTE["ink"])
    top2 = mid + 20
    second = []
    for i in range(2, 4):
        kicker, headline, body, mark = GRID[i]
        second.append(grid_story(sh, 32 + (i - 2) * 496, top2, 464, mark,
                                 kicker, headline, body))
    bottom = max(second)
    sh.box(32, bottom + 8, W - 64, 3, PALETTE["ink"])
    y = sh.para(32, bottom + 18, "ROSSTAT LEAK PUTS THE RUSSIAN TOLL NEAR "
                "500,000 + HOUTHI DRONE STRIKES RIYADH TOWER, 11 HURT + "
                "NORTH KOREA ORDERS THE SWISS ENVOY OUT + DOW SETTLES "
                "ABOVE 50,000", 2, PALETTE["grey"], W - 64, gap=18)
    sh.box(32, y + 6, W - 64, 3, PALETTE["ink"])
    sh.glyph(32, y + 18, "IN BRIEF", 2, PALETTE["red"])
    sh.para(32, y + 40, "SUDAN: RSF DRONE STRIKES KILL 19 CIVILIANS, A "
            "RIGHTS GROUP SAYS. GAZA: ISRAEL KILLS HAMAS SECURITY CHIEF "
            "ABUELOUF IN A STRIKE. CLIMATE: POPE LEO WARNS THE COP31 "
            "TALKS ENDED WITH NO DEAL.",
            2, PALETTE["ink"], W - 64, gap=18)
    folder = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(folder, exist_ok=True)
    save_png(os.path.join(folder, "entry.png"), sh)


if __name__ == "__main__":
    main()
