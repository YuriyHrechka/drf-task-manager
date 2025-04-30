from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Task, Board, Tag, BoardItem
from .serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    BoardListSerializer,
    BoardDetailSerializer,
    BoardItemListSerializer,
    BoardItemDetailSerializer,
    TagDetailSerializer,
)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()

    def get_serializer_class(self):
        return TaskListSerializer if self.action == "list" else TaskDetailSerializer

    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "priority", "assignees", "tags"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "deadline"]
    ordering = ["-created_at"]
    pagination_class = None

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(created_by=user) | Task.objects.filter(
            assignees=user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()

    def get_serializer_class(self):
        return BoardListSerializer if self.action == "list" else BoardDetailSerializer

    permission_classes = [IsAuthenticated]
    filterset_fields = ["owner", "members"]
    search_fields = ["name"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    pagination_class = None

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(owner=user) | Board.objects.filter(members=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagDetailSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["name"]
    search_fields = ["name"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    pagination_class = None

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class BoardItemViewSet(ModelViewSet):
    queryset = BoardItem.objects.all()

    def get_serializer_class(self):
        return (
            BoardItemListSerializer
            if self.action == "list"
            else BoardItemDetailSerializer
        )

    permission_classes = [IsAuthenticated]
    filterset_fields = ["board", "task"]
    search_fields = ["board__name", "task__title"]
    ordering_fields = ["position"]
    ordering = ["position"]
    pagination_class = None

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
