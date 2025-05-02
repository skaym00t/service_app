from django.db.models import Prefetch, F, Sum
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
        # 'service', # Предзагрузка услуги, чтобы избежать проблемы N+1(1 cпособ это префетчить метод по получению цены,
        # реализованный в сериализаторе (см. сериализатор SubscriptionSerializer))
        Prefetch('client', queryset=Client.objects.all().select_related('user').only(
            'company_name',
            'user__email',
        )) # Предзагрузка клиента с выборкой только необходимых полей, select_related для получения связанных объектов
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
    # WHERE "clients_client"."id" IN (1, 2); args=(1, 2))
    )#.annotate(price=F('service__full_price') -
     #          F('service__full_price') * (F('plan__discount_percent') / 100.00)) # 2 способ -
    # Аннотация для получения цены подписки,
    # чтобы не делать лишний запрос к базе данных, а сразу получить цену подписки
    # (аннотация - это создание нового(виртуального) поля в запросе, которое будет доступно в сериализаторе)
    # price - это поле, которое будет доступно в сериализаторе
    # F - это функция, которая позволяет использовать поля модели в запросах к базе данных
    # (например, F('service__full_price') - это поле full_price из модели Service(обращаемся через ForeignKey в Subscription к
    # Service)).
    serializer_class = SubscriptionSerializer # Указываем сериализатор для подписок

    def list(self, request, *args, **kwargs): # Переопределяем метод list для получения списка подписок
        """
        Переопределяем метод list для получения списка подписок. (так не рекомендовано делать, но в данном случае
        нужно получить общую сумму стоимости подписок) Выполняем агрегацию по всем подпискам и
        добавляем ее в ответ.
        """
        queryset = self.filter_queryset(self.get_queryset()) # Получаем queryset подписок(результат запроса queryset выше)
        response = super().list(request, *args, **kwargs) # Получаем ответ от родительского метода list
        # (это результат запроса(queryset) к базе данных, который описан в этом классе выше
        response_data = {'results': response.data} # Создаем словарь с результатами
        # (превращаем список в словарь, ключом которого будет results)
        response_data['total_amount'] = queryset.aggregate(total=Sum('price')).get('total', 0) # Получаем общую сумму подписок или 0, если подписок нет
        # (используем метод aggregate для получения общей суммы подписок по полю price) - вычисление на уровне базы данных
        response.data = response_data # Присваиваем ответу новый словарь с результатами
        return response # Возвращаем ответ
        # (это будет JSON-ответ с общим количеством подписок и общей суммой подписок)

# Ответ до переопределения метода list:
    # [ # Список подписок
    #   {
    #     "id": 3,
    #     "plan_id": 3,
    #     "client_name": "Company First",
    #     "email": "user@company.com",
    #     "plan": {
    #       "id": 3,
    #       "plan_type": "discount",
    #       "discount_percent": 5
    #     },
    #     "price": 237.5
    #   },
    #   {
    #     "id": 1,
    #     "plan_id": 3,
    #     "client_name": "Только клиент 1",
    #     "email": "",
    #     "plan": {
    #       "id": 3,
    #       "plan_type": "discount",
    #       "discount_percent": 5
    #     },
    #     "price": 237.5
    #   },
    #   {
    #     "id": 2,
    #     "plan_id": 2,
    #     "client_name": "Только клиент 1",
    #     "email": "",
    #     "plan": {
    #       "id": 2,
    #       "plan_type": "студент",
    #       "discount_percent": 20
    #     },
    #     "price": 200
    #   }
    # ]

# Ответ после переопределения метода list:
    # {
    #   "results": [ # Список подписок
    #     {
    #       "id": 3,
    #       "plan_id": 3,
    #       "client_name": "Company First",
    #       "email": "user@company.com",
    #       "plan": {
    #         "id": 3,
    #         "plan_type": "discount",
    #         "discount_percent": 5
    #       },
    #       "price": 237.5
    #     },
    #     {
    #       "id": 1,
    #       "plan_id": 3,
    #       "client_name": "Just client 1",
    #       "email": "",
    #       "plan": {
    #         "id": 3,
    #         "plan_type": "discount",
    #         "discount_percent": 5
    #       },
    #       "price": 237.5
    #     },
    #     {
    #       "id": 2,
    #       "plan_id": 2,
    #       "client_name": "Just client 1",
    #       "email": "",
    #       "plan": {
    #         "id": 2,
    #         "plan_type": "student",
    #         "discount_percent": 20
    #       },
    #       "price": 200
    #     }
    #   ],
    #   "total_amount": 675 # Общая сумма подписок
    # }
