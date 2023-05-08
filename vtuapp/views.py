import csv
import hashlib
import hmac
import json
import random
from typing import Any
import urllib.parse
import uuid
from datetime import datetime

import requests
from core.models import CustomUser
from django import forms, http
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q, Sum
from django.forms.utils import ErrorList
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str as force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.timezone import datetime as datetimex
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist


# new import for webhook
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormMixin
from notifications.signals import notify
from requests.auth import HTTPBasicAuth
from rest_framework.authtoken.models import Token
from twilio.twiml.messaging_response import MessagingResponse

from .forms import *
from .helper import get_config
from .models import *
from nelly_api.tokens import account_activation_token

# Create your views here.
def user_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)

    writer.writerow([x.Phone for x in CustomUser.objects.all()])

    return response


# convert string to JSON or Object
class PyJSON(object):
    def __init__(self, d):
        if type(d) is str:
            d = json.loads(d)

        self.from_dict(d)

    def from_dict(self, d):
        self.__dict__ = {}
        for key, value in d.items():
            if type(value) is dict:
                value = PyJSON(value)
            self.__dict__[key] = value

    def to_dict(self):
        d = {}
        for key, value in self.__dict__.items():
            if type(value) is PyJSON:
                value = value.to_dict()
            d[key] = value
        return d

    def to_json(self):
        return json.loads(json.dumps(self.__dict__))

    def __repr__(self):
        return str(self.to_dict())

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]


def create_id():
    random.randint(1, 10)
    num_2 = random.randint(1, 10)
    num_3 = random.randint(1, 10)
    return str(num_2) + str(num_3) + str(uuid.uuid4())[:4]


ident = create_id()


def sendmail(subject, message, user_email, username):
    ctx = {"message": message, "subject": subject, "username": username}
    message = get_template("email.html").render(ctx)
    msg = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
    )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()


def RetailWebFaqs(request):
    faq_question = RetailWebFrequentlyAskedQuestion.objects.order_by("pk")
    context = {"question": faq_question}
    return render(request, "faq2.html", context)


class KYCCreate(generic.CreateView):
    form_class = KYCForm
    template_name = "kyc_form.html"

    def form_valid(self, form):
        form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
            ["use updated browser and retry"]
        )
        return self.form_invalid(form)

        return super(KYCCreate, self).form_valid(form)


# whatappp bot


@require_POST
@csrf_exempt
def replybot(request):
    text1 = request.POST.get("Body")
    response = MessagingResponse()

    if "log_in" not in request.session:
        request.session["log_in"] = False
        # print(request.session["log_in"], "ww2222")

    elif True:
        # print(request.session["log_in"], "ww223333333322")

        response.message(
            "Welcome to MsorgSMEBOT enter your username and password seperate with comma to start i.e musa,12345"
        )
        # request.session["level"] = request.session["level"] + 1

        if "," not in text1:
            # response = MessagingResponse()
            response.message(
                "Please enter your username and password seperate with comma to start i.e musa,12345"
            )

        else:
            username = text1.split(",")[0]
            password = text1.split(",")[1]

            headers = {"Content-Type": "application/json"}
            url = "https://www.IMCdata.com/rest-auth/login/"
            data = {"username": username, "password": password}
            c = requests.post(url, data=json.dumps(data), headers=headers)
            a = json.loads(c.text)

            if "key" in a:
                response = MessagingResponse()
                response.message("Login successful")
                request.session["log_in"] = True

                # request.session["log_in"] = True

            else:
                response = MessagingResponse()
                response.message("Unable to log in with provided credentials.")

    if request.session["log_in"] is True:
        # print(request.session["log_in"], "ww2233333tuyuyyu33322")

        response = MessagingResponse()
        response.message(
            "Welcome back {0}\n 1.Buy Data \n2.Buy Airtime \n3.Cable subscription \n4.Bill payment".format(
                username
            )
        )
        if text1 == "1":
            response = MessagingResponse()
            response.message("data")
        elif text1 == "2":
            response = MessagingResponse()
            response.message("airtime")
        elif text1 == "3":
            response = MessagingResponse()
            response.message("cable")
        elif text1 == "4":
            response = MessagingResponse()
            response.message("bill")

    return HttpResponse(response)


def selfCenter(request):
    if request.is_ajax():
        transaction_type = request.GET["type"]
        reference = request.GET["ref"]

        status = False
        receipt_id = None

        if transaction_type.upper() == "AIRTIME":
            qs = AirtimeTopup.objects.filter(ident=reference, user=request.user)
            if qs.exists():
                resp = "well done hameed"
                status = True
                receipt_id = qs.first().id
            else:
                resp = f"Airtime TopUp Transaction matching query(id: {reference}) does not exist"

        elif transaction_type.upper() == "DATA":
            qs = Data.objects.filter(ident=reference, user=request.user)
            if qs.exists():
                resp = "well done hameed"
                status = True
                receipt_id = qs.first().id
            else:
                resp = (
                    f"Data Transaction matching query(id: {reference}) does not exist"
                )

        elif transaction_type.upper() == "CABLE":
            qs = Cablesub.objects.filter(ident=reference, user=request.user)
            if qs.exists():
                resp = "weldone hameed"
                status = True
                receipt_id = qs.first().id
            else:
                resp = f"Cable Subscription Transaction matching query(id: {reference}) does not exist"

        elif transaction_type.upper() == "BILL":
            qs = Billpayment.objects.filter(ident=reference, user=request.user)
            if qs.exists():
                resp = "weldone hameed"
                status = True
                receipt_id = qs.first().id
            else:
                resp = f"Bill Payment Transaction matching query(id: {reference}) does not exist"
        else:
            resp = f"Transaction matching query(id: {reference}) does not exist"

        data = {"message": resp, "valid": status, "id": receipt_id}
        return JsonResponse(data)

    else:
        return render(request, "selfhelp.html")


def Faqs(request):
    faq_question = frequentlyAskedQuestion.objects.order_by("pk")
    context = {"question": faq_question}
    return render(request, "faq.html", context)


class TopuserWebsiteview(generic.CreateView):
    form_class = TopuserWebsiteForm
    template_name = "website.html"
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        if object.SSL_Security is True:
            amount = 50000
        else:
            amount = 50000
            object.SSL_Security = True
        object.amount = amount

        if amount > object.user.Account_Balance:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["insufficient balance"]
            )
            return self.form_invalid(form)

        else:
            withdraw = object.user.withdraw(object.user.id, amount)
            if withdraw is False:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["insufficient balance"]
                )
                return self.form_invalid(form)

            object.user.user_type = "TopUser"

            object.user.save()
            try:
                # Upgrade_user.objects.create(user=request.user,from_package=p_level,to_package="Affilliate",amount ="2000",previous_balance = previous_bal, after_balance= (previous_bal - 2000))
                if object.user.referer_username:
                    if CustomUser.objects.filter(
                        username__iexact=object.user.referer_username
                    ).exists():
                        CustomUser.objects.get(
                            username__iexact=object.user.referer_username
                        )
                        # referer.ref_deposit(2000)
                        # notify.send(referer, recipient=referer, verb='N2000 TopUser Upgarde Bonus from  {} your referal has been added to your referal bonus wallet'.format(
                        #     object.user.username))

            except:
                pass
            messages.success(
                self.request,
                "Your website order has submitted successful will contact you when the website is ready",
            )
            WalletSummary.objects.create(
                user=object.user,
                product="Affillite Website  ",
                amount=amount,
                previous_balance=object.user.Account_Balance,
                after_balance=object.user.Account_Balance - amount,
            )

        form.save()

        return super(TopuserWebsiteview, self).form_valid(form)


def Affilliate(request):
    message = ""
    amt_to_pay = float(get_config().affiliate_upgrade_fee)
    upline_bonus = float(get_config().affiliate_referral_bonus)
    if amt_to_pay > request.user.Account_Balance:
        message = " Insufficient Balance please fund your wallet and try to upgrade"

    else:
        previous_bal = request.user.Account_Balance
        p_level = request.user.user_type
        request.user.user_type = "Affilliate"
        request.user.save()
        withdraw = request.user.withdraw(request.user.id, float(amt_to_pay))
        if withdraw is False:
            message = " Insufficient Balance please fund your wallet and try to upgrade"

        try:
            Upgrade_user.objects.create(
                user=request.user,
                from_package=p_level,
                to_package="Affilliate",
                amount=f"{amt_to_pay}",
                previous_balance=previous_bal,
                after_balance=(previous_bal - amt_to_pay),
            )
            if request.user.referer_username:
                if CustomUser.objects.filter(
                    username__iexact=request.user.referer_username
                ).exists():
                    referer = CustomUser.objects.get(
                        username__iexact=request.user.referer_username
                    )
                    referer.ref_deposit(upline_bonus)
                    notify.send(
                        referer,
                        recipient=referer,
                        verb=f"N{upline_bonus} Affilliate Upgarde Bonus from  {request.user.username} your referal has been added to your referal bonus wallet",
                    )

        except:
            pass

        message = f"Your account has beeen succesfully upgraded from {p_level} to Affilliate package, balance before upgrade N{previous_bal} and balance after upgrade N{previous_bal - amt_to_pay}"
        WalletSummary.objects.create(
            user=object.user,
            product=f"Your account has beeen succesfully upgraded from {p_level} to Affilliate package, balance before upgrade N{previous_bal} and balance after upgrade N{previous_bal - amt_to_pay}",
            amount=amt_to_pay,
            previous_balance=previous_bal,
            after_balance=previous_bal - amt_to_pay,
        )

    data = {
        "message": message,
    }
    return JsonResponse(data)


def Topuser(request):
    message = ""
    if request.user.user_type == "Affilliate":
        amt_to_withdraw = float(get_config().affiliate_to_topuser_upgrade_fee)
        upline_bonus = float(get_config().affiliate_to_topuser_referral_bonus)
    else:
        amt_to_withdraw = float(get_config().topuser_upgrade_fee)
        upline_bonus = float(get_config().topuser_referral_bonus)

    if amt_to_withdraw > request.user.Account_Balance:
        message = " Insufficient Balance please fund your wallet and try to upgrade"

    else:
        previous_bal = request.user.Account_Balance
        p_level = request.user.user_type
        request.user.user_type = "TopUser"
        request.user.save()

        withdraw = request.user.withdraw(request.user.id, amt_to_withdraw)

        if withdraw is False:
            message = " Insufficient Balance please fund your wallet and try to upgrade"

        try:
            Upgrade_user.objects.create(
                user=request.user,
                from_package=p_level,
                to_package="Topuser",
                amount=f"{amt_to_withdraw}",
                previous_balance=previous_bal,
                after_balance=(previous_bal - amt_to_withdraw),
            )
            if request.user.referer_username:
                if CustomUser.objects.filter(
                    username__iexact=request.user.referer_username
                ).exists():
                    referer = CustomUser.objects.get(
                        username__iexact=request.user.referer_username
                    )
                    referer.ref_deposit(upline_bonus)
                    notify.send(
                        referer,
                        recipient=referer,
                        verb=f"N{upline_bonus} TopUser Upgarde Bonus from  {request.user.username} your referal has been added to your referal bonus wallet",
                    )
        except:
            pass

        message = f"Your account has beeen succesfully upgraded from {p_level} to Topuser package, balance before upgrade N{previous_bal} and balance after upgrade N{previous_bal - amt_to_withdraw}"
        WalletSummary.objects.create(
            user=object.user,
            product=f"Your account has beeen succesfully upgraded from {p_level} to Topuser package, balance before upgrade N{previous_bal} and balance after upgrade N{previous_bal - amt_to_withdraw}",
            amount=amt_to_withdraw,
            previous_balance=previous_bal,
            after_balance=previous_bal - amt_to_withdraw,
        )

    data = {
        "message": message,
    }
    return JsonResponse(data)


def Paymentpage(request):

    options = ["Bankpayment", "Monnfy bank", "Monnify ATM", "paystack", "Airtime_Funding"]
    results = []

    for item in options:
        dis_obj = Disable_Service.objects.filter(service = item ).first()
        if dis_obj:
            results.append(dis_obj.disable)
        else:
            results.append(False)



    return render(
        request,
        "pamentpage.html",
        context={
            "bank": results[0],
            "monnifybank": results[1],
            "monnifyatm": results[2],
            "paystack": results[3],
            "air2cash": results[4],
        },
    )


class referalView(TemplateView):
    template_name = "referal.html"

    def get_context_data(self, **kwargs):
        context = super(referalView, self).get_context_data(**kwargs)
        context["referal"] = Referal_list.objects.filter(user=self.request.user)
        context["referal_total"] = Referal_list.objects.filter(
            user=self.request.user
        ).count()

        # get current month
        import datetime

        today = datetime.date.today()
        current_month = today.month
        # get current month

        context["month_leader_board"] = Referal_list.objects.filter(
            referal_user__date_joined__month=current_month
        )

        return context


def monnifypage(request):
    return render(
        request,
        "bankpage.html",
        context={
            "bankname": request.user.reservedbankName,
            "banknumber": request.user.reservedaccountNumber,
        },
    )


class PostList(generic.ListView):
    template_name = "blog.html"
    paginate_by = 5
    queryset = Post.objects.filter(status=1).order_by("-created_on")
    context_object_name = "post_list"
    model = Post


class PostDetail(generic.DetailView):
    model = Post
    template_name = "post_detail.html"


class Postcreateview((generic.CreateView)):
    form_class = Postcreate
    template_name = "post_create.html"

    def form_valid(self, form):
        object = form.save(commit=False)
        object.author = self.request.user

        form.save()

        return super(Postcreateview, self).form_valid(form)


class Post_Edit(generic.UpdateView):
    form_class = Postcreate
    template_name = "post_create.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.all()


class History(TemplateView):
    template_name = "history.html"

    def get_context_data(self, **kwargs):
        context = super(History, self).get_context_data(**kwargs)
        context["airtime"] = Airtime.objects.filter(user=self.request.user).order_by(
            "-create_date"
        )
        context["withdraw"] = Withdraw.objects.filter(user=self.request.user).order_by(
            "-create_date"
        )
        context["data"] = Data.objects.filter(user=self.request.user).order_by(
            "-create_date"
        )
        context["airtimeswap"] = Airtimeswap.objects.filter(
            user=self.request.user
        ).order_by("-create_date")
        context["airtimeTopup"] = AirtimeTopup.objects.filter(
            user=self.request.user
        ).order_by("-create_date")
        context["transfer"] = Transfer.objects.filter(user=self.request.user).order_by(
            "-create_date"
        )
        context["Airtime_funding"] = Airtime_funding.objects.filter(
            user=self.request.user
        ).order_by("-create_date")
        context["CouponPayment"] = CouponPayment.objects.filter(
            user=self.request.user
        ).order_by("-create_date")
        context["Cablesub"] = Cablesub.objects.filter(user=self.request.user).order_by(
            "-create_date"
        )
        context["bank"] = Bankpayment.objects.filter(user=self.request.user).order_by(
            "-create_date"
        )
        context["bulk"] = Bulk_Message.objects.filter(user=self.request.user).order_by(
            "-create_date"
        )
        context["bill"] = Billpayment.objects.filter(user=self.request.user).order_by(
            "-create_date"
        )
        context["paystact"] = paymentgateway.objects.filter(
            user=self.request.user
        ).order_by("-created_on")
        context["Result_Checker"] = Result_Checker_Pin_order.objects.filter(
            user=self.request.user
        ).order_by("-create_date")
        context["epin"] = Recharge_pin_order.objects.filter(
            user=self.request.user
        ).order_by("-create_date")

        return context


def Data_History_new(request):
    search = request.GET.get("q", None)

    if search:
        transactionslist = (
            Data.objects.filter(user=request.user)
            .filter(
                Q(id__icontains=search)
                | Q(ident__icontains=search)
                | Q(mobile_number__icontains=search)
                | Q(Status__icontains=search)
            )
            .order_by("-create_date")
        )

    else:
        transactionslist = Data.objects.filter(user=request.user).order_by(
            "-create_date"
        )

    page = request.GET.get("page", 1)
    paginator = Paginator(transactionslist, 20)
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    return render(
        request,
        "data_history_new.html",
        {
            "search": search,
            "transactions": transactions,
        },
    )


class WalletSummaryView(TemplateView):
    template_name = "wallet.html"

    def get_context_data(self, **kwargs):
        context = super(WalletSummaryView, self).get_context_data(**kwargs)
        context["wallet"] = WalletSummary.objects.filter(
            user=self.request.user
        ).order_by("-create_date")

        return context


class UserHistory(TemplateView):
    template_name = "userhistory.html"

    def get_context_data(self, **kwargs):
        query = self.request.GET.get("q")

        if CustomUser.objects.filter(username__iexact=query).exists():
            user_h = CustomUser.objects.get(username__iexact=query)
            context = super(UserHistory, self).get_context_data(**kwargs)
            context["user"] = user_h
            context["airtime"] = Airtime.objects.filter(user=user_h).order_by(
                "-create_date"
            )
            context["withdraw"] = Withdraw.objects.filter(user=user_h).order_by(
                "-create_date"
            )
            context["data"] = Data.objects.filter(user=user_h).order_by("-create_date")
            context["airtimeswap"] = Airtimeswap.objects.filter(user=user_h).order_by(
                "-create_date"
            )
            context["airtimeTopup"] = AirtimeTopup.objects.filter(user=user_h).order_by(
                "-create_date"
            )
            context["transfer"] = Transfer.objects.filter(user=user_h).order_by(
                "-create_date"
            )
            context["Airtime_funding"] = Airtime_funding.objects.filter(
                user=user_h
            ).order_by("-create_date")
            context["CouponPayment"] = CouponPayment.objects.filter(
                user=user_h
            ).order_by("-create_date")
            context["Cablesub"] = Cablesub.objects.filter(user=user_h).order_by(
                "-create_date"
            )
            context["bank"] = Bankpayment.objects.filter(user=user_h).order_by(
                "-create_date"
            )
            context["bulk"] = Bulk_Message.objects.filter(user=user_h).order_by(
                "-create_date"
            )
            context["bill"] = Billpayment.objects.filter(user=user_h).order_by(
                "-create_date"
            )
            context["paystact"] = paymentgateway.objects.filter(user=user_h).order_by(
                "-created_on"
            )
            context["Result_Checker"] = Result_Checker_Pin_order.objects.filter(
                user=user_h
            ).order_by("-create_date")
            context["epin"] = Recharge_pin_order.objects.filter(user=user_h).order_by(
                "-create_date"
            )

            return context


def sendmessage(sender, message, to, route):
    baseurl = f"https://sms.hollatags.com/api/send/?user={get_config().hollatag_username}&pass={get_config().hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}"
    requests.get(baseurl, verify=False)
    # print('---------- sneding to HOLLTAGS')
    # print(f'baseurl = {baseurl}')
    # print('')
    # print(f'response = {response.text}')


class ApiDoc(TemplateView):
    template_name = "swagger-ui.html"

    def get_context_data(self, **kwargs):
        context = super(ApiDoc, self).get_context_data(**kwargs)
        context["plans"] = Plan.objects.all()
        context["network"] = Network.objects.all()
        context["cableplans"] = CablePlan.objects.all()
        context["cable"] = Cable.objects.all()
        context["disco"] = Disco_provider_name.objects.all()

        if Token.objects.filter(user=self.request.user).exists():
            context["token"] = Token.objects.get(user=self.request.user)
        else:
            Token.objects.create(user=self.request.user)
            context["token"] = Token.objects.get(user=self.request.user)

        return context


class WelcomeView(TemplateView):
    template_name = "index.html"

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        #Calling config before the view loads to create a webconfig if it does not already exist
        #This is only useful when the website is loaded for the very first time on a new database.
        get_config()
        return super().dispatch(request, *args, **kwargs)
    
    def referal_user(self):
        if self.request.GET.get("referal"):
            self.request.session["referal"] = self.request.GET.get("referal")
            # print(self.request.session["referal"])
            # print("sessin set")

    def get_context_data(self, **kwargs):
        context = super(WelcomeView, self).get_context_data(**kwargs)

        networks = {
            "MTN": "plan",
            "GLO": "plan_2",
            "9MOBILE": "plan_3",
            "AIRTEL": "plan_4"
        }

        for network_name, context_key in networks.items():
            network = Network.objects.filter(name=network_name).first()
            if network:
                context[context_key] = Plan.objects.filter(network=network).order_by("plan_amount")

        context["networks"] = Network.objects.all()
        context["book1"] = Book.objects.all().order_by("-created_at")[:10]
        context["book2"] = Book.objects.all().order_by("-created_at")[:6]
        context["post_list1"] = Post.objects.all().order_by("-created_on")[:10]
        context["ref"] = self.referal_user()

        return context


class PricingView(TemplateView):
    template_name = "pricing.html"

    def get_context_data(self, **kwargs):
        context = super(PricingView, self).get_context_data(**kwargs)

        networks = {
            "MTN": "plan",
            "GLO": "plan_2",
            "9MOBILE": "plan_3",
            "AIRTEL": "plan_4"
        }

        for network_name, context_key in networks.items():
            network = Network.objects.filter(name=network_name).first()
            if network:
                context[context_key] = Plan.objects.filter(network=network).order_by("plan_amount")

        context["airtime"] = TopupPercentage.objects.all()
        context["result_checker"] = Result_Checker_Pin.objects.all()
        context["recharge"] = Recharge.objects.all()

        return context


class Profile(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        current_month = datetime.datetime.now().month
        net = Network.objects.filter(name="MTN").first()
        net_2 = Network.objects.filter(name="GLO").first()
        net_3 = Network.objects.filter(name="9MOBILE").first()
        net_4 = Network.objects.filter(name="AIRTEL").first()
        # (network=net,plan__plan_size__lt=100,create_date__month= current_month)
        data_mtn_obj = Data.objects.filter(
            network=net, plan__plan_size__lt=60, create_date__month=current_month
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        data_mtn_obj_2 = Data.objects.filter(
            network=net, plan__plan_size__gt=60, create_date__month=current_month
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        data_glo_obj = Data.objects.filter(
            network=net_2, plan__plan_size__lt=60, create_date__month=current_month
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        data_glo_obj_2 = Data.objects.filter(
            network=net_2, plan__plan_size__gt=60, create_date__month=current_month
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        data_9mobile_obj = Data.objects.filter(
            network=net_3, plan__plan_size__lt=60, create_date__month=current_month
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        data_9mobile_obj_2 = Data.objects.filter(
            network=net_3, plan__plan_size__gt=60, create_date__month=current_month
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        data_airtel_obj = Data.objects.filter(
            network=net_4, plan__plan_size__lt=60, create_date__month=current_month
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        data_airtel_obj_2 = Data.objects.filter(
            network=net_4, plan__plan_size__gt=60, create_date__month=current_month
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        total_wallet = CustomUser.objects.all().aggregate(Sum("Account_Balance"))[
            "Account_Balance__sum"
        ]
        total_bonus = CustomUser.objects.all().aggregate(Sum("Referer_Bonus"))[
            "Referer_Bonus__sum"
        ]
        bill_obj = Billpayment.objects.filter(
            create_date__month=current_month
        ).aggregate(Sum("amount"))["amount__sum"]
        cable_obj = Cablesub.objects.filter(create_date__month=current_month).aggregate(
            Sum("plan_amount")
        )["plan_amount__sum"]
        Topup_obj1 = AirtimeTopup.objects.filter(
            network=net, create_date__month=current_month
        ).aggregate(Sum("amount"))["amount__sum"]
        Topup_obj2 = AirtimeTopup.objects.filter(
            network=net_2, create_date__month=current_month
        ).aggregate(Sum("amount"))["amount__sum"]
        Topup_obj3 = AirtimeTopup.objects.filter(
            network=net_3, create_date__month=current_month
        ).aggregate(Sum("amount"))["amount__sum"]
        Topup_obj4 = AirtimeTopup.objects.filter(
            network=net_4, create_date__month=current_month
        ).aggregate(Sum("amount"))["amount__sum"]
        bank_obj = Bankpayment.objects.filter(
            Status="successful", create_date__month=current_month
        ).aggregate(Sum("amount"))["amount__sum"]
        atm_obj = paymentgateway.objects.filter(
            Status="successful", created_on__month=current_month
        ).aggregate(Sum("amount"))["amount__sum"]
        pin_obj = Airtime.objects.filter(
            Status="successful", create_date__month=current_month
        ).aggregate(Sum("amount"))["amount__sum"]
        Airtime_funding.objects.filter(
            Status="successful", create_date__month=current_month
        ).aggregate(Sum("amount"))["amount__sum"]
        coupon_obj = (
            CouponPayment.objects.all()
            .filter(create_date__month=current_month)
            .aggregate(Sum("amount"))["amount__sum"]
        )
        try:

            def create_id():
                random.randint(1, 10)
                num_2 = random.randint(1, 10)
                num_3 = random.randint(1, 10)
                return str(num_2) + str(num_3) + str(uuid.uuid4())[:4]

            body = {
                "accountReference": create_id(),
                "accountName": self.request.user.username,
                "currencyCode": "NGN",
                "contractCode": f"{get_config().monnify_contract_code}",
                "customerEmail": self.request.user.email,
                "incomeSplitConfig": [],
                "restrictPaymentSource": False,
                "allowedPaymentSources": {},
                "customerName": self.request.user.username,
                "getAllAvailableBanks": True,
            }

            if not self.request.user.reservedaccountNumber:
                data = json.dumps(body)
                ad = requests.post(
                    "https://api.monnify.com/api/v1/auth/login",
                    auth=HTTPBasicAuth(
                        f"{get_config().monnify_API_KEY}",
                        f"{get_config().monnify_SECRET_KEY}",
                    ),
                )
                mydata = json.loads(ad.text)

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(
                        mydata["responseBody"]["accessToken"]
                    ),
                }
                ab = requests.post(
                    "https://api.monnify.com/api/v1/bank-transfer/reserved-accounts",
                    headers=headers,
                    data=data,
                )

                mydata = json.loads(ab.text)

                user = self.request.user

                user.reservedaccountNumber = mydata["responseBody"]["accountNumber"]
                user.reservedbankName = mydata["responseBody"]["bankName"]
                user.reservedaccountReference = mydata["responseBody"][
                    "accountReference"
                ]
                user.save()

            if not self.request.user.accounts:
                data = json.dumps(body)
                ad = requests.post(
                    "https://api.monnify.com/api/v1/auth/login",
                    auth=HTTPBasicAuth(
                        f"{get_config().monnify_API_KEY}",
                        f"{get_config().monnify_SECRET_KEY}",
                    ),
                )
                mydata = json.loads(ad.text)

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(
                        mydata["responseBody"]["accessToken"]
                    ),
                }
                ab = requests.post(
                    "https://api.monnify.com/api/v2/bank-transfer/reserved-accounts",
                    headers=headers,
                    data=data,
                )

                mydata = json.loads(ab.text)

                user = CustomUser.objects.get(id=self.request.user.id)

                user.reservedaccountNumber = mydata["responseBody"]["accounts"][0][
                    "accountNumber"
                ]
                user.reservedbankName = mydata["responseBody"]["accounts"][0][
                    "bankName"
                ]
                user.reservedaccountReference = mydata["responseBody"][
                    "accountReference"
                ]
                user.accounts = json.dumps(
                    {"accounts": mydata["responseBody"]["accounts"]}
                )
                user.save()

            else:
                pass

        except:
            pass

        context = super(Profile, self).get_context_data(**kwargs)
        context["airtime"] = Airtime.objects.filter(Status="processing").count()
        context["withdraw"] = Withdraw.objects.filter(Status="processing").count()
        context["data"] = Data.objects.filter(Status="processing").count()
        context["airtimeswap"] = Airtimeswap.objects.filter(Status="processing").count()
        context["airtimeTopup"] = AirtimeTopup.objects.filter(
            Status="processing"
        ).count()
        context["transfer"] = Transfer.objects.filter(Status="processing").count()
        context["Airtime_funding"] = Airtime_funding.objects.filter(
            Status="processing"
        ).count()
        context["CouponPayment"] = CouponPayment.objects.filter(
            Status="processing"
        ).count()
        context["unusedcoupon"] = Couponcode.objects.filter(Used=False).count()
        context["usedcoupon"] = Couponcode.objects.filter(Used=True).count()
        context["bank"] = Bankpayment.objects.filter(Status="processing").count()
        context["cable"] = Cablesub.objects.filter(Status="processing").count()

        try:
            if data_mtn_obj_2:
                context["totalmtnsale"] = data_mtn_obj + (data_mtn_obj_2 / 1000)
            else:
                context["totalmtnsale"] = data_mtn_obj
            if data_glo_obj_2:
                context["totalglosale"] = data_glo_obj + (data_glo_obj_2 / 1000)
            else:
                context["totalglosale"] = data_glo_obj

            if data_airtel_obj_2:
                context["totalairtelsale"] = data_airtel_obj + (
                    data_airtel_obj_2 / 1000
                )

            else:
                context["totalairtelsale"] = data_airtel_obj
            if data_9mobile_obj_2:
                context["totalmobilesale"] = data_9mobile_obj + (
                    data_9mobile_obj_2 / 1000
                )
            else:
                context["totalmobilesale"] = data_9mobile_obj
        except:
            pass
        context["banktotal"] = bank_obj
        context["atmtotal"] = atm_obj
        context["coupontotal"] = coupon_obj
        context["airtimetotal"] = pin_obj
        context["Noti"] = self.request.user.notifications.all()[:1]
        context["twallet"] = round(total_wallet, 2)
        context["tbonus"] = round(total_bonus, 2)
        context["alert"] = Info_Alert.objects.all()[:1]
        context["transactions"] = Transactions.objects.all()[:1]
        context["wallet"] = WalletSummary.objects.filter(
            user=self.request.user
        ).order_by("-create_date")
        context["users"] = CustomUser.objects.all().count()
        context["referral"] = (
            Referal_list.objects.filter(user=self.request.user).all().count()
        )
        context["Billpayment_obj"] = bill_obj
        context["cable"] = cable_obj
        context["AirtimeTopup_obj"] = Topup_obj1
        context["AirtimeTopup_obj2"] = Topup_obj2
        context["AirtimeTopup_obj3"] = Topup_obj3
        context["AirtimeTopup_obj4"] = Topup_obj4

        context["verify"] = KYC.objects.filter(user=self.request.user).last()

        context["total_wallet_fund"] = (
            WalletFunding.objects.filter(user=self.request.user).aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )
        context["total_amount_spent"] = (
            Transactions.objects.filter(
                user=self.request.user, transaction_type="DEBIT"
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        return context


def monnify_payment(request):
    if request.method == "POST":
        form = monnify_payment_form(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            username = request.user.username
            email = request.user.email

            amount = (amount) + (0.015 * amount)

            headers = {
                "Content-Type": "application/json",
            }

            def create_id():
                random.randint(1, 10)
                num_2 = random.randint(1, 10)
                num_3 = random.randint(1, 10)
                return str(num_2) + str(num_3) + str(uuid.uuid4())

            ab = {
                "amount": amount,
                "customerName": username,
                "customerEmail": email,
                "paymentReference": create_id(),
                "paymentDescription": "Wallet Funding",
                "currencyCode": "NGN",
                "contractCode": f"{get_config().monnify_contract_code}",
                "paymentMethods": ["CARD"],
                "redirectUrl": "https://www.legitdata.com.ngprofile",
                "incomeSplitConfig": [],
            }
            data = json.dumps(ab)

            response = requests.post(
                "https://api.monnify.com/api/v1/merchant/transactions/init-transaction",
                headers=headers,
                data=data,
                auth=HTTPBasicAuth(
                    f"{get_config().monnify_API_KEY}",
                    f"{get_config().monnify_SECRET_KEY}",
                ),
            )

            loaddata = json.loads(response.text)
            url = loaddata["responseBody"]["checkoutUrl"]

            # print(username, email, phone)

            return HttpResponseRedirect(url)

    else:
        form = monnify_payment_form()

    return render(request, "monnify.html", {"form": form})


@require_POST
@csrf_exempt
# @require_http_methods(["GET", "POST"])
def monnify_payment_done(request):
    # secret = b'sk_live_627a99148869d929fdad838a74996891f5b660b5'
    payload = request.body

    # forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
    forwarded_for = "{}".format(request.META.get("REMOTE_ADDR"))

    dat = json.loads(payload)
    a = "{}|{}|{}|{}|{}".format(
        get_config().monnify_SECRET_KEY,
        dat["paymentReference"],
        dat["amountPaid"],
        dat["paidOn"],
        dat["transactionReference"],
    )
    # print(forwarded_for)
    c = bytes(a, "utf-8")
    hashkey = hashlib.sha512(c).hexdigest()
    if hashkey == dat["transactionHash"] and forwarded_for == "35.242.133.146":
        # print("correct")
        # print("IP whilelisted")
        response = requests.get(
            "https://api.monnify.com/api/v1/merchant/transactions/query?paymentReference={}".format(
                dat["paymentReference"]
            ),
            auth=HTTPBasicAuth(
                f"{get_config().monnify_API_KEY}", f"{get_config().monnify_SECRET_KEY}"
            ),
        )
        # print(response.text)
        ab = json.loads(response.text)

        if (response.status_code == 200 and ab["requestSuccessful"] is True) and (
            ab["responseMessage"] == "success"
            and ab["responseBody"]["paymentStatus"] == "PAID"
        ):
            user = dat["customer"]["email"]
            mb = CustomUser.objects.get(email__iexact=user)
            amount = ab["responseBody"]["amount"]
            fee = ab["responseBody"]["fee"]

            if ab["responseBody"]["paymentMethod"] == "CARD":
                paynow = round(amount - fee)

            else:
                # paynow = (round(amount - 50))
                paynow = amount - (round(amount * 0.01))
            ref = dat["paymentReference"]
            # print("hoooooook paid")

            if not paymentgateway.objects.filter(reference=ref).exists():
                try:
                    previous_bal = mb.Account_Balance
                    mb.deposit(mb.id, paynow, False, "Monnify Funding")
                    paymentgateway.objects.create(
                        user=mb,
                        reference=ref,
                        amount=paynow,
                        Status="successful",
                        gateway="monnify",
                    )
                    WalletSummary.objects.create(
                        user=mb,
                        product=" N{} Monnify Funding ".format(paynow),
                        amount=paynow,
                        previous_balance=previous_bal,
                        after_balance=(previous_bal + paynow),
                    )
                    notify.send(
                        mb,
                        recipient=mb,
                        verb="Monnify Payment successful you account has been credited with sum of #{}".format(
                            paynow
                        ),
                    )
                except:
                    return HttpResponse(status=200)

            else:
                pass

        else:
            messages.error(
                request,
                "Our payment gateway return Payment tansaction failed status {}".format(
                    ab["message"]
                ),
            )

    else:
        return HttpResponseForbidden("Permission denied.")
    # print("after monnify hook")
    return HttpResponse(status=200)


@require_POST
@csrf_exempt
def UWS_Webhook(request):
    data = request.body
    "{}".format(request.META.get("HTTP_X_FORWARDED_FOR"))
    result = json.loads(data)

    # print(' ')
    # print('................RECIEVED FROM UWS HOOK................')
    # print(forwarded_for)
    # print("result = ", result)

    # {'status': 'success', 'data': {'transId': 'sme-2776663', 'customRef': 'dt9984632', 'transactionMessage': 'Data Purchase Successful'}}
    # {"status":"failed", "data": {"transId":"sm-230221122249", "customRef":"DT-788b4", "transactionMessage":"Data Purchase Failed"}}

    ident = result["data"]["customRef"]

    # try:
    trans = Data.objects.filter(ident=ident).first()
    if trans:
        if trans.Status != "successful" and result["status"] == "failed":
            api_msg = f"customRef({ident}) is valid, refund complete"

            trans.Status == "failed"
            trans.save()

        else:
            api_msg = f"{ident} was successful"

    else:
        api_msg = f"customRef({ident}) not found"
        print(f"customRef({ident}) not found")

    # except:
    #     print('transaction not found')
    #     api_msg = "unable to handle request, maintenanace mode"

    return JsonResponse(
        {"status": "connection successful", "message": f"{api_msg}"}, status=200
    )


class TestimonialView(generic.ListView):
    template_name = "Testimonial.html"
    paginate_by = 3
    queryset = Testimonial.objects.all().order_by("-create_date")
    context_object_name = "testimonial"
    model = Testimonial


class TestimonialCreate(generic.CreateView):
    form_class = Testimonialform
    template_name = "testimonialform.html"
    success_url = reverse_lazy("Testimonials")

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        form.save()

        return super(TestimonialCreate, self).form_valid(form)


class Testimonial_Detail(generic.DetailView):
    model = Testimonial
    template_name = "Testimonialdetail.html"
    queryset = Testimonial.objects.all()
    context_object_name = "testimonial"


class Result_Checker_Pin_order_view(generic.CreateView):
    form_class = Result_Checker_Pin_order_form
    template_name = "resultchecker.html"

    def get_context_data(self, **kwargs):
        context = super(Result_Checker_Pin_order_view, self).get_context_data(**kwargs)
        if self.request.user.user_type == "Affilliate":
            context["amt1"] = Result_Checker_Pin.objects.get(
                exam_name="WAEC"
            ).Affilliate_price
            context["amt2"] = Result_Checker_Pin.objects.get(
                exam_name="NECO"
            ).Affilliate_price
            # context['amt3'] = Result_Checker_Pin.objects.get(exam_name="NABTEB").Affilliate_price

        elif self.request.user.user_type == "TopUser":
            context["amt1"] = Result_Checker_Pin.objects.get(
                exam_name="WAEC"
            ).TopUser_price
            context["amt2"] = Result_Checker_Pin.objects.get(
                exam_name="NECO"
            ).TopUser_price
            # context['amt3'] = Result_Checker_Pin.objects.get(exam_name="NABTEB").TopUser_price

        elif self.request.user.user_type == "API":
            context["amt1"] = Result_Checker_Pin.objects.get(exam_name="WAEC").api_price
            context["amt2"] = Result_Checker_Pin.objects.get(exam_name="NECO").api_price
            # context['amt3'] = Result_Checker_Pin.objects.get(exam_name="NABTEB").api_price
        else:
            context["amt1"] = Result_Checker_Pin.objects.get(exam_name="WAEC").amount
            context["amt2"] = Result_Checker_Pin.objects.get(exam_name="NECO").amount
            # context['amt3'] = Result_Checker_Pin.objects.get(exam_name="NABTEB").amount

        return context


class Result_Checker_Pin_order_success(generic.DetailView):
    model = Result_Checker_Pin_order
    template_name = "resultchecker_success.html"
    context_object_name = "resultchecker"

    def get_queryset(self):
        return Result_Checker_Pin_order.objects.filter(user=self.request.user)


############### Recharge card #printing ######################


class Recharge_pin_order_view(generic.CreateView):
    form_class = Recharge_Pin_order_form
    template_name = "rechargepin.html"

    def get_context_data(self, **kwargs):
        context = super(Recharge_pin_order_view, self).get_context_data(**kwargs)

        net = Network.objects.filter(name="MTN").first()
        net_2 = Network.objects.filter(name="GLO").first()
        net_3 = Network.objects.filter(name="9MOBILE").first()
        net_4 = Network.objects.filter(name="AIRTEL").first()

        context["amt1"] = (
            Recharge_pin.objects.filter(network=net)
            .filter(available=True)
            .count()
        )
        context["amt2"] = (
            Recharge_pin.objects.filter(network=net_2)
            .filter(available=True)
            .count()
        )
        context["amt3"] = (
            Recharge_pin.objects.filter(network=net_4)
            .filter(available=True)
            .count()
        )
        context["amt4"] = (
            Recharge_pin.objects.filter(network=net_3)
            .filter(available=True)
            .count()
        )

        return context


class Recharge_pin_order_success(generic.DetailView):
    model = Recharge_pin_order
    template_name = "rechargepin_success.html"
    context_object_name = "rechargepin"

    def get_queryset(self):
        return Recharge_pin_order.objects.filter(user=self.request.user)


def loadrechargeplans(request):
    network_id = request.GET.get("network")
    plans = Recharge.objects.filter(network=network_id).order_by("amount")

    # print(plans)
    return render(request, "rechargelist.html", {"plans": plans})


class TestimonialReply(generic.CreateView):
    form_class = Commentform
    template_name = "TestimonialReply.html"
    success_url = reverse_lazy("testimonial")

    def form_valid(self, form, *args, **kwargs):
        object = form.save(commit=False)
        test = get_object_or_404(Testimonial, pk=kwargs["pk"])
        object.testimonial = test
        form.save()

        return super(TestimonialReply, self).form_valid(form)


"""
   def form_valid(self,form,request,pk):
        testim =  get_object_or_404(Testimonial ,pk = pk)
        object = form.save(commit=False)
        object.testimonial = testim
        form.save()

        return super(TestimonialReply,self).form_valid(form)
"""


def add_comment_to_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        form = Commentform(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.testimonial = testimonial
            comment.save()
            return redirect("testimonialdetail", pk=testimonial.pk)
    else:
        form = Commentform()
    return render(request, "TestimonialReply.html", {"form": form})


class NotificationView(TemplateView):
    template_name = "Notification.html"

    def get_context_data(self, **kwargs):
        context = super(NotificationView, self).get_context_data(**kwargs)
        # context['Notification'] =Notification.objects.filter(user=self.request.user)
        user = CustomUser.objects.get(pk=self.request.user.pk)
        context["Noti"] = user.notifications.all()
        return context


class HomeView(generic.DetailView):
    model = CustomUser
    template_name = "detail.html"
    slug_field = "username"


class AirlisView(generic.ListView):
    template_name = "airtime_success.html"
    context_object_name = "Airtime_funding_list"

    def get_queryset(self):
        return Airtime_funding.objects.all()


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        # print(uid)
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        # user.is_active = True
        user.email_verify = True
        user.save()

        messages.success(
            request,
            "Thank you for your email confirmation. Now you can login your account.",
        )

        return redirect("profile")

    else:
        return HttpResponse("Activation link is invalid!")


def sendverificationlink(request):
    try:
        user = request.user
        current_site = get_current_site(request)
        mail_subject = "Activate your legitdata account."
        message = {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        }
        message = get_template("acc_active_email.html").render(message)
        to_email = request.user.email
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.content_subtype = "html"
        email.send()

        data = {
            "message": f"Verification link sent to {request.user.email}",
        }
    except:
        data = {
            "message": "Unable to send account verification link, contact admin",
        }

    return JsonResponse(data)


class SignUp(SuccessMessageMixin, generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"
    # success_messages = 'Please confirm your email address to complete the registration,activation link has been sent to your email, also check your email spam folder'
    success_messages = "You have successfully Registered, Kindly login to continue"

    def abc(self):
        ref = ""
        if "referal" in self.request.session:
            ref = self.request.session["referal"]

        return ref

    def get_context_data(self, **kwargs):
        context = super(SignUp, self).get_context_data(**kwargs)
        context["referal_user"] = self.abc()

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        username = object.username
        email = object.email
        # object.email_verify = False
        # object.is_active = False
        user = object

        if CustomUser.objects.filter(username__iexact=object.username).exists():
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["This username has been taken"]
            )
            return self.form_invalid(form)

        elif CustomUser.objects.filter(email__iexact=object.email).exists():
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["This email has been taken"]
            )
            return self.form_invalid(form)
        elif CustomUser.objects.filter(Phone__iexact=object.Phone).exists():
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["This Phone has been taken"]
            )
            return self.form_invalid(form)

        elif not object.email.endswith(("@gmail.com", "@yahoo.com")):
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["We accept only valid gmail or yahoo mail account"]
            )
            return self.form_invalid(form)

        elif object.referer_username:
            if CustomUser.objects.filter(
                username__iexact=object.referer_username
            ).exists():
                referal_user = CustomUser.objects.get(
                    username__iexact=object.referer_username
                )

            else:
                object.referer_username = None

        form.save()

        try:
            current_site = get_current_site(self.request)
            mail_subject = "Activate your legitdata account."
            message = {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            }
            message = get_template("acc_active_email.html").render(message)
            to_email = email
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.content_subtype = "html"
            email.send()

        except:
            pass
        try:
            Referal_list.objects.create(user=referal_user, username=username)
        except:
            pass
        try:
            # messages.success( self.request, 'Please confirm your email address to complete the registration,activation link has been sent to your email,, also check your email spam folder')

            sendmail(
                "Welcome to legitdata.com.ng",
                "Welcome to alegitdata.com.ngWe offer instant recharge of Airtime, Databundle, CableTV (DStv, GOtv & Startimes), Electricity Bill Payment and Airtime to Cash.",
                email,
                username,
            )

        except:
            pass
        try:

            def create_id():
                random.randint(1, 10)
                num_2 = random.randint(1, 10)
                num_3 = random.randint(1, 10)
                return str(num_2) + str(num_3) + str(uuid.uuid4())[:4]

            body = {
                "accountReference": create_id(),
                "accountName": username,
                "currencyCode": "NGN",
                "contractCode": f"{get_config().monnify_contract_code}",
                "customerEmail": email,
                "incomeSplitConfig": [],
                "restrictPaymentSource": False,
                "allowedPaymentSources": {},
            }

            if not email:
                data = json.dumps(body)
                ad = requests.post(
                    "https://api.monnify.com/api/v1/auth/login",
                    auth=HTTPBasicAuth(
                        f"{get_config().monnify_API_KEY}",
                        f"{get_config().monnify_SECRET_KEY}",
                    ),
                )
                mydata = json.loads(ad.text)

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(
                        mydata["responseBody"]["accessToken"]
                    ),
                }
                ab = requests.post(
                    "https://api.monnify.com/api/v1/bank-transfer/reserved-accounts",
                    headers=headers,
                    data=data,
                )

                mydata = json.loads(ab.text)

                user = CustomUser.objects.get(email__iexact=email)

                user.reservedaccountNumber = mydata["responseBody"]["accountNumber"]
                user.reservedbankName = mydata["responseBody"]["bankName"]
                user.reservedaccountReference = mydata["responseBody"][
                    "accountReference"
                ]
                user.save()

            else:
                pass

        except:
            pass
        return super(SignUp, self).form_valid(form)


class UserEdit(generic.UpdateView):
    form_class = CustomUserChangeForm
    models = CustomUser
    success_url = reverse_lazy("userdetails")
    template_name = "Editprofile.html"
    context_object_name = "Edit"

    def get_object(self):
        return CustomUser.objects.get(pk=self.request.user.id)

    def get_queryset(self):
        return CustomUser.objects.all()


class BankpaymentCreate(generic.CreateView):
    form_class = Bankpaymentform
    template_name = "bank_form.html"

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        if float(object.amount) < get_config().manual_bank_funding_limit:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                [
                    "Minimun deposit is #{}".format(
                        get_config().manual_bank_funding_limit
                    )
                ]
            )
            return self.form_invalid(form)

        msg = f"{object.user.username} want to fund his/her account with  bank payment  amount:{object.user.username} https://www.legitdata.com.ngpage-not-found-error/page/vtuapp/bankpayment/"

        try:
            sendmail(
                "MANUAL BANK FUNDING Notification",
                msg,
                get_config().gmail,
                "legitdata.com.ng",
            )
            sendmessage("Msorg", msg, f"{get_config().sms_notification_number}", "2")
        except:
            pass

        form.save()

        return super(BankpaymentCreate, self).form_valid(form)


class bonus_transferCreate(generic.CreateView):
    form_class = bonus_transfer_form
    template_name = "bonus_transfer_form.html"
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        if float(object.amount) > object.user.Referer_Bonus:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                [
                    "You can't Tranfer to your wallet due to insufficientr bonus balance, Current BONUS Balance #{}".format(
                        object.user.Referer_Bonus
                    )
                ]
            )
            return self.form_invalid(form)

        elif float(object.amount) < 100:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["minimum of N100".format()]
            )
            return self.form_invalid(form)

        else:
            try:
                mb = CustomUser.objects.get(pk=self.request.user.pk)
                ms = object.amount
                mb.ref_withdraw(float(ms))
                mb.deposit(mb.id, float(ms), True, "Bonus to Wallet")

                messages.success(
                    self.request,
                    "#{} referer bonus has been added to your wallet,refer more people to get more bonus".format(
                        object.amount
                    ),
                )

            except:
                pass

        form.save()
        return super(bonus_transferCreate, self).form_valid(form)


class paymentgatewayCreate(generic.CreateView):
    form_class = paymentgateway_form
    template_name = "paystack.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        object.reference = create_id

        headers = {
            "authorization": "Bearer sk_c8986fb38180f0b006e276637c2437870d08b1d5",
            "content-type": "application/json",
            "cache-control": "no-cache",
        }
        url = "https://api.paystack.co/transaction/initialize"
        payload = {
            "email": "customer@email.com",
            "amount": 500000,
            "reference": "7PVGX8MEk85tgeEpVDtD",
            "callback_url": "www.legitdata.com.ng",
        }
        requests.post(url, headers=headers, params=payload)
        HttpResponseRedirect("Location: ".response["data"]["authorization_url"])

        form.save()

        return super(paymentgatewayCreate, self).form_valid(form)


class Bankpaymentsuccess(generic.DetailView):
    model = Bankpayment
    template_name = "bank_payment_success.html"
    queryset = Bankpayment.objects.all()
    context_object_name = "bank"


class airtimeCreate(generic.CreateView):
    form_class = airtimeform
    template_name = "airtime_form.html"

    def get_context_data(self, **kwargs):
        net = Network.objects.filter(name="MTN").first()
        net_2 = Network.objects.filter(name="GLO").first()
        net_3 = Network.objects.filter(name="9MOBILE").first()
        net_4 = Network.objects.filter(name="AIRTEL").first()

        context = super(airtimeCreate, self).get_context_data(**kwargs)
        context["mtn"] = Percentage.objects.get(
            network=net
        ).percent
        context["glo"] = Percentage.objects.get(
            network=net_2
        ).percent
        context["mobie"] = Percentage.objects.get(
            network=net_3
        ).percent
        context["airtel"] = Percentage.objects.get(
            network=net_4
        ).percent

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        net = str(object.network)
        amt = float(object.amount)

        def sendmessage(sender, message, to, route):
            baseurl = f"https://sms.hollatags.com/api/send/?user={get_config().hollatag_username}&pass={get_config().hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}"
            requests.get(baseurl, verify=False)

        if net == "MTN" and (len(object.pin) < 16 or len(object.pin) > 17):
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Invalid MTN card pin "]
            )
            return self.form_invalid(form)

        elif net == "9MOBILE" and (len(object.pin) < 16 or len(object.pin) > 17):
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Invalid 9MOBILE card pin"]
            )
            return self.form_invalid(form)

        elif net == "GLO" and (len(object.pin) < 16 or len(object.pin) > 17):
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Invalid GLO card pin"]
            )
            return self.form_invalid(form)

        elif net != "MTN" and (amt == 400.0):
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["#400 airtime only available for MTN"]
            )
            return self.form_invalid(form)

        elif net == "AIRTEL" and (len(object.pin) < 16 or len(object.pin) > 17):
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Invalid AIRTEL card pin"]
            )
            return self.form_invalid(form)

        elif net == "MTN":
            perc = Percentage.objects.get(id=1)
            object.Receivece_amount = float(object.amount) * int(perc.percent) / 100

        elif net == "GLO":
            perc = Percentage.objects.get(id=2)
            object.Receivece_amount = float(object.amount) * int(perc.percent) / 100

        elif net == "9MOBILE":
            perc = Percentage.objects.get(id=3)
            object.Receivece_amount = float(object.amount) * int(perc.percent) / 100

        elif net == "AIRTEL":
            perc = Percentage.objects.get(id=4)
            object.Receivece_amount = float(object.amount) * int(perc.percent) / 100

        sendmessage(
            "Msorg",
            "{0} want to fund his/her account with airtime pin:{1} network: {2} amount:{3} https://www.legitdata.com.ngpage-not-found-error/page/vtuapp/airtime/".format(
                object.user.username, object.pin, object.network, object.amount
            ),
            f"{get_config().sms_notification_number}",
            "2",
        )

        form.save()

        return super(airtimeCreate, self).form_valid(form)


class BulkCreate(generic.CreateView):
    form_class = Bulk_Message_form
    template_name = "bulk.html"

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        num = object.to.split(",")
        invalid = 0
        unit = 0
        numberlist = []
        page = 1
        previous_bal = object.user.Account_Balance

        def send_bulksms9ja(sender, to, message):
            print(
                "------------------------------------------------GOING TO BULKSMS 9JA"
            )

            url = "https://www.bulksmsnigeria.com/api/v1/sms/create"
            payload = json.dumps(
                {"api_token": "", "from": sender, "to": to, "body": message}
            )
            headers = {"Content-Type": "application/json"}

            response = requests.request("POST", url, headers=headers, data=payload)
            print(payload)
            print(response.text)

            return response

        def sendmessage(sender, message, to, route):
            baseurl = f"https://sms.hollatags.com/api/send/?user={get_config().hollatag_username}&pass={get_config().hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}"
            requests.get(baseurl, verify=False)

        for real in num:
            if len(real) == 11:
                if real.startswith("0"):
                    sender = list(real)
                    sender[0] = "234"
                    sender = "".join(sender)

                    numberlist.append(sender)

                    unit += 1
                else:
                    invalid += 1

            elif len(real) == 13:
                if real.startswith("234"):
                    numberlist.append(real)

                    unit += 1

                else:
                    invalid += 1
            else:
                invalid += 1

        numberset = ",".join(numberlist)
        object.total = len(numberlist)
        if len(object.message) % 160 > 1:
            page = page + len(object.message) // 160

        if object.DND is True:
            if numberset == "" or numberset is None:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["No valid Number found"]
                )
                return self.form_invalid(form)

            elif Disable_Service.objects.get(service="Bulk sms").disable is True:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["This Service is not currently available please check back"]
                )
                return self.form_invalid(form)

            else:
                if float(object.total * 3.5 * page) > object.user.Account_Balance:
                    form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                        [
                            "You can't send bulk sms  due to insufficientr balance, Current Balance #{}".format(
                                object.user.Account_Balance
                            )
                        ]
                    )
                    return self.form_invalid(form)

                else:
                    sendmessage(object.sendername, object.message, numberset, "03")
                    object.unit = unit
                    object.invalid = invalid
                    object.page = page
                    object.total = len(numberlist)
                    object.amount = object.total * 3.5 * int(object.page)
                    mb = CustomUser.objects.get(pk=object.user.pk)
                    withdraw = mb.withdraw(mb.id, float(object.amount))
                    if withdraw is False:
                        form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                            [
                                "You can't send bulk sms  due to insufficientr balance, Current Balance #{}".format(
                                    object.user.Account_Balance
                                )
                            ]
                        )
                        return self.form_invalid(form)
                    object.Status = "successful"
                    WalletSummary.objects.create(
                        user=object.user,
                        product="bulk sms service charge  N{} ".format(object.amount),
                        amount=object.amount,
                        previous_balance=previous_bal,
                        after_balance=(previous_bal - float(object.amount)),
                    )

        else:
            if numberset == "" or numberset is None:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["No valid Number found"]
                )
                return self.form_invalid(form)

            elif Disable_Service.objects.get(service="Bulk sms").disable is True:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["This Service is not currently available please check back"]
                )
                return self.form_invalid(form)
            else:
                if float(object.total * 3.5 * page) > object.user.Account_Balance:
                    form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                        [
                            "You can't send bulk sms  due to insufficientr balance, Current Balance #{}".format(
                                object.user.Account_Balance
                            )
                        ]
                    )
                    return self.form_invalid(form)

                else:
                    sendmessage(object.sendername, object.message, numberset, "02")
                    object.unit = unit
                    object.invalid = invalid
                    object.page = page
                    object.total = len(numberlist)
                    object.amount = object.total * 3.5 * int(object.page)
                    mb = CustomUser.objects.get(pk=object.user.pk)
                    withdraw = mb.withdraw(mb.id, float(object.amount))
                    if withdraw is False:
                        form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                            [
                                "You can't send bulk sms  due to insufficientr balance, Current Balance #{}".format(
                                    object.user.Account_Balance
                                )
                            ]
                        )
                        return self.form_invalid(form)
                    object.Status = "successful"
                    WalletSummary.objects.create(
                        user=object.user,
                        product="bulk sms N{} ".format(object.amount),
                        amount=object.amount,
                        previous_balance=previous_bal,
                        after_balance=(previous_bal - float(object.amount)),
                    )

        form.save()

        return super(BulkCreate, self).form_valid(form)


class Bulk_success(generic.DetailView):
    model = Bulk_Message
    template_name = "bulk_success.html"
    queryset = Bulk_Message.objects.all()
    context_object_name = "bulk_success"


class airtime_success(generic.DetailView):
    model = Airtime
    template_name = "Airtime_suc.html"
    queryset = Airtime.objects.all()
    context_object_name = "Airtime_success"

    def get_context_data(self, **kwargs):
        context = super(airtime_success, self).get_context_data(**kwargs)

        context["net"] = Network.objects.filter(name="MTN").first()
        context["net_2"] = Network.objects.filter(name="GLO").first()
        context["net_3"] = Network.objects.filter(name="9MOBILE").first()
        context["net_4"] = Network.objects.filter(name="AIRTEL").first()
        return context


class Airtime_fundingCreate(generic.CreateView):
    form_class = Airtime_fundingform
    template_name = "Airtime_funding_form.html"

    def get_context_data(self, **kwargs):
        context = super(Airtime_fundingCreate, self).get_context_data(**kwargs)

        context["mtn"] = Percentage.objects.get(
            network=Network.objects.filter(name="MTN").first()
        ).percent
        context["glo"] = Percentage.objects.get(
            network=Network.objects.filter(name="GLO").first()
        ).percent
        context["mobie"] = Percentage.objects.get(
            network=Network.objects.filter(name="9MOBILE").first()
        ).percent
        context["airtel"] = Percentage.objects.get(
            network=Network.objects.filter(name="AIRTEL").first()
        ).percent
        context["num_1"] = Admin_number.objects.get(network="MTN")
        context["num_2"] = Admin_number.objects.get(network="GLO")
        context["num_3"] = Admin_number.objects.get(network="9MOBILE")
        context["num_4"] = Admin_number.objects.get(network="AIRTEL")

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        str(object.network)
        mobilenumber = str(object.mobile_number)
        mobilenumber.replace(" ", "")

        form.save()

        return super(Airtime_fundingCreate, self).form_valid(form)


class Airtime_funding_success(generic.DetailView):
    model = Airtime_funding
    template_name = "Airtime_funding_success.html"
    queryset = Airtime_funding.objects.all()
    context_object_name = "Airtime_funding_list"

    def get_context_data(self, **kwargs):
        context = super(Airtime_funding_success, self).get_context_data(**kwargs)
        context["net"] = Network.objects.filter(name="MTN").first()
        context["net_2"] = Network.objects.filter(name="GLO").first()
        context["net_3"] = Network.objects.filter(name="9MOBILE").first()
        context["net_4"] = Network.objects.filter(name="AIRTEL").first()
        context["num_1"] = Admin_number.objects.get(network="MTN")
        context["num_2"] = Admin_number.objects.get(network="GLO")
        context["num_3"] = Admin_number.objects.get(network="9MOBILE")
        context["num_4"] = Admin_number.objects.get(network="AIRTEL")
        return context


class CouponCodePayment(generic.CreateView):
    form_class = CouponCodeform
    template_name = "Coupon.html"
    Coupo = Couponcode.objects.all()

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        previous_bal = object.user.Account_Balance

        # for codes in self.Coupo:
        # exists()
        if not Couponcode.objects.filter(Coupon_Code=object.Code).exists():
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Invalid Coupon code note that its case sensetive"]
            )
            return self.form_invalid(form)
        elif Couponcode.objects.filter(Coupon_Code=object.Code, Used=True).exists():
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["This Coupon code has been used"]
            )
            return self.form_invalid(form)
        elif Couponcode.objects.filter(Coupon_Code=object.Code).exists():
            mb = CustomUser.objects.get(pk=object.user.pk)
            Couponcode.objects.get(Coupon_Code=object.Code).amount
            object.amount = Couponcode.objects.get(Coupon_Code=object.Code).amount
            amount = float(object.amount)
            mb.deposit(mb.id, amount, False, "Coupon Funding")
            sta = Couponcode.objects.get(Coupon_Code=object.Code)
            sta.Used = True
            WalletSummary.objects.create(
                user=object.user,
                product=" N{} Coupon Funding  ".format(amount),
                amount=amount,
                previous_balance=previous_bal,
                after_balance=(previous_bal + amount),
            )

            # REFERRAL BONUS FOR FUNDING
            # user = object.user
            # chek =  Wallet_Funding.objects.filter(user=user).count()
            # # try:
            # #print(f'referral bonus inititated for {user}')
            # #print(user.referer_username)
            # #print(chek)
            # if user.referer_username and chek == 1:
            #     #print('---------------------------------------------------------')
            #     #print(f'referral bonus inititated, no wallet funding record found for {user}')
            #     #print('---------------------------------------------------------')
            #     if CustomUser.objects.filter(username__iexact=user.referer_username).exists():
            #         referer = CustomUser.objects.get(username__iexact=user.referer_username)
            #         ref_previous_bal = referer.Account_Balance
            #         referer.ref_deposit(200)
            #         notify.send(referer, recipient=referer, verb='you Earned N200 Bonus from your referal: {user.username} first funding and has been added to your referal bonus wallet')
            #         WalletSummary.objects.create(user=referer, product=f"Earned N200 referral bonus from {user} first funding", amount=200, previous_balance=ref_previous_bal, after_balance=(ref_previous_bal + 200))
            # REFERRAL BONUS FOR FUNDING

            sta.save()
            messages.success(
                self.request,
                "your account has been credited with sum of #{} .".format(
                    object.amount
                ),
            )

        form.save()
        return super(CouponCodePayment, self).form_valid(form)


class Coupon_success(generic.DetailView):
    model = CouponPayment
    template_name = "Payment.html"
    context_object_name = "Coupon"

    def get_queryset(self):
        return CouponPayment.objects.filter(user=self.request.user)


class PinView(generic.CreateView):
    form_class = Pinform
    template_name = "pin.html"

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        form.save()
        return super(PinView, self).form_valid(form)


class withdrawCreate(generic.CreateView):
    form_class = withdrawform
    template_name = "withdraw_form.html"

    def sendmessage(sender, message, to, route):
        baseurl = f"https://sms.hollatags.com/api/send/?user={get_config().hollatag_username}&pass={get_config().hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}"
        requests.get(baseurl, verify=False)

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        object.amount = float(object.amount) + 100
        previous_bal = object.user.Account_Balance

        if float(object.amount) > object.user.Account_Balance:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                [
                    "Insufficient balance ,Try to fund your account :Account Balance #{}".format(
                        object.user.Account_Balance
                    )
                ]
            )
            return self.form_invalid(form)

        elif float(object.amount) > object.user.Account_Balance:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                [
                    "Insufficient balance ,Try to fund your account :You can only withdraw #{}".format(
                        object.user.Account_Balance - 100
                    )
                ]
            )
            return self.form_invalid(form)

        elif (
            object.user.is_superuser is False
            and Withdraw.objects.filter(create_date__date=datetimex.date.today()).count
            > 1
        ):
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Exceed Maximum withdraw limit for today."]
            )

        elif float(object.amount) < 1000:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Minimun withdraw is #1000 per transaction"]
            )
            return self.form_invalid(form)

        elif float(object.amount) > 20000:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                [" Maximum withdraw is #20000 per transaction"]
            )
            return self.form_invalid(form)
        else:
            try:
                mb = CustomUser.objects.get(pk=object.user.pk)
                ms = object.amount
                check = mb.withdraw(mb.id, float(ms))
                if check is False:
                    form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                        [
                            "Insufficient balance ,Try to fund your account :You can only withdraw #{}".format(
                                object.user.Account_Balance - 100
                            )
                        ]
                    )
                    return self.form_invalid(form)

                WalletSummary.objects.create(
                    user=object.user,
                    product="Wallet Withdraw ",
                    amount=object.amount,
                    previous_balance=previous_bal,
                    after_balance=(previous_bal - object.amount),
                )

                sendmessage(
                    "Msorg",
                    "{0} want to withdraw   amount:{1}   https://www.legitdata.com.ngpage-not-found-error/page/vtuapp/withdraw/".format(
                        object.user.username, object.amount
                    ),
                    f"{get_config().sms_notification_number}",
                    "2",
                )
            except:
                pass

        form.save()

        return super(withdrawCreate, self).form_valid(form)


class Withdraw_success(generic.DetailView):
    model = Withdraw
    template_name = "Withdraw-detail.html"
    context_object_name = "Withdraw_list"

    def get_queryset(self):
        return Withdraw.objects.filter(user=self.request.user)


class dataCreate(generic.CreateView):
    form_class = dataform
    template_name = "data_form.html"

    def get_context_data(self, **kwargs):
        context = super(dataCreate, self).get_context_data(**kwargs)
        context["network"] = Network.objects.filter(name="MTN").first()
        context["networks"] = Network.objects.all()
        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
            ["use updated browser and retry"]
        )
        return self.form_invalid(form)

        return super(dataCreate, self).form_valid(form)


def loadplans(request):
    network_id = request.GET.get("network")
    Network.objects.get(id=network_id)
    plans = Plan.objects.filter(network_id=network_id).order_by("plan_amount")

    # print(plans)
    return render(request, "planslist.html", {"plans": plans})


class Data_success(generic.DetailView):
    model = Data
    template_name = "Data-detail.html"
    queryset = Data.objects.all()
    context_object_name = "Data_list"


class Airtime_to_Data_Create(generic.CreateView):
    form_class = Airtime_to_Data_pin_form
    template_name = "data_form_2.html"

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        Mtn = [
            "0702",
            "0704",
            "0706",
            "0703",
            "0903",
            "0906",
            "0706",
            "0803",
            "0806",
            "0810",
            "0813",
            "0816",
            "0814",
        ]
        ETISALATE = ["0809", "0817", "0818", "0909", "0908"]
        GLO = ["0705", "0805", "0811", "0807", "0815", "0905"]
        AIRTEL = [
            "0702",
            "0708",
            "0802",
            "0808",
            "0812",
            "0907",
            "0701",
            "0902",
            "0901",
            "0904",
        ]
        net = str(object.network)
        mobilenumber = str(object.mobile_number)
        num = mobilenumber.replace(" ", "")

        if object.Ported_number is True:
            if len(num) != 11:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Invalid mobile number"]
                )
                return self.form_invalid(form)

        else:
            if len(num) != 11:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Invalid mobile number"]
                )
                return self.form_invalid(form)

            elif net == "9MOBILE" and not num.startswith(tuple(ETISALATE)):
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Please check entered number is not 9MOBILE user"]
                )
                return self.form_invalid(form)

            elif net == "MTN" and not num.startswith(tuple(Mtn)):
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Please check entered number is not MTN user"]
                )
                return self.form_invalid(form)

            elif net == "GLO" and not num.startswith(tuple(GLO)):
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Please check entered number is not GLO user"]
                )
                return self.form_invalid(form)

            elif net == "AIRTEL" and not num.startswith(tuple(AIRTEL)):
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Please check entered number is not AIRTEL user"]
                )
                return self.form_invalid(form)

            def sendmessage(sender, message, to, route):
                baseurl = f"https://sms.hollatags.com/api/send/?user={get_config().hollatag_username}&pass={get_config().hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}"
                requests.get(baseurl, verify=False)

            sendmessage(
                "Msorg",
                "{0} want to buy  data plan  plan size:{1} network{2} https://www.legitdata.com.ngpage-not-found-error/page/vtuapp/data/".format(
                    object.user.username, object.plan.plan_size, object.network
                ),
                f"{get_config().sms_notification_number}",
                "02",
            )

        form.save()
        return super(Airtime_to_Data_Create, self).form_valid(form)


def loadplans_2(request):
    network_id = request.GET.get("network")
    plans = Airtime_to_data_Plan.objects.filter(network_id=network_id).order_by(
        "plan_amount"
    )
    return render(request, "planslist_1.html", {"plans": plans})


class Airtime_to_Data__success(generic.DetailView):
    model = Data
    template_name = "Airtime_to_Data_detail.html"
    queryset = Airtime_to_Data_pin.objects.all()
    context_object_name = "Data_list"


class Airtime_to_Data_tranfer_Create(generic.CreateView):
    form_class = Airtime_to_Data_tranfer_form
    template_name = "data_form_3.html"

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        Mtn = [
            "0702",
            "0704",
            "0706",
            "0703",
            "0903",
            "0906",
            "0706",
            "0803",
            "0806",
            "0810",
            "0813",
            "0816",
            "0814",
        ]

        str(object.network)
        mobilenumber = str(object.Transfer_number)
        num = mobilenumber.replace(" ", "")

        if len(num) != 11:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Invalid mobile number"]
            )
            return self.form_invalid(form)

        elif not num.startswith(tuple(Mtn)):
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Please check entered Tranfer from number is not MTN user"]
            )
            return self.form_invalid(form)

        def sendmessage(sender, message, to, route):
            baseurl = f"https://sms.hollatags.com/api/send/?user={get_config().hollatag_username}&pass={get_config().hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}"
            requests.get(baseurl, verify=False)

        sendmessage(
            "Msorg",
            "{0} want to buy  data plan  plan size:{1} network{2} https://www.legitdata.com.ngpage-not-found-error/page/vtuapp/data/".format(
                object.user.username, object.plan.plan_size, object.network
            ),
            f"{get_config().sms_notification_number}",
            "02",
        )

        form.save()
        return super(Airtime_to_Data_tranfer_Create, self).form_valid(form)


class Airtime_to_Data_tranfer_success(generic.DetailView):
    model = Data
    template_name = "Airtime_to_Data_tranfer_detail.html"
    queryset = Airtime_to_Data_tranfer.objects.all()
    context_object_name = "Data_list"

    def get_context_data(self, **kwargs):
        context = super(Airtime_to_Data_tranfer_success, self).get_context_data(
            **kwargs
        )
        context["net_1"] = Admin_number.objects.get(network="MTN")
        return context


class TransferCreate(generic.CreateView):
    form_class = Transferform
    template_name = "Transfer_form.html"

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        if float(object.amount) > object.user.Account_Balance:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                [
                    "You can't Tranfer to other due to insufficientr balance, Current Balance #{}".format(
                        object.user.Account_Balance
                    )
                ]
            )
            return self.form_invalid(form)

        elif not CustomUser.objects.filter(
            username__iexact=object.receiver_username
        ).exists():
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Invalid user or no user with that username."]
            )
            return self.form_invalid(form)

        elif (
            object.user.is_superuser is False
            and Transfer.objects.filter(create_date__date=datetimex.date.today()).count
            > 2
        ):
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Exceed Maximum tranfer limit for today."]
            )

        elif object.user.username.lower() == object.receiver_username.lower():
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["You cannot transfer to yourself."]
            )
            return self.form_invalid(form)

        else:
            mb = CustomUser.objects.get(pk=object.user.pk)
            mb_2 = CustomUser.objects.get(username__iexact=object.receiver_username)
            ms = object.amount
            previous_bal1 = mb.Account_Balance
            previous_bal2 = mb_2.Account_Balance
            check = mb.withdraw(mb.id, float(ms))
            if check is False:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    [
                        "You can't Tranfer to other due to insufficientr balance, Current Balance #{}".format(
                            object.user.Account_Balance
                        )
                    ]
                )
                return self.form_invalid(form)

            mb_2.deposit(mb_2.id, float(ms), True, "Wallet to Wallet Transfer")
            notify.send(
                mb_2,
                recipient=mb_2,
                verb="You Received sum of #{} from {} ".format(
                    object.amount, object.user
                ),
            )

            WalletSummary.objects.create(
                user=mb,
                product="Transfer N{} to {}".format(object.amount, mb_2.username),
                amount=object.amount,
                previous_balance=previous_bal1,
                after_balance=(previous_bal1 - float(object.amount)),
            )

            WalletSummary.objects.create(
                user=mb_2,
                product="Received sum N{} from {}".format(object.amount, mb.username),
                amount=object.amount,
                previous_balance=previous_bal2,
                after_balance=(previous_bal2 + float(object.amount)),
            )

            messages.success(
                self.request,
                "Transfer sum of #{} to {} was successful".format(
                    object.amount, object.receiver_username
                ),
            )

        form.save()
        return super(TransferCreate, self).form_valid(form)


class BuybtcCreate(generic.CreateView):
    form_class = Buybtcform
    template_name = "buybitcoin_form.html"

    def get_context_data(self, **kwargs):
        context = super(BuybtcCreate, self).get_context_data(**kwargs)
        context["buyrate"] = Btc_rate.objects.get(rate="Selling_rate").amount

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        response = requests.get("https://api.coindesk.com/v1/bpi/currentprice/usd.json")
        data = json.loads(response.text)
        amt = data["bpi"]["USD"]["rate_float"]
        rate = Btc_rate.objects.get(rate="Buying_rate").amount
        object.Btc = round((object.amount / (amt * rate)), 5)
        round((object.Btc * amt * rate), 2)

        if float(object.amount) > object.user.Account_Balance:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                [
                    " insufficientr balance, Current Balance #{}".format(
                        object.user.Account_Balance
                    )
                ]
            )
            return self.form_invalid(form)

        def sendmessage(sender, message, to, route):
            baseurl = f"https://sms.hollatags.com/api/send/?user={get_config().hollatag_username}&pass={get_config().hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}"
            requests.get(baseurl, verify=False)

        sendmessage(
            "Msorg",
            "{0} want to do buy bitcoin wallet address {1} amount {2}".format(
                object.user.username, object.Btc_address, object.amount
            ),
            f"{get_config().sms_notification_number}",
            "02",
        )
        mb = CustomUser.objects.get(pk=object.user.pk)
        check = mb.withdraw(mb.id, object.amount)
        if check is False:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                [
                    " insufficientr balance, Current Balance #{}".format(
                        object.user.Account_Balance
                    )
                ]
            )
            return self.form_invalid(form)

        form.save()
        return super(BuybtcCreate, self).form_valid(form)


class Buybtc_success(generic.DetailView):
    model = Buybtc
    template_name = "Buybtc_success.html"
    queryset = Buybtc.objects.all()
    context_object_name = "buybtc_list"


class SellbtcCreate(generic.CreateView):
    form_class = SellBtcform
    template_name = "sellbitcoin_form.html"

    def get_context_data(self, **kwargs):
        context = super(SellbtcCreate, self).get_context_data(**kwargs)
        context["sellrate"] = Btc_rate.objects.get(rate="Buying_rate").amount

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        response = requests.get("https://api.coindesk.com/v1/bpi/currentprice/usd.json")
        data = json.loads(response.text)
        amt = data["bpi"]["USD"]["rate_float"]
        rate = Btc_rate.objects.get(rate="Selling_rate").amount
        object.Btc = round(object.Btc, 5)
        object.amount = round((object.Btc * float(amt) * rate), 2)

        def sendmessage(sender, message, to, route):
            payload = {
                "sender": sender,
                "to": to,
                "message": message,
                "type": "0",
                "routing": route,
                "token": "cYTj0CCFuGM4PSrvABkoANCBNlNF2SoipZFSNlz5hmKnejg6fubGLFu7Ph2URDj22dWGYjlRqDILQz7kHxARBlAwdC4CpTKHGC5D",
                "schedule": "",
            }

            baseurl = "https://smartsmssolutions.com/api/json.php?"
            requests.post(baseurl, params=payload, verify=False)

        sendmessage(
            "Msorg",
            "{0} want to do sell amount {1}".format(
                object.user.username, object.amount
            ),
            f"{get_config().sms_notification_number}",
            "02",
        )

        form.save()
        return super(SellbtcCreate, self).form_valid(form)


class Sellbtc_success(generic.DetailView):
    model = SellBtc
    template_name = "SellBtc_success.html"
    queryset = SellBtc.objects.all()
    context_object_name = "sellbtc_list"

    def get_context_data(self, **kwargs):
        context = super(Sellbtc_success, self).get_context_data(**kwargs)
        context["adminwallet"] = Btc_rate.objects.get(
            rate="Selling_rate"
        ).btc_wallet_address

        return context


class Transfer_success(generic.DetailView):
    model = Transfer
    template_name = "Transfer.html"
    queryset = Transfer.objects.all()
    context_object_name = "Transfer_list"


class Notify_User(generic.CreateView):
    form_class = Notify_user_form
    template_name = "Notify_user_form.html"
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user

        if CustomUser.objects.filter(username=object.username).exists():
            mb = CustomUser.objects.get(pk=object.user.pk)
            mb_2 = CustomUser.objects.get(username=object.username)
            notify.send(
                mb_2, recipient=mb_2, verb="{} from admin".format(object.message)
            )
            sendmail(
                " New Notification from legitdata.com.ng",
                f"{object.message} ",
                mb_2.email,
                mb_2.username,
            )
            messages.success(
                self.request, "Message sent successful to {}".format(object.username)
            )

        elif (object.username).lower() == "all":
            # user_number = [musa.Phone  for musa in CustomUser.objects.all()]
            for name in CustomUser.objects.all():
                mb = CustomUser.objects.get(pk=object.user.pk)
                mb_2 = CustomUser.objects.get(username=name.username)
                notify.send(
                    mb, recipient=mb_2, verb="{} from admin".format(object.message)
                )
                # emails = [x.email for x in CustomUser.objects.all()]
                try:
                    sendmail(
                        " New Notification from legitdata.com.ng",
                        f"{object.message} ",
                        name.email,
                        name.username,
                    )
                except:
                    pass

            messages.success(self.request, "Message sent successful ")

        else:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Invalid user or no user with that username."]
            )
            return self.form_invalid(form)

        form.save()
        return super(Notify_User, self).form_valid(form)


class AirtimeTopupCreate(generic.CreateView):
    form_class = AirtimeTopupform
    template_name = "AirtimeTopup_form.html"


    def get_context_data(self, **kwargs):
        context = super(AirtimeTopupCreate, self).get_context_data(**kwargs)
        user_type = self.request.user.user_type

        networks = {
            "MTN": ("mtn", "mtn_s"),
            "GLO": ("glo", "glo_s"),
            "AIRTEL": ("airtel", "airtel_s"),
            "9MOBILE": ("mobile", "mobile_s")
        }

        for network, (attr, attr_s) in networks.items():
            try:
                network_obj = Network.objects.get(name=network)
                try:
                    percentage = TopupPercentage.objects.get(network=network_obj)
                    if user_type == "Affilliate":
                        context[attr] = percentage.Affilliate_percent / 100
                        context[attr_s] = percentage.share_n_sell_affilliate_percent / 100
                    elif user_type == "API":
                        context[attr] = percentage.api_percent / 100
                        context[attr_s] = percentage.share_n_sell_api_percent / 100
                    elif user_type == "TopUser":
                        context[attr] = percentage.topuser_percent / 100
                        context[attr_s] = percentage.share_n_sell_topuser_percent / 100
                    else:
                        context[attr] = percentage.percent / 100
                        context[attr_s] = percentage.share_n_sell_percent / 100
                except TopupPercentage.DoesNotExist:
                    # Handle the case when the TopupPercentage object does not exist for the network
                    pass
            except ObjectDoesNotExist:
                # Handle the case when the Network object does not exist
                pass

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
            ["use updated browser and retry"]
        )
        return self.form_invalid(form)

        return super(AirtimeTopupCreate, self).form_valid(form)


class AirtimeTopup_success(generic.DetailView):
    model = AirtimeTopup
    template_name = "AirtimeTopup.html"
    queryset = AirtimeTopup.objects.all()
    context_object_name = "AirtimeTopup_list"


class AirtimeswapCreate(generic.CreateView):
    form_class = Airtimeswapform
    template_name = "Airtimeswap_form.html"

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        Mtn = [
            "0702",
            "0704",
            "0706",
            "0703",
            "0903",
            "0906",
            "0706",
            "0803",
            "0806",
            "0810",
            "0813",
            "0816",
            "0814",
        ]
        ETISALATE = ["0809", "0817", "0818", "0909", "0908"]
        GLO = ["0705", "0805", "0811", "0807", "0815", "0905"]
        AIRTEL = [
            "0702",
            "0708",
            "0802",
            "0808",
            "0812",
            "0907",
            "0701",
            "0902",
            "0901",
            "0904",
        ]
        net = str(object.swap_to_network)
        str(object.swap_from_network)
        mobilenumber = str(object.mobile_number)
        num = mobilenumber.replace(" ", "")

        if object.Ported_number is True:
            if len(num) != 11:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Invalid mobile number"]
                )
                return self.form_invalid(form)

            elif object.swap_from_network == object.swap_to_network:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["You cannot swap to same network"]
                )
                return self.form_invalid(form)

        else:
            if len(num) != 11:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Invalid mobile number"]
                )
                return self.form_invalid(form)

            elif object.swap_from_network == object.swap_to_network:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["You cannot swap to same network"]
                )
                return self.form_invalid(form)

            elif net == "9MOBILE" and not num.startswith(tuple(ETISALATE)):
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Please check entered number is not 9MOBILE user"]
                )
                return self.form_invalid(form)

            elif net == "MTN" and not num.startswith(tuple(Mtn)):
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Please check entered number is not MTN user"]
                )
                return self.form_invalid(form)

            elif net == "GLO" and not num.startswith(tuple(GLO)):
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Please check entered number is not GLO user"]
                )
                return self.form_invalid(form)

            elif net == "AIRTEL" and not num.startswith(tuple(AIRTEL)):
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Please check entered number is not AIRTEL user"]
                )
                return self.form_invalid(form)

            elif net == "MTN":
                object.Receivece_amount = float(object.amount) * 0.9

            elif net == "GLO":
                object.Receivece_amount = float(object.amount) * 0.8

            elif net == "9MOBILE":
                object.Receivece_amount = float(object.amount) * 0.85

            elif net == "AIRTEL":
                object.Receivece_amount = float(object.amount) * 0.85

        form.save()
        return super(AirtimeswapCreate, self).form_valid(form)


class Airtimeswap_success(generic.DetailView):
    model = Airtimeswap
    template_name = "Airtimeswap.html"
    queryset = Airtimeswap.objects.all()
    context_object_name = "Airtimeswap_list"

    def get_context_data(self, **kwargs):
        context = super(Airtimeswap_success, self).get_context_data(**kwargs)
        context["net"] = Network.objects.filter(name="MTN").first()
        context["net_2"] = Network.objects.filter(name="GLO").first()
        context["net_3"] = Network.objects.filter(name="9MOBILE").first()
        context["net_4"] = Network.objects.filter(name="AIRTEL").first()
        context["num_1"] = Admin_number.objects.get(network="MTN")
        context["num_2"] = Admin_number.objects.get(network="GLO")
        context["num_3"] = Admin_number.objects.get(network="9MOBILE")
        context["num_4"] = Admin_number.objects.get(network="AIRTEL")
        return context


def validate_meter_number(request):
    meternumber = request.GET.get("meternumber", None)
    disconame = request.GET.get("disconame", None)
    mtype = request.GET.get("mtype", None)

    if get_config().Bill_provider == "VTPASS":
        # print(meternumber, disconame, mtype)

        if disconame == "Ikeja Electric":
            disconame = "ikeja-electric"

        elif disconame == "Eko Electric":
            disconame = "eko-electric"

        elif disconame == "Kaduna Electric":
            disconame = "kaduna-electric"

        elif disconame == "Port Harcourt Electric":
            disconame = "portharcourt-electric"

        elif disconame == "Jos Electric":
            disconame = "jos-electric"

        elif disconame == "Ibadan Electric":
            disconame = "ibadan-electric"

        elif disconame == "Kano Electric":
            disconame = "kano-electric"

        elif disconame == "Abuja Electric":
            disconame = "abuja-electric"

        data = {"billersCode": meternumber, "serviceID": disconame, "type": mtype}
        invalid = False
        authentication = (
            f"{get_config().vtpass_email}",
            f"{get_config().vtpass_password}",
        )

        resp = requests.post(
            "https://vtpass.com/api/merchant-verify", data=data, auth=authentication
        )
        # print(resp.text)
        res = json.loads(resp.text)
        dat = res["content"]
        if "Customer_Name" in dat:
            name = res["content"]["Customer_Name"]
            address = res["content"]["Address"]
        else:
            invalid = True
            name = "INVALID METER NUMBER"
            address = "INVALID METER NUMBER"

    else:
        invalid = False
        address = False
        name = "NO NAME RETURN"

        url = "https://www.api.ringo.ng/api/agent/p2"
        payload = {
            "serviceCode": "V-ELECT",
            "disco": Disco_provider_name.objects.get(name=disconame).p_id,
            "meterNo": meternumber,
            "type": mtype,
        }

        headers = {
            "email": f"{get_config().ringo_email}",
            "password": f"{get_config().ringo_password}",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # #print(payload)
        # #print(response.text)

        a = json.loads(response.text)
        status = a["status"]

        if status == "200":
            name = a["customerName"]
            invalid = False

        else:
            name = "NO NAME RETURN"
            invalid = True

    data = {"invalid": invalid, "name": name, "address": address}

    return JsonResponse(data)


def validate_iuc(request):
    iuc = request.GET.get("smart_card_number", None)
    cable_id = request.GET.get("cablename", None)

    if get_config().Cable_provider == "VTPASS":
        if cable_id == "DSTV":
            data = {"billersCode": iuc, "serviceID": "dstv"}

        elif cable_id == "GOTV":
            data = {"billersCode": iuc, "serviceID": "gotv"}

        elif cable_id == "STARTIME":
            data = {"billersCode": iuc, "serviceID": "startimes"}

        invalid = False
        authentication = (
            f"{get_config().vtpass_email}",
            f"{get_config().vtpass_password}",
        )

        resp = requests.post(
            "https://vtpass.com/api/merchant-verify", data=data, auth=authentication
        )
        # print(resp.text)
        res = json.loads(resp.text)
        dat = res["content"]
        if "Customer_Name" in dat:
            name = res["content"]["Customer_Name"]

        else:
            invalid = True
            name = "INVALID IUC/SMARTCARD"

    else:
        print("......................... CABLE TO RINGO")

        if cable_id == "STARTIME":
            cable_id = "STARTIMES"

        url = "https://www.api.ringo.ng/api/agent/p2"
        payload = {"serviceCode": "V-TV", "type": cable_id, "smartCardNo": iuc}

        print(payload)

        headers = {
            "email": f"{get_config().ringo_email}",
            "password": f"{get_config().ringo_password}",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(response.text)
        a = json.loads(response.text)

        if response.status_code == 200:
            if a["status"] == 300 or a["status"] == "300":
                name = "INVALID SMARTCARD NUMBER"
                invalid = True
            else:
                name = a["customerName"]
                invalid = False
        else:
            name = "INVALID_SMARTCARDNO"
            invalid = True

    data = {"invalid": invalid, "name": name}
    return JsonResponse(data)


class Cablesubscription(generic.CreateView):
    form_class = cableform
    template_name = "cable_form.html"

    def get_context_data(self, **kwargs):
        context = super(Cablesubscription, self).get_context_data(**kwargs)
        service = ServicesCharge.objects.filter(service="Cablesub").first()
        
        if service:
            if self.request.user.user_type == "Affilliate":
                if service.Affilliate_charge > 0.0:
                    context["charge"] = f"N{service.Affilliate_charge } Charge "

                elif service.Affilliate_discount > 0.0:
                    context["charge"] = f"{service.Affilliate_discount} Percent Discount "

            elif self.request.user.user_type == "TopUser":
                if service.topuser_charge > 0.0:
                    context["charge"] = f"N{service.topuser_charge } Charge "

                elif service.topuser_discount > 0.0:
                    context["charge"] = f"{service.topuser_discount} Percent Discount "

            elif self.request.user.user_type == "API":
                if service.api_charge > 0.0:
                    context["charge"] = f"N{service.api_charge } Charge "

                elif service.api_discount > 0.0:
                    context["charge"] = f"{service.api_discount} Percent Discount "

            else:
                if service.charge > 0.0:
                    context["charge"] = f"N{service.charge } Charge "

                elif service.discount > 0.0:
                    context["charge"] = f"{service.discount} Percent Discount "

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
            ["use updated browser and retry"]
        )
        return self.form_invalid(form)

        return super(Cablesubscription, self).form_valid(form)


class BillpaymentView(generic.CreateView):
    form_class = Billpaymentform
    template_name = "bill_form.html"

    def get_context_data(self, **kwargs):
        context = super(BillpaymentView, self).get_context_data(**kwargs)
        service = ServicesCharge.objects.filter(service="Bill").first()

        if service:
            if self.request.user.user_type == "Affilliate":
                if service.Affilliate_charge > 0.0:
                    context["charge"] = f"N{service.Affilliate_charge } Charge "

                elif service.Affilliate_discount > 0.0:
                    context["charge"] = f"{service.Affilliate_discount} Percent Discount "

            elif self.request.user.user_type == "TopUser":
                if service.topuser_charge > 0.0:
                    context["charge"] = f"N{service.topuser_charge } Charge "

                elif service.topuser_discount > 0.0:
                    context["charge"] = f"{service.topuser_discount} Percent Discount "

            elif self.request.user.user_type == "API":
                if service.api_charge > 0.0:
                    context["charge"] = f"N{service.api_charge } Charge "

                elif service.api_discount > 0.0:
                    context["charge"] = f"{service.api_discount} Percent Discount "

            else:
                if service.charge > 0.0:
                    context["charge"] = f"N{service.charge } Charge "

                elif service.discount > 0.0:
                    context["charge"] = f"{service.discount} Percent Discount "

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
            ["use updated browser and retry"]
        )
        return self.form_invalid(form)

        return super(BillpaymentView, self).form_valid(form)


def loadcableplans(request):
    cablename_id = request.GET.get("cablename")
    cableplans = CablePlan.objects.filter(cablename_id=cablename_id).order_by(
        "plan_amount"
    )
    return render(request, "cableplanslist.html", {"cableplans": cableplans})


class Cablesub_success(generic.DetailView):
    model = Cablesub
    template_name = "cablesuccess.html"
    context_object_name = "cable_list"

    def get_queryset(self):
        return Cablesub.objects.filter(user=self.request.user)


class BillPayment_success(generic.DetailView):
    model = Billpayment
    template_name = "billsuccess.html"
    context_object_name = "bill_list"

    def get_queryset(self):
        return Billpayment.objects.filter(user=self.request.user)


class BookList(generic.ListView):
    template_name = "book-list.html"
    paginate_by = 20
    queryset = Book.objects.all().order_by("-created_at")
    context_object_name = "book_list"
    model = Book

    def get_context_data(self, **kwargs):
        context = super(BookList, self).get_context_data(**kwargs)
        context["category"] = Category.objects.all()

        return context


class BookDetail(FormMixin, generic.DetailView):
    model = Book
    template_name = "Book_detail.html"
    context_object_name = "book"
    form_class = Book_order_Form

    def get_success_url(self):
        return reverse("book_detail", kwargs={"slug": self.object.slug})

    def get_context_data(self, **kwargs):
        context = super(BookDetail, self).get_context_data(**kwargs)
        context["category"] = Category.objects.all()
        context["form"] = Book_order_Form(initial={"book_name": self.object})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        object.price = self.object.price
        object.book_name = self.object

        if float(object.price) > object.user.Account_Balance:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                [
                    "You can't purchase this book due to insufficientr balance, Current Balance #{}".format(
                        object.user.Account_Balance
                    )
                ]
            )
            messages.error(
                self.request,
                "You can't purchase this book due to insufficientr balance, Current Balance #{}".format(
                    object.user.Account_Balance
                ),
            )
            return self.form_invalid(form)
        mb = CustomUser.objects.get(pk=object.user.pk)
        ms = object.price
        check = mb.withdraw(mb.id, float(ms))
        if check is False:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
                [
                    " insufficientr balance, Current Balance #{}".format(
                        object.user.Account_Balance
                    )
                ]
            )
            return self.form_invalid(form)
        messages.success(
            self.request,
            "Your order has been sent you receive download link on email you provided",
        )

        def sendmessage(sender, message, to, route):
            baseurl = f"https://sms.hollatags.com/api/send/?user={get_config().hollatag_username}&pass={get_config().hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}"
            requests.get(baseurl, verify=False)

        sendmessage(
            "Msorg",
            "{0} order {1} email address {2}".format(
                object.user.username, object.book_name, object.email
            ),
            f"{get_config().sms_notification_number}",
            "02",
        )

        form.save()

        return super(BookDetail, self).form_valid(form)


def ravepaymentdone(request):
    ref = request.GET.get("txref")

    headers = {
        "content-type": "application/json",
    }

    data = {"txref": ref, "SECKEY": "FLWSECK-fd7f78dd615d0d7b2f87447f60979fba-X"}
    data = json.dumps(data)
    response = requests.post(
        "https://api.ravepay.com/flwv3-pug/getpaidx/api/v2/verify",
        headers=headers,
        data=data,
    )

    data = json.loads(response.text)
    context = {"data": response.text}
    if data["data"]["status"] == "successful":
        if data["data"]["chargecode"] == "00" or data["data"]["chargecode"] == "0":
            amt = float(data["data"]["amount"])
            payamount = amt / 100
            amt = payamount * 0.02
            paynow = round(payamount - amt)
            mb = CustomUser.objects.get(pk=request.user.pk)
            context = {"data": data}

            mb = CustomUser.objects.get(pk=request.user.pk)
            if "reference" not in request.session:
                mb.deposit(mb.id, paynow, False, "Flutterwave Funding")
                notify.send(
                    mb,
                    recipient=mb,
                    verb="Flutterwave Payment successful you account has been credited with sum of #{}".format(
                        paynow
                    ),
                )

                paymentgateway.objects.create(
                    user=request.user, reference=ref, amount=paynow, Status="successful"
                )
                request.session["reference"] = ref
            else:
                refere = request.session["reference"]
                if ref == refere:
                    pass
                else:
                    mb.deposit(mb.id, paynow, False, "Paystack Funding")
                    notify.send(
                        mb,
                        recipient=mb,
                        verb="Paystack Payment successful you account has been credited with sum of #{}".format(
                            paynow
                        ),
                    )

                    paymentgateway.objects.create(
                        user=request.user,
                        reference=ref,
                        amount=paynow,
                        Status="successful",
                    )
                    request.session["reference"] = ref

    else:
        messages.error(
            request,
            "Our payment gateway return Payment tansaction failed status {}".format(
                data["data"]["status"]
            ),
        )

    return render(request, "ravepaymentdone.html", context)


def paymentrave(request):
    if request.method == "POST":
        form = paymentraveform(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            email = request.user.email
            amount = (amount * 100) + (0.02 * amount * 100)

            headers = {
                "Authorization": f"Bearer {get_config().Paystack_secret_key}",
                "Content-Type": "application/json",
            }

            ab = {"amount": amount, "email": email}
            data = json.dumps(ab)
            response = requests.post(
                "https://api.paystack.co/transaction/initialize",
                headers=headers,
                data=data,
            )
            # print(response.text)
            loaddata = json.loads(response.text)
            amt = loaddata["data"]["authorization_url"]

            # print(username, email, phone)

            return HttpResponseRedirect(amt)

    else:
        form = paymentraveform()

    return render(request, "payonline.html", {"form": form})


@require_POST
@csrf_exempt
# @require_http_methods(["GET", "POST"])
def payonlinedone(request):
    a = f"{get_config().Paystack_secret_key}"
    secret = bytes(a, encoding="ascii")
    payload = request.body
    sign = hmac.new(secret, payload, hashlib.sha512).hexdigest()
    code = request.META.get("HTTP_X_PAYSTACK_SIGNATURE")

    bodydata = json.loads(payload)
    ref = bodydata["data"]["reference"]

    # forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
    forwarded_for = "{}".format(request.META.get("REMOTE_ADDR"))
    whitelist = ["52.31.139.75", "52.49.173.169", "52.214.14.220"]
    if forwarded_for in whitelist:
        if code == sign:
            url = "https://api.paystack.co/transaction/verify/{}".format(ref)
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {get_config().Paystack_secret_key}",
                    "Content-Type": "application/json",
                },
            )
            ab = json.loads(response.text)

            if (response.status_code == 200 and ab["status"] is True) and (
                ab["message"] == "Verification successful"
                and ab["data"]["status"] == "success"
            ):
                user = ab["data"]["customer"]["email"]
                mb = CustomUser.objects.get(email__iexact=user)
                amount = ab["data"]["amount"]
                paynow = round(amount / 100 - 0.02 * amount / 100)

                if not paymentgateway.objects.filter(reference=ref).exists():
                    try:
                        previous_bal = mb.Account_Balance
                        mb.deposit(mb.id, paynow + 1, False, "Paystack Funding")
                        paymentgateway.objects.create(
                            user=mb,
                            reference=ref,
                            amount=paynow,
                            Status="successful",
                            gateway="paystack",
                        )
                        WalletSummary.objects.create(
                            user=mb,
                            product=" N{} paystack Funding ".format(paynow),
                            amount=paynow,
                            previous_balance=previous_bal,
                            after_balance=(previous_bal + paynow),
                        )
                        notify.send(
                            mb,
                            recipient=mb,
                            verb="Paystack Payment successful you account has been credited with sum of #{}".format(
                                paynow
                            ),
                        )
                    except:
                        return HttpResponse(status=200)
                else:
                    pass

            else:
                messages.error(
                    request,
                    "Our payment gateway return Payment tansaction failed status {}".format(
                        ab["message"]
                    ),
                )

    else:
        return HttpResponseForbidden("Permission denied.")
    # print("hello")
    return HttpResponse(status=200)


@csrf_exempt
# @require_http_methods(["GET", "POST"])
def ussdcallback(request):

    return HttpResponse(status=200)


def create_id():
    random.randint(1, 10)
    num_2 = random.randint(1, 10)
    num_3 = random.randint(1, 10)
    return str(num_2) + str(num_3) + str(uuid.uuid4())


def flutterwavepayment(request):
    if request.method == "POST":
        form = paymentraveform(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            email = request.user.email
            amount = (amount) + (0.015 * amount)

            headers = {
                "content-type": "application/json",
            }

            ab = {
                "txref": create_id(),
                "PBFPubKey": "FLWPUBK-7e02397bad16e051a49495ef37b4cc23-X",
                "customer_email": email,
                "amount": amount,
                "currency": "NGN",
                "redirect_url": "https://www.legitdata.com.ngweb/profile/",
            }
            data = json.dumps(ab)
            # print(data)
            # data = '{"txref":"MC-1520443531487","PBFPubKey":"FLWPUBK-d029dfa2c4130538504aa1fb7e85a7cd-X", "customer_email": "user@example.com", "amount": 1000, "currency": "NGN", "redirect_url": "https://www.dataworld.com/ravepaymentdone"}'

            # response = requests.post('https://api.ravepay.co/flwv3-pug/getpaidx/api/v2/hosted/pay', headers=headers, data=data)

            response = requests.post(
                "https://api.ravepay.co/flwv3-pug/getpaidx/api/v2/hosted/pay",
                headers=headers,
                data=data,
            )


            loaddata = json.loads(response.text)
            amt = loaddata["data"]["link"]

            return HttpResponseRedirect(amt)

    else:
        form = paymentraveform()

    return render(request, "ravepayment.html", {"form": form})


@require_POST
@csrf_exempt
def flutterwavepaymentdone(request):
    hash_code = request.META.get("HTTP_VERIF_HASH")
   

    if hash_code == "MSORGHOOT$@#$$#%":
        data = json.loads(request.body)

        data = json.loads(request.body)
        headers = {
            "content-type": "application/json",
        }

        ab = {
            "txref": data["txRef"],
            "SECKEY": "FLWSECK-ce1767f49ae239374339ff27e0cf2659-X",
        }
        data = json.dumps(ab)

        response = requests.post(
            "https://api.ravepay.co/flwv3-pug/getpaidx/api/v2/verify",
            headers=headers,
            data=data,
        )
        data = json.loads(response.text)

        if (
            response.status_code == 200
            and data["data"]["chargecode"] == "00"
            and data["data"]["status"] == "successful"
        ):
            ab = json.loads(request.body)
            user = ab["customer"]["email"]
            # print(user)
            mb = CustomUser.objects.get(email__iexact=user)
            amount = data["data"]["amount"]
            paynow = round(amount - (0.015 * amount))

            if not paymentgateway.objects.filter(
                reference=data["data"]["txref"]
            ).exists():
                mb.deposit(mb.id, paynow + 1, False, "Flutterwave Funding")
                notify.send(
                    mb,
                    recipient=mb,
                    verb="flutterwave Payment successful you account has been credited with sum of #{}".format(
                        paynow
                    ),
                )

                paymentgateway.objects.create(
                    user=mb,
                    reference=data["data"]["txref"],
                    amount=paynow,
                    gateway="Flutterwave",
                    Status="successful",
                )

            else:
                pass

        else:
            messages.error(
                request, "Our payment gateway return Payment tansaction failed statuss"
            )

    return HttpResponse(status=200)


@require_POST
@csrf_exempt
def Vtpass_Webhook(request):
    print(
        "------------------------------------------- VTPASS WEBHOOOK ----------------------------------"
    )
    data = request.body
    print(f"data = {data}")

    "{}".format(request.META.get("HTTP_X_FORWARDED_FOR"))
    result = json.loads(data)
    print(f"result = {result}")

    return Response({"response": "success"}, status=200)


@require_POST


# SAMPLE
# {
#   "transaction": {
#     "status": "success",
#     "reference": "46634e8384c7c68f5baa",
#     "customer_reference": "38dhdhdsk",
#     "type": "Data purchase",
#     "beneficiary": "090XXXXXXXX",
#     "memo": "500MB (SME) - Monthly data purchase for 090XXXXXXXX",
#     "response": "500MB (SME) - Monthly data purchase for 090XXXXXXXX",
#     "price": "200"
#   }
# }


@require_POST
@csrf_exempt
def Smeplug_Webhook(request):
    print(
        "------------------------------------------- SMEPLUG  WEBHOOOK ----------------------------------"
    )
    data = request.body
    "{}".format(request.META.get("HTTP_X_FORWARDED_FOR"))
    result = json.loads(data)
    print(f"result = {result}")

    ident = result["transaction"]["reference"]
    trans = Data.objects.filter(ident=ident).first()
    if trans:
        if (
            trans.Status != "successful"
            and result["transaction"]["status"] != "success"
        ):
            trans.Status == "failed"
            trans.save()

            print("------------------ order failed, complete")

        else:
            print(f"{ident} was successful")
            pass

    else:
        print(f"customRef({ident}) not found")
        pass

    return Response({"response": "success"}, status=200)
