import logging
from django.db import models

from qbwc.models import BaseObjectMixin
from qbwc.utils import parse_time_stamp
from qbwc.parser import string_to_xml, parse_query_element


class GlAccount(BaseObjectMixin):
    class GLAccountType(models.Choices):
        AP = (
            "AccountsPayable",
            "AccountsPayable",
        )
        AR = (
            "AccountsReceivable",
            "AccountsReceivable",
        )
        BANK = (
            "Bank",
            "Bank",
        )
        COGS = (
            "CostOfGoodsSold",
            "CostOfGoodsSold",
        )
        CREDIT_CARD = (
            "CreditCard",
            "CreditCard",
        )
        EQUITY = (
            "Equity",
            "Equity",
        )
        EXPENSE = ("Expense", "Expense")
        FIXED_ASSET = (
            "FixedAsset",
            "FixedAsset",
        )
        INCOME = (
            "Income",
            "Income",
        )
        LONG_TERM_LIABILITY = (
            "LongTermLiability",
            "LongTermLiability",
        )
        NON_POSTING = (
            "NonPosting",
            "NonPosting",
        )
        OTHER_ASSET = (
            "OtherAsset",
            "OtherAsset",
        )
        OTHER_CURRENT_ASSET = (
            "OtherCurrentAsset",
            "OtherCurrentAsset",
        )
        OTHER_CURRENT_LIABILITY = (
            "OtherCurrentLiability",
            "OtherCurrentLiability",
        )
        OTHER_EXPENSE = ("OtherExpense", "OtherExpense")
        OTHER_INCOME = (
            "OtherIncome",
            "OtherIncome",
        )

    # Mirror QB attributes
    name = models.CharField(max_length=60, unique=True)
    full_name = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True, null=True)
    account_type = models.CharField(max_length=50)
    account_number = models.CharField(max_length=40, unique=True)
    is_active = models.BooleanField(default=True)

    # Application info
    help_name = models.CharField(max_length=30, blank=True, null=True)
    help_description = models.TextField(blank=True, null=True)

    # Limit which accounts are displayed in the application to choose from
    display = models.BooleanField(default=True)

    def request(self, method):
        """
        Write the requests that make the most sense for your application.
        """
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

        if method == "POST":
            return f"""
                <?qbxml version="16.0"?>
                <QBXML>
                <QBXMLMsgsRq onError="stopOnError">
                        <AccountAddRq>
                                <AccountAdd> 
                                        <Name >{self.name}</Name> 
                                        <AccountType >{self.account_type}</AccountType> 
                                        <AccountNumber >{self.account_number}</AccountNumber>
                                        <Desc >{self.description}</Desc>
                                </AccountAdd>
                        </AccountAddRq>
                    </QBXMLMsgsRq>
                    </QBXML>
                """

    def process(self, method, response, *args, **kwargs):
        """
        Response handler:
            Write custom logic tailored to your application.
            - Returns an instance of GlAccount?
        """
        try:
            if method == "GET":
                rs = string_to_xml(response)
                for rs in rs.iter("AccountQueryRs"):
                    for q in rs.iter("AccountRet"):
                        account = parse_query_element(q)
                        GlAccount.objects.update_or_create(
                            qbwc_list_id=account["ListID"],
                            defaults={
                                "name": account["Name"],
                                "full_name": account["FullName"],
                                "description": account.get("Desc", ""),
                                "account_type": account["AccountType"],
                                "account_number": account.get("AccountNumber", ""),
                                "qbwc_time_created": parse_time_stamp(
                                    account["TimeCreated"]
                                ),
                                "qbwc_time_modified": parse_time_stamp(
                                    account["TimeModified"]
                                ),
                            },
                        )

            if method == "POST":
                rs = string_to_xml(response)
                for rs in rs.iter("AccountAddRs"):
                    for q in rs.iter("AccountRet"):
                        account = parse_query_element(q)
                        self.qbwc_list_id = account["ListID"]
                        self.qbwc_time_created = parse_time_stamp(
                            account["TimeCreated"]
                        )
                        self.qbwc_time_modified = parse_time_stamp(
                            account["TimeModified"]
                        )
                        self.save()

        except Exception as e:
            raise KeyError(e) from e

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "GL Account"
        verbose_name_plural = "GL Accounts"


class OtherNameList(BaseObjectMixin):
    name = models.CharField(max_length=60)
