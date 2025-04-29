from datetime import datetime, timezone
from uuid import UUID
from monitoring_events.exceptions import GeneralContextNotFound
from monitoring_events.model import DowntimePeriod, GeneralContext
from monitoring_events.persistence import MonitoringEventsPersistence
import settings


class MonitoringEventsService():
    def __init__(self, persistence: MonitoringEventsPersistence):
        self._events = persistence

    def get_general_context_or_create(self, u_guid: str, url: str):
        try:
            status = self._events.get_general_context(u_guid, url)
        except GeneralContextNotFound:
            status = GeneralContext(
                u_guid=UUID(u_guid),
                url=url,
                status="unknown")
            self._events.persist(status)

        return status

    def update_general_context(self, u_guid: str, url: str, up_zones: int, down_zones: int, total_zones: int, region_errors: dict[str, int], earliest_region_m_at: datetime):
        general_context = self.get_general_context_or_create(u_guid, url)
        new_status = general_context.status
        new_error = general_context.error
        new_downtime_s_at = general_context.downtime_s_at

        if down_zones >= total_zones / 3:
            new_status = "down"
            new_error = max(
                region_errors, key=lambda k: region_errors.get(k, -1))

            if general_context.status != "down":
                print("Changing downtime s_at")
                new_downtime_s_at = earliest_region_m_at

            print(f"Downtime detected. Most likely error: {new_error}")
        elif down_zones == 0 and general_context.status == "down":
            new_status = "up"

            downtime_period = DowntimePeriod(
                u_guid=UUID(u_guid),
                url=url,
                error=new_error,
                s_at=general_context.downtime_s_at if general_context.downtime_s_at else earliest_region_m_at,
                r_at=earliest_region_m_at
            )

            self._events.persist(downtime_period)

            new_downtime_s_at = None
            new_error = None
        elif up_zones >= total_zones / 3 and general_context.status == "unknown":
            new_status = "up"

        if new_status != general_context.status or new_error != general_context.error:
            patched_general_context = GeneralContext.model_validate({
                **general_context.model_dump(exclude_none=True),
                "status": new_status,
                "error": new_error,
                "downtime_s_at": new_downtime_s_at
            })

            self._events.persist(patched_general_context)

            return patched_general_context
        else:
            return general_context

    def check_for_downtime(self, u_guid: str, url: str, regions: list[str]):
        total_zones = sum([len(settings.AVAILABLE_REGIONS[region])
                          for region in regions])

        down_zones = 0
        up_zones = 0
        region_errors: dict[str, int] = {}
        earliest_region_m_at = datetime.now(timezone.utc)

        for region_status in self._events.get_current_regions_status(u_guid, url):
            if region_status.m_at and region_status.m_at < earliest_region_m_at:
                earliest_region_m_at = region_status.m_at

            if region_status.status == "up":
                up_zones += 1

            if region_status.status == "down":
                down_zones += 1

                if region_status.error:
                    if region_status.error not in region_errors:
                        region_errors.update({region_status.error: 1})
                    else:
                        region_errors[region_status.error] += 1

        print(f"{down_zones} regions are down: {region_errors}")
        print(f"{up_zones} regions are up")
        print(f"{total_zones - down_zones - up_zones} regions unknown")

        patched_context = self.update_general_context(
            u_guid, url, up_zones, down_zones, total_zones, region_errors, earliest_region_m_at)

        return patched_context
