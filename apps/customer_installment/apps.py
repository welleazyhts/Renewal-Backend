from django.apps import AppConfig


class CustomerInstallmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.customer_installment'
    verbose_name = 'Customer Installments'
    
    def ready(self):
        import apps.customer_installment.signals
