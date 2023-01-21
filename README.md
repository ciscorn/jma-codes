# jma-codes

気象庁防災情報XMLに関係する各種コード表や定数値などをJSON形式で一元的に管理します。

気象庁が提供する Excel ファイル等を、加工用スクリプト ([`./tools/`](./tools/)) で、JSONファイル群 ([`./json/`](./json/)) に変換します。

（JSON をもとに、コードジェネレータ([`./codegen/`](./codegen/)) で Goなどの静的コード ([`./go-jmacodes/`](./go-jmacodes/)) を生成することも可能です。）

## Development

```console
$ poetry install
$ pre-commit install
```

## How to Update

[`./datasrc/`](./datasrc/) 配下のファイルを更新して、Makefileを実行すれば、JSONデータとGoコードが更新されます。

```console
$ make codegen_go
```

データソースの更新方法については [`./datasrc/`](./datasrc/) のREADMEを参照してください。
