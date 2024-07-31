"""指定河川洪水予報

"Information/@type"が"指定河川洪水予報（河川）"の場合に利用
"Warning/@type"が"指定河川洪水予報"の場合の場合に利用
"MeteorologicalInfos type"が"氾濫水の予報"の場合に利用
"""

import json
from typing import Optional

import pandas as pd

from .utils import get_filename_for


def process() -> None:
    df = pd.read_excel(get_filename_for("jmaxml_"), skiprows=3, dtype={"値": str})
    result = {}
    currentCodeName: Optional[str] = None
    isValueMode = False
    for _, row in df.iterrows():
        cn = row["コード名"]
        if not pd.isnull(cn):
            currentCodeName = cn

        attrib = row["属性"]
        if not pd.isnull(attrib):
            if attrib == "とりうる値":
                isValueMode = True
            else:
                isValueMode = False

        if isValueMode:
            value = row["値"]
            if not pd.isnull(value):
                value = str(int(row["値"])).zfill(2)  # 数値に変換できる値である
                desc = row["解説"]
                desc = desc.replace(
                    '（Control/Title="気象警報・注意報"の場合には出現しない。）', ""
                )
                if currentCodeName not in result:
                    result[currentCodeName] = {}
                result[currentCodeName][value] = desc

    for codeType, values in result.items():
        with open(f"./json/{codeType}.json", "w") as f:
            json.dump(
                {"items": values}, f, sort_keys=True, ensure_ascii=False, indent=2
            )
            f.write("\n")


if __name__ == "__main__":
    process()
