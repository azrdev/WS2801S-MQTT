import paho.mqtt.client
from LEDStrip2 import LEDStrip, MAX
import logging
import json


logger = logging.getLogger(__name__)
ZERO = {'r': 0, 'g': 0, 'b': 0}
ON = {'r': MAX, 'g': MAX, 'b': MAX}


class MqttLedServer(paho.mqtt.client.Client):
    def __init__(self,
                 strip_size = 64,
                 realm = 'light/ledstrip/',
                 broker = 'localhost'):
        super().__init__()
        self.strip = LEDStrip(strip_size)
        #self.enable_logger(logger)

        self.discovery_prefix = 'homeassistant/' + realm
        self.command_topic = realm + "switch"
        self.state_topic = realm + "status"

        self.connect_async(broker)

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
        self.subscribe(self.state_topic)  # initial fetch

    def on_message(self, connection, userdata, msg):
        # msg: a class with members topic, payload, qos, retain
        try:
            logger.debug("%s\t%s", msg.topic, msg.payload)
            if msg.topic == self.state_topic:
                self.unsubscribe(self.state_topic)
            if msg.topic in (self.command_topic, self.state_topic):
                command = json.loads(msg.payload.decode('utf8'))
                self.process_command(command)
            else:
                logger.info("got message for topic %s we don't know: %s", msg.topic, msg.payload)
        except BaseException as e:
            logger.info("handling message threw %r", e)

    def process_command(self, command):
        # TODO: transform() as hass-effect
        state = command.get('state')
        color = command.get('color')
        if state:
            if state == "ON":
                if color:
                    self.setColor(**color)
                else:
                    self.setColor(**ON)
            else:
                self.setColor(**ZERO)
        elif color:
            self.setColor(**color)

    def setColor(self, r=0, g=0, b=0):
        logger.debug("Setting all LEDs to color %d,%d,%d", r,g,b)
        for i in range(self.strip.size):
            self.strip.setColor(i, {k: self.transform(v)
                                    for k, v in {'r': r, 'g': g, 'b': b}.items()})
        self.publishBrightness()
        self.strip.update()

    def transform(self, color):
        return color
        #return math.log1p(color)
        #return int( color **3 / MAX **2 )

    def publishBrightness(self):
        color = self.strip.getColor(0)
        is_on = any((c > 0 for c in color.values()))
        msg = {"state": "ON", "color": color} if is_on else {"state": "OFF"}
        self.publish(self.state_topic, json.dumps(msg), retain=True)


if __name__ == "__main__":
    import logging.handlers
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    MqttLedServer().run()

