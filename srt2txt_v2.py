#!/usr/bin/env python
"""Convert a subtitles file into a transcript.

Usage: srt2txt_v2.py [-h] [--version]
       [-i FILE] [-o FILE]
       [--md]

Options:
  -h, --help                show this message and exit
  --version                 show version and exit

  -i FILE, --input FILE     subtitle file [default: input.srt]
  -o FILE, --output FILE    transcript file [default: output.txt]

  --md                      markdown format
"""
# native
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List

# lib
from attrbox import AttrDict
from attrbox import parse_docopt

__version__ = "0.1.0"


@dataclass
class Subtitle:
    """Represents a single subtitle."""

    idx: int = 0
    beg: str = ""
    end: str = ""
    who: str = ""
    txt: str = ""

    def __str__(self) -> str:
        """Return a string representation of this subtitle."""
        return f"{self.idx}\n{self.beg} --> {self.end}\n[{self.who}]: {self.txt}\n"

    def __add__(self, other: Subtitle) -> Subtitle:
        """Add two subtitles together."""
        return Subtitle(
            idx=min(self.idx, other.idx),
            beg=min(self.beg, other.beg),
            end=max(self.end, other.end),
            who=self.who,
            txt=self.txt + "\n" + other.txt,
        )

    def __iadd__(self, other: Subtitle) -> Subtitle:
        """Add a subtitle to this one."""
        self.idx = min(self.idx, other.idx)
        self.beg = min(self.beg, other.beg)
        self.end = max(self.end, other.end)
        self.txt += ". " + other.txt
        return self

    @staticmethod
    def parse(lines: List[str]) -> Subtitle:
        """Convert a list of lines into a `Subtitle`."""
        result = Subtitle()
        for line in lines:
            if line.isdecimal():
                result.idx = int(line)
            elif "-->" in line:
                result.beg, _, result.end = line.split()
            elif line.startswith("["):
                result.who = line[1 : line.find("]")]
                result.txt = line[line.find("]: ") + 3 :]
            else:
                result.txt += line

        return result


def parse_srt(text: str) -> List[Subtitle]:
    """Convert a subtitle file text into a list of `Subtitle`."""
    result: List[Subtitle] = []
    lines: List[str] = []
    for line in text.split("\n"):
        line = line.strip()
        if lines and not line:
            result.append(Subtitle.parse(lines))
            lines = []
            continue
        lines.append(line)
    return result


def merge_subtitles(subs: List[Subtitle]) -> List[Subtitle]:
    """Merge adjacent subtitles with the same speaker."""
    result: List[Subtitle] = []
    prev = None
    for curr in subs:
        if not prev or prev.who != curr.who:
            result.append(curr)
            prev = curr
        else:
            prev += curr
    return result


def srt2txt(srt: Path, txt: Path, md: bool = False):
    """Convert a subtitle file to a transcript.

    Args:
        srt (Path): path to subtitle file
        txt (Path): path to output file
        md (bool, optional): whether to render output as markdown instead of
            a subtitle-format. Defaults to `False`.
    """
    subs = parse_srt(srt.read_text(encoding="utf-8"))
    subs = merge_subtitles(subs)

    with txt.open("w", encoding="utf8") as out:
        for sub in subs:
            if md:
                out.write(f"**{sub.who}**: {sub.txt}\n")
            else:
                out.write(str(sub))
            out.write("\n")


def main() -> None:
    """Main entry point."""
    args = parse_docopt(__doc__, version=__version__)
    args.input = Path(args.input or "input.srt")
    args.output = Path(args.output or "output.txt")
    if not args.input.exists():
        print(f"ERROR: Cannot find file: {args.input}")
        exit()

    srt2txt(args.input, args.output, args.md)


if __name__ == "__main__":
    main()
