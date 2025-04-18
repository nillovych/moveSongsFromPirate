class Bad2FAPasswordGiven(Exception):
    """Raised when the password for 2FA is not valid"""

    error_message = "Bad 2FA user password was given."


class UnauthenticatedTelegramClientException(Exception):
    """Raised when the Telegram client is not authorized"""

    error_message = (
        "Telegram client is not yet authenticated. "
        "Provide valid api-id and api-hash or add them to your env."
    )
