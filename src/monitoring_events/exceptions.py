class GeneralContextNotFound(Exception):
    def __init__(self, msg=None, error_trace=None):
        super(GeneralContextNotFound, self).__init__(
            "General status context not found")
