"""予報区（府県予報区、一次細分区域、市町村等をまとめた地域、市町村等）

AreaInformationCity-AreaForecastLocalM をもとに、区域の名前や上位の区域を引くテーブルを作ります"""

import itertools
import json
from dataclasses import dataclass
from typing import Optional, cast

import pandas as pd

from .utils import get_filename_for


@dataclass
class MatomeProps:
    ichiji_code: str
    fuken_code: Optional[str]  # 府県予報区（気象警報等）
    saibun_code: Optional[str]  # 発表細分（竜巻注意情報等）


@dataclass
class AreaName:
    name: str
    kana: str


def make_matome_code_map() -> dict[str, MatomeProps]:
    matome_code_map: dict[
        str, MatomeProps
    ] = {}  # 予報区コードとその情報を対応づけるマップ

    df_city_m_ww = pd.read_excel(
        get_filename_for("AreaInformationCity-AreaForecastLocalM.xls"),
        sheet_name="AreaForecastLocalM（関係表　警報・注意報",
        skiprows=2,
        dtype={
            "コード\n(@code)": str,
            "コード\n(@code).1": str,
            "コード\n(@code).2": str,
        },
    )
    df_city_m_tornado = pd.read_excel(
        get_filename_for("AreaInformationCity-AreaForecastLocalM.xls"),
        sheet_name="AreaForecastLocalM（関係表　竜巻注意情報",
        skiprows=2,
        dtype={
            "コード\n(@code)": str,
            "コード\n(@code).1": str,
            "コード\n(@code).2": str,
        },
    )

    # 気象警報の関係表から、まとめた地域 -> 一次細分区域 -> 府県予報区 の関係を取得
    for _, row in itertools.chain(df_city_m_ww.iterrows()):
        matome_code = str(row["コード\n(@code)"])
        ichiji_code = str(row["コード\n(@code).1"])
        fuken_code = str(row["コード\n(@code).2"])
        if matome_code not in matome_code_map:
            matome_code_map[matome_code] = MatomeProps(
                ichiji_code=ichiji_code, fuken_code=fuken_code, saibun_code=None
            )
        else:
            assert matome_code_map[matome_code].ichiji_code == str(
                row["コード\n(@code).1"]
            )
            matome_code_map[matome_code].fuken_code = str(row["コード\n(@code).2"])

    # 竜巻注意情報の関係表から、まとめた地域 -> 一次細分区域 -> 発表細分 の関係を取得
    for _, row in itertools.chain(df_city_m_tornado.iterrows()):
        matome_code = str(row["コード\n(@code)"])
        ichiji_code = str(row["コード\n(@code).1"])
        saibun_code = str(row["コード\n(@code).2"])
        if matome_code not in matome_code_map:
            matome_code_map[matome_code] = MatomeProps(
                ichiji_code=ichiji_code,
                fuken_code=None,
                saibun_code=saibun_code,
            )
        else:
            assert matome_code_map[matome_code].ichiji_code == str(
                row["コード\n(@code).1"]
            )
            matome_code_map[matome_code].saibun_code = str(row["コード\n(@code).2"])

    return matome_code_map


def make_code_name_map(df_city) -> dict[str, AreaName]:
    code_name_map: dict[str, AreaName] = {}  # 予報区コードとその名称を対応づけるマップ

    df_city_m = pd.read_excel(
        get_filename_for("AreaInformationCity-AreaForecastLocalM.xls"),
        sheet_name="AreaForecastLocalM（コード表）",
        skiprows=3,
        dtype={
            "@code": str,
        },
    )

    for _, row in df_city_m.iterrows():
        code = cast(str, row["@code"])
        name = cast(str, row["@name"])
        kana = cast(str, row["Unnamed: 2"])
        code_name_map[code] = AreaName(name, kana)

    for _, row in df_city.iterrows():
        code = str(row["@code"])
        if code == "nan":
            continue

        name = row["@name"]
        if name == "nan" or pd.isnull(name):
            if not (name := row["@name.4"]) or (name == "nan" or pd.isnull(name)):
                if not (name := row["@name.2"]) or (name == "nan" or pd.isnull(name)):
                    name = row["@name.1"]

        kana = row["ふりがな"]
        if kana == "nan" or pd.isnull(kana):
            if not (kana := row["ふりがな.4"]) or (kana == "nan" or pd.isnull(kana)):
                if not (kana := row["ふりがな.2"]) or (
                    kana == "nan" or pd.isnull(kana)
                ):
                    kana = row["ふりがな.1"]

        if name != "nan":
            if kana == "nan":
                kana = ""
            assert isinstance(code, str)
            code_name_map[code] = AreaName(name, kana)

    return code_name_map


def process() -> None:
    df_city = pd.read_excel(
        get_filename_for("AreaInformationCity-AreaForecastLocalM.xls"),
        skiprows=2,
        dtype={
            "@code": str,
            "@name": str,
            "@name.1": str,
            "@name.2": str,
            "@name.3": str,
            "@name.4": str,
            "ふりがな": str,
            "ふりがな.1": str,
            "ふりがな.2": str,
            "ふりがな.3": str,
            "ふりがな.4": str,
            "属する「市町村等をまとめた地域等」\n(AreaForecastLocalMの@code値)": str,
        },
    )

    code_name_map = make_code_name_map(df_city)
    matome_code_map = make_matome_code_map()

    result = {}
    for _, row in df_city.iterrows():
        code = str(row["@code"])
        name = str(row["@name"])
        matome_code = str(
            row["属する「市町村等をまとめた地域等」\n(AreaForecastLocalMの@code値)"]
        )
        if matome_code and matome_code != "nan":
            spec = matome_code_map[matome_code]
            result[code] = {
                "level": "city",
                "name": name,
                "kana": code_name_map[code].kana,
                "fuken": spec.fuken_code,
                "saibun": spec.saibun_code,
                "ichiji": spec.ichiji_code,
                "matome": matome_code,
            }
            result[matome_code] = {
                "level": "matome",
                "name": code_name_map[matome_code].name,
                "kana": code_name_map[matome_code].kana,
                "fuken": spec.fuken_code,
                "saibun": spec.saibun_code,
                "ichiji": spec.ichiji_code,
            }
            result[spec.ichiji_code] = {
                "level": "ichiji",
                "name": code_name_map[spec.ichiji_code].name,
                "kana": code_name_map[spec.ichiji_code].kana,
                "fuken": spec.fuken_code,
                "saibun": spec.saibun_code,
            }
            if spec.fuken_code:
                result[spec.fuken_code] = {
                    "level": "fuken",
                    "name": code_name_map[spec.fuken_code].name,
                    "kana": code_name_map[spec.fuken_code].kana,
                }
            if spec.saibun_code:
                if spec.saibun_code not in result:
                    result[spec.saibun_code] = {
                        "level": "saibun",
                        "name": code_name_map[spec.saibun_code].name,
                        "kana": code_name_map[spec.saibun_code].kana,
                    }
        else:
            result[code] = {
                "level": "city",
                "name": code_name_map[code].name,
                "kana": code_name_map[code].kana,
            }

    for code, name in code_name_map.items():
        if code not in result:
            result[code] = {
                "level": "other",
                "name": name.name,
                "kana": name.kana,
            }

    verify_result(result, code_name_map, matome_code_map)

    with open("./json/forecast_area_tree.json", "w", encoding="utf-8") as f:
        json.dump({"items": result}, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write("\n")


def verify_result(result, code_name_map, matome_code_map):
    # verify
    for area in result.values():
        if fuken := area.get("fuken"):
            assert fuken in result
        if saibun := area.get("saibun"):
            assert saibun in result
        if ichiji := area.get("ichiji"):
            assert ichiji in result
        if matome := area.get("matome"):
            assert matome in result

    for code in code_name_map:
        assert code in result

    for code in matome_code_map:
        assert code in result


if __name__ == "__main__":
    process()
