"""指定河川洪水予報（予報区域）

"Information＠type"が"指定河川洪水予報（予報区域）"の場合に利用
"""

import json

import pandas

from .utils import get_filename_for

if __name__ == "__main__":
    df = pandas.read_excel(get_filename_for("AreaFloodForecast"), skiprows=2)

    result = {}
    for _, row in df.iterrows():
        code = row["@code"]
        result[code] = {"name": row["@name"], "kana": row["Unnamed: 2"]}

    with open("./json/AreaFloodForecast.json", "w") as f:
        json.dump({"items": result}, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write("\n")
