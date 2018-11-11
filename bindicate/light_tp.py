

from collections import OrderedDict
import itertools
import json
import logging
from pprint import pformat
import select
import socket
import time


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class LightTP(object):
    def __init__(self, addr, port, socket_timeout=2):
        self.addr = addr
        self.port = port
        self.socket_timeout = socket_timeout

        self.last_colour_state = {}
        self.socket = None

        self.change_state('INIT')


    def change_state(self, new_state):
        assert(new_state in ('INIT', 'READY'))
        self.state = new_state


    def do_init(self):
        message = OrderedDict(
            system=OrderedDict(
                get_sysinfo=OrderedDict()
        ))
        result = self.send_with_retries(message)
        LOGGER.info("Initialised light:\n%s", pformat(result))
        self.change_state('READY')


    def set_colour(self, colour_spec):
        if self.last_colour_state == colour_spec:
            LOGGER.debug("Colour unchanged: %s", pformat(colour_spec))
        else:
            if self.state == 'INIT':
                self.do_init()

            transition_light_state=OrderedDict(
                ignore_default=1
            )

            for key in sorted(colour_spec.keys()):
                assert(key in ('brightness','color_temp', 'hue', 'on_off', 'saturation', 'transition_period'))
                transition_light_state[key] = colour_spec[key]

            if colour_spec.get('brightness', 0) != 0 and self.last_colour_state.get('brightness', 0) == 0:
                transition_light_state['on_off'] = 1
            elif colour_spec.get('brightness') == 0 and self.last_colour_state.get('brightness') != 0:
                transition_light_state['on_off'] = 0

            message = {'smartlife.iot.smartbulb.lightingservice': dict(transition_light_state=transition_light_state)}

            result = self.send_with_retries(message)
            self.last_colour_state = colour_spec
            LOGGER.debug("Set colour:\n%s\n\n%s", pformat(colour_spec), pformat(result))


    @staticmethod
    def tp_encode(message):
        message_bytes = bytearray(json.dumps(message))
        encoded_bytes = bytearray()
        encoded_byte = 0xAB
        for message_byte in message_bytes:
            encoded_byte = message_byte ^ encoded_byte
            encoded_bytes.append(encoded_byte)

        return encoded_bytes


    def send_with_retries(self, message):
        encoded_bytes = self.tp_encode(message)

        for retry_count in itertools.count():

            xor_byte = 0xAB
            decoded_bytes = bytearray()
            bracket_depth = 0
            quote_state = False
            escape_count = 0
            terminated = False

            tp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tp_sock.setblocking(0)
            try:
                tp_sock.sendto(encoded_bytes, (self.addr, self.port))


                while not terminated:
                    ready = select.select([tp_sock], [], [], self.socket_timeout)
                    if ready and not ready[0]:
                        error_message = "Receive timed out.  Content so far was '%s'" % decoded_bytes.decode('latin_1')
                        if retry_count < 3:
                            LOGGER.warning("Retrying (%d): %s", retry_count, error_message)
                            time.sleep(0.1)
                            break
                        else:
                            raise Exception(error_message)
                    else:
                        received_bytes = bytearray(tp_sock.recv(4096))
                        for received_byte in received_bytes:
                            decoded_byte = received_byte ^ xor_byte
                            decoded_bytes.append(decoded_byte)
                            xor_byte = received_byte

                            # Parse data as much as we need to determine whther the message is terminated
                            if escape_count > 0:
                                escape_count = 0
                            else:
                                if decoded_byte == ord('\\'):
                                    escape_count = 1
                                elif decoded_byte == ord('"'):
                                    quote_state = not quote_state
                                elif not quote_state:
                                    if decoded_byte == ord('{'):
                                        bracket_depth += 1
                                    elif decoded_byte == ord('}'):
                                        bracket_depth -= 1
                                        if bracket_depth == 0:
                                            terminated = True

            finally:
                tp_sock.close()

            if terminated:
                try:
                    LOGGER.debug("Received: '%s'", decoded_bytes.decode('utf-8'))
                    decoded_json = json.loads(decoded_bytes.decode('utf-8'))
                    return decoded_json
                except Exception as e:
                    if retry_count < 3:
                        LOGGER.warning("Retrying (%d): %s", retry_count, e)
                        time.sleep(0.1)
                    else:
                        raise


