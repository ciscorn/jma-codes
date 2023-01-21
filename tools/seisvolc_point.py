import io
import json
import logging
import re
from dataclasses import dataclass
from typing import Optional

import lxml.html as html
import numpy as np
import pandas as pd
import requests

logger = logging.getLogger(__name__)

_REMOVE_CITY_PAT = re.compile("^.*?(?:市|町|村|区)")

PREFECTURE_MAP = {
    "01": "北海道",
    "02": "青森県",
    "03": "岩手県",
    "04": "宮城県",
    "05": "秋田県",
    "06": "山形県",
    "07": "福島県",
    "08": "茨城県",
    "09": "栃木県",
    "10": "群馬県",
    "11": "埼玉県",
    "12": "千葉県",
    "13": "東京都",
    "14": "神奈川県",
    "15": "新潟県",
    "16": "富山県",
    "17": "石川県",
    "18": "福井県",
    "19": "山梨県",
    "20": "長野県",
    "21": "岐阜県",
    "22": "静岡県",
    "23": "愛知県",
    "24": "三重県",
    "25": "滋賀県",
    "26": "京都府",
    "27": "大阪府",
    "28": "兵庫県",
    "29": "奈良県",
    "30": "和歌山県",
    "31": "鳥取県",
    "32": "島根県",
    "33": "岡山県",
    "34": "広島県",
    "35": "山口県",
    "36": "徳島県",
    "37": "香川県",
    "38": "愛媛県",
    "39": "高知県",
    "40": "福岡県",
    "41": "佐賀県",
    "42": "長崎県",
    "43": "熊本県",
    "44": "大分県",
    "45": "宮崎県",
    "46": "鹿児島県",
    "47": "沖縄県",
}


@dataclass
class PointInfo:
    kind: str
    name: str
    lat: float
    lng: float
    prefecture: str
    source_sub: Optional[str] = None


@dataclass
class PointTsunamiInfo:
    lat: float
    lng: float
    owner: str


class IntensityPoints:
    def __init__(self):
        self._load_jma_json()
        self._load_jma()
        self._load_nied()

    def _load_jma(self) -> None:
        """
        気象庁の観測点一覧ページをスクレイピングする
        https://www.data.jma.go.jp/eqev/data/kyoshin/jma-shindo.html#hokkaido
        """

        res = requests.get(
            "https://www.data.jma.go.jp/eqev/data/kyoshin/jma-shindo.html"
        )
        doc = html.fromstring(res.content)
        self._jma_points = {}
        for tr in doc.iterfind(".//tr"):
            tds = [td.text for td in tr.iterfind("./td")]
            if not tds or tds[0] == "地域名称":
                continue
            name = tds[1]
            self._jma_points[name] = PointInfo(
                kind="jma",
                name=name,
                prefecture="",
                lat=float(tds[3]) + float(tds[4]) / 60,
                lng=float(tds[5]) + float(tds[6]) / 60,
            )

    def _load_jma_json(self) -> None:
        """気象庁の震度観測点マップのJSONを読み込む"""
        res = requests.get(
            "https://www.data.jma.go.jp/eqev/data/intens-st/stations.json"
        )
        data = res.json()
        self._jma_json_points = {}
        for station in data:
            name = station["name"]
            self._jma_json_points[name] = PointInfo(
                kind="jma-json",
                name=name,
                prefecture="",
                lat=float(station["lat"]),
                lng=float(station["lon"]),
            )

    def _load_nied(self) -> None:
        """
        NIED K-net の観測点リストを読み込む
        https://www.kyoshin.bosai.go.jp/kyoshin/db/index.html
        """

        # OpenSSL の警告 DH_KEY_TOO_SMALL を無視する
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"

        res = requests.get(
            "https://www.kyoshin.bosai.go.jp/kyoshin/pubdata/knet/sitedb/sitepub_knet_sj.csv",
            headers={"Referer": "https://www.kyoshin.bosai.go.jp/"},
        )
        if res.status_code > 300:
            raise RuntimeError(f"failed to get NIED stations: {res.status_code}")
        columns = ["code", "name", "name_rome", "lat", "lng", "a", "b", "pref"]
        df = pd.read_csv(
            io.BytesIO(res.content),
            encoding="cp932",
            names=np.array(columns),
            usecols=np.array(columns),
        )

        self._nied_points = {}
        for _, row in df.iterrows():
            pref = row["pref"]
            name = row["name"]
            info = PointInfo(
                kind="k-net",
                name=name,
                lat=row["lat"],
                lng=row["lng"],
                prefecture=row["pref"],
            )
            self._nied_points[(pref, name)] = info

    def find_station(self, jma_name: str, jma_city_code: str) -> Optional[PointInfo]:
        # JMA のサイト上のテーブル
        if point := self._jma_points.get(jma_name):
            return point

        # NIED K-net CSV
        prefecture = PREFECTURE_MAP[jma_city_code[:2]]
        found: list[PointInfo] = []
        stripped_jma_name = _REMOVE_CITY_PAT.sub("", jma_name)
        for (_, name), info in self._nied_points.items():
            if info.prefecture != prefecture:
                continue
            if name in stripped_jma_name:
                found.append(info)
        if not found:
            pass
        elif len(found) == 1:
            return found[0]
        else:
            for info in found:
                if stripped_jma_name.endswith(info.name):
                    return info
            found.sort(key=lambda x: len(stripped_jma_name) - len(x.name))
            return found[0]

        # JMA 震度観測点マップ (最終手段)
        if station := self._jma_json_points.get(jma_name):
            return station

        logger.warning(f"station {jma_name} not found")
        return None


def get_volc_points():
    res = requests.get("https://www.jma.go.jp/bosai/volcano/const/volcano_list.json")
    volcs = res.json()
    result: dict[str, tuple[float, float]] = {}
    for volc in volcs:
        code = volc["code"]
        if "latlon" in volc:
            (lat, lon) = volc["latlon"]
            result[code] = (float(lon), float(lat))
        else:
            assert int(code) >= 900

    return result


def get_point_tsunami_locations() -> dict[str, PointTsunamiInfo]:
    r: dict[str, PointTsunamiInfo] = {}

    with open("./datasrc/manual_input/point_tsunami.json", encoding="utf-8") as f:
        data = json.load(f)

    for code, item in data.items():
        lat = item["lat_h"] + (item["lat_m"] / 60.0)
        lng = item["lng_h"] + (item["lng_m"] / 60.0)
        owner = item["owner"]
        r[code] = PointTsunamiInfo(lat=lat, lng=lng, owner=owner)

    res = requests.get(
        "https://www.data.jma.go.jp/svd/eqev/data/bulletin/data/tsunami/stat_j.txt"
    )
    text = res.content.decode("cp932")
    text = text.replace("度 分  度 分", "度 分  度 分  所属機関")  # fix headers
    text = text.replace("以下，", "# 以下，")  # comment out

    df = pd.read_csv(
        io.StringIO(text),
        index_col=False,
        encoding="cp932",
        skiprows=3,
        comment="#",
        delim_whitespace=True,
        dtype={"度": float, "分": float, "度.1": float, "分.1": float},
    )

    df = df.dropna(subset="度")

    for _, row in df.iterrows():
        code = row["コード"]
        if code.startswith("以下"):
            continue
        lat = row["度"] + (row["分"] / 60.0)
        lng = row["度.1"] + (row["分.1"] / 60.0)
        owner = row["所属機関"]
        r[code] = PointTsunamiInfo(lat=lat, lng=lng, owner=owner)

    return r
