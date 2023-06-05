import logging
from uuid import uuid4

from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.contenttypes.models import ContentType
from qbwc.exceptions import QBXMLProcessingError

logger = logging.getLogger(__name__)


class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ServiceAccount(TimeStampedModel):
    """
    Service account for the Quickbooks file.

    Generates a `.qwc` config to be installed to the QBWC. The name
    corresponds to the name of the application or integration goal.
    File path provides the option to ensure we're updating
    or querying the correct QuickBooks file. If a file moves, or is renamed, this would
    prevent the request from making any breaking changes.

    Per QBWC, the url of the calling app must be:
        - https://
        - localhost

    QBID is the guid of the user the QBWC will try to auth before accpeting a ticket.

    """

    app_name = models.CharField(max_length=30)
    app_url = models.CharField(max_length=150, default="http://localhost:8000")
    app_description = models.CharField(max_length=30)
    qbid = models.CharField(max_length=60, default=uuid4, editable=False)
    app_owner_id = models.CharField(max_length=60, default=uuid4, editable=False)
    app_file_id = models.CharField(max_length=60, default=uuid4, editable=False)
    file_path = models.CharField(max_length=150, blank=True, null=True)
    # URL of the application making requests
    # UUID included in the QBWC.qwc
    password = models.CharField(max_length=120, default="test")
    is_active = models.BooleanField(default=True)
    config = models.TextField(null=True, blank=True)

    def create_qwc_file(
        self,
        app_name="",
        url="",
        app_description="",
        username="",
        app_owner_id="",
        app_file_id="",
        sync_time=60,
    ):
        return f"""<?xml version='1.0' encoding='UTF-8'?>
            <QBWCXML>
                <AppName>{app_name}</AppName>
                <AppID></AppID>
                <AppURL>{url}/webconnector/</AppURL>
                <AppDescription>{app_description}</AppDescription>
                <AppSupport>{url}/support/</AppSupport>
                <UserName>{username}</UserName>
                <OwnerID>{{{app_owner_id}}}</OwnerID>
                <FileID>{{{app_file_id}}}</FileID>
                <QBType>QBFS</QBType>
                <Scheduler>
                    <RunEveryNMinutes>{sync_time}</RunEveryNMinutes>
                </Scheduler>
        </QBWCXML>
        """

    def authenticate(self, password):
        return check_password(password, self.password)

    def save(self, *args, **kwargs):
        self.config = self.create_qwc_file(
            app_name=self.app_name,
            url=self.app_url,
            app_description=self.app_description,
            username=self.qbid,
            app_owner_id=self.app_owner_id,
            app_file_id=self.app_file_id,
        )
        self.password = make_password(self.password)
        super(ServiceAccount, self).save(*args, **kwargs)

    def __str__(self):
        return self.app_name

    class Meta:
        verbose_name = "Service Account"
        verbose_name_plural = "Service Acounts"


class TicketManager(models.Manager):
    "Manages work to be preformed by QBWC"

    def check_approved_tickets(self) -> bool:
        "Called during authentication; determines whether new work is available."
        return self.filter(status=Ticket.TicketStatus.APPROVED).count() > 0

    def get_next_ticket(self) -> str:
        "Called during authentication; returns the next ticket in the stack."
        return self.filter(status=Ticket.TicketStatus.APPROVED).first()


class Ticket(TimeStampedModel):
    class TicketStatus(models.TextChoices):
        "Give the opportunity to review data transfers before they happen"
        CREATED = ("200", "Created")
        APPROVED = ("204", "Approved")
        PROCESSING = ("300", "Processing")
        SUCCESS = ("201", "Success")
        FAILED = ("500", "Failed")

    ticket = models.CharField(max_length=60, default=uuid4, editable=False, unique=True)

    # User defined batch Id: submits records to QuickBooks
    batch_id = models.CharField(
        max_length=60, default=uuid4, editable=False, unique=True
    )

    status = models.CharField(
        max_length=3, choices=TicketStatus.choices, default=TicketStatus.CREATED
    )

    owner = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)

    objects = models.Manager()
    process = TicketManager()

    def check_task_queue(self):
        """Check the related entities (reverse fk lookup) for unbatched work"""
        return self.tasks.filter(status=Task.TaskStatus.CREATED).count() > 0

    def get_task(self):
        """
        Returns an instance of dependant task
        FIFO: ordering may be important when grouping related tasks in a single Ticket
            - tasks are executed in the order they are created
        """
        return (
            self.tasks.filter(status=Task.TaskStatus.CREATED)
            .order_by("created_on")
            .first()
        )

    @property
    def processing(self):
        "View method: update ticket status to processing"
        self.status = Ticket.TicketStatus.PROCESSING
        self.save()

    @property
    def success(self):
        "View method: update ticket status to success"
        self.status = Ticket.TicketStatus.SUCCESS
        self.save()

    @property
    def failed(self):
        "View method: update ticket status to failed"
        try:
            failed_task = self.get_task()
            failed_task.mark_failed
        except Exception as e:
            logger.error("Could not mark task failed")

        self.status = Ticket.TicketStatus.FAILED
        self.save()

    def get_completion_status(self):
        return int(
            (
                self.tasks.filter(
                    Q(status=Task.TaskStatus.SUCCESS) | Q(status=Task.TaskStatus.FAILED)
                ).count()
                / self.tasks.all().count()
            )
            * 100
        )

    def __str__(self):
        return str(self.ticket)


class Task(TimeStampedModel):
    "Wrapper around app transactions that to affect change or action in QB"

    class TaskMethod(models.TextChoices):
        GET = (
            "GET",
            "GET",
        )
        POST = (
            "POST",
            "POST",
        )
        PATCH = (
            "PATCH",
            "PATCH",
        )
        VOID = (
            "VOID",
            "VOID",
        )
        DELETE = (
            "DELETE",
            "DELETE",
        )

    class TaskStatus(models.TextChoices):
        CREATED = (
            "CREATED",
            "CREATED",
        )
        SUCCESS = (
            "SUCCESS",
            "SUCCESS",
        )
        FAILED = (
            "FAILED",
            "FAILED",
        )

    status = models.CharField(
        max_length=20, choices=TaskStatus.choices, default=TaskStatus.CREATED
    )

    method = models.CharField(
        max_length=6, choices=TaskMethod.choices, default=TaskMethod.GET
    )

    ticket = models.ForeignKey(Ticket, related_name="tasks", on_delete=models.CASCADE)

    model = models.CharField(max_length=90)
    model_instance = models.CharField(max_length=120, null=True, editable=False)

    def get_model(self):
        """
        Tickets get models. Dependant tasks get assigned ticket numbers.
        Filter the dependant unbatched tasks by querying the model using the ticket number.
        """
        content_type = ContentType.objects.get(model=self.model.lower())
        model = content_type.model_class()
        return model

    def get_model_instance(self):
        if self.model_instance:
            model = self.get_model()
            return model.objects.get(id=self.model_instance)
        return None

    @property
    def mark_failed(self):
        self.status = self.TaskStatus.FAILED
        self.save()

    @property
    def mark_success(self):
        self.status = self.TaskStatus.SUCCESS
        self.save()

    def get_request(self):
        "Get the instance task request; or related model task query"
        if self.model_instance:
            return (
                self.get_model()
                .objects.get(id=self.model_instance)
                .request(self.method)
            )
        return self.get_model()().request(self.method)

    def process_response(self, *args, **kwargs):
        "An instance of a task"

        try:
            if self.model_instance:
                (
                    self.get_model()
                    .objects.get(id=self.model_instance)
                    .process(self.method, *args, **kwargs)
                )
            else:
                self.get_model()().process(self.method, *args, **kwargs)

            self.mark_success
            self.save()

        except Exception as e:
            logger.error(e)
            logger.error(f"Marking task id: {self.id} failed")
            self.mark_failed
            self.save()

    def __str__(self):
        return str(self.ticket)


class BaseObjectMixin(TimeStampedModel):
    "Base object mixing that associated dependent models with their tickets"

    # Quickbooks Fields: if the model creates or modifies a QB transaction sync the two
    qbwc_list_id = models.CharField(max_length=120, blank=True, null=True)
    qbwc_time_created = models.DateTimeField(blank=True, null=True)
    qbwc_time_modified = models.DateTimeField(blank=True, null=True)

    def request(self, method, *args, **kwargs):
        raise NotImplementedError

    def process(self, method, *args, **kwargs):
        raise NotImplementedError

    def get_str_id(self):
        return str(self.id)

    def get_model_name(self):
        return self._meta.object_name

    class Meta:
        abstract = True
