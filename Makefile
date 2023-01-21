.PHONY: run update_json codegen_go

help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

codegen_go: update_json  ## Go用のパッケージを生成します
	python3 codegen/go/gen_area_codes.py | gofmt > go-jmacodes/area_codes.go

update_json:  ## JSONファイルを更新します
	python3 -m tools.amedas
	python3 -m tools.area_flood_forecast
	python3 -m tools.area_forecast
	python3 -m tools.area_marine_aj
	python3 -m tools.area_river
	python3 -m tools.jmaxml_info_codes
	python3 -m tools.phenological_type
	python3 -m tools.river_offce
	python3 -m tools.seis_and_volc
	python3 -m tools.utils
	python3 -m tools.water_level_station
	python3 -m tools.wmo_observing_stations
	python3 -m tools.area_local_codes
