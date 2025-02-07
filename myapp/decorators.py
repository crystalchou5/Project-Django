from functools import wraps
from django.shortcuts import redirect

def for_captcha_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('for_captcha_verified', False):
            return redirect('/forget_captcha/')
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def captcha_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('for_captcha_verified', False):
            return redirect('/forget/')
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def seller_captcha_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('seller_captcha_verified', False):
            return redirect('/seller_login/')
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view