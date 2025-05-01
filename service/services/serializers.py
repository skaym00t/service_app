from rest_framework import serializers

from services.models import Subscription, Plan


class PlanSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Plan.
    """
    class Meta:
        model = Plan
        fields = '__all__' # Поля, которые будут сериализованы(выведены)

class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Subscription.
    """
    plan = PlanSerializer(read_only=True) # Сериализатор для плана (ссылка на модель Plan)
    client_name = serializers.CharField(source='client.company_name', read_only=True) # Имя клиента (ссылка на модель Client)
    email = serializers.EmailField(source='client.user.email', read_only=True) # Email клиента (ссылка на модель User,
    # в которую обращаемся через Client)
    price = serializers.SerializerMethodField() # Поле для получения цены подписки
    # (1 способ расчета цены подписки - через SerializerMethodField,
    # который потом оптимизируем через Prefetch, в SubscriptionView,
    # 2 способ - через аннотацию в SubscriptionView, который будет доступен в сериализаторе)
    # (SerializerMethodField - получает значение через метод get_<field_name>)

    def get_price(self, instance): # instance - это объект подписки(subscription)
        """
        Метод для получения цены подписки за вычетом скидки. (2 реализации - через
        """
        # # 1 способ:
        # return (instance.service.full_price -
        #         instance.service.full_price * (instance.plan.discount_percent / 100)) # Получаем цену подписки
        # # за вычетом скидки (аналогично аннотации в SubscriptionView, но выполняется для каждой подписки
        # # отдельно, что не оптимально, так как выполняется 1 запрос к базе данных для каждой подписки и поэтому нужно
        # # использовать Prefetch в SubscriptionView, чтобы избежать проблемы N+1)
        # # 2 способ:
        return instance.price # Получаем цену подписки (через аннотацию в SubscriptionView)
        # (аннотация - это создание нового(виртуального) поля в запросе, которое будет доступно в сериализаторе)

        # как выглядит запрос к базе данных(1 способ):
        # web-app-1   | (0.001) SELECT "services_subscription"."id", "services_subscription"."client_id", "services_subscription"."service_id", "services_subscription"."plan_id" FROM "services_subscription"; args=()
        # web-app-1   | (0.001) SELECT "services_plan"."id", "services_plan"."plan_type", "services_plan"."discount_percent" FROM "services_plan" WHERE "services_plan"."id" IN (2, 3); args=(2, 3)
        # web-app-1   | (0.001) SELECT "services_service"."id", "services_service"."name", "services_service"."full_price" FROM "services_service" WHERE "services_service"."id" IN (1); args=(1,)
        # web-app-1   | (0.002) SELECT "clients_client"."id", "clients_client"."user_id", "clients_client"."company_name", "auth_user"."id", "auth_user"."email" FROM "clients_client" INNER JOIN "auth_user" ON ("clients_client"."user_id" = "auth_user"."id") WHERE "clients_client"."id" IN (1, 2); args=(1, 2)

        # как выглядит запрос к базе данных(2 способ):
        # web-app-1   | (0.005) SELECT "services_subscription"."id", "services_subscription"."client_id", "services_subscription"."service_id", "services_subscription"."plan_id", ("services_service"."full_price" - ("services_service"."full_price" * ("services_plan"."discount_percent" / 100.0))) AS "price" FROM "services_subscription" INNER JOIN "services_service" ON ("services_subscription"."service_id" = "services_service"."id") INNER JOIN "services_plan" ON ("services_subscription"."plan_id" = "services_plan"."id"); args=(100.0,)
        # web-app-1   | (0.000) SELECT "services_plan"."id", "services_plan"."plan_type", "services_plan"."discount_percent" FROM "services_plan" WHERE "services_plan"."id" IN (2, 3); args=(2, 3)
        # web-app-1   | (0.001) SELECT "clients_client"."id", "clients_client"."user_id", "clients_client"."company_name", "auth_user"."id", "auth_user"."email" FROM "clients_client" INNER JOIN "auth_user" ON ("clients_client"."user_id" = "auth_user"."id") WHERE "clients_client"."id" IN (1, 2); args=(1, 2)

    class Meta:
        model = Subscription
        fields = ('id', 'plan_id', 'client_name', 'email', 'plan', 'price') # Поля, которые будут сериализованы(выведены)