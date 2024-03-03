from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

import requests

# Create your views here.


class CurrencyConverterAPIView(APIView):
    

    def get(self, request, *args, **kwargs):
        if ("to" and "from" and "amount") not in request.data:
            return Response({
                "error": "pls provide *to* and *from* and *amount* "
            },status=status.HTTP_400_BAD_REQUEST)
        
        converted_currency_amount = self.get_currency_conversion(request.data['to'], request.data['from'],request.data['amount'] )
        return Response({
            "converted amount": converted_currency_amount
        }, status=status.HTTP_200_OK)
    
    def get_currency_conversion(self, TO:str, FROM:str, amount:str):
        
        COMMON_CURRENCY = "XOF"

        countries_and_currency = {
            "NIGERIA": "NGN",
            "GHANA": "GHS",
            "BENIN": COMMON_CURRENCY,
            "MALI": COMMON_CURRENCY,
            "NIGER": COMMON_CURRENCY,
            "Kenya": "KES",
            "SOUTH_AFRICA": "ZAR",
            "SENEGAL": COMMON_CURRENCY,
            "TOGO": COMMON_CURRENCY
        }
        url = f"https://api.apilayer.com/exchangerates_data/convert?to={countries_and_currency[TO]}&from={countries_and_currency[FROM]}&amount={amount}"
        
        payload = {}
        headers= {
        "apikey": settings.CURRENCY_API_KEY 
        }

        try:
            response = requests.get(url, headers=headers, data = payload)
            print(response.json())
            converted_currency = round(response.json()["result"], 2)
            return converted_currency
        except Exception as e:
            print(e)




        
