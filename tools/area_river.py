"""指定河川洪水予報

"Information/@type"が"指定河川洪水予報（河川）"の場合に利用
"Warning/@type"が"指定河川洪水予報"の場合の場合に利用
"MeteorologicalInfos type"が"氾濫水の予報"の場合に利用
"""

import json

import pandas

from .utils import get_filename_for


def process() -> None:
    df = pandas.read_excel(get_filename_for("AreaRiver"), skiprows=2)

    result = {}
    for _, row in df.iterrows():
        code = row["@code"]
        result[code] = {"name": row["@name"], "kana": row["Unnamed: 2"]}
        if isinstance(row["@name.1"], str):
            result[code]["alias1_name"] = row["@name.1"]
            result[code]["alias1_kana"] = row["Unnamed: 4"]
        if isinstance(row["@name.2"], str):
            result[code]["alias2_kana"] = row["Unnamed: 6"]

    with open("./json/AreaRiver.json", "w") as f:
        json.dump({"items": result}, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    process()
