class UserAccountNotFound(Exception):
    def __init__(self, msg=None, error_trace=None):
        super(UserAccountNotFound, self).__init__(
            "User account not found")
