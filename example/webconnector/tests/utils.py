# Grouped tasks:
# Abstraction for linking together multiple entity calls within a single ticket:
# This prevents the user from having to take specific actions beofre an event to
# ensure the application, and quickbooks are in sync.


# \\TODO: A vendor, other name, or account is written into the app; and a QB
# sync replaces or overwrites the existing record
import pytest

pytestmark = pytest.mark.skip(reason="Skipping entire file")

from uuid import uuid4
from qbwc.models import Task, Ticket

gen_random_number = lambda x: str(uuid4())[:x]


def wrap_task(model, ticket, method):
    task = Task()
    task.ticket = ticket
    task.method = method
    task.model = model.get_model_name()
    instance = model.get_str_id()
    if instance != "None":
        task.model_instance = instance
    task.save()


def init_ticket():
    ticket = Ticket()
    ticket.status = Ticket.TicketStatus.APPROVED
    ticket.save()
    return ticket
