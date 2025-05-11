from monitored_webpages.persistence import MonitoredWebpagePersistence
from monitoring_events.persistence import MonitoringEventsPersistence
from monitoring_events.service import MonitoringEventsService
from scheduled_tasks.persistence import ScheduledTasksPersistence
from user_account.persistence import UserAccountPersistence


class ThreadSafeApplicationContext():
    def __init__(self):
        self._user_accounts_persistence = UserAccountPersistence()
        self._webpages_persistence = MonitoredWebpagePersistence()

        self._monitoring_events_persistence = MonitoringEventsPersistence()
        self.events = MonitoringEventsService(
            self._monitoring_events_persistence,
            self._user_accounts_persistence,
            self._webpages_persistence
        )

        self.scheduled_tasks_persistence = ScheduledTasksPersistence()
