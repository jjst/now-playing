#!/bin/bash
json=$(http $APP_HOSTNAME/api/stations/$NAMESPACE/)
echo $json
stations=$(echo $json | jq -r '.items | .[] | .id')
echo $stations
for id in $stations; do
	http $APP_HOSTNAME/api/stations/$NAMESPACE/$id/now-playing
done
