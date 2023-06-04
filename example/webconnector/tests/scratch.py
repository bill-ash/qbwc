"""
Reprovision an instance of example app for testing purposes
"""

from uuid import uuid4
from qbwc.models import Ticket, Task
from qbwc.models import ServiceAccount

gen_random_number = lambda x: str(uuid4())[:x]

# Grouped tasks:
# Abstraction for linking together multiple entity calls within a single ticket:
# This prevents the user from having to take specific actions beofre an event to
# ensure the application, and quickbooks are in sync.

# \\TODO: A vendor, other name, or account is written into the app; and a QB
# sync replaces or overwrites the existing record
def wrap_task(model, ticket, method):
    task = Task()
    task.ticket = ticket
    task.method = method
    task.model = model.get_model_name()
    instance = model.get_str_id()
    if instance != "None":
        task.model_instance = instance
    task.save()


from accounts.models import GlAccount
from qblists.models import OtherNameList
from vendors.models import Vendor

# ServiceAccount.objects.all()
# Ticket.objects.all().delete()
# Task.objects.all().delete()
# GlAccount.objects.all().delete()
# OtherNameList.objects.all().delete()

# service = ServiceAccount()
# service.app_name = "QBWC Data Sync"
# service.app_url = "http://localhost:8000"
# service.app_description = "Django QuickBooks WebConnector"
# service.qbid = "511829ea-f359-43cb-a885-844ebd8aabb1"
# service.app_owner_id = "63293baf-fc64-4747-afa4-3fb5861c9f48"
# service.app_file_id = "5d7eef11-6f07-4bc6-9c01-b911a6597f96"
# service.save()


# Create a ticket for a get request
def sync_qb_accounts():
    task = Task()
    task.model = GlAccount().get_model_name()
    task.method = Task.TaskMethod.GET
    task.model_instance = None
    ticket = Ticket()
    task.ticket = ticket
    ticket.status = Ticket.TicketStatus.APPROVED
    ticket.save()
    task.save()


# # The ticket will always have a task: reverse lookup the task by the ticket
sync_qb_accounts()

# Iterate through tickets
Ticket.objects.filter(status=Ticket.TicketStatus.FAILED).all()
Ticket.objects.filter(status=Ticket.TicketStatus.SUCCESS).all()
Ticket.objects.filter(status=Ticket.TicketStatus.CREATED).all()
Ticket.objects.filter(status=Ticket.TicketStatus.APPROVED).all()


def create_account():
    """
    Create an account
    Ensure special characters are escaped at model request level
    """

    a = GlAccount()
    a.name = f"M<>lo's && World's {gen_random_number(2)}"
    a.full_name = f"New Accoun|,'\" \Full Name {gen_random_number(5)}"
    a.description = "Hello, World!"
    a.account_type = GlAccount.AccountType.OTHER_CURRENT_ASSET
    a.account_number = gen_random_number(7)
    a.save()

    # Create a new ticket
    ticket = Ticket()
    ticket.status = ticket.TicketStatus.APPROVED
    ticket.batch_id = gen_random_number(7)

    # Wrapper for new account creation
    task = Task()
    task.model = a.get_model_name()
    task.model_instance = a.get_str_id()
    task.method = task.TaskMethod.POST
    task.ticket = ticket
    ticket.save()
    task.save()


# Delete user created account
# Deletes the account in QB and makes the account inactive in app
def delete_account():
    account_name = GlAccount.objects.last().name
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


# # Check the approved tickets
# Ticket.objects.filter(status=Ticket.TicketStatus.APPROVED)
# account_ticket = Ticket.process.get_next_ticket()
# account_ticket.check_unbatched_tasks()
# work = account_ticket.get_task()
# work.model_instance
# work.get_request()
# account_name = "New Account Name"
# GlAccount.objects.filter(name=account_name).delete()


def sync_other_names():
    ticket = Ticket()
    ticket.status = Ticket.TicketStatus.APPROVED
    ticket.save()
    task = Task()
    task.ticket = ticket
    task.method = task.TaskMethod.GET
    task.model = OtherNameList().get_model_name()
    task.save()


sync_other_names()


def create_other_name():
    ticket = Ticket()
    ticket.status = Ticket.TicketStatus.APPROVED
    ticket.batch_id = gen_random_number(5)
    ticket.save()

    for _ in range(0, 5):
        list_name = OtherNameList(name=f"w cas!{gen_random_number(5)}")
        list_name.save()
        task = Task()
        task.ticket = ticket
        task.model = list_name.get_model_name()
        task.model_instance = list_name.get_str_id()
        task.method = Task.TaskMethod.POST
        task.save()


create_other_name()



def create_account_other_name():
    ticket = Ticket()
    ticket.status = Ticket.TicketStatus.APPROVED
    ticket.save()

    for _ in range(0, 5):
        name = OtherNameList(name=f"azzzsd{gen_random_number(4)}")
        name.save()
        wrap_task(name, ticket, Task.TaskMethod.POST)

        account = GlAccount(
            name=f"zzzd{gen_random_number(8)}",
            full_name=f"azzzsd{gen_random_number(8)}",
            account_type=GlAccount.AccountType.OTHER_CURRENT_ASSET,
            account_number=gen_random_number(4),
        )
        account.save()

        wrap_task(account, ticket, Task.TaskMethod.POST)

    wrap_task(GlAccount(), ticket, Task.TaskMethod.GET)


create_account_other_name()


def sync_vendors():
    """Sync vendors from QuickBooks"""
    ticket = Ticket()
    ticket.status = ticket.TicketStatus.APPROVED
    ticket.save()

    task = Task()
    task.method = task.TaskMethod.GET
    task.model = Vendor().get_model_name()
    task.ticket = ticket
    task.save()


sync_vendors()


def create_vendors():
    ticket = Ticket()
    ticket.status = ticket.TicketStatus.APPROVED
    ticket.save()
    
    for _ in range(1, 5):
        vendor = Vendor()
        vendor.name = f"sdfj{gen_random_number(5)}"
        vendor.save()
        wrap_task(vendor, ticket, method=Task.TaskMethod.POST)
        
    wrap_task(Vendor(), ticket, "GET")
        

create_vendors()
