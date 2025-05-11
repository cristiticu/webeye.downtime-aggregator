from monitored_webpages.exceptions import MonitoredWebpageNotFound
from monitored_webpages.model import MonitoredWebpage
import settings
from utils.dynamodb import dynamodb_table


class MonitoredWebpagePersistence():
    def __init__(self):
        self.webpages = dynamodb_table(
            settings.MONITORED_WEBPAGES_TABLE_NAME, settings.MONITORED_WEBPAGES_TABLE_REGION)

    def get(self, u_guid: str, url: str):
        response = self.webpages.get_item(
            Key={"u_guid": u_guid, "url": url})
        item = response.get("Item")

        if item is None:
            raise MonitoredWebpageNotFound()

        return MonitoredWebpage.from_db_item(item)
