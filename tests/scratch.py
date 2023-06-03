"""
Reprovision an instance of example app for testing purposes
"""


from uuid import uuid4
from example.accounts.models import GlAccount
from qbwc.models import Ticket, Task

from qbwc.models import ServiceAccount

gen_random_number = lambda x: str(uuid4())[:x]


# ServiceAccount.objects.all()
# Ticket.objects.all().delete()
# Task.objects.all().delete()
# GlAccount.objects.all().delete()


service = ServiceAccount()
service.app_name = "QBWC Data Sync"
service.app_url = "http://localhost:8000"
service.app_description = "Django QuickBooks WebConnector"
service.qbid = "511829ea-f359-43cb-a885-844ebd8aabb1"
service.app_owner_id = "63293baf-fc64-4747-afa4-3fb5861c9f48"
service.app_file_id = "5d7eef11-6f07-4bc6-9c01-b911a6597f96"
service.save()


# Create a ticket for a get request
def new_gl_get():
    ticket = Ticket()
    ticket.status = Ticket.TicketStatus.APPROVED
    ticket.save()

    task = Task()
    task.ticket = ticket
    task.model = "GlAccount"
    task.method = Task.TaskMethod.GET
    task.model_instance = None
    task.save()


# # The ticket will always have a task: reverse lookup the task by the ticket
new_gl_get()
Ticket.objects.first().get_status_display()

Ticket.objects.filter(status=Ticket.TicketStatus.FAILED).all()
Ticket.objects.filter(status=Ticket.TicketStatus.SUCCESS).all()
Ticket.objects.filter(status=Ticket.TicketStatus.CREATED).all()
Ticket.objects.filter(status=Ticket.TicketStatus.APPROVED).all()


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


account_name = "New Account Name"

# Delete user created account
# Deletes the account in QB and makes the account inactive in app
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
