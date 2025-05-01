from django.db.models import Prefetch
from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    """
    Viewset для получения информации о подписках.
    """
    # queryset = Subscription.objects.all().prefetch_related('client', 'client__user') # Получаем все подписки
    # с предзагрузкой связанных объектов (prefetch_related) для оптимизации запросов к базе данных,
    # решение проблемы N+1
    queryset = Subscription.objects.all().prefetch_related(
        'plan', # Предзагрузка плана, чтобы избежать проблемы N+1
        Prefetch('client', queryset=Client.objects.all().select_related('user').only(
            'company_name',
            'user__email',
        ))) # Предзагрузка клиента с выборкой только необходимых полей, select_related для получения связанных объектов
    # (только те юзеры, которые есть в подписках, а не все юзеры из базы данных)
    # only для выбора только нужных полей из выбранных юзеров.
    # В этом случае будет только 1 запрос к Client c INNER JOIN к User, а не 2 запроса к Сlient и User:
    #
    # как было:
    # web-app-1   | (0.001) SELECT "clients_client"."id", "clients_client"."user_id", "clients_client"."company_name", "clients_client"."full_address" FROM "clients_client" WHERE "clients_client"."id" = 1 LIMIT 21; args=(1,)
    # web-app-1   | (0.000) SELECT "auth_user"."id", "auth_user"."password", "auth_user"."last_login", "auth_user"."is_superuser", "auth_user"."username", "auth_user"."first_name", "auth_user"."last_name", "auth_
    # user"."email", "auth_user"."is_staff", "auth_user"."is_active", "auth_user"."date_joined" FROM "auth_user" WHERE "auth_user"."id" = 1 LIMIT 21; args=(1,)
    # web-app-1   | (0.000) SELECT "clients_client"."id", "clients_client"."user_id", "clients_client"."company_name", "clients_client"."full_address" FROM "clients_client" WHERE "clients_client"."id" = 2 LIMIT 21; args=(2,)
    # web-app-1   | (0.000) SELECT "auth_user"."id", "auth_user"."password", "auth_user"."last_login", "auth_user"."is_superuser", "auth_user"."username", "auth_user"."first_name", "auth_user"."last_name", "auth_
    # user"."email", "auth_user"."is_staff", "auth_user"."is_active", "auth_user"."date_joined" FROM "auth_user" WHERE "auth_user"."id" = 2 LIMIT 21; args=(2,)
    #
    # стало:
    # web-app-1   | (0.002) SELECT "clients_client"."id", "clients_client"."user_id", "clients_client"."company_name",
    # "auth_user"."id", "auth_user"."email"
    # FROM "clients_client"
    # INNER JOIN "auth_user" ON ("clients_client"."user_id" = "auth_user"."id")
    # WHERE "clients_client"."id" IN (1, 2); args=(1, 2)
    serializer_class = SubscriptionSerializer # Указываем сериализатор для подписок

