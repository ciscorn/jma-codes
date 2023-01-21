"""アメダス"""

import json
import unicodedata
from typing import Any, cast

import pandas as pd

from .utils import get_filename_for

COLUMN_MAP_AME = {
    "都府県振興局": "regionalBreau",
    "種類": "kind",
    "観測所名": "name",
    "ｶﾀｶﾅ名": "kana",
    "所在地": "address",
    "海面上の高さ(ｍ)": "altitude",
    "風速計の高さ(ｍ)": "anemometerHeight",
    "温度計の高さ(ｍ)": "thermometerHeight",
    "観測開始年月日": "startDate",
    "備考1": "note1",
    "備考2": "note2",
}

COLUMN_MAP_SNOW = {
    "都府県振興局": "regionalBreau",
    "種類": "kind",
    "観測所名": "name",
    "ｶﾀｶﾅ名": "kana",
    "所在地": "address",
    "海面上の高さ(ｍ)": "altitude",
    "観測開始年月日": "startDate",
}


def convert(column_map: dict[str, Any], df: pd.DataFrame, output_name: str) -> None:
    result = {}
    for _, row in df.iterrows():
        r: dict[str, Any] = {}
        for k, v in column_map.items():
            value = row[k]
            if pd.isnull(value):
                continue
            elif isinstance(value, str):
                r[v] = unicodedata.normalize("NFKC", value)
            else:
                r[v] = row[k]
        r["lat"] = cast(float, row["緯度(度)"]) + cast(float, row["緯度(分)"]) / 60.0
        r["lng"] = cast(float, row["経度(度)"]) + cast(float, row["経度(分)"]) / 60.0
        code = row["観測所番号"]
        result[code] = r

    with open(f"./json/{output_name}.json", "w") as f:
        json.dump({"items": result}, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    df_ame = pd.read_csv(get_filename_for("ame_master"), na_values=["－", "-"])
    df_snow = pd.read_csv(get_filename_for("snow_master"), na_values=["－", "-"])

    convert(COLUMN_MAP_AME, df_ame, "amedas_ame")
    convert(COLUMN_MAP_SNOW, df_snow, "amedas_snow")
