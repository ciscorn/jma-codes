"""WmoObservingStations（国際地点番号）

特殊気象報
    "MeteorologicalInfos/@type"が"季節観測"、"特殊気象報（各種現象）"の場合に利用
生物季節観測報告気象報
    "MeteorologicalInfos/@type"が"生物季節観測"の場合に利用
環境気象情報
    "MeteorologicalInfos/@type"が"紫外線観測データ"の場合に利用
地方海上予報
    "MeteorologicalInfos/@type"が"観測実況"の場合に利用
指定河川洪水予報
    "Office/@type"が"気象関係"の場合に利用
天候情報
    "MeteorologicalInfos/@type"が"天候情報"の場合に利用
"""

import json
from typing import cast

import pandas

from .utils import get_filename_for


def process() -> None:
    df = pandas.read_excel(get_filename_for("WmoObservingStations"), skiprows=2)

    result = {}
    for _, row in df.iterrows():
        code = row["@code"]
        lat = cast(float, row["緯度（度）"]) + cast(float, row["緯度（分）"]) / 60
        lng = cast(float, row["経度（度）"]) + cast(float, row["経度（分）"]) / 60
        result[code] = {
            "point": row["コードが示す地点"],
            "lnglat": [lng, lat],
        }
        name = (row["@name"],)
        if isinstance(name, str):
            result[code]["name"] = name
        kana = row["ふりがな"]
        if isinstance(kana, str):
            result[code]["kana"] = kana

    with open("./json/WmoObservingStations.json", "w") as f:
        json.dump({"items": result}, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write("\n")

    result_geojson = []
    for item in result.values():
        lnglat = item.pop("lnglat")
        result_geojson.append(
            {
                "type": "Feature",
                "properties": item,
                "geometry": {
                    "type": "Point",
                    "coordinates": lnglat,
                },
            }
        )

    with open("./json/WmoObservingStations.geojson", "w") as f:
        json.dump(
            {"type": "FeatureCollection", "features": result_geojson},
            f,
            ensure_ascii=False,
            indent=2,
        )


if __name__ == "__main__":
    process()
