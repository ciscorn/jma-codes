"""指定河川洪水予報 水位観測所

"Station/Code@type"が"水位観測所"の場合
"Area@codeType"が"水位観測所"の場合に利用
"""

import json

import pandas

from .utils import get_filename_for


def process() -> None:
    df = pandas.read_excel(get_filename_for("WaterLevelStation"), skiprows=2)

    result = {}
    for _, row in df.iterrows():
        code = row["@code"]
        name = row["@name"]
        river = row["（参考）予報区域名"]
        result[code] = {
            "name": name,
            "river": river,
        }

    with open("./json/WaterLevelStation.json", "w") as f:
        json.dump({"items": result}, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    process()
