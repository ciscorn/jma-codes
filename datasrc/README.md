# データソース

## 更新方法
### `./jmaxml/` - 気象庁の各種 Excel ファイル

[気象庁防災情報XMLフォーマット情報提供ページ](http://xml.kishou.go.jp/tec_material.html) から最新の

- コード管理表一式
- 個別コード表

をダウンロードして、ファイルを置き換えれば更新できます。

### `amedas` - アメダス観測所一覧のCSV

[地域気象観測システム（アメダス）](https://www.jma.go.jp/jma/kishou/know/amedas/kaisetsu.html) から最新の

- 地域気象観測所一覧 (`ame_master_*.csv`)
- 地域気象観測所一覧（雪） (`snow_master_*.csv`)

をダウンロードして、ファイルを置き換えれば更新できます。

### `./shape_properties/`

気象庁GISデータの各領域の面積や重心などを保持したファイル群です。

[`jma-gis`](https://github.com/ciscorn/jma-gis) レポジトリで、GISデータを最新のものにしたうえで、 `$ make shape_properties` すれば生成できます。

生成されたJSONファイルで上書きすれば更新できます。

### `manual_input`

自動で取得できる情報源がないために手動で収集したデータが含まれています。手動で更新してください。
