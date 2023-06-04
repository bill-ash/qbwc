import pytest

from uuid import uuid4
from qblists.models import OtherNameList
from qbwc.models import Ticket, Task

gen_random_number = lambda x: str(uuid4())[:x]


@pytest.mark.django_db
def test_name_create():
    ticket = Ticket()
    ticket.status = Ticket.TicketStatus.APPROVED
    ticket.batch_id = gen_random_number(5)
    ticket.save()

    for _ in range(0, 5):
        list_name = OtherNameList(name=f"Hello Tom!{gen_random_number(2)}")
        list_name.save()
        task = Task()
        task.ticket = ticket
        task.model = list_name.get_model_name()
        task.model_instance = list_name.get_str_id()
        task.method = Task.TaskMethod.POST
        task.save()

    assert OtherNameList.objects.count() == 5
    assert Ticket.objects.first().status == "204"
    assert Task.objects.first().method == "POST"
    assert ticket.check_task_queue()
    assert Ticket.process.check_approved_tickets()
    assert Ticket.process.get_next_ticket().ticket == str(ticket.ticket)
    assert ticket.get_completion_status() == 0
    assert ticket.tasks.count() == 5


@pytest.mark.django_db
def test_sync_other_names():
    ticket = Ticket()
    ticket.status = Ticket.TicketStatus.APPROVED
    ticket.save()
    task = Task()
    task.ticket = ticket
    task.method = task.TaskMethod.GET
    task.model = OtherNameList().get_model_name()
    task.save()
