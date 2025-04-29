from datetime import datetime, timezone
from uuid import UUID
from monitoring_events.exceptions import GeneralContextNotFound
from monitoring_events.model import CurrentStatus, DowntimePeriod, GeneralContext
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

    def update_general_context(self, current_general_context: GeneralContext, region_status_list: list[CurrentStatus], total_zones: int):
        new_status = current_general_context.status
        new_error = current_general_context.error
        new_downtime_s_at = current_general_context.downtime_s_at

        down_zones = 0
        up_zones = 0
        region_errors: dict[str, int] = {}
        earliest_up_region_m_at = datetime.now(timezone.utc)
        earliest_down_region_m_at = datetime.now(timezone.utc)

        for region_status in region_status_list:
            if region_status.status == "up":
                up_zones += 1

                if region_status.m_at and region_status.m_at < earliest_up_region_m_at:
                    earliest_up_region_m_at = region_status.m_at

            if region_status.status == "down":
                down_zones += 1

                if region_status.m_at and region_status.m_at < earliest_down_region_m_at:
                    earliest_down_region_m_at = region_status.m_at

                if region_status.error:
                    if region_status.error not in region_errors:
                        region_errors.update({region_status.error: 1})
                    else:
                        region_errors[region_status.error] += 1

        print(f"{down_zones} regions are down: {region_errors}")
        print(f"{up_zones} regions are up")
        print(f"{total_zones - down_zones - up_zones} regions unknown")

        if down_zones >= total_zones / 3:
            new_status = "down"
            new_error = max(
                region_errors, key=lambda k: region_errors.get(k, -1))

            if current_general_context.status != "down":
                print("Changing downtime s_at")
                new_downtime_s_at = earliest_down_region_m_at

            print(f"Downtime detected. Most likely error: {new_error}")
        elif down_zones == 0 and current_general_context.status == "down":
            new_status = "up"

            downtime_period = DowntimePeriod(
                u_guid=current_general_context.u_guid,
                url=current_general_context.url,
                error=new_error,
                s_at=current_general_context.downtime_s_at if current_general_context.downtime_s_at else earliest_up_region_m_at,
                r_at=earliest_up_region_m_at
            )

            self._events.persist(downtime_period)

            new_downtime_s_at = None
            new_error = None
        elif up_zones >= total_zones / 3 and current_general_context.status == "unknown":
            new_status = "up"

        if new_status != current_general_context.status or new_error != current_general_context.error:
            patched_general_context = GeneralContext.model_validate({
                **current_general_context.model_dump(exclude_none=True),
                "status": new_status,
                "error": new_error,
                "downtime_s_at": new_downtime_s_at
            })

            self._events.persist(patched_general_context)

            return patched_general_context
        else:
            return current_general_context

    def check_for_downtime(self, u_guid: str, url: str, regions: list[str]):
        total_zones = sum([len(settings.AVAILABLE_REGIONS[region])
                          for region in regions])
        region_status_list = self._events.get_current_regions_status(
            u_guid, url)
        general_context = self.get_general_context_or_create(u_guid, url)

        patched_context = self.update_general_context(
            general_context, region_status_list, total_zones)

        return patched_context
