from django.test import TestCase
import unittest

from django.contrib.auth.models import User
from .models import Couple

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
            team = "Team 1"
        )

    

    def test_user (self):
        self.assertEqual(self.user1.first_name, 'John')
        self.assertEqual(self.user1.last_name, 'Smith')
        self.assertEqual(self.user1.username, "John_Smith")
        self.assertTrue(isinstance(self.user1, User))

    def test_couple(self):
        self.assertEqual(self.couple1.team, 'Team 1')
        self.assertTrue(isinstance(self.couple1, Couple))

        self.couple1.partner_names.add(self.user1)
        self.couple1.partner_names.add(self.user2)
        self.couple1.save()
        print("testing -> ", self.couple1.partner_names.first() )
        self.assertTrue(isinstance(self.couple1.partner_names.first(), User))
        

    def test_golfGame(self):
        pass
        

# class Test_Utils(unittest.TestCase):

#     def test_decode_name(self):
        
#         pass


