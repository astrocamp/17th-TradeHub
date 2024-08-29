from apps.users.models import CustomUser
from django.forms import TextInput, PasswordInput, HiddenInput, DateInput
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'password1', 'first_name', 'email', 'phone', 'address', 'title', 'hire_date']  # 根據需要添加字段
        widgets = {
            # 名稱、電話、地址、email、帳號、密碼、職稱、入職時間、備註
            'username': TextInput(attrs={'class': 'form-control w-full input input-bordered', 'label': '帳號', 'required': 'True', 'placeholder': '請設定您的帳號'}),
            'first_name': TextInput(attrs={'class': 'form-control w-full input input-bordered', 'label': '名稱', 'placeholder': '請輸入您的姓名'}),
            'email': TextInput(attrs={'class': 'form-control w-full input input-bordered', 'label': '電子郵件', 'required': 'True', 'placeholder': '請輸入您的電子郵件'}),
            'phone': TextInput(attrs={'class': 'form-control w-full input input-bordered', 'label': '電話', 'required': 'True', 'placeholder': '請輸入您的電話號碼'}),
            'address': TextInput(attrs={'class': 'form-control w-full input input-bordered', 'label': '地址', 'required': 'True', 'placeholder': '請輸入您的地址'}),
            'title': TextInput(attrs={'class': 'form-control w-full input input-bordered', 'label': '職稱', 'readonly': 'readonly'}),
            'hire_date': DateInput(attrs={'class': 'form-control w-full input input-bordered text-gray-200', 'label': '入職時間', 'readonly': 'readonly'}),
            'remark': TextInput(attrs={'class': 'form-control w-full input input-bordered', 'label': '備註'}),
            'password': PasswordInput(attrs={'class': 'form-control w-full input input-bordered', 'label': '密碼', 'required': 'True', 'placeholder': '請設定您的密碼'}),
            'password1': PasswordInput(attrs={'class': 'form-control w-full input input-bordered', 'label': '確認密碼', 'required': 'True', 'placeholder': '請再次確認您的密碼'}),
        }
        labels = {
            'username': '帳號',
            'password': '密碼',
            'first_name': '姓名',
            'email': '電子郵件',
            'phone': '電話',
            'address': '地址',
            'title': '職稱',
            'hire_date': '入職時間',
            'remark': '備註',
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if 'name' not in self.labels:
                self.fields['password-based authentication'].widget = HiddenInput()
