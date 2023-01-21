"""指定河川洪水予報 河川事務所

"Office/@type"が"水位関係"の場合に利用
"""

import json

import pandas

from .utils import get_filename_for


def process() -> None:
    df = pandas.read_excel(get_filename_for("RiverOffice"), skiprows=2)

    result = {}
    for _, row in df.iterrows():
        code = row["@code"]
        name = row["@name"]
        result[code] = name

    with open("./json/RiverOffice.json", "w") as f:
        json.dump({"items": result}, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    process()
