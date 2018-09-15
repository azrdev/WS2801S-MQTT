import paho.mqtt.client
from LEDStrip2 import LEDStrip, MAX
import logging
import json


logger = logging.getLogger(__name__)
ZERO = {'r': 0, 'g': 0, 'b': 0}
ON = {'r': MAX, 'g': MAX, 'b': MAX}
MQTT_BROKER = 'localhost'


class MqttLedServer(paho.mqtt.client.Client):
    def __init__(self):
        super().__init__()
        self.strip = LEDStrip(64)
        #self.enable_logger(logger)

        self.realm = 'light/ledstrip/'
        self.discovery_prefix = 'homeassistant/' + self.realm
        self.command_topic = self.realm + "switch"
        self.state_topic = self.realm + "status"

        self.connect_async(MQTT_BROKER)

    def run(self):
        self.loop_forever()

    def on_connect(self, connection, userdata, flags, rc):
        logger.debug("Connected with rc " + str(rc))
        self.publish(
                self.discovery_prefix + 'config',
                json.dumps({
                    "name": "ledstrip",
                    "platform": "mqtt_json",
                    "state_topic": self.state_topic,
                    "command_topic": self.command_topic,
                    "rgb": True,
                }),
                retain=True)
        self.subscribe(self.command_topic)

    def on_message(self, connection, userdata, msg):
        # msg: a class with members topic, payload, qos, retain
        try:
            logger.debug("%s\t%s", msg.topic, msg.payload)
            if msg.topic == self.command_topic:
                command = json.loads(msg.payload.decode('utf8'))
                if "color" in command:
                    self.setColor(**command["color"])
                elif "state" in command:
                    if command["state"] == "ON":
                        self.setColor(**ON)
                    else:
                        self.setColor(**ZERO)
            elif msg.topic == self.state_topic:
                command = json.loads(msg.payload.decode('utf8'))
                if "state" in command:
                    if command["state"] == "ON":
                        self.setColor(**ON)
                    else:
                        self.setColor(**ZERO)
            else:
                logger.info("got message for topic %s we don't know: %s", msg.topic, msg.payload)
        except BaseException as e:
            logger.info("handling message threw %r", e)

    def setColor(self, r=0, g=0, b=0):
        logger.debug("Setting all LEDs to color %d,%d,%d", r,g,b)
        for i in range(self.strip.size):
            self.strip.setColor(i, {'r': self.transform(r), 'g': self.transform(g), 'b': self.transform(b)})
        self.publishBrightness()
        self.strip.update()

    def transform(self, color):
        return color
        #return math.log1p(color)
        #return int( color **3 / MAX **2 )

    def publishBrightness(self):
        color = self.strip.getColor(0)
        is_on = any((c > 0 for c in color.values()))
        self.publish(self.state_topic, json.dumps({
                "state": "ON" if is_on else "OFF",
                "color": color,
            }), retain=True)


if __name__ == "__main__":
    import logging.handlers
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    mls = MqttLedServer()
    mls.run()

