# apps/tasks/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TaskViewSet, BoardViewSet, TagViewSet, BoardItemViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'board-tasks', BoardItemViewSet, basename='board-task')

urlpatterns = [
    path('', include(router.urls)),
]
