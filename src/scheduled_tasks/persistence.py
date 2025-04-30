from scheduled_tasks.model import ScheduledCheck
import settings
from boto3.dynamodb.conditions import Key
from utils.dynamodb import dynamodb_table


class ScheduledTasksPersistence():
    def __init__(self):
        self.tasks = dynamodb_table(
            settings.SCHEDULED_TASKS_TABLE_NAME, settings.SCHEDULED_TASKS_TABLE_REGION)

    def get_all_scheduled_checks(self, u_guid: str, url: str):
        h_key = u_guid
        s_key = f"CHECK#{url}#"

        response = self.tasks.query(
            KeyConditionExpression=Key("h_key").eq(h_key) &
            Key("s_key").begins_with(s_key)
        )
        items = response.get("Items")

        return [ScheduledCheck.from_db_item(item) for item in items]
