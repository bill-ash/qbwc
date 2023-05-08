from django.db import models

from qbwc.models import BaseObjectMixin
from qbwc.utils import parse_time_stamp


class GlAccount(BaseObjectMixin):
    name = models.CharField(max_length=60)
    full_name = models.CharField(max_length=60)
    account_number = models.CharField(max_length=40, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    account_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    # Application info
    help_name = models.CharField(max_length=30, blank=True, null=True)
    help_description = models.TextField(blank=True, null=True)

    # Limit which accounts are displayed in the application to choose from
    display = models.BooleanField(default=True)

    def get():
        reqXML = """
        <?qbxml version="15.0"?>
            <QBXML>
            <QBXMLMsgsRq onError="stopOnError">
                <AccountQueryRq requestID="1">
                    <ActiveStatus>All</ActiveStatus> 
                </AccountQueryRq>
            </QBXMLMsgsRq>
        </QBXML>
        """
        return reqXML

    def request(self, method):
        if method == "GET":
            return """
                <?qbxml version="15.0"?>
                    <QBXML>
                    <QBXMLMsgsRq onError="stopOnError">
                        <AccountQueryRq requestID="1">
                            <ActiveStatus>All</ActiveStatus> 
                        </AccountQueryRq>
                    </QBXMLMsgsRq>
                </QBXML>
            """

    def process(self, method, response, *args, **kwargs):
        for account in response:
            breakpoint()

            self.objects.update_or_create(
                qb_list_id=account["ListID"],
                defaults={
                    "name": account["Name"],
                    "full_name": account["FullName"],
                    "description": account.get("Desc", ""),
                    "account_type": account["AccountType"],
                    "qb_time_created": parse_time_stamp(account["TimeCreated"]),
                    "qb_time_modified": parse_time_stamp(account["TimeModified"]),
                },
            )

    def __str__(self):
        return self.name


class OtherNameList(BaseObjectMixin):
    name = models.CharField(max_length=60)

    def get():
        reqXML = """
        <?qbxml version="15.0"?>
            <QBXML>
            <QBXMLMsgsRq onError="stopOnError">
                <AccountQueryRq requestID="1">
                    <ActiveStatus>All</ActiveStatus> 
                </AccountQueryRq>
            </QBXMLMsgsRq>
        </QBXML>
        """
        return reqXML

    def post():
        pass

    def patch():
        pass

    def __str__(self):
        return self.name
