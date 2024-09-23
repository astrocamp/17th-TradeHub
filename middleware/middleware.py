from django.contrib import messages
from django.shortcuts import redirect


class Redirect404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            messages.error(request, "抱歉，找不到您要的頁面")
            return redirect("pages:home")
        return response
