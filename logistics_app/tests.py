from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from logistics_app.models import Event, Shipment

class UserRegistrationLoginTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'role': 'customer'
        })
        if response.status_code == 200:
            print("Registration form errors:", response.context.get('form').errors)
        self.assertRedirects(response, reverse('dashboard'))
        user = User.objects.get(username='testuser')
        user.refresh_from_db()
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.role, 'customer')

    def test_login(self):
        user = User.objects.create_user(username='loginuser', password='ComplexPass123!')
        user.refresh_from_db()
        response = self.client.post(reverse('login'), {
            'username': 'loginuser',
            'password': 'ComplexPass123!'
        })
        self.assertEqual(response.status_code, 302)

class CRUDTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an admin user (for event creation if EventCreateView is restricted to admin)
        self.admin = User.objects.create_user(username='admin', password='ComplexPass123!')
        self.admin.refresh_from_db()
        self.admin.profile.role = 'admin'
        self.admin.profile.save()
        # Create a warehouse manager for shipment creation
        self.manager = User.objects.create_user(username='manager', password='ComplexPass123!')
        self.manager.refresh_from_db()
        self.manager.profile.role = 'warehouse_manager'
        self.manager.profile.save()

    def test_create_event(self):
        # Login as admin because EventCreateView requires admin role.
        self.client.login(username='admin', password='ComplexPass123!')
        response = self.client.post(reverse('event_create'), {
            'name': 'Test Event',
            'date': '2025-03-11T00:00',  # ISO 8601 format for datetime
            'location': 'Stadium',
            'description': 'Event description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(name='Test Event').exists())

    def test_create_shipment(self):
        # Login as warehouse manager since shipment creation requires that role.
        self.client.login(username='manager', password='ComplexPass123!')
        response = self.client.post(reverse('shipment_create'), {
            'tracking_number': '123ABC',
            'status': 'PENDING',
            'date_created': timezone.now().isoformat(),
            'date_delivered': (timezone.now() + timedelta(days=1)).isoformat(),
            'origin': 'Warehouse A',
            'destination': 'Stadium',
            'contents': 'Equipment'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Shipment.objects.filter(tracking_number='123ABC').exists())

class RoleAccessTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(username='customer', password='ComplexPass123!')
        self.customer.refresh_from_db()
        self.customer.profile.role = 'customer'
        self.customer.profile.save()
        self.manager = User.objects.create_user(username='manager', password='ComplexPass123!')
        self.manager.refresh_from_db()
        self.manager.profile.role = 'warehouse_manager'
        self.manager.profile.save()

    def test_shipment_create_inaccessible_to_customer(self):
        self.client.login(username='customer', password='ComplexPass123!')
        response = self.client.get(reverse('shipment_create'))
        self.assertNotEqual(response.status_code, 200)

    def test_shipment_create_accessible_to_manager(self):
        self.client.login(username='manager', password='ComplexPass123!')
        response = self.client.get(reverse('shipment_create'))
        self.assertEqual(response.status_code, 200)

class ProfileAjaxTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='profileuser', password='ComplexPass123!')
        self.user.refresh_from_db()
        self.user.profile.role = 'customer'
        self.user.profile.save()
        self.client.login(username='profileuser', password='ComplexPass123!')

    def test_profile_update_ajax(self):
        response = self.client.post(
            reverse('profile'),
            {'role': 'customer'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn('status', json_response)
        self.assertEqual(json_response['status'], 'success')
