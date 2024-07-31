# jma-codes

気象庁の気象庁防災情報XMLに関係する各種コード表や定数値などをJSON形式で一元的に管理します。

気象庁が提供する Excel ファイル等を、加工用スクリプト ([`./tools/`](./tools/)) で、JSONファイル群 ([`./json/`](./json/)) に変換します。

## Development

- Python
- パッケージ管理: Rye 

## 更新方法

[`./datasrc/`](./datasrc/) 配下のファイルを更新して、Makefileを実行すれば、JSONデータが更新されます。

```console
$ make codegen_go
```

データソースの更新方法については [`./datasrc/`](./datasrc/) のREADMEを参照してください。

## Authors

- MIERUNE Inc.
- Taku Fukada (original author)
