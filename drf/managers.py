from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class UsersManager(models.Manager):

    def get_user_by_id(self, id: int):
        if users := self.filter(id=id):
            return users[0]
        raise ObjectDoesNotExist('No such user')


    def get_users_by_inns(self, inns: list[int]):
        if users := self.filter(inn__in=inns):
            return users
        raise ObjectDoesNotExist('No such users')
