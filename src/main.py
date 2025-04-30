from concurrent.futures import ThreadPoolExecutor
import itertools
import json
from typing import Any, TYPE_CHECKING

from context import ApplicationContext

if TYPE_CHECKING:
    from aws_lambda_typing.context import Context
    from aws_lambda_typing.events import SQSEvent


application_context = ApplicationContext()


def process_record(aggregate_request) -> dict[str, Any]:
    print(f"Processing record {aggregate_request}")

    try:
        u_guid: str = aggregate_request["u_guid"]
        configuration = aggregate_request["configuration"]

        url: str = configuration["url"]

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


def lambda_handler(event: "SQSEvent", context: "Context"):
    records = event.get("Records")

    with ThreadPoolExecutor() as executor:
        executor.map(process_record, [json.loads(record.get(
            "body", "")) for record in records], timeout=20)


# if __name__ == "__main__":
#     if settings.ENVIRONMENT == "test":
#         application_context.events.check_for_downtime(
#             "fb8b90bc-6015-4b46-8e6a-c2bb178d97f6", "https://weather.cristit.icu", ['america'])
