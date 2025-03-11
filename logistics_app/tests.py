from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from logistics_app.models import Event, Shipment

class UserRegistrationLoginTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'role': 'customer'  # Assuming the registration form handles role selection
        })
        # Expect a redirect after successful registration (e.g., to dashboard)
        self.assertRedirects(response, reverse('dashboard'))
        # Verify the user was created
        user = User.objects.get(username='testuser')
        self.assertIsNotNone(user)

    def test_login(self):
        user = User.objects.create_user(username='loginuser', password='ComplexPass123!')
        response = self.client.post(reverse('login'), {
            'username': 'loginuser',
            'password': 'ComplexPass123!'
        })
        # A successful login should redirect (status code 302)
        self.assertEqual(response.status_code, 302)

class CRUDTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a user with warehouse_manager role (ensure the role is assigned as required)
        self.user = User.objects.create_user(username='manager', password='ComplexPass123!')
        # Manually assign role if necessary, for example:
        self.user.userprofile.role = 'warehouse_manager'
        self.user.userprofile.save()
        self.client.login(username='manager', password='ComplexPass123!')

    def test_create_event(self):
        response = self.client.post(reverse('event_create'), {
            'name': 'Test Event',
            'date': '2025-03-11',
            'location': 'Stadium',
            'description': 'Event description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(name='Test Event').exists())

    def test_create_shipment(self):
        response = self.client.post(reverse('shipment_create'), {
            'tracking_number': '123ABC',
            'status': 'pending',
            'creation_date': '2025-03-11',
            'delivery_date': '2025-03-12',
            'origin': 'Warehouse A',
            'destination': 'Stadium',
            'contents': 'Equipment'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Shipment.objects.filter(tracking_number='123ABC').exists())
