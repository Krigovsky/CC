from django.test import TestCase

from django.contrib.auth.models import User
from models import Couple

# Create your tests here.
class Test_Models (TestCase):

    def setUp(self):
        self.user1 = User.objects.create(
            first_name = "John",
            last_name = "Smith",
            username = "John_Smith",
        )
        self.user2 = User.objects.create(
            first_name = "Jane",
            last_name = "Smith",
            username = "Jane_Smith",
        )
        self.couple1 = Couple.objects.create(
            team = "Team 1",
            partner_names = f"{}"
        )

    def test_user (self):
        self.assertEqual(self.user1.first_name, 'John')
        self.assertEqual(self.user1.last_name, 'Smith')
        self.assertEqual(self.user1.username, "John_Smith")

    def test_couple(self):
        pass

class Test_Utils()


