from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User

from .serializers import TransferSerializer
from .models import Users

'''
 не рационально делать через ViewSet (нам нужны только ListView и CreateView, причем crate view мы польностью перепишем)
лучше: 

    class GetUsers(ListAPIView): ...
    
    class MakeTransfer(APIView): ...
    
'''

class TransferViewSet(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = TransferSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        # метод сериализатора принимает строги один ИМЕННОВАННЫЙ аргумент
        # raise_exception=True (в данном случае свалится ошибка)
        serializer.is_valid(True)
        # бизнес-логика внутри контроллера (оч плохо, не надо так)

        # зачем мы сериализовывали данные, если потом напрямую преобразуем request.POST
        # serializer.
        amount = float(request.POST['amount'])
        sum_part = 0

        user_from = User.objects.get(id=request.data['user_from'])
        # лучше сразу достать всю инфу о юзере (и использовать get_or_404, чтоб не писать доп. условия)

        # # ищем сумму на счёте пользователя

        # us - (не понятный нейминг)
        us = user_from.users_set.all()


        if us:
            acc_sum = us[0].account
            # нужно уточнить по ТЗ, как нам потупить
            #   а) кидать ошибку если не найдет хотя бы одного юзера из указанных
            #   б) кидать ошибку если не найдет ни одного юзера
            #       б.1) если не найдет хотя бы одного юзера из указанных, разделит сумму на кол-во найденных
            #       б.2) если не найдет хотя бы одного юзера из указанных, разделит сумму на кол-во ожидаемых

            inn_to = Users.objects.filter(inn=request.data['inn_to'])
            users_count = 0

            #  нужно сделать транзакцию
            if inn_to and acc_sum >= amount:
                users_count = len(inn_to)
                sum_part = round(amount / users_count, 2)

                # со счёта донора списать всю сумму
                res_user = user_from.users_set.get()
                result_sum = float(res_user.account) - sum_part * users_count
                res_user.account = result_sum
                res_user.save()

                # не эффективно, т.к кидается N запросов (где N - кол-во пользователей), сделать через F()

                # # на счёт каждого записать по части
                for i in inn_to:
                    result_sum = float(i.account) + sum_part
                    i.account = result_sum
                    i.save()

                return Response(serializer.data)
            else:
                return Response('перевод не выполнен')
        else:
            # ответ не соответствует условию (условие отработает если мы не нашли юзера)
            acc_sum = 0
            return Response('На счёте недостаточно средств')
