"""全般海上海域名と地方海上予報区

AreaMarineAコード表（全般海上海域名）
全般海上警報で利用
    "Information/@type"が"全般海上警報"の場合に利用
    "MeteorologicalInfos/@type"が "全般海上警報"の場合に利用
天気図情報で利用
    "MeteorologicalInfos/@type"が "悪天情報"の場合に利用

AreaMarineJ（地方海上予報区）
地方海上警報
    "Information/@type"が"地方海上警報"の場合に利用
    "Warning/@type"が"地方海上警報"の場合に利用
    "MeteorologicalInfos/@type"が"気象要因"の場合に利用
地方海上予報
    "Warning/@type"が"地方海上警報発表状況"の場合に利用
    "MeteorologicalInfos/@type"が"地方海域の予報"の場合に利用
"""

import json

import pandas

from .utils import get_filename_for


def process() -> None:
    df = pandas.read_excel(
        get_filename_for("AreaMarineAJ"), skiprows=2, sheet_name="AreaMarineA"
    )

    result = {}
    for _, row in df.iterrows():
        code = row["@code"]
        result[code] = {"name": row["@name"], "kana": row["Unnamed: 2"]}

    with open("./json/AreaMarineA.json", "w") as f:
        json.dump({"items": result}, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write("\n")

    df = pandas.read_excel(
        get_filename_for("AreaMarineAJ"), skiprows=3, sheet_name="AreaMarineJ"
    )

    result = {}
    for _, row in df.iterrows():
        code = row["@code"]
        result[code] = {"name": row["@name"], "kana": row["Unnamed: 2"]}

    with open("./json/AreaMarineJ.json", "w") as f:
        json.dump({"items": result}, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    process()
