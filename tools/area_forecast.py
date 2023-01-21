"""全国・地方予報区等"""

import json

import pandas

from .utils import get_filename_for

df = pandas.read_excel(get_filename_for("AreaForecast"), skiprows=1)


def process() -> None:
    result = {}
    for _, row in df.iterrows():
        _type = row["コードタイプ"]
        name = row["XML名称"]
        note = row["備考"] if isinstance(row["備考"], str) else ""
        code = row["新コード値"]
        result[code] = {
            "type": _type,
            "name": name,
            "note": note,
        }

    with open("./json/AreaForecast.json", "w") as f:
        json.dump({"items": result}, f, sort_keys=True, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    process()
