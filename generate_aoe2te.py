#!/usr/bin/env python

import json
import os
import keyvalue
from pathlib import Path
from genieutils.datfile import DatFile
from constants import *

AOE2DE_ABSPATH = Path("C:/Program Files (x86)/Steam/steamapps/common/AoE2DE")
MODS_ABSPATH = Path.home() / "Desktop"
MOD_ABSPATH = MODS_ABSPATH / "Timeless Edition"
DAT_RELPATH = Path("resources/_common/dat")
CIV_RELFILEPATH = DAT_RELPATH / "civilizations.json"
DATA_RELFILEPATH = DAT_RELPATH / "empires2_x2_p1.dat"

os.makedirs(MOD_ABSPATH / DAT_RELPATH, exist_ok=True)

dat_file = DatFile.parse(AOE2DE_ABSPATH / DATA_RELFILEPATH)
with open(AOE2DE_ABSPATH / CIV_RELFILEPATH, "r") as civ_file:
    civ_data = json.load(civ_file)

languages = {}
for path in filter(Path.is_dir, (AOE2DE_ABSPATH / "resources").iterdir()):
    if "_" in path.name:  # _common, _launcher, _packages
        continue

    strings = {}
    for file_ in (path / "strings/key-value").glob("*.txt"):
        with open(file_, "r", encoding="utf-8") as strings_file:
            strings |= keyvalue.load(strings_file)
    languages[path.name] = strings

# removing civs should be the very last thing to happen, because from now on, the constants are wrong
civs_to_be_removed = [
    civilizations.ACHAEMENIDS, civilizations.ATHENIANS, civilizations.SPARTANS,
    civilizations.SHU, civilizations.WU, civilizations.WEI,
    civilizations.MACEDONIANS, civilizations.THRACIANS, civilizations.PURU
]

civs_to_be_removed.sort(reverse=True)
modded_languages = dict([(language, {}) for language in languages])
for civ in civs_to_be_removed:
    for tech in dat_file.techs:
        if tech.civ == civ:
            tech.civ = civilizations.NONE
        elif tech.civ > civ:
            tech.civ -= 1

    for civ2 in range(civ + 1, len(dat_file.civs)):
        id_changes = {}

        # civ description
        description_base_id = 120149
        id_changes[f"{description_base_id + civ2}"] = f"{description_base_id + civ2 - 1}"

        # civ tips
        tips_base_string = "IDS_CIVTIPS"
        for i in range(4):
            id_changes[f"{tips_base_string}_{civ2}_{i}"] = f"{tips_base_string}_{civ2 - 1}_{i}"

        for language, strings in languages.items():
            for old_id, new_id in id_changes.items():
                strings[new_id] = strings[old_id]

                if civ == civs_to_be_removed[-1]:
                    modded_languages[language][new_id] = strings[new_id]

    del civ_data["civilization_list"][civ]
    del dat_file.civs[civ]

for language, modded_strings in modded_languages.items():
    dir_ = MOD_ABSPATH / "resources" / language / "strings/key-value"
    os.makedirs(dir_, exist_ok=True)
    with open(dir_ / "key-value-modded-strings-utf8.txt", "w", encoding="utf-8") as strings_file:
        keyvalue.dump(modded_strings, strings_file)

os.makedirs(MOD_ABSPATH / DAT_RELPATH, exist_ok=True)
dat_file.save(MOD_ABSPATH / DATA_RELFILEPATH)
with open(MOD_ABSPATH / CIV_RELFILEPATH, "w") as civ_file:
    json.dump(civ_data, civ_file, indent=3)
