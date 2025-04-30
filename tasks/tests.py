from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.utils import timezone
from django.contrib.auth import get_user_model

from tasks.models import Task, Board, Tag, BoardItem

User = get_user_model()

class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.other = User.objects.create_user(username='other', password='pass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

class TaskAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url_list = reverse('task-list')

    def test_create_task_valid(self):
        data = {
            'title': 'New Task',
            'description': 'Test',
            'created_by': self.user.id,
            'assignees': [self.other.id],
            'status': Task.Status.TODO,
            'priority': Task.Priority.HIGH,
            'deadline': (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            'tags': []
        }
        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(title='New Task')
        self.assertEqual(task.created_by, self.user)

    def test_create_task_past_deadline(self):
        past = timezone.now() - timezone.timedelta(days=1)
        data = {
            'title': 'Bad Task',
            'created_by': self.user.id,
            'deadline': past.isoformat()
        }
        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('deadline', response.data)

    def test_list_and_retrieve(self):
        task = Task.objects.create(title='List Task', created_by=self.user)
        list_resp = self.client.get(self.url_list)
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertIn(task.id, [item['id'] for item in list_resp.data])

        url_detail = reverse('task-detail', args=[task.id])
        detail_resp = self.client.get(url_detail)
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_resp.data['title'], 'List Task')

    def test_update_and_delete(self):
        task = Task.objects.create(title='ToUpdate', created_by=self.user)
        url = reverse('task-detail', args=[task.id])
        patch = {'status': Task.Status.DONE}
        resp = self.client.patch(url, patch, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], Task.Status.DONE)

        del_resp = self.client.delete(url)
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

class TagAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('tag-list')

    def test_create_tag_valid(self):
        data = {'name': 'Urgent', 'owner': self.user.id, 'color': '#FF0000'}
        resp = self.client.post(self.url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tag.objects.filter(name='Urgent').exists())

    def test_create_tag_invalid_color(self):
        data = {'name': 'BadColor', 'owner': self.user.id, 'color': 'red'}
        resp = self.client.post(self.url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('color', resp.data)

    def test_unique_name_per_owner(self):
        Tag.objects.create(name='Work', owner=self.user)
        data = {'name': 'Work', 'owner': self.user.id, 'color': '#00FF00'}
        resp = self.client.post(self.url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

class BoardAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('board-list')

    def test_create_board_valid(self):
        data = {'name': 'Project Board', 'owner': self.user.id, 'members': [self.other.id]}
        resp = self.client.post(self.url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Board.objects.filter(name='Project Board').exists())

    def test_create_board_owner_in_members(self):
        data = {'name': 'BadBoard', 'owner': self.user.id, 'members': [self.user.id]}
        resp = self.client.post(self.url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('The owner', str(resp.data))

class BoardItemAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.board = Board.objects.create(name='B', owner=self.user)
        self.task1 = Task.objects.create(title='T1', created_by=self.user)
        self.task2 = Task.objects.create(title='T2', created_by=self.user)
        self.task3 = Task.objects.create(title='T3', created_by=self.user)
        self.url = reverse('board-task-list')

    def test_create_and_unique_constraint(self):
        data = {'board': self.board.id, 'task': self.task1.id, 'position': 1}
        resp1 = self.client.post(self.url, data, format='json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        resp2 = self.client.post(self.url, data, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('unique', str(resp2.data).lower())

    def test_ordering(self):
        BoardItem.objects.create(board=self.board, task=self.task1, position=5)
        BoardItem.objects.create(board=self.board, task=self.task2, position=1)
        BoardItem.objects.create(board=self.board, task=self.task3, position=3)
        resp = self.client.get(self.url)
        positions = [item['position'] for item in resp.data]
        self.assertEqual(positions, sorted(positions))
