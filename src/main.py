from concurrent.futures import ThreadPoolExecutor
import itertools
import json
from typing import Any, TYPE_CHECKING

from context import ThreadSafeApplicationContext

if TYPE_CHECKING:
    from aws_lambda_typing.context import Context
    from aws_lambda_typing.events import SQSEvent


def process_record(aggregate_request) -> dict[str, Any]:
    print(f"Processing record {aggregate_request}")

    application_context = ThreadSafeApplicationContext()

    try:
        u_guid: str = aggregate_request["u_guid"]
        configuration = aggregate_request["configuration"]

        url: str = configuration["url"]

        scheduled_checks = application_context.scheduled_tasks_persistence.get_all_scheduled_checks(
            u_guid, url)

        zones = list(set(list(itertools.chain.from_iterable(
            [check.configuration.zones for check in scheduled_checks]))))

        application_context.events.check_for_downtime(u_guid, url, zones)

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
