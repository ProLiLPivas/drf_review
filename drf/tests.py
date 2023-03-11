from unittest.mock import MagicMock

from django.test import TestCase
from django.core.exceptions import BadRequest, ObjectDoesNotExist

from drf import transfer_service, models


# Create your tests here.
class TestWithUsersContextManager:
    def __enter__(self):
        self.u1 = models.User.objects.create(username='q', inn=1, money_amount=300)
        self.u2 = models.User.objects.create(username='w', inn=2, money_amount=200)
        self.u3 = models.User.objects.create(username='s', inn=3, money_amount=200)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.u1.delete()
        self.u2.delete()
        self.u3.delete()


class TestTransferService(TestCase):
    def test_transaction_one_to_one(self):
        with TestWithUsersContextManager() as users:
            transfer_service.make_transfer(50, users.u1, models.User.objects.filter(id__in=[users.u2.id]))
            u1, u2 = models.User.objects.filter(id__in=[users.u1.id, users.u2.id])
            self.assertEqual(u1.money_amount, 250)
            self.assertEqual(u2.money_amount, 250)

    def test_transaction_one_to_many(self):
        with TestWithUsersContextManager() as users:
            transfer_service.make_transfer(100, users.u1, models.User.objects.filter(id__in=[users.u2.id, users.u3.id]))
            u1, u2, u3 = models.User.objects.filter(id__in=[users.u1.id, users.u2.id, users.u3.id])
            self.assertEqual(u1.money_amount, 200)
            self.assertEqual(u2.money_amount, 250)
            self.assertEqual(u3.money_amount, 250)

    def test_transaction_run_out_of_money(self):
        with self.assertRaises(BadRequest) as ex:
            transfer_service.check_balance(sender=MagicMock(money_amount=30), amount=300)

    def test_transaction_one_to_one_calculation(self):
        self.assertEqual(*transfer_service.calculate_transfer_per_user_and_total(money_amount=121.32, users_amount=1))

    def test_transaction_one_to_many_calculation(self):
        self.assertEqual(
            transfer_service.calculate_transfer_per_user_and_total(money_amount=121.32, users_amount=5),
            (24.26, 121.3)
        )

class TestUsersManager(TestCase):
    def __compare_user_data(self, user: models.User, example_user):
        self.assertEqual(user.id, example_user.id)
        self.assertEqual(user.inn, example_user.inn)
        self.assertEqual(user.username, example_user.username)

    def test_get_user(self):
        with TestWithUsersContextManager() as users:
            user = models.User.manager.get_user_by_id(id=users.u1.id)
            self.__compare_user_data(user, users.u1)

    def test_get_users_by_inns(self):
        with TestWithUsersContextManager() as users:
            example_users = [users.u1, users.u2]
            selected_users = models.User.manager.get_users_by_inns(inns=[users.u1.inn, users.u2.inn]).order_by('id')
            for i, user in enumerate(selected_users):
                self.__compare_user_data(user, example_users[i])

    def test_sender_do_not_exists(self):
        with self.assertRaises(ObjectDoesNotExist) as ex:
            models.User.manager.get_user_by_id(id=-1)

    def test_recipients_do_not_exists(self):
        with self.assertRaises(ObjectDoesNotExist) as ex:
            models.User.manager.get_users_by_inns(inns=[-1, -2, -3])