from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # 不用登入就能看到的頁面：登入、註冊、忘記密碼
        exempt_urls = [
            reverse("users:log_in"),
            reverse("users:register"),
            reverse("users:forget_password"),
        ]

        # 檢查用戶是否登錄
        if not request.user.is_authenticated and request.path not in exempt_urls:
            if request.method == "POST" and request.path == reverse("users:index"):
                return self.get_response(request)
            return redirect("users:log_in")

        response = self.get_response(request)
        return response
