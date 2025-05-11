from datetime import datetime, timezone
from uuid import UUID
from monitoring_events.exceptions import GeneralContextNotFound
from monitoring_events.model import CurrentStatus, DowntimePeriod, GeneralContext
from monitoring_events.persistence import MonitoringEventsPersistence
import settings
from utils.datetime_parsing import split_interval_by_days


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

    def create_downtime_period(self, u_guid: UUID, url: str, s_at: datetime, r_at: datetime, error: str | None = None):
        with self._events.batch_persist() as batch:
            for s_at_index, r_at_index in split_interval_by_days(s_at, r_at):
                downtime_period = DowntimePeriod(
                    u_guid=u_guid,
                    url=url,
                    error=error,
                    s_at=s_at_index,
                    r_at=r_at_index
                )

                batch.persist(downtime_period)

    def update_general_context(self, current_general_context: GeneralContext, region_status_list: list[CurrentStatus], total_regions: int):
        new_status = current_general_context.status
        new_error = current_general_context.error
        new_downtime_s_at = current_general_context.downtime_s_at

        down_regions = 0
        up_regions = 0
        region_errors: dict[str, int] = {}
        earliest_up_region_m_at = datetime.now(timezone.utc)
        earliest_down_region_m_at = datetime.now(timezone.utc)

        for region_status in region_status_list:
            if region_status.status == "up":
                up_regions += 1

                if region_status.m_at and region_status.m_at < earliest_up_region_m_at:
                    earliest_up_region_m_at = region_status.m_at

            if region_status.status == "down":
                down_regions += 1

                if region_status.m_at and region_status.m_at < earliest_down_region_m_at:
                    earliest_down_region_m_at = region_status.m_at

                if region_status.error:
                    if region_status.error not in region_errors:
                        region_errors.update({region_status.error: 1})
                    else:
                        region_errors[region_status.error] += 1

        print(f"{down_regions} regions are down: {region_errors}")
        print(f"{up_regions} regions are up")
        print(f"{total_regions - down_regions - up_regions} regions unknown")

        if down_regions >= total_regions / 3:
            new_status = "down"
            new_error = max(
                region_errors, key=lambda k: region_errors.get(k, -1))

            if current_general_context.status != "down":
                print("Changing downtime s_at")
                new_downtime_s_at = earliest_down_region_m_at

            print(f"Downtime detected. Most likely error: {new_error}")
        elif down_regions == 0 and current_general_context.status == "down":
            new_status = "up"

            self.create_downtime_period(
                current_general_context.u_guid,
                current_general_context.url,
                current_general_context.downtime_s_at if current_general_context.downtime_s_at else earliest_up_region_m_at,
                earliest_up_region_m_at,
                new_error,
            )

            new_downtime_s_at = None
            new_error = None
        elif up_regions >= total_regions / 3 and current_general_context.status == "unknown":
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

    def check_for_downtime(self, u_guid: str, url: str, zones: list[str]):
        total_regions = sum([len(settings.AVAILABLE_REGIONS[zone])
                             for zone in zones])
        region_status_list = self._events.get_current_regions_status(
            u_guid, url)
        general_context = self.get_general_context_or_create(u_guid, url)

        patched_context = self.update_general_context(
            general_context, region_status_list, total_regions)

        return patched_context
