import decimal

from django.db import transaction
from django.db.models import QuerySet, F

from .models import User


class RunOutOFMoneyException(Exception): ...


def make_transfer(amount: decimal, sender: User, recipients: QuerySet[User]):
    check_balance(sender=sender, amount=amount)
    transfer_amount_per_user, total_transfer_amount = calculate_transfer_per_user_and_total(
        money_amount=amount, users_amount=len(recipients)
    )

    with transaction.atomic():
        recipients.update(money_amount=F('money_amount') + transfer_amount_per_user)
        sender.money_amount = F('money_amount') - total_transfer_amount
        sender.save()


def calculate_transfer_per_user_and_total(money_amount: decimal, users_amount: int):
    transfer_amount_per_user = round(money_amount / users_amount, 2)
    total_transfer_amount = round(transfer_amount_per_user * users_amount, 2)
    return transfer_amount_per_user, total_transfer_amount


def check_balance(sender: User, amount: decimal):
    if amount >= sender.money_amount:
        raise RunOutOFMoneyException('На счёте недостаточно средств')
