"""同一現象"""

import json
from typing import cast

import pandas

from .utils import get_filename_for


def process() -> None:
    df = pandas.read_excel(get_filename_for("PhenologicalType"), skiprows=1)

    result = {}
    for _, row in df.iterrows():
        code = row["Code"]
        classNames = [s.strip() for s in cast(str, row["ClassName"]).split("\n")]
        result[code] = {"name": row["Name"], "classNames": classNames}

    with open("./json/PhenologicalType.json", "w") as f:
        json.dump({"items": result}, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    process()
