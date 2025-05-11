import settings
from user_account.exceptions import UserAccountNotFound
from user_account.model import UserAccount
from utils.dynamodb import dynamodb_table


class UserAccountPersistence():
    def __init__(self):
        self.users = dynamodb_table(
            settings.USER_ACCOUNTS_TABLE_NAME, settings.USER_ACCOUNTS_TABLE_REGION)

    def get(self, guid: str):
        response = self.users.get_item(Key={"guid": guid, "s_key": "DATA"})
        item = response.get("Item")

        if item is None:
            raise UserAccountNotFound()

        return UserAccount.from_db_item(item)
