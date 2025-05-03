from django.contrib import admin

from services.models import Plan, Service, Subscription

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('plan_type', 'discount_percent')
    list_display_links = ('plan_type',)
    search_fields = ('plan_type',)
    list_filter = ('plan_type',)
    ordering = ('plan_type',)
    class Meta:
        model = Plan

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_price')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    class Meta:
        model = Service

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'plan', 'price', 'comment')
    list_display_links = ('client',)
    search_fields = ('client__user__username', 'service__name', 'plan__plan_type')
    list_filter = ('client__user__is_active',)
    ordering = ('client__user__username',)
    class Meta:
        model = Subscription