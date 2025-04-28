from datetime import datetime, timezone
from monitoring_events.persistence import MonitoringEventsPersistence
import settings


class MonitoringEventsService():
    def __init__(self, persistence: MonitoringEventsPersistence):
        self._events = persistence

    def check_for_downtime(self, u_guid: str, url: str, regions: list[str]):
        zones_count = sum([len(settings.AVAILABLE_REGIONS[region])
                          for region in regions])

        total_down_zones = 0
        downtime_s_at = datetime.now(timezone.utc)

        for region_status in self._events.get_current_regions_status(u_guid, url):
            if region_status.status == "down":
                total_down_zones += 1

                if region_status.downtime_s_at and region_status.downtime_s_at < downtime_s_at:
                    downtime_s_at = region_status.downtime_s_at

        print(total_down_zones)
        if total_down_zones > zones_count / 2:
            print(f"Downtime! started at {downtime_s_at}")
