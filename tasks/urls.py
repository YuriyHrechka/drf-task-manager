from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TaskViewSet, BoardViewSet, TagViewSet, BoardItemViewSet, UserListView

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"boards", BoardViewSet, basename="board")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"board-items", BoardItemViewSet, basename="board-item")

urlpatterns = [
    path("", include(router.urls)),
    path("users/", UserListView.as_view(), name="user-list"),
]
