import time

from rtc import RTC


class RealTimeClockModule:
    seconds_in_minute = 60
    minutes_in_hour = 60

    def __init__(self, network):
        self.network = network
        self.last_sync = None
        self.update_frequency = self.seconds_in_minute * self.minutes_in_hour * 5  # 5 hours

    def _parse_time(self, timestring):
        # Separate into date and time
        # YYYY-MM-DD
        # HH:MM:SS.SS-HH:MM
        date_time = timestring.split('T')
        # Separate date into an array
        year_month_day = date_time[0].split('-')
        # Extract HH/MM/SS
        hour_minute_second = date_time[1].split('.')[0].split(':')

        return time.struct_time(
            [
                int(year_month_day[0]),
                int(year_month_day[1]),
                int(year_month_day[2]),
                int(hour_minute_second[0]),
                int(hour_minute_second[1]),
                int(hour_minute_second[2]),
                -1,
                -1,
                -1,
            ]
        )

    def sync_time_online(self):
        print("Syncing time online")
        if self.network.wifi_settings.skip_connection:
            print("Skipping online time sync because of skip_connection")
            return
        try:
            time_data = self.network.get_json('http://worldtimeapi.org/api/ip')
            time_struct = self._parse_time(time_data.get("datetime"))
            RTC().datetime = time_struct
            # print("Localtime after updating device", time.localtime())
            self.last_sync = time.time()
        except Exception as e:
            print("Couldn't fetch time from server.")
            print(e)
            # Try again in 1/4 of the update frequency time
            self.last_sync = time.time() - (self.update_frequency * 0.75)

    def check_for_time_sync(self):
        if self.network.wifi_settings.skip_connection:
            return
        # Sync with time server if we haven't synced yet or every `update_frequency` seconds
        if self.last_sync is None or (time.time() - self.last_sync) > self.update_frequency:
            self.sync_time_online()
