from django import forms
from captcha.fields import CaptchaField

class PostForm(forms.Form):
    customname = forms.CharField(max_length=100)
    customphone = forms.CharField(max_length=15)
    customemail = forms.EmailField()
    content = forms.CharField(widget=forms.Textarea)
    captcha = CaptchaField()

class UserForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(max_length=15)
    confirm_password = forms.CharField(max_length=15)
    captcha = CaptchaField()

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=15)
    captcha = CaptchaField()

class OloginForm(forms.Form):
    serial_number = forms.CharField(max_length=15)
    email = forms.CharField(max_length=50)
    captcha = CaptchaField()

class ForgetForm(forms.Form):
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    captcha = CaptchaField() 

class ChangepwForm(forms.Form):
    c_password = forms.CharField(max_length=15)
    c_confirm_password = forms.CharField(max_length=15)
    captcha = CaptchaField()

