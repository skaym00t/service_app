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
    email = serializers.EmailField(source='client.user.email', read_only=True) # Email клиента (ссылка на модель User)
    class Meta:
        model = Subscription
        fields = ('id', 'plan_id', 'client_name', 'email', 'plan') # Поля, которые будут сериализованы(выведены)