"""ユーティリティ"""

from pathlib import Path


def get_filename_for(codeType: str) -> str:
    """指定されたコード表に該当するファイルを返す

    複数のファイルが該当する場合は例外を投げる
    """

    filenames = list(Path("./datasrc/").glob("**/*" + codeType + ".xls"))
    if len(filenames) == 1:
        return str(filenames[0])
    elif filenames := list(Path("./datasrc/").glob("**/*" + codeType + "*")):
        # 少し条件を緩める
        assert len(filenames) != 0, "ファイルが存在しません"
        assert len(filenames) == 1, "該当するファイルが重複して存在します"
        return str(filenames[0])
    raise RuntimeError("not found")
