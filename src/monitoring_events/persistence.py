from boto3.dynamodb.conditions import Key

from monitoring_events.exceptions import GeneralContextNotFound
from monitoring_events.model import CurrentStatus, DowntimePeriod, GeneralContext
from utils.dynamodb import dynamodb_table
import settings


class MonitoringEventsPersistence():
    def __init__(self):
        self.events = dynamodb_table(
            settings.MONITORING_EVENTS_TABLE_NAME, settings.MONITORING_EVENTS_TABLE_REGION)

    def persist(self, payload:  CurrentStatus | GeneralContext | DowntimePeriod):
        self.events.put_item(Item=payload.to_db_item())

    def get_current_regions_status(self, u_guid: str, url: str):
        h_key = f"{u_guid}#{url}"
        s_key = "CURRENT#"

        response = self.events.query(
            KeyConditionExpression=Key("h_key").eq(h_key) & Key("s_key").begins_with(s_key))

        items = response.get("Items")

        return [CurrentStatus.from_db_item(item) for item in items]

    def get_general_context(self, u_guid: str, url: str):
        h_key = f"{u_guid}#{url}"
        s_key = "GENERAL"

        response = self.events.get_item(Key={"h_key": h_key, "s_key": s_key})
        item = response.get("Item")

        if item is None:
            raise GeneralContextNotFound()

        return GeneralContext.from_db_item(item)
