from dotenv import load_dotenv
import os

load_dotenv('.env')

ENVIRONMENT = os.environ.get('ENVIRONMENT')
AWS_REGION = os.environ.get('AWS_REGION', '')
BACKEND_BASE_URL = os.environ.get(
    'BACKEND_BASE_URL', "https://webeye.cristit.icu")

RESOURCE_PREFIX = "production" if ENVIRONMENT == "production" else "stage"

DYNAMODB_URL_OVERRIDE = os.environ.get('DYNAMODB_URL_OVERRIDE')
TABLE_PREFIX = os.environ.get('TABLE_PREFIX', RESOURCE_PREFIX)
SCHEDULED_TASKS_TABLE_NAME = "webeye.scheduled-tasks"
SCHEDULED_TASKS_TABLE_REGION = "eu-central-1"
SCHEDULED_TASKS_SCHEDULE_GSI = "schedule-gsi"
MONITORING_EVENTS_TABLE_NAME = "webeye.monitoring-events"
MONITORING_EVENTS_TABLE_REGION = "eu-central-1"
USER_ACCOUNTS_TABLE_NAME = "webeye.user-accounts"
USER_ACCOUNTS_TABLE_REGION = "eu-central-1"
MONITORED_WEBPAGES_TABLE_NAME = "webeye.monitored-webpages"
MONITORED_WEBPAGES_TABLE_REGION = "eu-central-1"


SES_REGION = "eu-central-1"
SES_SOURCE = "notifications@webeye.cristit.icu"

AVAILABLE_REGIONS = {
    "america": [
        "ca-central-1",
        "us-east-1",
        "us-east-2",
        "us-west-1",
        "us-west-2",
        "sa-east-1"
    ],
    "europe": [
        "eu-central-1",
        "eu-west-1",
        "eu-west-2",
        "eu-west-3",
        "eu-north-1",
    ],
    "asia_pacific": [
        "ap-south-1",
        "ap-northeast-1",
        "ap-northeast-2",
        "ap-northeast-3",
        "ap-southeast-1",
        "ap-southeast-2",
    ]
}
