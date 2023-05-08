class QBWC_CODES:
    """
    Response codes from webconnector
    """

    # no work to do for the service
    NONE = "none"

    # service is busy with other task
    BUSY = "busy"

    # invalid user is sent to the service
    INVALID_USER = "nvu"

    # indicates current company to use for the web connector to proceed further
    CURRENT_COMPANY = ""

    # indicates web connector and web service _set_connection closed successfully
    CONN_CLOSE_OK = "ok"

    # indicates web connector failed connecting to web service and finished its job
    CONN_CLOSE_ERROR = "done"

    # indicates web connector finished interactive session with web service
    INTERACTIVE_COMPLETE = "done"

    # unexpected error received from web connector
    UNEXPECTED_ERROR = "unexpected error"

    # no update needed for web connector to update its version, it can proceed further
    CURRENT_VERSION = ""


QBWC_VERSION = ""
