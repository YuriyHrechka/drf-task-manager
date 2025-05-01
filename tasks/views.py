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
from .permissions import IsBoardOwnerOrBoardAdmin
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserDetailSerializer
from django.conf import settings
from rest_framework.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name="dispatch")
class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = Response()
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = (
            "Authorization, X-Frontend-Access, Content-Type"
        )
        return response

    def get(self, request):
        frontend_access_key = request.headers.get("X-Frontend-Access")
        if frontend_access_key != getattr(settings, "FRONTEND_ACCESS_KEY", None):
            raise PermissionDenied("Access denied.")

        users = get_user_model().objects.all()
        serializer = UserDetailSerializer(users, many=True)
        response = JsonResponse(serializer.data, safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        return response


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
    permission_classes = [IsAuthenticated]
    filterset_fields = ["owner", "members"]
    search_fields = ["name"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    pagination_class = None

    def get_serializer_class(self):
        return BoardListSerializer if self.action == "list" else BoardDetailSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsBoardOwnerOrBoardAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        return (
            Board.objects.filter(owner=user)
            | Board.objects.filter(members=user)
            | Board.objects.filter(admins=user)
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagDetailSerializer
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

    def get_queryset(self):
        user = self.request.user
        return Tag.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


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
