.PHONY: run update_json codegen_go

help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

update_json:  ## JSONファイルを更新します
	python -m tools.amedas
	python -m tools.area_flood_forecast
	python -m tools.area_forecast
	python -m tools.area_local_codes
	python -m tools.area_marine_aj
	python -m tools.area_river
	python -m tools.jmaxml_info_codes
	python -m tools.phenological_type
	python -m tools.river_offce
	python -m tools.seis_and_volc
	python -m tools.water_level_station
	python -m tools.wmo_observing_stations
