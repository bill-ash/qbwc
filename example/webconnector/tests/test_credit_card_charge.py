from datetime import datetime
from webconnector.tests.utils import *

from creditcards.models import CreditCard, CreditCardCharge
from accounts.models import GlAccount
from qblists.models import OtherNameList

# Populate all expense accounts
t = init_ticket()
wrap_task(GlAccount(), t, "GET")

# Populate candidate vendors
wrap_task(OtherNameList(), t, "GET")

# Populate Credit Cards
wrap_task(CreditCard(), t, "GET")

charge = CreditCardCharge(
    credit_card=CreditCard.objects.last(),
    vendor=OtherNameList.objects.last(),
    account=(
        GlAccount.objects.filter(account_type=GlAccount.AccountType.EXPENSE).first()
    ),
    date=datetime.now(),
    reference_number=gen_random_number(6),
    memo="Hello, world!",
    description="This is a description of the expense...",
    amount=100.12,
)


charge.save()

ticket = init_ticket()
wrap_task(charge, ticket, "POST")
