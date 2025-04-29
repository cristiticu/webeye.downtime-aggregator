import itertools
from typing import Any

from context import ApplicationContext
import settings

if settings.ENVIRONMENT != "production":
    from aws_lambda_typing.context import Context
else:
    type Context = Any


application_context = ApplicationContext()


def lambda_handler(event: dict[str, Any], context: Context) -> dict[str, Any]:
    u_guid = event["u_guid"]
    url = event["url"]

    try:
        scheduled_checks = application_context.scheduled_tasks_persistence.get_all_scheduled_checks(
            u_guid, url)

        regions = list(set(list(itertools.chain.from_iterable(
            [check.configuration.regions for check in scheduled_checks]))))

        application_context.events.check_for_downtime(u_guid, url, regions)

        return {
            "statusCode": 200,
            "body": "Completed check",
            "headers": {
                "Content-Type": "application/json"
            }
        }

    except Exception as e:
        print(e)

        return {
            "statusCode": 400,
            "body": "Bad Request. No result",
            "headers": {
                "Content-Type": "application/json"
            }
        }


if __name__ == "__main__":
    if settings.ENVIRONMENT == "dev":
        application_context.events.check_for_downtime(
            "fb8b90bc-6015-4b46-8e6a-c2bb178d97f6", "https://weather.cristit.icu", ['america'])
