#!/bin/bash
http --verbose GET "$APP_HOSTNAME/api/stations"
json=$(http GET "$APP_HOSTNAME/api/stations")
echo $json
stations=$(echo $json | jq -r '.items | .[] | .id')
echo $stations
for id in $stations; do
	http GET $APP_HOSTNAME/api/stations/$id/now-playing
done
