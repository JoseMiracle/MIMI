from django.urls import path

from mimi.currencies.api.v1.views import CurrencyConverterAPIView

app_name = "currencies"
urlpatterns = [
    path(
        "convert-currency/", CurrencyConverterAPIView.as_view(), name="convert_currency"
    )
]
