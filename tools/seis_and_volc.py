"""地震火山関連コード表.xls を JSON に変換する"""

import json
from typing import Any, cast

import pandas as pd

from .utils import get_filename_for, seisvolc_point

SHEETS_IGNORE: list[str] = ["エクセルシート一覧", "更新履歴"]

# 一部のシートの一部のカラムは名前を変更する
RENAME_COLUMNS: dict[str, dict[str, str]] = {
    "24": {
        "Code": "seisSaibunCode",
        "Code.1": "cityCode",
        "Code.2": "Code",
        "Name": "seisSaibunName",
        "Name.1": "cityName",
        "Name.2": "Name",
        "ふりがな": "seisSaibunKana",
        "ふりがな.1": "cityKana",
        "ふりがな.2": "ふりがな",
    },
    "25": {
        "Code": "seisSaibunCode",
        "Code.1": "cityCode",
        "Code.2": "Code",
        "Name": "seisSaibunName",
        "Name.1": "cityName",
        "Name.2": "Name",
        "ふりがな": "seisSaibunKana",
        "ふりがな.1": "cityKana",
        "ふりがな.2": "ふりがな",
    },
}

# カラム名の変換マップ
NAME_MAP: dict[str, str] = {
    "Code": "code",
    "Name": "name",
    "備考": "note",
    "ふりがな": "kana",
    "Text": "text",
    "Name.1": "name2",
    "Code.1": "code2",
    "Name.2": "name3",
    "Code.2": "code3",
    "seisSaibunCode": "seisSaibunCode",
    "seisSaibunName": "seisSaibunName",
    "seisSaibunKana": "seisSaibunKana",
    "cityCode": "cityCode",
    "cityName": "cityName",
    "cityKana": "cityKana",
}

# シート名をコード表名に変換するマップ
SHEET_NAME_MAP: dict[str, str] = {
    "11": "EarthquakeWarning",
    "12": "EarthquakeForecast",
    "14": "TsunamiWarning",
    "21": "AreaForecastEEW",
    "22": "AreaForecastLocalEEW",
    "23": "AreaInformationPrefectureEarthquake",
    "24": "PointSeismicIntensity",
    "25": "PointRealtimeSeismicIntensity",
    "26": "PointSeismicLgIntensity",
    "31": "AreaTsunami",
    "34": "CoastTsunami",
    "35": "PointTsunami",
    "41": "AreaEpicenter",
    "42": "AreaEpicenterAbbreviation",
    "43": "AreaEpicenterDetail",
    "44": "AreaEpicenterSuppliment",
    "51": "TokaiInformation",
    "52": "EarthquakeInformation",
    "62": "AdditionalCommentEarthquake",
    "81": "VolcanicWarning",
    "82": "PointVolcano",
}

# コード名が整数で記録されているシートについて、コードをゼロ埋めする
SHEET_CODE_ZERO_PAD: dict[str, int] = {
    "35": 5,
}


def process() -> None:
    dfs = pd.read_excel(
        get_filename_for("地震火山関連"),
        sheet_name=None,
        skiprows=2,
        dtype={
            "Code": str,
            "Code.1": str,
            "Code.2": str,
        },
    )

    # 震度観測点の座標をインターネット上のソースから取得
    intensity_points = seisvolc_point.IntensityPoints()
    # 火山の座標をインターネット上のソースから取得
    volc_points = seisvolc_point.get_volc_points()

    for sheet_name, df in dfs.items():
        sheet_name = sheet_name.strip()
        if sheet_name in SHEETS_IGNORE:
            continue

        if sheet_name in RENAME_COLUMNS:
            df = df.rename(columns=RENAME_COLUMNS[sheet_name])

        items: dict[str, dict] = {}
        for _, row in df.iterrows():
            r: dict[str, Any] = {}
            for k, v in NAME_MAP.items():
                if k in row and (not pd.isnull(row[k])):
                    value = cast(str, row[k]).strip()
                    if ("Code" in k) and (sheet_name in SHEET_CODE_ZERO_PAD):
                        value = value.zfill(SHEET_CODE_ZERO_PAD[sheet_name])
                    r[v] = value

            code = cast(str, row["Code"])

            # PointSeismicIntensity に座標を与える
            if sheet_name in ["24"]:
                station = intensity_points.find_station(
                    cast(str, r["name"]), cast(str, r["cityCode"])
                )
                if station is not None:
                    r["lnglat"] = [station.lng, station.lat]
                else:
                    r["lnglat"] = None

            # PointVolcano に座標を与える
            if sheet_name in ["82"]:
                if code in volc_points:
                    r["lnglat"] = volc_points[code]

            if sheet_name in SHEET_CODE_ZERO_PAD:
                code = code.zfill(SHEET_CODE_ZERO_PAD[sheet_name])

            items[code] = r

        result = {}
        if sheet_name in ["24", "25"]:
            # 震度観測点の表については、"市町村等" を "地震情報／細分区域" に変換するマップも作る
            city_to_saibun = {
                item["cityCode"]: dict(
                    (k, v)
                    for (k, v) in item.items()
                    if k not in ["name", "code", "kana", "lnglat"]
                )
                for item in items.values()
                if "cityCode" in item
            }
            result = {
                "pointToCity": items,
                "cityToSaibun": city_to_saibun,
            }
        elif sheet_name == "35":
            locs = seisvolc_point.get_point_tsunami_locations()
            for code, item in items.items():
                loc = locs.get(code)
                if loc is None:
                    if not (code.startswith("0") and "沖" in item["name"]):
                        print("no location found for", code, item)  # raise an error
                    continue
                item["lnglat"] = [loc.lng, loc.lat]
                item["owner"] = loc.owner
            result = {"items": items}
        else:
            # 震度観測点以外の表
            result = {"items": items}

        with open(
            f"./json/{SHEET_NAME_MAP[sheet_name]}.json", "w", encoding="utf-8"
        ) as f:
            json.dump(result, f, sort_keys=True, ensure_ascii=False, indent=2)
            f.write("\n")


if __name__ == "__main__":
    process()
