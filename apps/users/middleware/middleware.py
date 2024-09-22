from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        exempt_urls = [
            reverse("pages:out_home"),
            reverse("users:log_in"),
            reverse("users:register"),
            reverse("users:forget_password"),
            reverse("social:begin", args=["google-oauth2"]),
            reverse("social:complete", args=["google-oauth2"]),
            reverse("social:begin", args=["github"]),
            reverse("social:complete", args=["github"]),
            reverse("users:log_out"),
        ]

        if not request.user.is_authenticated and request.path not in exempt_urls:
            if request.method == "POST":
                # 檢查請求的路徑是否為特定的 URL，會先執行請求
                if request.path in [
                    reverse("users:index"),
                    reverse("users:reset_password"),
                ]:
                    return self.get_response(request)
            return redirect("pages:out_home")

        response = self.get_response(request)
        return response
