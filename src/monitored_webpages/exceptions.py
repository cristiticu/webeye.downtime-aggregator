class MonitoredWebpageNotFound(Exception):
    def __init__(self, msg=None, error_trace=None):
        super(MonitoredWebpageNotFound, self).__init__(
            "Webpage not found")
