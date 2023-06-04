import pytest
from qbwc.models import Task
from qbwc.models import Ticket


def test_task_status():
    assert Task.TaskMethod.POST == "POST"
