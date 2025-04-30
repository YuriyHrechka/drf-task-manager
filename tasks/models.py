from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.validators import RegexValidator


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks"
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="assigned_tasks", blank=True
    )
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.TODO
    )
    priority = models.CharField(
        max_length=50, choices=Priority.choices, default=Priority.MEDIUM
    )
    tags = models.ManyToManyField("Tag", blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.deadline and self.deadline < timezone.now():
            raise ValidationError(
                {
                    "deadline": "The deadline cannot be in the past. Please select a future date."
                }
            )
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
        ]
        ordering = ["-deadline", "created_at"]

    def __str__(self):
        return f"{self.title} - {self.status} (Priority: {self.priority}) Owner: {self.created_by.username}"


class Board(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_boards"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="task_board_members",
        blank=True,
        null=True,
    )
    tasks = models.ManyToManyField(
        "Task",
        through="BoardItem",
        related_name="task_boards",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("owner", "name"),)
        ordering = ["-created_at", "name"]

    def clean(self):
        if self.members.filter(pk=self.owner.pk).exists():
            raise ValidationError(
                "The owner cannot be added as a member of their own task board."
            )
        return super().clean()

    def __str__(self):
        return f"Name: {self.name} Owner: {self.owner.username} Created At: {self.created_at}"


class BoardItem(models.Model):
    board = models.ForeignKey("Board", on_delete=models.CASCADE)
    task = models.ForeignKey("Task", on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("board", "task")
        ordering = ["position"]


class Tag(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tags"
    )
    color = models.CharField(
        max_length=7,
        default="#FFFFFF",
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$", message="Enter a valid hex color code."
            )
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("owner", "name"),)

    def __str__(self):
        return f"ID: {self.id} Name: {self.name} Owner: {self.owner.username}"
