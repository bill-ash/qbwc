from example.accounts.models import GlAccount
from qbwc.models import Ticket, Task, ServiceAccount
from uuid import uuid4


import pytest

@pytest.mark.skip(reason="Tests not implemented yet")
def test_something():
    pass

# Create a generic service account..
service = ServiceAccount()
service.app_name = "QBWC Data Sync"
service.app_url = "http://localhost:8000"
service.app_description = "Django QuickBooks WebConnector"
service.qbid = "511829ea-f359-43cb-a885-844ebd8aabb1"
service.app_owner_id = "63293baf-fc64-4747-afa4-3fb5861c9f48"
service.app_file_id = "5d7eef11-6f07-4bc6-9c01-b911a6597f96"
service.save()

# ServiceAccount.objects.all()

# Ticket.objects.all().delete()
# Task.objects.all().delete()
# GlAccount.objects.all().delete()

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


# The ticket will always have a task: reverse lookup the task by the ticket
new_gl_get()
Ticket.objects.first().get_status_display()

Ticket.objects.filter(status=Ticket.TicketStatus.FAILED).all()
Ticket.objects.filter(status=Ticket.TicketStatus.SUCCESS).all()
Ticket.objects.filter(status=Ticket.TicketStatus.CREATED).all()
Ticket.objects.filter(status=Ticket.TicketStatus.APPROVED).all()


# Create a new account in QB
a = GlAccount()
a.name = "New Account Name"
a.full_name = "New Account Full Name"
a.description = "Hello, World!"
a.account_type = "OtherCurrentAsset"
a.account_number = str(uuid4())[:4]
a.save()


# Create a new ticket
ticket = Ticket()
ticket.status = ticket.TicketStatus.APPROVED
ticket.batch_id = str(uuid4())[:8]


# Wrapper for new account creation
task = Task()
task.model = a._meta.model_name
task.model_instance = a.get_str_id()
task.method = task.TaskMethod.POST
task.ticket = ticket
ticket.save()
task.save()


# Check the approved tickets
Ticket.objects.filter(status=Ticket.TicketStatus.APPROVED)
account_ticket = Ticket.process.get_next_ticket()
account_ticket.check_unbatched_tasks()
work = account_ticket.get_task()
work.model_instance
work.get_request()

