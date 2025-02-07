from django.shortcuts import render
from myapp import models
from django.shortcuts import redirect
from email.mime.text import MIMEText
from smtplib import SMTP, SMTPAuthenticationError, SMTPException
from .forms import PostForm,UserForm,LoginForm,OloginForm,ForgetForm,ChangepwForm
from django.template.loader import render_to_string
from django.core.mail import send_mail
from email.mime.multipart import MIMEMultipart
from django.contrib.auth.models import User 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import random 
import os
from dotenv import load_dotenv
from .decorators import for_captcha_required,seller_captcha_required,captcha_required
from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
# Create your views here.

load_dotenv(".env.local")


cartlist=[]
cartlist_m=[]
customname = ''
customphone = ''
customaddress = ''
customemail = ''
page = 0


def index(request):
    return render(request,'index.html')

def tea(request,pageindex=None):
    if 'cartlist' in request.session :
        cartlist = request.session['cartlist']
    else :
        cartlist = []
    request.session['now_page'] = '挑選茶葉'
    request.session['now_path'] = 'tea/default'

    now_page = request.session['now_page']
    now_path = request.session['now_path']

    global page
    
    pagesize = 8
    sortproduct = models.ProductModel.objects.all().order_by('-id')
    all = sortproduct.count()
    endpage = (all // pagesize) +1
    
    if pageindex == 'default':
        page = 1
    elif pageindex == 'pre':
        page = max(1, page - 1)  
    elif pageindex == 'next':
        page = min((all // pagesize) + 1, page + 1)  

    start = (page - 1) * pagesize
    
    if start >= all:
        start = (all // pagesize) * pagesize  

    page1  = page
    products = sortproduct[start:start+pagesize]


    return render(request,'tea.html',locals())
    



def detail(request,id=None):
    product = models.ProductModel.objects.get(id=id)
    now_page = request.session['now_page']
    now_path = request.session['now_path']
    return render(request,'detail.html',locals())

def cart(request):
    global cartlist
    cartlist1 = cartlist
    total = 0
    shipping = 70
    for unit in cartlist :
        total += int(unit[5])
    grandtotal = total + shipping
    return render(request,'cart.html',locals())



def addcart(request,type=None,id=None):
    global cartlist
    if type == 'add':
        product = models.ProductModel.objects.get(id=id)
        flag = True
        for unit in cartlist :
            if unit[1] == product.pname :
                unit[4] = str(int(unit[4]) + 1)
                unit[5] = str( int(unit[3]) * int(unit[4]) )
                flag = False
                break
        if flag :
            tem = []
            tem.append(product.id)
            tem.append(product.pname)
            tem.append(product.pimage)
            tem.append(str(product.pprice))
            tem.append('1')
            tem.append(str(product.pprice))
            cartlist.append(tem)
        request.session['cartlist'] = cartlist
        return redirect('/cart/')
    elif type == 'detailadd':
        product = models.ProductModel.objects.get(id=id)
        quantity = request.POST.get('quantity','')
        flag = True
        for unit in cartlist :
            if unit[1] == product.pname:
                unit[4] = str(int(quantity) + int(unit[4]))
                unit[5] = str( int(unit[4]) *  int(unit[3]) )
                flag = False 
                break
        if flag :
            tem = []
            tem.append(product.id)
            tem.append(product.pname)
            tem.append(product.pimage)
            tem.append(product.pprice)
            tem.append(quantity)
            total = str(int(quantity)* int(product.pprice))
            tem.append(total)
            cartlist.append(tem)
        request.session['cartlist'] = cartlist
        return  render(request,'detail.html',locals()) 
    elif type == 'update':
        product = models.ProductModel.objects.get(id=id)
        for unit in cartlist:
            quantity = int(request.POST.get(f'quantity_{unit[0]}',) ) # 確保轉換為整數
            unit[4] = str(quantity)
            unit[5] = str(int(unit[3])*int(unit[4]))
        request.session['cartlist'] = cartlist
        return redirect('/cart/')
    elif type == 'empty' :
        cartlist = []
        request.session['cartlist'] = cartlist
        return redirect('/cart/')    
    elif type == 'remove' :
        product = models.ProductModel.objects.get(id=id)
        product_id = product.id
        cartlist = [item for item in cartlist if item[0] != product_id]
        request.session['cartlist'] = cartlist
        return redirect('/cart/')
       
        
        
        
def order(request):
    global cartlist,customname,customphone,customemail,customaddress
    total = 0
    shipping= 70
    cartlist1 = cartlist
    for unit in cartlist:
        total += int(unit[5])
    grandtotal = total + shipping
    customname1 = customname
    customphone1 = customphone
    customemail1 = customemail
    customaddress1 = customaddress

    return render(request,'order.html',locals())

def ok(request):
    global cartlist,customname,customphone,customemail,customaddress
    total = 0
    shipping= 70
    messages = ''
    cartlist1 = cartlist
    for unit in cartlist:
        total += int(unit[5])
    grandtotal = total + shipping
    customname = request.POST.get('customname','')
    customphone = request.POST.get('customphone','')
    customaddress = request.POST.get('customaddress','')
    customemail = request.POST.get('customemail','')
    customname1 = customname
    paytype = request.POST.get('paytype','')
    if customname == '' or customphone == '' or customemail == '' or customaddress == '':
        message = '請將資料填寫完整！'
        return redirect('/order/')
    else:
        order = models.OrderModel.objects.create(total=total,shipping=shipping,grandtotal=grandtotal,customname=customname,customphone=customphone,
                                                  customaddress=customaddress,customemail=customemail,paytype=paytype)
        products = models.ProductModel.objects.all()

        for unit in cartlist:
            numtotal = int(unit[3]) * int(unit[4])
            detail = models.DetailModel.objects.create(dorder=order,pname=unit[1],pimage=unit[2],unitprice=unit[3],quantity=unit[4],total=numtotal)
            for product in products:
                if product.pname == unit[1] :
                    product.hot += 1 
                    product.save()
                else :
                    product.hot += 0
                    product.save()
        order_id = order.id

        mail_content = render_to_string('order_confirmation.html', {
            'customname': customname,
            'order_id': order_id,
            'cartlist': cartlist,
            'total': total,
            'shipping': shipping,
            'customaddress': customaddress,
        })

        mailfrom = os.getenv('MAIL_FROM')
        mailpw = os.getenv('MAIL_PASSWORD')
        mailto = customemail
        mailsubject = "一盞茶時-訂單通知"
        send_order_email(mailfrom,mailpw,mailto,mailsubject,mail_content)
        cartlist = []
        request.session['cartlist'] = cartlist
    return render(request,'ok.html',locals())


def send_order_email(mailfrom,mailpw,mailto,mailsubject,mail_content):
    strSmtp = "smtp.gmail.com:587"  # 主機
    strAccount = mailfrom  # 帳號
    strPassword = mailpw  # 應用程式專用密碼

    content = mail_content  # 郵件內容
    msg = MIMEMultipart() 
    msg["Subject"] = mailsubject  # 郵件標題
    mailto = mailto  # 收件者

    msg.attach(MIMEText(mail_content, 'html'))

    server = SMTP(strSmtp)  # 建立 SMTP 連線
    server.ehlo()  # 跟主機溝通
    server.starttls()  # TTLS 安全認證
    try:
        server.login(strAccount, strPassword)  # 登入
        server.sendmail(strAccount, mailto, msg.as_string())  # 寄信
        hint = "郵件已發送！"
    except SMTPAuthenticationError:
        hint = "無法登入！"
    except SMTPException as e:
        hint = f"郵件發送產生錯誤！錯誤內容：{e}"
    finally:
        server.quit()  # 關閉連線

def mail(request,indexfrom=None):
    indexfrom = indexfrom
    messages =''
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            # 從 cleaned_data 獲取已經驗證過的資料
            customname = form.cleaned_data.get('customname', '')
            customphone = form.cleaned_data.get('customphone', '')
            customemail = form.cleaned_data.get('customemail', '')
            content = form.cleaned_data.get('content', '')

            # 渲染郵件內容
            mail_content = render_to_string('Feedback_mail.html', {
                'customname': customname,
                'customphone': customphone,
                'customemail': customemail,
                'content': content,
            })

            # 發送郵件
            mailfrom = os.getenv('MAIL_FROM')
            mailpw = os.getenv('MAIL_PASSWORD')
            mailto = mailfrom  # 根據需要修改
            mailsubject = '一盞茶時 - 意見反饋'
            send_Feedback_email(mailfrom, mailpw, mailto, mailsubject, mail_content)

            return redirect(f'/sendmail/{indexfrom}/')
    else:
        form = PostForm()
    
    return render(request,'mail.html',locals())

def send_Feedback_email(mailfrom,mailpw,mailto,mailsubject,mail_content):
    strSmtp = "smtp.gmail.com:587"  # 主機
    strAccount = mailfrom  # 帳號
    strPassword = mailpw  # 應用程式專用密碼

    content = mail_content  # 郵件內容
    msg = MIMEMultipart() 
    msg["Subject"] = mailsubject  # 郵件標題
    mailto = mailto  # 收件者

    msg.attach(MIMEText(mail_content, 'html'))

    server = SMTP(strSmtp)  # 建立 SMTP 連線
    server.ehlo()  # 跟主機溝通
    server.starttls()  # TTLS 安全認證
    try:
        server.login(strAccount, strPassword)  # 登入
        server.sendmail(strAccount, mailto, msg.as_string())  # 寄信
        hint = "郵件已發送！"
    except SMTPAuthenticationError:
        hint = "無法登入！"
    except SMTPException as e:
        hint = f"郵件發送產生錯誤！錯誤內容：{e}"
    finally:
        server.quit()  # 關閉連線

def sendmail(request,indexfrom=None):
    indexfrom = indexfrom
    return render(request,'sendmail.html',locals())


def register(request):
    message = ''
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username','')
            email = form.cleaned_data.get('email','')
            password = form.cleaned_data.get('password','')
            confirm_password = form.cleaned_data.get('confirm_password','')
            first_name = form.cleaned_data.get('first_name','')
            if password == confirm_password :
                if User.objects.filter(username=username).exists():
                    message = '此名稱已被使用，請換一個名稱'
                else :
                    user = User.objects.create_user(username=username, password=password, email=email,first_name=first_name)
                    message = '已成功加入會員！'
                    return redirect('/login/')
            else : 
                message = '確認密碼不正確'
        else:
            message = '資料無效，請重新輸入內容'
    else :
        form = UserForm()
    return render(request,'register.html',locals())

@login_required
def tea2(request,pageindex=None):
    if 'cartlist_m' in request.session :
        cartlist_m = request.session['cartlist_m']
    else :
        cartlist_m = []
    request.session['now_page'] = '挑選茶葉'
    request.session['now_path'] = 'tea2/default'

    now_page = request.session['now_page']
    now_path = request.session['now_path']     
    products = models.ProductModel.objects.all()

    global page
    
    pagesize = 8
    sortproduct = models.ProductModel.objects.all().order_by('-id')
    all = sortproduct.count()
    endpage = (all // pagesize) +1
    
    if pageindex == 'default':
        page = 1
    elif pageindex == 'pre':
        page = max(1, page - 1)  
    elif pageindex == 'next':
        page = min((all // pagesize) + 1, page + 1)  

    start = (page - 1) * pagesize
    
    if start >= all:
        start = (all // pagesize) * pagesize  

    page1  = page
    products = sortproduct[start:start+pagesize]
    return render(request,'tea2.html',locals())

@login_required
def index2(request):
    return render(request,'index2.html')

def logout(request):
    auth_logout(request)
    return redirect('/index/')



def detail2(request,id=None):
    product = models.ProductModel.objects.get(id=id)
    now_page = request.session['now_page']
    now_path = request.session['now_path']
    return render(request,'detail2.html',locals())
    
@login_required
def cart2(request):
    global cartlist_m
    cartlist2 = cartlist_m
    total_m = 0
    shipping = 70
    for unit in cartlist_m :
        total_m += int(unit[5])
    grandtotal_m = total_m + shipping
    return render(request,'cart2.html',locals())


def addcart_m(request,type=None,id=None):
    global cartlist_m
    if type == 'add':
        product = models.ProductModel.objects.get(id=id)
        flag = True
        for unit in cartlist_m :
            if unit[1] == product.pname :
                unit[4] = str(int(unit[4]) + 1)
                unit[5] = str( int(product.member_price) * int(unit[4]) )
                flag = False
                break
        if flag :
            tem = []
            tem.append(product.id)
            tem.append(product.pname)
            tem.append(product.pimage)
            tem.append(str(product.member_price))
            tem.append('1')
            tem.append(str(product.member_price))
            cartlist_m.append(tem)
        request.session['cartlist_m'] = cartlist_m
        return redirect('/cart2/')
    elif type == 'detailadd':
        product = models.ProductModel.objects.get(id=id)
        quantity = request.POST.get('quantity','')
        flag = True
        for unit in cartlist_m :
            if unit[1] == product.pname:
                unit[4] = str(int(quantity) + int(unit[4]))
                unit[5] = str( int(unit[4]) *  int(product.member_price) )
                flag = False 
                break
        if flag :
            tem = []
            tem.append(product.id)
            tem.append(product.pname)
            tem.append(product.pimage)
            tem.append(product.member_price)
            tem.append(quantity)
            total_m = str(int(quantity)* int(product.member_price))
            tem.append(total_m)
            cartlist_m.append(tem)
        request.session['cartlist_m'] = cartlist_m
        return  render(request,'detail2.html',locals()) 
    elif type == 'update':
        product = models.ProductModel.objects.get(id=id)
        for unit in cartlist_m:
            quantity = int(request.POST.get(f'quantity_{unit[0]}','1') ) # 確保轉換為整數
            unit[4] = str(quantity)
            unit[5] = str(int(unit[4]) * int(unit[3])) 
        request.session['cartlist_m'] = cartlist_m
        return redirect('/cart2/')
    elif type == 'empty' :
        cartlist_m = []
        request.session['cartlist_m'] = cartlist_m
        return redirect('/cart2/')    
    elif type == 'remove' :
        product = models.ProductModel.objects.get(id=id)
        product_id = product.id
        cartlist_m = [item for item in cartlist_m if item[0] != product_id]
        request.session['cartlist_m'] = cartlist_m
        return redirect('/cart2/')
    
@login_required
def order2(request):
    global cartlist_m
    total_m = 0
    shipping= 70
    cartlist2 = cartlist_m
    for unit in cartlist_m:
        total_m += int(unit[5]) 
    grandtotal_m = total_m + shipping
    if request.user.is_authenticated :
        user = request.user 
        member_name = user.username
        member_email = user.email
    else:
        member_name = ''
        member_email = ''
    return render(request,'order2.html',locals())

def ok2(request):
    global cartlist_m
    total_m = 0
    shipping= 70
    cartlist2 = cartlist_m
    for unit in cartlist_m:
        total_m += int(unit[5])
    grandtotal_m = total_m + shipping
    customname = request.POST.get('member_name','')
    customphone = request.POST.get('member_phone','')
    customaddress = request.POST.get('member_address','')
    customemail = request.POST.get('member_email','')
    customname1 = customname
    paytype = request.POST.get('paytype','')
    if customname == '' or customphone == '' or customemail == '' or customaddress == '':
        return redirect('/order/')
    else:
        order = models.OrderModel.objects.create(total=total_m,shipping=shipping,grandtotal=grandtotal_m,customname=customname,customphone=customphone,
                                                  customaddress=customaddress,customemail=customemail,paytype=paytype)
        products = models.ProductModel.objects.all()
        for unit in cartlist_m:
            numtotal = int(unit[3]) * int(unit[4])
            detail = models.DetailModel.objects.create(dorder=order,pname=unit[1],pimage=unit[2],unitprice=unit[3],quantity=unit[4],total=numtotal)
            for product in products :
                if product.pname == unit[1]:
                    product.hot += 1 
                    product.save()
                else :
                    product.hot += 0 
                    product.save()
        order_id = order.id


        mail_content = render_to_string('order_confirmation.html', {
            'customname': customname,
            'order_id': order_id,
            'cartlist': cartlist,
            'total': total_m,
            'shipping': shipping,
            'customaddress': customaddress,
        })

        mailfrom = os.getenv('MAIL_FROM')
        mailpw = os.getenv('MAIL_PASSWORD')
        mailto = customemail
        mailsubject = "一盞茶時-訂單通知"
        send_order_email(mailfrom,mailpw,mailto,mailsubject,mail_content)
        cartlist_m = []
        request.session['cartlist_m'] = cartlist_m
    return render(request,'ok.html',locals())


def orderlogin(request,indexfrom=None):
    message = ''
    indexfrom = indexfrom
    form = OloginForm(request.POST)
    if request.user.is_authenticated:
        user = request.user
        email_m = user.email
    else:
        email_m = '' 
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email','')
            serial_number =  int(form.cleaned_data.get('serial_number',''))
            if models.OrderModel.objects.filter(id = serial_number).exists():
                if models.OrderModel.objects.filter(customemail=email).exists():
                    return redirect(f'/checkorder/{serial_number}/{indexfrom}/')        
                else :
                    message = '信箱輸入錯誤'
            else : 
                message = '訂單編號輸入錯誤'
        else :
            message = '驗證碼輸入錯誤'
    else:
        form = OloginForm()
    return render(request,'orderlogin.html',locals())

def checkorder(request,serial_number=None,indexfrom=None):
    indexfrom = indexfrom
    order = models.OrderModel.objects.filter(id=serial_number).first()
    details = models.DetailModel.objects.filter(dorder=order)
    return render(request,'checkorder.html',locals())

def check(request):
    orderid = request.GET.get('orderid')
    customemail = request.GET.get('customemail')
    
    if orderid is not None :
        order = models.OrderModel.objects.filter(id=orderid).first()
        details = models.DetailModel.objects.filter(dorder=order)
    else:
        order = None
        details = None
    
    return render(request,'checkorder.html',locals()) 


def hotproduct(request,indexfrom= None):
    indexfrom = indexfrom
    products = models.ProductModel.objects.filter(hot__gt=0).order_by('-hot')
    if indexfrom == 'index' :
        request.session['now_page'] ='熱銷商品'
        request.session['now_path'] = 'hotproduct/index'
    elif indexfrom == 'index2':
        request.session['now_page'] ='熱銷商品'
        request.session['now_path'] = 'hotproduct/index2'
    
    now_page = request.session['now_page']
    now_path = request.session['now_path']

    if not products.exists() :
        products = models.ProductModel.objects.all()
    return render(request,'hotproduct.html',locals())

def aboutus(request,indexfrom=None):
    indexfrom = indexfrom
    if indexfrom == 'index':
        request.session['now_page'] = '關於我們'
        request.session['now_path'] = 'aboutus/index'
    elif indexfrom == 'index2':
        request.session['now_page'] = '關於我們'
        request.session['now_path'] = 'aboutus/index2'
    now_page = request.session['now_page']
    now_path = request.session['now_path']
    return render(request,'aboutus.html',locals())

def member(request,indexfrom=None):
    indexfrom = indexfrom
    if indexfrom == 'index':
        request.session['now_page'] = '會員福利'
        request.session['now_path'] = 'member/index'
    elif indexfrom == 'index2':
        request.session['now_page'] = '會員福利'
        request.session['now_path'] = 'member/index2'
    now_page = request.session['now_page']
    now_path = request.session['now_path']
    return render(request,'member.html',locals())


def reference(request):
    return render(request,'reference.html')

def forget(request):
    message = ''
    random_int = []
    if request.method  == 'POST' :
        form = ForgetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email', '')
            username = form.cleaned_data.get('username', '')
            request.session['f_username'] = username
            if User.objects.filter(username=username).exists():
                if User.objects.filter(email=email).exists():
                    for i in range(6):
                        random_int.append(random.randint(1,9))
                    r_int = ''.join(map(str, random_int))
                    request.session['r_int'] = r_int
                    ran_int = request.session['r_int'] 
                    mailfrom = os.getenv('MAIL_FROM')
                    mailpw = os.getenv('MAIL_PASSWORD')
                    mailto = email
                    mailsubject = "一盞茶時-變更密碼"
                    mail_content = render_to_string('forget_mail.html', {
                        'r_int':r_int
                    })
                    send_forget_mail(mailfrom,mailpw,mailto,mailsubject,mail_content)
                    message = '已將驗證碼的信件寄送至您信箱'
                    request.session['for_captcha_verified'] = True
                    return redirect('/forget_captcha/')      
                else:
                    message = '信箱輸入不正確'
            else:
                message = '會員不存在'
    else:
        form = ForgetForm()
    return render(request,'forget.html',locals())

def send_forget_mail(mailfrom,mailpw,mailto,mailsubject,mail_content):
    strSmtp = "smtp.gmail.com:587"  # 主機
    strAccount = mailfrom  # 帳號
    strPassword = mailpw # 應用程式專用密碼

    content = mail_content  # 郵件內容
    msg = MIMEText(mail_content, 'html')
    msg["Subject"] = mailsubject  # 郵件標題
    mailto = mailto  # 收件者
    

    server = SMTP(strSmtp)  # 建立 SMTP 連線
    server.ehlo()  # 跟主機溝通
    server.starttls()  # TTLS 安全認證
    try:
        server.login(strAccount, strPassword)  # 登入
        server.sendmail(strAccount, mailto, msg.as_string())  # 寄信
        hint = "郵件已發送！"
    except SMTPAuthenticationError:
        hint = "無法登入！"
    except SMTPException as e:
        hint = f"郵件發送產生錯誤！錯誤內容：{e}"
    finally:
        server.quit()  # 關閉連線

@captcha_required
def forget_captcha(request):
    message = ''
    if request.method == 'POST' :
        f_captcha = request.POST.get('f_captcha','')
        r_int = request.session['r_int']
        if f_captcha == r_int :
            request.session['for_captcha_verified'] = True
            return redirect('/changepw/')
        else:
            message = '驗證碼錯誤'
    return render(request,'forget_captcha.html',locals())

@for_captcha_required
def changepw(request):
    message = ''
    if request.method == 'POST' :
        form = ChangepwForm(request.POST)
        if form.is_valid():
            c_password = form.cleaned_data.get('c_password','')
            c_confirm_password = form.cleaned_data.get('c_confirm_password','')
            if c_password == c_confirm_password:
                username = request.session['f_username']
                user = User.objects.get(username=username)
                user.set_password(c_password)
                user.save()
                message = '密碼更改成功！'
                return redirect('/login/')
            else:
                message = '確認密碼錯誤'
        else:
            message = '資料有誤，請重新輸入'
    else:
        form = ChangepwForm()
    return render(request,'changepw.html',locals())


def common_login(request, user_type=''):
    type = user_type
    message = ''
    if request.method == 'POST':
        # 檢查登入表單
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # 登入
                # 根據用戶類型做不同的跳轉
                if user_type == 'seller' and user.is_superuser:
                    # 賣家登入後，跳轉到賣家儀表板
                    request.session['seller_captcha_verified'] = True
                    return redirect('/seller_manage/')
                elif user_type == 'user':
                    # 會員登入後，跳轉到主頁
                    return redirect('/index2/')
                else:
                    message = '賣家帳號密碼輸入錯誤！'
            else:
                message = '帳號或密碼錯誤！'
    else:
        form = LoginForm()

    return render(request, 'login.html',locals())



def seller_login(request):
    return common_login(request, user_type='seller')

def login(request):
    return common_login(request, user_type='user')

@seller_captcha_required
def seller_manage(request,page=None):
    page = page 
    if page == None or page == 'product':
        request.session['now_page'] = '商品管理'
        request.session['now_path'] = 'seller_manage/product'
        products = models.ProductModel.objects.all().order_by('-id')
    elif page == 'order':
        request.session['now_page'] = '訂單管理'
        request.session['now_path'] = 'seller_manage/order'
        orders  = models.OrderModel.objects.all().order_by('-id')
    elif page == 'memeber' :
        memebers = User.objects.all()
    now_page = request.session['now_page']
    now_path = request.session['now_path']
    return render(request,'seller_manage.html',locals())

@seller_captcha_required
def edit_product(request,id=None,type=None):
    message = ''
    now_page = request.session['now_page']
    now_path = request.session['now_path']
    product = models.ProductModel.objects.get(id=id)
    if request.method == 'POST' :
        product.pname = request.POST.get('name','')
        product.pprice = request.POST.get('price','')
        product.pimage = request.POST.get('image','')
        product.pdescription = request.POST.get('description','')
        product.hot = request.POST.get('hot','')
        product.save()
        message ='更改成功！'
    if type == 'delete':
        try:
            product.delete()
            return redirect('/seller_manage/product/')
        except models.ProductModel.DoesNotExist:
            return HttpResponse("指定的商品不存在。")
    return render(request, 'edit_product.html',locals())

@seller_captcha_required
def add_product(request):
    message = ''
    now_page = request.session['now_page']
    now_path = request.session['now_path']
    if request.method == 'POST' :
        name = request.POST.get('name','')
        price = request.POST.get('price','')
        image = request.POST.get('image','')
        description = request.POST.get('description','')
        product = models.ProductModel.objects.create(pname=name,pprice=price,pimage=image,pdescription=description,
                                                     hot=0)
        product.save()
        return redirect('/seller_manage/product/')
    return render(request,'add_product.html',locals())

@seller_captcha_required
def manage_order(request,id=None,type=None):
    now_page = request.session['now_page']
    now_path = request.session['now_path']
    order = models.OrderModel.objects.get(id=id)
    details = models.DetailModel.objects.filter(dorder = order)
    if type == 'delete':
        order.delete()
        return redirect('/seller_manage/order/')
    return render(request,'manage_order.html',locals())