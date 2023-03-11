from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from . import models, serializers, transfer_service


class UsersList(ListAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class MoneyTransfer(APIView):

    def post(self, request: Request):
        transfer_data = serializers.TransferSerializer(data=request.data)
        transfer_data.is_valid(raise_exception=True)

        try:
            sender = models.User.manager.get_user_by_id(transfer_data.validated_data['sender']),
            recipients = models.User.manager.get_users_by_inns(transfer_data.validated_data['inns'])
        except ObjectDoesNotExist as ex:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            transfer_service.make_transfer(
                amount=transfer_data.validated_data['amount'], sender=sender, recipients=recipients
            )
        except transfer_service.RunOutOFMoneyException:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
