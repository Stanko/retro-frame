import time

import board

try:
    from adafruit_seesaw import digitalio as seesaw_digitalio
    from adafruit_seesaw import rotaryio as seesaw_rotaryio
    from adafruit_seesaw import seesaw
except ImportError:
    seesaw = None
    seesaw_digitalio = None
    seesaw_rotaryio = None


class I2CSeesawDiagnostic:
    def __init__(self, button_pin=24):
        self.button_pin = button_pin
        self.i2c = board.I2C()
        self.seesaw_devices = []

    def _scan_addresses(self):
        while not self.i2c.try_lock():
            pass
        try:
            return list(self.i2c.scan())
        finally:
            self.i2c.unlock()

    def _probe_seesaw_devices(self, addresses):
        self.seesaw_devices = []

        if seesaw is None or seesaw_digitalio is None or seesaw_rotaryio is None:
            print("adafruit_seesaw is not installed; only raw I2C addresses will be shown.")
            return

        for address in addresses:
            try:
                device = seesaw.Seesaw(self.i2c, addr=address)
                device.pin_mode(self.button_pin, device.INPUT_PULLUP)
                button = seesaw_digitalio.DigitalIO(device, self.button_pin)
                encoder = seesaw_rotaryio.IncrementalEncoder(device)
                self.seesaw_devices.append((address, button, encoder))
                print("Seesaw device responded at", hex(address))
            except Exception:
                continue

    def run(self):
        print("Starting I2C/Seesaw diagnostic")
        addresses = self._scan_addresses()

        if not addresses:
            print("No I2C devices detected.")
        else:
            print("I2C addresses:", ", ".join(hex(address) for address in addresses))

        self._probe_seesaw_devices(addresses)

        if not self.seesaw_devices:
            print("No Seesaw devices detected.")
            while True:
                time.sleep(1)

        print("Rotate the encoder and press the button to identify its address.")
        last_button_values = {}
        last_positions = {}

        while True:
            for address, button, encoder in self.seesaw_devices:
                try:
                    value = button.value
                except Exception as error:
                    print("Button read failed for", hex(address), ":", error)
                    continue

                previous_button = last_button_values.get(address)
                if previous_button is None or previous_button != value:
                    state = "released" if value else "pressed"
                    print(hex(address), "button is", state)
                    last_button_values[address] = value

                try:
                    position = -encoder.position
                except Exception as error:
                    print("Encoder read failed for", hex(address), ":", error)
                    continue

                previous_position = last_positions.get(address)
                if previous_position is None or previous_position != position:
                    print(hex(address), "position:", position)
                    last_positions[address] = position

            time.sleep(0.1)


I2CSeesawDiagnostic().run()
