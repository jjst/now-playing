#!/bin/bash
stations=$(http $APP_HOSTNAME/api/stations/$NAMESPACE/ | jq -r '.items | .[] | .id')
echo $stations
for id in $stations; do
	http $APP_HOSTNAME/api/stations/$NAMESPACE/$id/now-playing
done
