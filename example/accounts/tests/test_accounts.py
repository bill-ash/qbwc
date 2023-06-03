import pytest

from uuid import uuid4
from accounts.models import GlAccount
from qbwc.models import Ticket, Task

gen_random_number = lambda x: str(uuid4())[:x]


@pytest.mark.django_db
def test_account_create():
    """
    Create a new account in QB
    """

    account_name = "New Account Name"

    a = GlAccount()
    a.name = account_name
    a.full_name = "New Account Full Name"
    a.description = "Hello, World!"
    a.account_type = GlAccount.AccountType.OTHER_CURRENT_ASSET
    a.account_number = gen_random_number(8)
    a.save()

    # Create a new ticket
    ticket = Ticket()
    ticket.status = ticket.TicketStatus.APPROVED
    ticket.batch_id = gen_random_number(6)

    # Wrapper for new account creation
    task = Task()
    task.model = a.get_model_name()
    task.model_instance = a.get_str_id()
    task.method = task.TaskMethod.POST
    task.ticket = ticket
    ticket.save()
    task.save()

    assert GlAccount.objects.count() == 1
    assert GlAccount.objects.first().name == account_name
    assert Ticket.objects.first().status == "204"
    assert Task.objects.first().method == "POST"


@pytest.mark.django_db
def test_account_delete():
    """
    Delete user created account
    Deletes the account in QB and makes the account inactive in app
    """
    account_name = "New Account Name"

    a = GlAccount()
    a.name = account_name
    a.full_name = "New Account Full Name"
    a.description = "Hello, World!"
    a.account_type = GlAccount.AccountType.OTHER_CURRENT_ASSET
    a.account_number = gen_random_number(8)
    a.save()

    account = GlAccount.objects.filter(name=account_name, mark_for_delete=False).last()
    account.mark_for_delete = True
    account.save()

    ticket = Ticket()
    ticket.status = ticket.TicketStatus.APPROVED
    ticket.batch_id = gen_random_number(8)
    ticket.save()
    task = Task()

    task.model = account.get_model_name()
    task.model_instance = account.get_str_id()
    task.method = Task.TaskMethod.DELETE
    task.ticket = ticket
    task.save()
