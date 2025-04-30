from rest_framework import serializers
from .models import BoardItem, Task, Board, Tag
from django.utils import timezone
from django.contrib.auth import get_user_model
from .validators import validate_color


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username"]
        read_only_fields = ["id", "username"]


class TaskDetailSerializer(serializers.ModelSerializer):
    created_by = UserDetailSerializer(read_only=True)
    assignees = serializers.PrimaryKeyRelatedField(
        many=True, queryset=get_user_model().objects.all()
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "created_by",
            "assignees",
            "status",
            "priority",
            "tags",
            "deadline",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("The deadline cannot be in the past.")
        return value

    def create(self, validated_data):
        assignees = validated_data.pop("assignees", [])
        tags = validated_data.pop("tags", [])
        task = Task.objects.create(**validated_data)
        task.assignees.set(assignees)
        task.tags.set(tags)
        return task


class TaskListSerializer(serializers.ModelSerializer):
    assignees = serializers.SlugRelatedField(
        many=True, slug_field="username", read_only=True
    )

    class Meta:
        model = Task
        fields = ["id", "title", "status", "priority", "assignees"]


class BoardDetailSerializer(serializers.ModelSerializer):
    owner = UserDetailSerializer(read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=get_user_model().objects.all()
    )
    tasks = serializers.PrimaryKeyRelatedField(many=True, queryset=Task.objects.all())
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "name",
            "owner",
            "members",
            "tasks",
            "created_at",
            "member_count",
        ]
        read_only_fields = ["owner", "created_at", "member_count"]

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        tasks = validated_data.pop("tasks", [])
        board = Board.objects.create(**validated_data)
        board.members.set(members)
        board.tasks.set(tasks)
        return board

    def update(self, instance, validated_data):
        members = validated_data.pop("members", [])
        tasks = validated_data.pop("tasks", [])
        instance = super().update(instance, validated_data)
        instance.members.set(members)
        instance.tasks.set(tasks)
        return instance

    def get_member_count(self, obj):
        return obj.members.count() if obj.members else 0


class BoardListSerializer(serializers.ModelSerializer):
    owner = UserDetailSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "name", "owner", "member_count"]
        read_only_fields = ["owner", "member_count"]

    def get_member_count(self, obj):
        return obj.members.count() if obj.members else 0


class BoardItemDetailSerializer(serializers.ModelSerializer):
    task = TaskDetailSerializer()
    board = BoardDetailSerializer()

    class Meta:
        model = BoardItem
        fields = [
            "id",
            "task",
            "board",
            "position",
            "added_at",
        ]
        read_only_fields = ["added_at"]


class BoardItemListSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(read_only=True)
    board = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = BoardItem
        fields = ["id", "task", "board", "position"]


class TagDetailSerializer(serializers.ModelSerializer):
    owner = UserDetailSerializer(read_only=True)
    color = serializers.CharField(validators=[validate_color])

    class Meta:
        model = Tag
        fields = ["id", "name", "color", "owner", "created_at"]
        read_only_fields = ["created_at", "owner"]
