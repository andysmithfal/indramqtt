Export data from your Indra Smart Pro EV charger to MQTT. Connects to the API every 60 seconds and publishes basic topics, including charging state, current energy usage, and connected state. 

This was hacked together very quickly but works, I will update this if I get the time to include energy usage/cost data. 

You will need to provide the Indra device ID, which can be obtained looking at the requests the web app sends to the API. 

I recommend running this in Docker: 

```
docker build indramqtt .

docker run -e indrausername=user \
-e indrapassword=pass \
-e indradeviceid=aa-bb-cc \
-e mqttserver=192.168.1.1 \
-e mqttport=1883 \
-e mqttuser=user \
-e mqttpassword=pass \
-e mqtttopic=evcharger \
indramqtt
```