import uuid

from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=30)
    # 統一編號 設定為可接受空值，個人試用者不需填寫也沒關係
    gui_number = models.CharField(max_length=8, unique=True, blank=True, null=True)
    address = models.CharField(max_length=50, blank=False, null=False, default="")
    contact_person = models.CharField(max_length=20, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    identifier = models.UUIDField(default=uuid.uuid4, unique=True)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # 獲取當前用戶
        super().__init__(*args, **kwargs)
        if user:
            self.fields["contact_person"].initial = (
                user.username
            )  # 自動填入當前用戶名稱
