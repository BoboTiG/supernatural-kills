import json
import re
from collections import defaultdict, Counter
from pathlib import Path
from typing import Pattern

import requests
from bs4 import BeautifulSoup


class Supernatural:
    def __init__(self) -> None:
        self.content = ""
        self.kills = defaultdict(Counter)
        self.url = "http://www.supernaturalwiki.com/Table_of_Death"
        self.file = Path("raw") / "table-of-death.html"
        self.output_dir = Path("formatted")

    def download(self, force: bool = False) -> None:
        if force:
            self.content = requests.get(self.url).text
            self.file.write_text(self.content, encoding="utf-8")
        else:
            self.content = self.file.read_text(encoding="utf-8")

    def get_killed(
        self, kills: str, pattern: Pattern = re.compile(r"(\d+)")
    ) -> Counter:
        cat = Counter({"angels": 0, "demons": 0, "humans": 0})
        kills = kills.lower()
        key = "humans"

        if (
            "demon" in kills
            or "vampire" in kills
            or "ghost" in kills
            or "meatsuit" in kills
            or "werewolf" in kills
            or "djinn" in kills
            or "zombie" in kills
            or "creature" in kills
            or "reaper" in kills
            or "gorgon" in kills
            or "leviathan" in kills
            or "vengeful" in kills
            or "bloody" in kills
            or "tulpa" in kills
            or "shtriga" in kills
            or "shapeshifter" in kills
            or "poltergeist" in kills
            or "rawhead" in kills
            or "rakshasa" in kills
            or "croat" in kills
            or "changleing" in kills
            or "witch" in kills
            or "crocotta" in kills
            or "rugaru" in kills
            or "racist" in kills
            or "pagan" in kills
            or "buruburu" in kills
            or "siren" in kills
            or "ghoul" in kills
            or "yeager" in kills
            or "wraith" in kills
            or "whore" in kills
            or "goons" in kills
            # Bad guys
            or "famine" in kills
            or kills
            in (
                "cain",
                "katja",
                "meg",
                "seth",
                "war",
                "pestilence",
                "the vanir",
                "zao shen",
            )
        ):
            key = "demons"
        elif "angel" in kills or "castiel" in kills or "metatron" in kills:
            key = "angels"

        # Remove "#N" to prevent bad counts
        kills = re.sub(r"(#\d+)", "", kills)
        # Remove comma to ease computing 1,234 -> 1234
        kills = kills.replace(",", "")

        matches = pattern.findall(kills)
        if matches:
            count = sum(map(int, matches))
        else:
            # Handle "X and Y"
            kills = kills.replace(" and ", " & ")
            count = kills.count("&") + 1

        cat[key] += count
        return cat

    def guess_data(self, rows):
        try:
            row = next(rows)
        except StopIteration:
            return

        cols = row.find_all("td")
        if cols[0].has_attr("rowspan"):
            # Multi lines
            episode = cols[0].text.strip()
            try:
                kills = cols[2].text.strip()
            except IndexError:
                # Some episodes have just the episode and name, no killed
                pass
            else:
                yield (episode, kills)

            # Iterate over that specific episode deads
            for _ in range(int(cols[0]["rowspan"]) - 1):
                row = next(rows)
                cols = row.find_all("td")
                kills = cols[0].text.strip()
                # The table has inconsistency, some rows are left empty
                if kills:
                    yield episode, kills
        else:
            # One line
            episode = cols[0].text.strip()
            kills = cols[2].text.strip()
            yield episode, kills

        # Continue
        yield from self.guess_data(rows)

    def parse(self) -> None:
        soup = BeautifulSoup(self.content, "html.parser")
        rows = iter(soup.find_all("tr")[1:])
        for episode, kills in self.guess_data(rows):
            self.kills[episode] += self.get_killed(kills)

    @staticmethod
    def natural_sort_key(string, pattern: Pattern = re.compile(r"(\d+)")):
        """Natural sort function.
        Source: https://stackoverflow.com/a/16090640/1117028
        """
        return [
            int(text) if text.isdigit() else text.lower()
            for text in pattern.split(string)
        ]

    def dump(self) -> None:
        episodes = sorted(self.kills.keys(), key=self.natural_sort_key)
        for episode in episodes:
            print(episode, self.kills[episode])

    def export_json(self) -> None:
        """Export data to JSON."""
        file = self.output_dir / "kills.json"
        file.write_text(json.dumps(self.kills))
