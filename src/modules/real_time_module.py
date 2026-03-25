import time
import microcontroller
from rtc import RTC
from src.settings_utils import RealTimeSettings


def format_time_struct(time_struct):
    weekday_names = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    weekday_index = getattr(time_struct, "tm_wday", -1)
    weekday_name = weekday_names[weekday_index] if 0 <= weekday_index < len(weekday_names) else "Unknown"
    return (
        f"{time_struct.tm_year:04d}-{time_struct.tm_mon:02d}-{time_struct.tm_mday:02d} "
        f"{time_struct.tm_hour:02d}:{time_struct.tm_min:02d}:{time_struct.tm_sec:02d} "
        f"({weekday_name})"
    )


class HardwareRealTimeClock:
    sync_marker_nvm_index = 0
    synced_marker_value = 1

    def __init__(self, i2c, settings: RealTimeSettings):
        self.settings = settings
        self.i2c = i2c
        self.device = self._create_device()

    @property
    def is_available(self):
        return self.device is not None

    def _create_device(self):
        if self.settings.chip_name is None:
            return None

        try:
            if self.settings.chip_name != "pcf8523":
                print("Unsupported RTC chip:", self.settings.chip_name)
                return None

            # Requires adafruit_pcf8523, adafruit_bus_device, and adafruit_register libraries to be installed.
            from adafruit_pcf8523.pcf8523 import PCF8523

            device = PCF8523(self.i2c)

            print("Initialized hardware RTC:", self.settings.chip_name)
            return device
        except Exception as error:
            print("Could not initialize hardware RTC. Falling back to software RTC.")
            print("Reason:", error)
            return None

    def has_been_synced(self):
        if not self.is_available:
            return False

        try:
            return microcontroller.nvm[self.sync_marker_nvm_index] == self.synced_marker_value
        except (AttributeError, IndexError, OSError) as error:
            print("Could not read RTC sync marker from NVM.")
            print("Reason:", error)
            return False

    def mark_as_synced(self):
        if not self.is_available:
            return

        try:
            microcontroller.nvm[self.sync_marker_nvm_index] = self.synced_marker_value
        except (AttributeError, IndexError, OSError) as error:
            print("Could not persist RTC sync marker to NVM.")
            print("Reason:", error)

    def read_time(self):
        if not self.is_available:
            return None

        if not self.has_been_synced():
            print("Hardware RTC has not been synced yet. Ignoring stored time until first online sync.")
            return None

        try:
            time_struct = self.device.datetime
            print("Using stored hardware RTC time:", format_time_struct(time_struct))
            print("If this value is wrong, check the RTC backup battery.")
            return time_struct
        except Exception as error:
            print("Could not read time from hardware RTC.")
            print("Reason:", error)
            return None

    def write_time(self, time_struct):
        if not self.is_available:
            return

        try:
            self.device.datetime = time_struct
        except Exception as error:
            print("Could not update hardware RTC.")
            print("Reason:", error)


class OnlineTimeSource:
    def __init__(self, network, timezone):
        self.network = network
        self.timezone = timezone

    def _weekday(self, year, month, day):
        # Zeller's congruence, converted to Python/CircuitPython weekday format where Monday=0.
        if month < 3:
            month += 12
            year -= 1

        day_of_week = (
            day
            + ((13 * (month + 1)) // 5)
            + year
            + (year // 4)
            - (year // 100)
            + (year // 400)
        ) % 7

        # Zeller returns Saturday=0; convert to Monday=0..Sunday=6.
        return (day_of_week + 5) % 7

    def _parse_time(self, timestring):
        # Separate into date and time.
        # Example: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM:SS.sss
        date_time = timestring.split("T")
        year_month_day = date_time[0].split("-")
        hour_minute_second = date_time[1].split(".")[0].split(":")
        year = int(year_month_day[0])
        month = int(year_month_day[1])
        day = int(year_month_day[2])
        weekday = self._weekday(year, month, day)

        return time.struct_time(
            [
                year,
                month,
                day,
                int(hour_minute_second[0]),
                int(hour_minute_second[1]),
                int(hour_minute_second[2]),
                weekday,
                -1,
                -1,
            ]
        )

    def _get_time_api_url(self):
        timezone = self.timezone.replace("/", "%2F").replace(" ", "%20")
        return f"https://timeapi.io/api/v1/timezone/zone?timeZone={timezone}"

    def read_time(self):
        time_api_url = self._get_time_api_url()
        print("Time API URL:", time_api_url)
        time_data = self.network.get_json(time_api_url)
        return self._parse_time(time_data["local_time"])


class RealTimeClockModule:
    seconds_in_minute = 60
    minutes_in_hour = 60

    def __init__(self, i2c, network, settings: RealTimeSettings):
        self.i2c = i2c
        self.network = network
        self.settings = settings
        self.last_sync = None
        self.update_frequency = self.seconds_in_minute * self.minutes_in_hour * 5  # 5 hours
        self.hardware_clock = HardwareRealTimeClock(self.i2c, self.settings)
        self.online_time_source = OnlineTimeSource(self.network, self.settings.timezone)
        hardware_time = self.hardware_clock.read_time()
        if hardware_time is not None:
            self._set_runtime_clock(hardware_time)

    def _set_runtime_clock(self, time_struct):
        RTC().datetime = time_struct

    def _persist_time(self, time_struct):
        self._set_runtime_clock(time_struct)
        self.hardware_clock.write_time(time_struct)
        self.hardware_clock.mark_as_synced()
        print("Time synced and persisted to hardware RTC:", format_time_struct(time_struct))

    def sync_time_online(self):
        print("Syncing time online")
        if self.network.wifi_settings.skip_connection:
            print("Skipping online time sync because of skip_connection")
            return

        try:
            time_struct = self.online_time_source.read_time()
            self._persist_time(time_struct)
            self.last_sync = time.time()
        except Exception as error:
            print("Couldn't fetch time from server.")
            print("Reason:", error)
            self.network.run_connection_diagnostics()
            # Try again in 1/4 of the update frequency time
            self.last_sync = time.time() - (self.update_frequency * 0.75)

    def check_for_time_sync(self):
        if self.network.wifi_settings.skip_connection:
            return
        
        if self.hardware_clock.is_available and self.hardware_clock.has_been_synced():
            return

        # Sync with time server if we haven't synced yet or every `update_frequency` seconds
        if self.last_sync is None or (time.time() - self.last_sync) > self.update_frequency:
            self.sync_time_online()
