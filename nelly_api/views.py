import json
import logging
import random
import urllib.parse
import uuid
from datetime import datetime as Mdate

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.core import serializers as seria2
from django.core.mail import EmailMessage
from django.db import transaction
from django.forms.utils import ErrorList
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

# new import for webhook
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView
from notifications.signals import notify
from requests.auth import HTTPBasicAuth
from rest_auth.registration.views import SocialLoginView
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated  # <-- Here
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.twiml.messaging_response import MessagingResponse

# from .forms import *
from vtuapp.models import *
from core.models import *

from .serializers import *
from .tokens import account_activation_token

# Create your views here.


class UserCreate(APIView):
    """
    Creates the user.
    """

    def post(self, request, format="json"):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json["token"] = token.key

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
                    to_email = user.email
                    email = EmailMessage(mail_subject, message, to=[to_email])
                    email.content_subtype = "html"
                    email.send()

                except:
                    pass

                return Response(json, status=200)

        return Response(serializer.errors, status=400)


# API VIEW START HERE CREATED BY MUSA ABDUL GANIYU


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


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


###API ####
class Wallet_summaryListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = WalletSummary.objects.filter(user=request.user).order_by(
            "-create_date"
        )
        serializer = Wallet_summarySerializer(items, many=True)
        return Response(serializer.data)


class PasswordChangeAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        try:
            serializer = PasswordChangeSerializer(data=request.data)
            if serializer.is_valid():
                if not request.user.check_password(serializer.data.get("old_password")):
                    return Response(
                        {"old_password": "Wrong old password entered."}, status=400
                    )

                elif str(serializer.data.get("new_password1")) != str(
                    serializer.data.get("new_password2")
                ):
                    return Response(
                        {"new_password2": "new Passwords are not match"}, status=400
                    )

                elif len(serializer.data.get("new_password1")) < 8:
                    return Response(
                        {
                            "new_password1": "new password too short, minimum of 8 character."
                        },
                        status=400,
                    )

                # set_password also hashes the password that the user will get
                request.user.set_password(serializer.data.get("new_password1"))
                request.user.save()

            return Response({"status": "New password has been saved."}, status=200)

            # return Response(serializer.errors,status=400)

        except CustomUser.DoesNotExist:
            return Response(status=500)


class VerificationEmailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        # try:

        user = request.user
        current_site = get_current_site(self.request)
        mail_subject = "Activate your legitdata account."
        message = {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        }
        message = get_template("acc_active_email.html").render(message)
        to_email = user.email
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.content_subtype = "html"
        email.send()
        return Response(status=200)

        # except :
        #     return Response(status=500)


class CustomUserCreate(APIView):
    def post(self, request, format="json"):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json["token"] = token.key

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
                    to_email = user.email
                    email = EmailMessage(mail_subject, message, to=[to_email])
                    email.content_subtype = "html"
                    email.send()
                except:
                    pass

                return Response(json, status=201)

        return Response(serializer.errors, status=400)


class Api_History(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **kwargs):
        data = Data.objects.filter(user=request.user).order_by("-create_date")[:10]
        data_serializer = DataSerializer(data, many=True)
        airtimetopup = AirtimeTopup.objects.filter(user=request.user).order_by(
            "-create_date"
        )[:10]
        airtimetopup_serializer = AirtimeTopupSerializer(airtimetopup, many=True)
        payment = paymentgateway.objects.filter(user=request.user).order_by(
            "-created_on"
        )[:10]
        payment_serializer = paymentgatewaySerializer(payment, many=True)
        cablesub = Cablesub.objects.filter(user=request.user).order_by("-create_date")[
            :10
        ]
        cablesub_serializer = CablesubSerializer(cablesub, many=True)

        return Response(
            {
                "data": data_serializer.data,
                "topup": airtimetopup_serializer.data,
                "paymentgateway": payment_serializer.data,
                "cablesub": cablesub_serializer.data,
            }
        )


class UserListView(generics.ListAPIView):
    permission_classes = (IsAdminUser,)
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class UserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:

            def create_id():
                random.randint(1, 10)
                num_2 = random.randint(1, 10)
                num_3 = random.randint(1, 10)
                return str(num_2) + str(num_3) + str(uuid.uuid4())[:4]

            body = {
                "accountReference": create_id(),
                "accountName": request.user.username,
                "currencyCode": "NGN",
                "contractCode": f"{config.monnify_contract_code}",
                "customerEmail": request.user.email,
                "incomeSplitConfig": [],
                "restrictPaymentSource": False,
                "allowedPaymentSources": {},
                "customerName": request.user.username,
                "getAllAvailableBanks": True,
            }

            if not request.user.accounts:
                data = json.dumps(body)
                ad = requests.post(
                    "https://api.monnify.com/api/v1/auth/login",
                    auth=HTTPBasicAuth(
                        f"{config.monnify_API_KEY}", f"{config.monnify_SECRET_KEY}"
                    ),
                    timeout=10,
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
                    timeout=20,
                )

                mydata = json.loads(ab.text)

                user = request.user
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

        try:
            if request.user.user_type == "Affilliate":
                mtn = TopupPercentage.objects.get(
                    network=Network.objects.get(name="MTN")
                ).Affilliate_percent
                glo = TopupPercentage.objects.get(
                    network=Network.objects.get(name="GLO")
                ).Affilliate_percent
                airtel = TopupPercentage.objects.get(
                    network=Network.objects.get(name="AIRTEL")
                ).Affilliate_percent
                mobile = TopupPercentage.objects.get(
                    network=Network.objects.get(name="9MOBILE")
                ).Affilliate_percent

                mtn_s = TopupPercentage.objects.get(
                    network=Network.objects.get(name="MTN")
                ).share_n_sell_affilliate_percent
                glo_s = TopupPercentage.objects.get(
                    network=Network.objects.get(name="GLO")
                ).share_n_sell_affilliate_percent
                airtel_s = TopupPercentage.objects.get(
                    network=Network.objects.get(name="AIRTEL")
                ).share_n_sell_affilliate_percent
                mobile_s = TopupPercentage.objects.get(
                    network=Network.objects.get(name="9MOBILE")
                ).share_n_sell_affilliate_percent

            elif request.user.user_type == "TopUser":
                mtn = TopupPercentage.objects.get(
                    network=Network.objects.get(name="MTN")
                ).topuser_percent
                glo = TopupPercentage.objects.get(
                    network=Network.objects.get(name="GLO")
                ).topuser_percent
                airtel = TopupPercentage.objects.get(
                    network=Network.objects.get(name="AIRTEL")
                ).topuser_percent
                mobile = TopupPercentage.objects.get(
                    network=Network.objects.get(name="9MOBILE")
                ).topuser_percent

                mtn_s = TopupPercentage.objects.get(
                    network=Network.objects.get(name="MTN")
                ).share_n_sell_topuser_percent
                glo_s = TopupPercentage.objects.get(
                    network=Network.objects.get(name="GLO")
                ).share_n_sell_topuser_percent
                airtel_s = TopupPercentage.objects.get(
                    network=Network.objects.get(name="AIRTEL")
                ).share_n_sell_topuser_percent
                mobile_s = TopupPercentage.objects.get(
                    network=Network.objects.get(name="9MOBILE")
                ).share_n_sell_topuser_percent

            else:
                mtn = TopupPercentage.objects.get(
                    network=Network.objects.get(name="MTN")
                ).percent
                glo = TopupPercentage.objects.get(
                    network=Network.objects.get(name="GLO")
                ).percent
                airtel = TopupPercentage.objects.get(
                    network=Network.objects.get(name="AIRTEL")
                ).percent
                mobile = TopupPercentage.objects.get(
                    network=Network.objects.get(name="9MOBILE")
                ).percent

                mtn_s = TopupPercentage.objects.get(
                    network=Network.objects.get(name="MTN")
                ).share_n_sell_percent
                glo_s = TopupPercentage.objects.get(
                    network=Network.objects.get(name="GLO")
                ).share_n_sell_percent
                airtel_s = TopupPercentage.objects.get(
                    network=Network.objects.get(name="AIRTEL")
                ).share_n_sell_percent
                mobile_s = TopupPercentage.objects.get(
                    network=Network.objects.get(name="9MOBILE")
                ).share_n_sell_percent

        except:
            pass

        try:
            plan_item = Plan.objects.filter(
                network=Network.objects.get(name="MTN")
            ).order_by("plan_amount")
            plan_item_2 = Plan.objects.filter(
                network=Network.objects.get(name="GLO")
            ).order_by("plan_amount")
            plan_item_3 = Plan.objects.filter(
                network=Network.objects.get(name="AIRTEL")
            ).order_by("plan_amount")
            plan_item_4 = Plan.objects.filter(
                network=Network.objects.get(name="9MOBILE")
            ).order_by("plan_amount")

            user = request.user
            if user.user_type == "Affilliate":
                plan_serializer = PlanSerializer2(plan_item, many=True)
                plan_serializerG = PlanSerializer2(
                    Plan.objects.filter(network=Network.objects.get(name="MTN"))
                    .order_by("plan_amount")
                    .filter(plan_type="GIFTING"),
                    many=True,
                )
                plan_serializerSME = PlanSerializer2(
                    Plan.objects.filter(network=Network.objects.get(name="MTN"))
                    .order_by("plan_amount")
                    .filter(plan_type="SME"),
                    many=True,
                )
                plan_serializerCG = PlanSerializer2(
                    Plan.objects.filter(network=Network.objects.get(name="MTN"))
                    .order_by("plan_amount")
                    .filter(plan_type="CORPORATE GIFTING"),
                    many=True,
                )

                plan_serializer_2 = PlanSerializer2(plan_item_2, many=True)
                plan_serializer_3 = PlanSerializer2(plan_item_3, many=True)
                plan_serializer_4 = PlanSerializer2(plan_item_4, many=True)

            elif user.user_type == "TopUser":
                plan_serializer = PlanSerializer3(plan_item, many=True)
                plan_serializerG = PlanSerializer3(
                    Plan.objects.filter(network=Network.objects.get(name="MTN"))
                    .order_by("plan_amount")
                    .filter(plan_type="GIFTING"),
                    many=True,
                )
                plan_serializerSME = PlanSerializer3(
                    Plan.objects.filter(network=Network.objects.get(name="MTN"))
                    .order_by("plan_amount")
                    .filter(plan_type="SME"),
                    many=True,
                )
                plan_serializerCG = PlanSerializer3(
                    Plan.objects.filter(network=Network.objects.get(name="MTN"))
                    .order_by("plan_amount")
                    .filter(plan_type="CORPORATE GIFTING"),
                    many=True,
                )

                plan_serializer_2 = PlanSerializer3(plan_item_2, many=True)
                plan_serializer_3 = PlanSerializer3(plan_item_3, many=True)
                plan_serializer_4 = PlanSerializer3(plan_item_4, many=True)

            else:
                plan_serializer = PlanSerializer(plan_item, many=True)
                plan_serializerG = PlanSerializer(
                    Plan.objects.filter(network=Network.objects.get(name="MTN"))
                    .order_by("plan_amount")
                    .filter(plan_type="GIFTING"),
                    many=True,
                )
                plan_serializerSME = PlanSerializer(
                    Plan.objects.filter(network=Network.objects.get(name="MTN"))
                    .order_by("plan_amount")
                    .filter(plan_type="SME"),
                    many=True,
                )
                plan_serializerCG = PlanSerializer(
                    Plan.objects.filter(network=Network.objects.get(name="MTN"))
                    .order_by("plan_amount")
                    .filter(plan_type="CORPORATE GIFTING"),
                    many=True,
                )
                plan_serializer_2 = PlanSerializer(plan_item_2, many=True)
                plan_serializer_3 = PlanSerializer(plan_item_3, many=True)
                plan_serializer_4 = PlanSerializer(plan_item_4, many=True)

        except:
            pass

        try:
            item = request.user
            cplan_item = CablePlan.objects.filter(
                cablename=Cable.objects.get(name="GOTV")
            ).order_by("plan_amount")
            cplan_item_2 = CablePlan.objects.filter(
                cablename=Cable.objects.get(name="DSTV")
            ).order_by("plan_amount")
            cplan_item_3 = CablePlan.objects.filter(
                cablename=Cable.objects.get(name="STARTIME")
            ).order_by("plan_amount")
            cable_item = CablenameSerializer(Cable.objects.all(), many=True)

        except:
            pass

        try:
            if request.user.user_type == "Affilliate":
                amt1 = Result_Checker_Pin.objects.get(exam_name="WAEC").Affilliate_price
                amt2 = Result_Checker_Pin.objects.get(exam_name="NECO").Affilliate_price
            elif request.user.user_type == "TopUser":
                amt1 = Result_Checker_Pin.objects.get(exam_name="WAEC").TopUser_price
                amt2 = Result_Checker_Pin.objects.get(exam_name="NECO").TopUser_price

            else:
                amt1 = Result_Checker_Pin.objects.get(exam_name="WAEC").amount
                amt2 = Result_Checker_Pin.objects.get(exam_name="NECO").amount

        except:
            pass

        try:
            item = request.user
            user_serializer = CustomUserSerializer(item)
            if request.user.notifications.all():
                x = [x.verb for x in request.user.notifications.all()[:1]][0]
            else:
                x = ""

            return Response(
                {
                    "user": user_serializer.data,
                    "notification": {"message": x},
                    "percentage": {
                        "MTN": {
                            "percent": 0
                            if not Percentage.objects.filter(network__name="MTN")
                            else Percentage.objects.get(network__name="MTN").percent,
                            "phone": Admin_number.objects.filter(network="MTN")
                            .first()
                            .phone_number,
                        },
                        "GLO": {
                            "percent": 0
                            if not Percentage.objects.filter(network__name="GLO")
                            else Percentage.objects.get(network__name="GLO").percent,
                            "phone": Admin_number.objects.filter(network="GLO")
                            .first()
                            .phone_number,
                        },
                        "9MOBILE": {
                            "percent": 0
                            if not Percentage.objects.filter(network__name="9MOBILE")
                            else Percentage.objects.get(
                                network__name="9MOBILE"
                            ).percent,
                            "phone": Admin_number.objects.filter(network="9MOBILE")
                            .first()
                            .phone_number,
                        },
                        "AIRTEL": {
                            "percent": 0
                            if not Percentage.objects.filter(network__name="AIRTEL")
                            else Percentage.objects.get(network__name="AIRTEL").percent,
                            "phone": Admin_number.objects.filter(network="AIRTEL")
                            .first()
                            .phone_number,
                        },
                    },
                    "topuppercentage": {
                        "MTN": {"VTU": mtn, "Share and Sell": mtn_s},
                        "GLO": {"VTU": glo, "Share and Sell": glo_s},
                        "9MOBILE": {"VTU": mobile, "Share and Sell": mobile_s},
                        "AIRTEL": {"VTU": airtel, "Share and Sell": airtel_s},
                    },
                    "Admin_number": Admin_numberSerializer(
                        Admin_number.objects.all(), many=True
                    ).data,
                    #  "Exam":Result_Checker_PinSerializer(Result_Checker_Pin.objects.all(),many=True).data,
                    "Exam": {"WAEC": {"amount": amt1}, "NECO": {"amount": amt2}},
                    "banks": BankAccount_PinSerializer(
                        BankAccount.objects.all(), many=True
                    ).data,
                    "banners": AppAdsImageSerializer(
                        AppAdsImage.objects.all(), many=True
                    ).data,
                    "Dataplans": {
                        "MTN_PLAN": {
                            "CORPORATE": plan_serializerCG.data,
                            "SME": plan_serializerSME.data,
                            "GIFTING": plan_serializerG.data,
                            "ALL": plan_serializer.data,
                        },
                        "GLO_PLAN": {"ALL": plan_serializer_2.data},
                        "AIRTEL_PLAN": {"ALL": plan_serializer_3.data},
                        "9MOBILE_PLAN": {"ALL": plan_serializer_4.data},
                    },
                    "Cableplan": {
                        "GOTVPLAN": CablePlanSerializer(cplan_item, many=True).data,
                        "DSTVPLAN": CablePlanSerializer(cplan_item_2, many=True).data,
                        "STARTIMEPLAN": CablePlanSerializer(
                            cplan_item_3, many=True
                        ).data,
                        "cablename": cable_item.data,
                    },
                    "support_phone_number": config.support_phone_number,
                    "upgrade_to_affiliate_fee": config.affiliate_upgrade_fee,
                    "upgrade_to_topuser_fee": config.topuser_upgrade_fee,
                    "recharge": {
                        "mtn": Recharge_pin.objects.filter(
                            network=Network.objects.get(name="MTN")
                        )
                        .filter(available=True)
                        .count(),
                        "glo": Recharge_pin.objects.filter(
                            network=Network.objects.get(name="GLO")
                        )
                        .filter(available=True)
                        .count(),
                        "airtel": Recharge_pin.objects.filter(
                            network=Network.objects.get(name="AIRTEL")
                        )
                        .filter(available=True)
                        .count(),
                        "9mobile": Recharge_pin.objects.filter(
                            network=Network.objects.get(name="9MOBILE")
                        )
                        .filter(available=True)
                        .count(),
                        "mtn_pin": RechargeSerializer(
                            Recharge.objects.filter(
                                network=Network.objects.get(name="MTN")
                            ),
                            many=True,
                        ).data,
                        "glo_pin": RechargeSerializer(
                            Recharge.objects.filter(
                                network=Network.objects.get(name="GLO")
                            ),
                            many=True,
                        ).data,
                        "airtel_pin": RechargeSerializer(
                            Recharge.objects.filter(
                                network=Network.objects.get(name="AIRTEL")
                            ),
                            many=True,
                        ).data,
                        "9mobile_pin": RechargeSerializer(
                            Recharge.objects.filter(
                                network=Network.objects.get(name="9MOBILE")
                            ),
                            many=True,
                        ).data,
                    },
                }
            )

        except CustomUser.DoesNotExist:
            return Response(status=404)


class AlertAPIView(APIView):
    def get(self, request, format=None):
        if Info_Alert.objects.all():
            y = [x.message for x in Info_Alert.objects.all()[:1]][0]

        else:
            y = ""

        return Response({"alert": y})


class CablenameAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            cplan_item = CablePlan.objects.filter(
                cablename=Cable.objects.get(name="GOTV")
            ).order_by("plan_amount")
            cplan_item_2 = CablePlan.objects.filter(
                cablename=Cable.objects.get(name="DSTV")
            ).order_by("plan_amount")
            cplan_item_3 = CablePlan.objects.filter(
                cablename=Cable.objects.get(name="STARTIME")
            ).order_by("plan_amount")
            cable_item = CablenameSerializer(Cable.objects.all(), many=True)

            return Response(
                {
                    "GOTVPLAN": CablePlanSerializer(cplan_item, many=True).data,
                    "DSTVPLAN": CablePlanSerializer(cplan_item_2, many=True).data,
                    "STARTIME": CablePlanSerializer(cplan_item_3, many=True).data,
                    "cablename": cable_item.data,
                }
            )

        except:
            return Response(status=404)


class DiscoAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            disko_item = DiscoSerializer(Disco_provider_name.objects.all(), many=True)

            return Response(
                {
                    "disko": disko_item.data,
                }
            )

        except:
            return Response(status=404)


class NetworkAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            plan_item = Plan.objects.filter(
                network=Network.objects.get(name="MTN")
            ).order_by("plan_amount")
            plan_item_2 = Plan.objects.filter(
                network=Network.objects.get(name="GLO")
            ).order_by("plan_amount")
            plan_item_3 = Plan.objects.filter(
                network=Network.objects.get(name="AIRTEL")
            ).order_by("plan_amount")
            plan_item_4 = Plan.objects.filter(
                network=Network.objects.get(name="9MOBILE")
            ).order_by("plan_amount")

            plan_serializer = PlanSerializer(plan_item, many=True)
            plan_serializer_2 = PlanSerializer(plan_item_2, many=True)
            plan_serializer_3 = PlanSerializer(plan_item_3, many=True)
            plan_serializer_4 = PlanSerializer(plan_item_4, many=True)

            return Response(
                {
                    "MTN_PLAN": plan_serializer.data,
                    "GLO_PLAN": plan_serializer_2.data,
                    "AIRTEL_PLAN": plan_serializer_3.data,
                    "9MOBILE_PLAN": plan_serializer_4.data,
                }
            )

        except:
            return Response(status=404)


class DataAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        try:
            item = Data.objects.filter(user=request.user).get(pk=id)
            serializer = DataSerializer(item)
            return Response(serializer.data)
        except Data.DoesNotExist:
            return Response(status=404)


class DataAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Data.objects.filter(user=request.user).order_by("-create_date")
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = DataSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        status = "processing"

        serializer = DataSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            (serializer.validated_data["user"]).username
            num = serializer.validated_data["mobile_number"]
            plan = serializer.validated_data["plan"]

            def create_id():
                random.randint(1, 10)
                num_2 = random.randint(1, 10)
                num_3 = random.randint(1, 10)
                return str(num_2) + str(num_3) + str(uuid.uuid4())

            ident = create_id()

            net = str(serializer.validated_data["network"])
            user = serializer.validated_data["user"]
            errors = {}
            api_response = ""

            previous_bal = user.Account_Balance

            if user.user_type == "Affilliate":
                amount = float(plan.Affilliate_price)

            elif user.user_type == "API":
                amount = float(plan.api_price)

            elif user.user_type == "TopUser":
                amount = float(plan.TopUser_price)
            else:
                amount = float(plan.plan_amount)

            #            try:
            #                if plan.commission > 0:
            #                    if user.referer_username:
            #                        if CustomUser.objects.filter(username__iexact = user.referer_username).exists():
            #                            referer  = CustomUser.objects.get(username__iexact = user.referer_username)
            #
            #                            # if  referer.user_type == "TopUser" or referer.user_type == "Affilliate":
            #                            if  user.user_type == "Smart Earner":
            #                                com =  referer.Referer_Bonus
            #                                referer.ref_deposit(plan.commission)
            #
            #                                Wallet_summary.objects.create(user= referer, product="[Referal bonus ] you received  N{} commission  from your referal {} Data Transaction".format(plan.commission,user.username), amount = plan.commission, previous_balance = com, after_balance= (com + plan.commission))
            #
            #                                notify.send(referer, recipient=referer, verb=" [Referal bonus ] you received   N{}commission  from your referal {} Data Transaction".format(plan.commission,user.username))
            #
            #            except:
            #                pass

            with transaction.atomic():
                check = user.withdraw(user.id, amount)
                if check is False:
                    errors["error"] = "Y insufficient balance "
                    raise serializers.ValidationError(errors)
                Wallet_summary.objects.create(
                    user=user,
                    product="{} {}{}   N{}  DATA topup  with {} ".format(
                        net, plan.plan_size, plan.plan_Volume, amount, num
                    ),
                    amount=amount,
                    previous_balance=previous_bal,
                    after_balance=(previous_bal - amount),
                )

            def sendmessage(sender, message, to, route):
                baseurl = f"https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}"
                requests.get(baseurl, verify=False)

            def senddatasmeplug(net, plan_id, num):
                url = "https://smeplug.ng/api/v1/data/purchase"
                payload = {"network_id": net, "plan_id": plan_id, "phone": num}
                payload = json.dumps(payload)

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.sme_plug_secret_key}",
                }
                # print("payload",payload)
                response = requests.request("POST", url, headers=headers, data=payload)
                return response

            def sendsmedata(shortcode, servercode, message, mytype):
                payload = {
                    "shortcode": shortcode,
                    "servercode": servercode,
                    "message": message,
                    "token": f"{config.simhost_API_key}",
                    "type": mytype,
                }

                baseurl = "https://ussd.simhosting.ng/api/?"
                requests.get(baseurl, params=payload, verify=False)

            def senddata_ussdsimhost(ussd, servercode, mytype):
                payload = {
                    "ussd": ussd,
                    "servercode": servercode,
                    "token": f"{config.simhost_API_key}",
                    "type": mytype,
                }

                baseurl = "https://ussd.simhosting.ng/api/?"
                requests.get(baseurl, params=payload, verify=False)
                # print(response.text)

            def senddata_simhostng(ussd, servercode, mytype, sim, msg=None):
                # print('------------ simhostng.COM DATA RESPONSE -----------------')
                if mytype == "SMS":
                    url = "https://simhostng.com/api/sms"
                    requests.post(
                        f"{url}?apikey={config.simhost_API_key}&server={servercode}&sim={sim}&number={ussd}&message={msg}"
                    )
                    # print(response.text)
                else:
                    url = "https://simhostng.com/api/ussd"
                    requests.post(
                        f"{url}?apikey={config.simhost_API_key}&server={servercode}&sim={sim}&number={urllib.parse.quote(ussd)}"
                    )
                    # print(response.text)

            def msorg_senddata(website, token, netid, num, plan_id):
                url = f"{website}/api/data/"

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Token {token}",
                }
                param = {
                    "network": netid,
                    "mobile_number": num,
                    "plan": plan_id,
                    "Ported_number": True,
                }
                param_data = json.dumps(param)
                try:
                    response = requests.post(
                        url, headers=headers, data=param_data, timeout=60
                    )
                    logging.error(
                        "###################################################################"
                    )
                    logging.error(url)
                    logging.error(response.status_code)
                    logging.error(response.text)

                    print(
                        "###################################################################"
                    )

                    resp = json.loads(response.text)
                    if "Status" in resp and resp["Status"] == "successful":
                        return "successful"
                    elif "Status" in resp and resp["Status"] == "processing":
                        return "successful"
                    else:
                        return "failed"

                except requests.exceptions.HTTPError:
                    return "failed"
                except requests.exceptions.ConnectionError:
                    return "failed"
                except requests.exceptions.Timeout:
                    return "processing"
                except requests.exceptions.RequestException:
                    return "failed"

            def Msplug_Data_vending(net, plan, num, sim, rtype, device_id):
                url = "https://www.msplug.com/api/buy-data/"
                payload = {
                    "network": net,
                    "plan_id": plan,
                    "phone": num,
                    "device_id": device_id,
                    "sim_slot": sim,
                    "request_type": rtype,
                    "webhook_url": "http://www.legitdata.com.ngbuydata/webhook/",
                }
                headers = {
                    "Authorization": f"Token {config.msplug_API_key}",
                    "Content-Type": "application/json",
                }

                requests.post(url, headers=headers, data=json.dumps(payload))

            def VTUAUTO_Shortcode(shortcode, message, device_id, slot):
                payload = {
                    "device_id": device_id,
                    "message": message,
                    "message_recipient": shortcode,
                    "sim": slot,
                }
                requests.post(
                    "https://vtuauto.ng/api/v1/request/sms",
                    auth=HTTPBasicAuth(
                        f"{config.vtu_auto_email}", f"{config.vtu_auto_password}"
                    ),
                    data=payload,
                )
                # print(response.text)

            def VTUAUTO_USSD(ussd, device_id, sim):
                payload = {"device_id": device_id, "ussd_string": ussd, "sim": sim}
                requests.post(
                    "https://vtuauto.ng/api/v1/request/ussd",
                    auth=HTTPBasicAuth(
                        f"{config.vtu_auto_email}", f"{config.vtu_auto_password}"
                    ),
                    data=payload,
                )
                # print(response.text)

            def senddatasmeify(net, plan, num, validity):
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {SmeifyAuth.objects.first().get_token()}",
                }
                url = "https://api.smeify.com/api/v2/data"
                payload = json.dumps({"phones": str(num), "plan": plan})
                requests.post(url, headers=headers, data=payload)

            if net == "MTN":
                mtn_text = SME_text.objects.get(network=Network.objects.get(name="MTN"))

                if plan.plan_type == "GIFTING":
                    if (
                        Network.objects.get(name=net).gifting_vending_medium
                        == "SMEPLUG"
                    ):
                        resp = senddatasmeplug("1", plan.smeplug_id, num)
                        status = "successful"
                        try:
                            if resp.status_code == 400 or resp.status_code == 404:
                                status = "failed"
                            else:
                                result = json.loads(resp.text)
                                ident = result["data"]["reference"]

                                if result["transaction"]["status"] == "failed":
                                    status = "failed"
                                else:
                                    pass
                        except:
                            pass

                    elif (
                        Network.objects.get(name=net).gifting_vending_medium == "SMEIFY"
                    ):
                        senddatasmeify(
                            net, plan.smeify_plan_name_id, num, plan.month_validate
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).gifting_data_vending_medium
                        == "CHEAPESTDATASUB"
                    ):
                        print("")
                        print(".........sending DATA to CHEAPESTDATASUB ..........")

                        url = "https://cheapestsub.com/account/api/v1/buycorporate"

                        payload = json.dumps(
                            {
                                "bundle": f"{int(plan.plan_size)}{plan.plan_Volume}",
                                "mobile": str(num),
                            }
                        )
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": "Basic TWFsaWtpZGk6dUdNcjR6NEpAaDVCcQ==",
                        }

                        response = requests.request(
                            "POST", url, headers=headers, data=payload
                        )
                        print(payload)
                        print(response.text)

                        status = "successful"

                    elif (
                        Network.objects.get(name=net).gifting_vending_medium == "QTopUp"
                    ):
                        url = f"https://sme.qtopup.com.ng/api/v1/data?api-token={config.qtopup_api_key}&network=MTNCG&phone={num}&amount={plan.qtopup_id}"
                        headers = {"Content-Type": "application/json"}
                        response = requests.get(url, headers=headers)
                        result = response.text

                        # print('')
                        # print('SENDING TO qtopup')
                        # print('url = ', url)
                        # print('result = ', result)

                        Wallet_summary.objects.create(
                            user=user,
                            product="{} {}{}   N{}  DATA topup topup  with {} ".format(
                                net, plan.plan_size, plan.plan_Volume, amount, num
                            ),
                            amount=amount,
                            previous_balance=previous_bal,
                            after_balance=(previous_bal - amount),
                        )
                        status = "successful"

                    # elif Network.objects.get(name=net).gifting_vending_medium == "MSORG_DEVELOPED_WEBSITE":
                    #           msorg_senddata(Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                    #           status = "successful"
                    elif (
                        Network.objects.get(name=net).gifting_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        msorg_senddata(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).gifting_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        msorg_senddata(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id_2,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).gifting_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        msorg_senddata(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id_3,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).gifting_vending_medium
                        == "SIMHOST"
                    ):

                        def sendussddata(ussd, num, servercode):
                            payload = {
                                "ussd": ussd,
                                "servercode": servercode,
                                "multistep": num,
                                "token": f"{config.simhost_API_key}",
                            }

                            baseurl = "https://ussd.simhosting.ng/api/ussd/?"
                            requests.get(baseurl, params=payload, verify=False)
                            # print(response.text)

                        ussd = plan.ussd_string
                        sendussddata(
                            f"{ussd}", num, mtn_text.sim_host_server_id_for_data
                        )
                        status = "successful"

                    elif Network.objects.get(name=net).gifting_vending_medium == "UWS":

                        def create_id():
                            random.randint(1, 10)
                            num_2 = random.randint(1, 10)
                            num_3 = random.randint(1, 10)
                            return str(num_2) + str(num_3) + str(uuid.uuid4())

                        ident = create_id()

                        while Data.objects.filter(ident=ident).exists():
                            ident = create_id()

                        url = "https://api.uws.com.ng/api/v1/mtn_coperate_data/purchase"

                        headers = {
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "Authorization": f"Bearer {config.uws_token}",
                        }
                        payload = {
                            "phone": num,
                            "plan_id": str(plan.uws_plan_name_id),
                            "customRef": ident,
                        }

                        response = requests.request(
                            "POST", url, headers=headers, data=json.dumps(payload)
                        )
                        result = json.loads(response.text)
                        # print(result)
                        # print(response.status_code)

                        if result["status"] == "success":
                            status = "successful"

                        elif result["status"] == "failed":
                            status = "failed"

                        else:
                            status = "processing"

                    else:
                        try:
                            sendmessage(
                                "myweb",
                                "{0} want to buy {1}{3}  M_TN data on {2} ".format(
                                    user.username, plan.plan_size, num, plan.plan_Volume
                                ),
                                f"{config.sms_notification_number}",
                                "02",
                            )
                            status = "successful"
                        except:
                            pass

                elif plan.plan_type == "CORPORATE GIFTING":
                    if (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "SMEPLUG"
                    ):
                        resp = senddatasmeplug("1", plan.smeplug_id, num)
                        status = "successful"

                        try:
                            if resp.status_code == 400 or resp.status_code == 404:
                                status = "failed"
                            else:
                                result = json.loads(resp.text)
                                ident = result["data"]["reference"]

                                if result["transaction"]["status"] == "failed":
                                    status = "failed"
                                else:
                                    pass
                        except:
                            pass

                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "CHEAPESTDATASUB"
                    ):
                        print("")
                        print(".........sending DATA to CHEAPESTDATASUB ..........")

                        url = "https://cheapestsub.com/account/api/v1/buycorporate"

                        payload = json.dumps(
                            {
                                "bundle": f"{int(plan.plan_size)}{plan.plan_Volume}",
                                "mobile": str(num),
                            }
                        )
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": "Basic TWFsaWtpZGk6dUdNcjR6NEpAaDVCcQ==",
                        }

                        response = requests.request(
                            "POST", url, headers=headers, data=payload
                        )
                        print(payload)
                        print(response.text)

                        status = "successful"

                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "SMEIFY"
                    ):
                        senddatasmeify(
                            net, plan.smeify_plan_name_id, num, plan.month_validate
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "QTopUp"
                    ):
                        url = f"https://sme.qtopup.com.ng/api/v1/data?api-token={config.qtopup_api_key}&network=MTNCG&phone={num}&amount={plan.qtopup_id}"
                        headers = {"Content-Type": "application/json"}
                        response = requests.get(url, headers=headers)
                        result = response.text

                        # print('')
                        # print('SENDING TO qtopup')
                        # print('url = ', url)
                        # print('result = ', result)

                        Wallet_summary.objects.create(
                            user=user,
                            product="{} {}{}   N{}  DATA topup topup  with {} ".format(
                                net, plan.plan_size, plan.plan_Volume, amount, num
                            ),
                            amount=amount,
                            previous_balance=previous_bal,
                            after_balance=(previous_bal - amount),
                        )
                        status = "successful"

                    # elif Network.objects.get(name=net).corporate_data_vending_medium == "MSORG_DEVELOPED_WEBSITE":
                    #           msorg_senddata(Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                    #           status = "successful"
                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        msorg_senddata(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        msorg_senddata(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id_2,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        msorg_senddata(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id_3,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "SIMHOST"
                    ):

                        def sendsmedata(ussd, num, servercode):
                            payload = {
                                "ussd": ussd,
                                "servercode": servercode,
                                "multistep": num,
                                "token": f"{config.simhost_API_key}",
                            }

                            baseurl = "https://ussd.simhosting.ng/api/ussd/?"
                            requests.get(baseurl, params=payload, verify=False)
                            # print(response.text)

                        ussd = plan.ussd_string
                        senddata_ussdsimhost(
                            f"{ussd}", num, mtn_text.sim_host_server_id_for_data
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "UWS"
                    ):

                        def create_id():
                            random.randint(1, 10)
                            num_2 = random.randint(1, 10)
                            num_3 = random.randint(1, 10)
                            return str(num_2) + str(num_3) + str(uuid.uuid4())

                        ident = create_id()

                        while Data.objects.filter(ident=ident).exists():
                            ident = create_id()

                        url = "https://api.uws.com.ng/api/v1/mtn_coperate_data/purchase"

                        headers = {
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "Authorization": f"Bearer {config.uws_token}",
                        }
                        payload = {
                            "phone": num,
                            "plan_id": str(plan.uws_plan_name_id),
                            "customRef": ident,
                        }

                        response = requests.request(
                            "POST", url, headers=headers, data=json.dumps(payload)
                        )
                        result = json.loads(response.text)
                        # print(result)
                        # print(response.status_code)

                        if result["status"] == "success":
                            status = "successful"

                        elif result["status"] == "failed":
                            status = "failed"

                        else:
                            status = "processing"

                    else:
                        try:
                            sendmessage(
                                "myweb",
                                "{0} want to buy {1}{3}  M_TN data on {2} ".format(
                                    user.username, plan.plan_size, num, plan.plan_Volume
                                ),
                                f"{config.sms_notification_number}",
                                "02",
                            )
                            status = "successful"
                        except:
                            pass

                else:
                    if Network.objects.get(name=net).data_vending_medium == "SIMHOST":
                        if plan.plan_type == "SME":
                            if mtn_text.mtn_sme_route == "SMS":
                                command = plan.sms_command.replace("n", num).replace(
                                    "p", mtn_text.pin
                                )
                                sendsmedata(
                                    "131",
                                    mtn_text.sim_host_server_id_for_data,
                                    f"{command}",
                                    "SHORTCODE",
                                )
                                status = "successful"
                            else:
                                ussd = plan.ussd_string.replace("n", num).replace(
                                    "p", mtn_text.pin
                                )
                                senddata_ussdsimhost(
                                    f"{ussd}",
                                    mtn_text.sim_host_server_id_for_data,
                                    "USSD",
                                )
                                status = "successful"
                        else:
                            sendmessage(
                                "myweb",
                                "{0} want to buy {1}{3}  M_TN data on {2} ".format(
                                    user.username, plan.plan_size, num, plan.plan_Volume
                                ),
                                mtn_text.number,
                                "02",
                            )

                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "MYSIMHOSTING"
                    ):

                        def smeserver(plan_id, num):
                            url = "https://api.mysimhosting.cloud/v1/data/"

                            payload = {
                                "serverName": "LegitData-6362a353e8c85",
                                "plan": plan_id,
                                "number": num,
                                "senderID": "LegitData",
                            }

                            payload_data = json.dumps(payload)
                            headers = {
                                "Content-Type": "application/json",
                                "Authorization": "Bearer 4441d363345eebda4e01adfa0759eaa874151639762364d61371881647725921163",
                            }

                            response = requests.request(
                                "POST", url, headers=headers, data=payload_data
                            )
                            # print("##########################################################################")
                            # print("payload ==",payload)
                            # print("result =====",response.text)
                            # print("result status =====",response.status_code)
                            # print("##########################################################################")

                            if (
                                response.status_code == 200
                                or response.status_code == 201
                            ):
                                result = json.loads(response.text)
                                print("print result ===", result)

                                if "status" in result and result["status"] == "failed":
                                    return "failed"

                                    # if "error" in result :
                                    #     return "failed",result["error"]
                                    # else:
                                    #     return "failed",result["message"]

                                else:
                                    return "successful"

                                    # if "error" in result :
                                    #     return "successful",result["error"]
                                    # else:
                                    #     return "successful",result["message"]

                            elif (
                                response.status_code == 400
                                or response.status_code == 401
                            ):
                                return "failed", "No Response"

                            else:
                                return "processing", "Response not Available"

                        result = smeserver(plan.mysimhosting_plan_id, num)
                        status = result
                        # api_response = result[1]

                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "SIM_SERVER"
                    ):

                        def create_id():
                            random.randint(1, 10)
                            num_2 = random.randint(1, 10)
                            num_3 = random.randint(1, 10)
                            return str(num_2) + str(num_3) + str(uuid.uuid4())

                        ident = create_id()

                        def sendsimserver(num, plan_id):
                            url = "https://api.simservers.io"

                            payload = {
                                "process": "buy",
                                "api_key": "7x4ezoqrvuhz4d1a7t7aq8k5opissi0jgxjp4hfyxa8g90dgrkfmzipnndr604u9auuwv9ggwejwgruryhzf0ekp470j2vvb23ko9ulpn03zvdta433bb0rtw3m0otfn",
                                "product_code": plan_id,
                                "amount": "1",
                                "recipient": num,
                                "callback": " ",
                                "user_reference": ident,
                            }

                            payload_data = json.dumps(payload)
                            headers = {
                                "Content-Type": "application/json",
                            }

                            try:
                                response = requests.request(
                                    "POST",
                                    url,
                                    headers=headers,
                                    data=payload_data,
                                    timeout=60,
                                )
                                # print("##########################################################################")
                                # print("payload ==",payload)
                                # print("result =====",response.text)
                                # print("result status =====",response.status_code)
                                # print("##########################################################################")
                                # if response.status_code == 200 or response.status_code == 201:
                                #     result = json.loads(response.text)
                                #     print("print result ===", result)

                                #     if "status" in result and result["status"] == True:
                                #             return 'successful'

                                #     else:
                                #             return "failed"

                                # elif response.status_code == 400 or response.status_code == 401:
                                #     return "failed"

                                # else:
                                #     return "processing"

                                if (
                                    response.status_code == 200
                                    or response.status_code == 201
                                ):
                                    result = json.loads(response.text)
                                    print("print result ===", result)

                                    if (
                                        "status" in result
                                        and result["data"]["text_status"] == "success"
                                    ):
                                        return (
                                            "successful",
                                            result["data"]["true_response"],
                                        )
                                    elif (
                                        "status" in result
                                        and result["data"]["text_status"] == "pending"
                                    ):
                                        return (
                                            "pending",
                                            result["data"]["true_response"],
                                        )
                                    else:
                                        return "failed", result["data"]["true_response"]
                                elif (
                                    response.status_code == 400
                                    or response.status_code == 408
                                    or response.status_code == 502
                                    or response.status_code == 401
                                ):
                                    return "failed", "No Response"

                                else:
                                    return "processing", "Response Not available"

                            except requests.exceptions.HTTPError:
                                return "failed", ""
                            except requests.exceptions.ConnectionError:
                                return "failed", ""
                            except requests.exceptions.Timeout:
                                return "processing", ""
                            except requests.exceptions.RequestException:
                                return "failed", ""

                        result = sendsimserver(num, plan.simserver_plan_id)
                        status = result[0]
                        api_response = result[1]
                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "SIMHOST_NG"
                    ):
                        if plan.plan_type == "SME":
                            if mtn_text.mtn_sme_route == "SMS":
                                command = plan.sms_command.replace("n", num).replace(
                                    "p", mtn_text.pin
                                )
                                senddata_simhostng(
                                    "131",
                                    mtn_text.sim_host_server_id_for_data,
                                    "SMS",
                                    mtn_text.vtu_sim_slot,
                                    f"{command}",
                                )  ## simcard.ng
                                status = "successful"
                            else:
                                ussd = plan.ussd_string.replace("n", num).replace(
                                    "p", mtn_text.pin
                                )
                                senddata_simhostng(
                                    f"{ussd}",
                                    mtn_text.sim_host_server_id_for_data,
                                    "USSD",
                                    mtn_text.vtu_sim_slot,
                                )
                                status = "successful"
                        else:
                            sendmessage(
                                "myweb",
                                "{0} want to buy {1}{3}  M_TN data on {2} ".format(
                                    user.username, plan.plan_size, num, plan.plan_Volume
                                ),
                                mtn_text.number,
                                "02",
                            )

                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "CHEAPESTDATASUB"
                    ):
                        print("")
                        print(".........sending DATA to CHEAPESTDATASUB ..........")

                        url = "https://cheapestsub.com/account/api/v1/buycorporate"

                        payload = json.dumps(
                            {
                                "bundle": f"{int(plan.plan_size)}{plan.plan_Volume}",
                                "mobile": str(num),
                            }
                        )
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": "Basic TWFsaWtpZGk6dUdNcjR6NEpAaDVCcQ==",
                        }

                        response = requests.request(
                            "POST", url, headers=headers, data=payload
                        )
                        print(payload)
                        print(response.text)

                        status = "successful"

                    elif Network.objects.get(name=net).data_vending_medium == "UWS":

                        def create_id():
                            random.randint(1, 10)
                            num_2 = random.randint(1, 10)
                            num_3 = random.randint(1, 10)
                            return str(num_2) + str(num_3) + str(uuid.uuid4())

                        ident = create_id()

                        while Data.objects.filter(ident=ident).exists():
                            ident = create_id()

                        url = "https://api.uws.com.ng/api/v1/sme_data/purchase"

                        payload = {
                            "phone": num,
                            "network_id": "2",
                            "plan_id": str(plan.uws_plan_name_id),
                            "customRef": ident,
                        }

                        headers = {
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "Authorization": f"Bearer {config.uws_token}",
                        }

                        response = requests.request(
                            "POST", url, headers=headers, data=json.dumps(payload)
                        )
                        result = json.loads(response.text)
                        # print(result)
                        # print(response.status_code)

                        if result["status"] == "success":
                            status = "successful"

                        elif result["status"] == "failed":
                            status = "failed"

                        else:
                            status = "processing"

                    elif Network.objects.get(name=net).data_vending_medium == "SMEPLUG":
                        resp = senddatasmeplug("1", plan.smeplug_id, num)
                        status = "successful"

                        try:
                            if resp.status_code == 400 or resp.status_code == 404:
                                status = "failed"
                            else:
                                result = json.loads(resp.text)
                                ident = result["data"]["reference"]

                                if result["transaction"]["status"] == "failed":
                                    status = "failed"
                                else:
                                    pass
                        except:
                            pass

                    elif Network.objects.get(name=net).data_vending_medium == "SMS":
                        sendmessage(
                            "myweb",
                            "{0} want to buy {1}{3}  M_TN data on {2} ".format(
                                user.username, plan.plan_size, num, plan.plan_Volume
                            ),
                            f"{config.sms_notification_number}",
                            "02",
                        )

                    # elif Network.objects.get(name=net).data_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                    #           msorg_senddata(Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                    #           status = "successful"
                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        msorg_senddata(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        msorg_senddata(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id_2,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        msorg_senddata(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id_3,
                        )
                        status = "successful"

                    elif Network.objects.get(name=net).data_vending_medium == "VTUAUTO":
                        if mtn_text.mtn_sme_route == "SMS":
                            command = plan.sms_command.replace("n", num).replace(
                                "p", mtn_text.pin
                            )
                            VTUAUTO_Shortcode(
                                "131",
                                f"{command}",
                                mtn_text.vtu_auto_device_id,
                                mtn_text.vtu_sim_slot,
                            )

                            status = "successful"
                        else:
                            ussd = plan.ussd_string.replace("n", num).replace(
                                "p", mtn_text.pin
                            )
                            VTUAUTO_USSD(
                                f"{ussd}",
                                mtn_text.vtu_auto_device_id,
                                mtn_text.vtu_sim_slot,
                            )
                            status = "successful"

                    elif Network.objects.get(name=net).data_vending_medium == "MSPLUG":
                        if mtn_text.mtn_sme_route == "SMS":
                            Msplug_Data_vending(
                                net,
                                plan.msplug_plan_name_id,
                                num,
                                mtn_text.msplug_sim_slot,
                                "SMS",
                                mtn_text.msplug_device_id,
                            )
                            status = "successful"
                        else:
                            Msplug_Data_vending(
                                net,
                                plan.msplug_plan_name_id,
                                num,
                                mtn_text.msplug_sim_slot,
                                "USSD",
                                mtn_text.msplug_device_id,
                            )
                            status = "successful"

                    elif Network.objects.get(name=net).data_vending_medium == "SMEIFY":
                        senddatasmeify(
                            net, plan.smeify_plan_name_id, num, plan.month_validate
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "OGDAMS_DOUBLE"
                    ):

                        def create_id():
                            random.randint(1, 10)
                            num_2 = random.randint(1, 10)
                            random.randint(1, 10)
                            x = uuid.uuid4()
                            return str(num_2) + str(x)[:8]

                        ident = create_id()

                        def sendogdamnew(net_id, plan_id, num):
                            url = "https://simhosting.ogdams.ng/api/v1/vend/data"

                            payload = json.dumps(
                                {
                                    "networkId": net_id,
                                    "planId": plan_id,
                                    "phoneNumber": num,
                                    "reference": ident,
                                }
                            )
                            headers = {
                                "Authorization": "Bearer sk_live_9ea3607c-5650-4440-971f-d9921d397e25",
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                            }

                            response = requests.request(
                                "POST", url, headers=headers, data=payload
                            )

                            print("response ====", response.text)
                            print("fdschfdfjdfkfd", response.status_code)
                            if (
                                response.status_code == 200
                                or response.status_code == 202
                            ):
                                resp = json.loads(response.text)
                                if "status" in resp and resp["status"] is True:
                                    return "successful"
                                else:
                                    return "failed"

                            elif (
                                response.status_code == 424
                                or response.status_code == 400
                            ):
                                return "failed"

                            else:
                                return "processing"

                        def sendogdamold(net_id, plan_id, num):
                            url = "https://simhosting.ogdams.ng/api/v1/vend/data"

                            payload = json.dumps(
                                {
                                    "networkId": net_id,
                                    "planId": plan_id,
                                    "phoneNumber": num,
                                    "reference": ident,
                                }
                            )
                            headers = {
                                "Authorization": "Bearer sk_live_7f0af162-3bf1-4f20-af09-4a327123034a",
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                            }

                            response = requests.request(
                                "POST", url, headers=headers, data=payload
                            )

                            print("response ====", response.text)
                            print("fdschfdfjdfkfd", response.status_code)
                            if (
                                response.status_code == 200
                                or response.status_code == 202
                            ):
                                resp = json.loads(response.text)
                                if "status" in resp and resp["status"] is True:
                                    return "successful"
                                else:
                                    return "failed"

                            elif (
                                response.status_code == 424
                                or response.status_code == 400
                            ):
                                return "failed"

                            else:
                                return "processing"

                        if float(plan.plan_size) == 1.0:
                            if (
                                mtn_text.data_vending_medium_for_1_gb_under_ogdams_double_account
                                == "OGDAMS1"
                            ):
                                resp = sendogdamnew("1", plan.ogdams_plan_id, num)
                                status = resp
                            else:
                                resp = sendogdamold("1", plan.ogdams_plan_id, num)
                                status = resp
                        elif float(plan.plan_size) == 500.0:
                            if (
                                mtn_text.data_vending_medium_for_500_mb_under_ogdams_double_account
                                == "OGDAMS1"
                            ):
                                resp = sendogdamnew("1", plan.ogdams_plan_id, num)
                                status = resp
                            else:
                                resp = sendogdamold("1", plan.ogdams_plan_id, num)
                                status = resp

                        elif float(plan.plan_size) == 2.0:
                            if (
                                mtn_text.data_vending_medium_for_2_gb_under_ogdams_double_account
                                == "OGDAMS1"
                            ):
                                resp = sendogdamnew("1", plan.ogdams_plan_id, num)
                                status = resp
                            else:
                                resp = sendogdamold("1", plan.ogdams_plan_id, num)
                                status = resp

                        elif float(plan.plan_size) == 3.0:
                            if (
                                mtn_text.data_vending_medium_for_3_gb_under_ogdams_double_account
                                == "OGDAMS1"
                            ):
                                resp = sendogdamnew("1", plan.ogdams_plan_id, num)
                                status = resp
                            else:
                                resp = sendogdamold("1", plan.ogdams_plan_id, num)
                                status = resp
                        elif float(plan.plan_size) == 5.0:
                            if (
                                mtn_text.data_vending_medium_for_5_gb_under_ogdams_double_account
                                == "OGDAMS1"
                            ):
                                resp = sendogdamnew("1", plan.ogdams_plan_id, num)
                                status = resp
                            else:
                                resp = sendogdamold("1", plan.ogdams_plan_id, num)
                                status = resp

                        elif float(plan.plan_size) == 10.0:
                            if (
                                mtn_text.data_vending_medium_for_10_gb_under_ogdams_double_account
                                == "OGDAMS1"
                            ):
                                resp = sendogdamnew("1", plan.ogdams_plan_id, num)
                                status = resp
                            else:
                                resp = sendogdamold("1", plan.ogdams_plan_id, num)
                                status = resp
                    elif Network.objects.get(name=net).data_vending_medium == "OGDAMS2":

                        def create_id():
                            random.randint(1, 10)
                            num_2 = random.randint(1, 10)
                            random.randint(1, 10)
                            x = uuid.uuid4()
                            return str(num_2) + str(x)[:8]

                        ident = create_id()

                        def sendogdam(net_id, plan_id, num):
                            url = "https://simhosting.ogdams.ng/api/v1/vend/data"

                            payload = json.dumps(
                                {
                                    "networkId": net_id,
                                    "planId": plan_id,
                                    "phoneNumber": num,
                                    "reference": ident,
                                }
                            )
                            headers = {
                                "Authorization": "Bearer sk_live_7f0af162-3bf1-4f20-af09-4a327123034a",
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                            }

                            response = requests.request(
                                "POST", url, headers=headers, data=payload, verify=False
                            )
                            print(response.text)

                            if (
                                response.status_code == 200
                                or response.status_code == 202
                            ):
                                resp = json.loads(response.text)
                                if "status" in resp and resp["status"] is True:
                                    return "successful"
                                else:
                                    return "failed"

                            elif (
                                response.status_code == 424
                                or response.status_code == 400
                            ):
                                return "failed"

                            else:
                                return "processing"

                        resp = sendogdam("1", plan.ogdams_plan_id, num)
                        status = resp

                    elif Network.objects.get(name=net).data_vending_medium == "OGDAMS":

                        def create_id():
                            random.randint(1, 10)
                            num_2 = random.randint(1, 10)
                            random.randint(1, 10)
                            x = uuid.uuid4()
                            return str(num_2) + str(x)[:8]

                        ident = create_id()

                        def sendogdam(net_id, plan_id, num):
                            url = "https://simhosting.ogdams.ng/api/v1/vend/data"

                            payload = json.dumps(
                                {
                                    "networkId": net_id,
                                    "planId": plan_id,
                                    "phoneNumber": num,
                                    "reference": ident,
                                }
                            )
                            headers = {
                                "Authorization": "Bearer sk_live_9ea3607c-5650-4440-971f-d9921d397e25",
                                "Content-Type": "application/json",
                                "Accept": "application/json",
                            }

                            response = requests.request(
                                "POST", url, headers=headers, data=payload, verify=False
                            )
                            print(response.text)

                            if (
                                response.status_code == 200
                                or response.status_code == 202
                            ):
                                resp = json.loads(response.text)
                                if "status" in resp and resp["status"] is True:
                                    return "successful"
                                else:
                                    return "failed"

                            elif (
                                response.status_code == 424
                                or response.status_code == 400
                            ):
                                return "failed"

                            else:
                                return "processing"

                        resp = sendogdam("1", plan.ogdams_plan_id, num)
                        status = resp

            elif net == "GLO":
                glo_text = SME_text.objects.get(network=Network.objects.get(name="GLO"))
                try:
                    ussd = plan.ussd_string.replace("n", num)
                except:
                    ussd = ""

                if Network.objects.get(name=net).data_vending_medium == "SIMHOST":
                    senddata_ussdsimhost(
                        f"{ussd}", glo_text.sim_host_server_id_for_data, "USSD"
                    )
                    status = "successful"

                elif Network.objects.get(name=net).data_vending_medium == "SIMHOST_NG":
                    senddata_simhostng(
                        f"{ussd}",
                        glo_text.sim_host_server_id_for_data,
                        "USSD",
                        glo_text.vtu_sim_slot,
                    )
                    status = "successful"

                elif Network.objects.get(name=net).data_vending_medium == "SIM_SERVER":

                    def create_id():
                        random.randint(1, 10)
                        num_2 = random.randint(1, 10)
                        num_3 = random.randint(1, 10)
                        return str(num_2) + str(num_3) + str(uuid.uuid4())

                    ident = create_id()

                    def sendsimserver(num, plan_id):
                        url = "https://api.simservers.io"

                        payload = {
                            "process": "buy",
                            "api_key": "7x4ezoqrvuhz4d1a7t7aq8k5opissi0jgxjp4hfyxa8g90dgrkfmzipnndr604u9auuwv9ggwejwgruryhzf0ekp470j2vvb23ko9ulpn03zvdta433bb0rtw3m0otfn",
                            "product_code": plan_id,
                            "amount": "1",
                            "recipient": num,
                            "callback": " ",
                            "user_reference": ident,
                        }

                        payload_data = json.dumps(payload)
                        headers = {
                            "Content-Type": "application/json",
                        }

                        try:
                            response = requests.request(
                                "POST",
                                url,
                                headers=headers,
                                data=payload_data,
                                timeout=60,
                            )
                            print(
                                "##########################################################################"
                            )
                            print("payload ==", payload)
                            print("result =====", response.text)
                            print("result status =====", response.status_code)
                            print(
                                "##########################################################################"
                            )

                            if (
                                response.status_code == 200
                                or response.status_code == 201
                            ):
                                result = json.loads(response.text)
                                print("print result ===", result)

                                if "status" in result and result["status"] is True:
                                    return "successful"

                                else:
                                    return "failed"
                            elif (
                                response.status_code == 400
                                or response.status_code == 401
                            ):
                                return "failed"

                            else:
                                return "processing"

                        except requests.exceptions.HTTPError:
                            return "failed"
                        except requests.exceptions.ConnectionError:
                            return "failed"
                        except requests.exceptions.Timeout:
                            return "processing"
                        except requests.exceptions.RequestException:
                            return "failed"

                    result = sendsimserver(num, plan.simserver_plan_id)
                    status = result
                elif Network.objects.get(name=net).data_vending_medium == "SMEPLUG":
                    resp = senddatasmeplug("4", plan.smeplug_id, num)
                    status = "successful"

                    try:
                        if resp.status_code == 400 or resp.status_code == 404:
                            status = "failed"
                        else:
                            result = json.loads(resp.text)
                            ident = result["data"]["reference"]

                            if result["transaction"]["status"] == "failed":
                                status = "failed"
                            else:
                                pass
                    except:
                        pass

                # elif Network.objects.get(name=net).data_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                #             msorg_senddata(Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                #             status = "successful"
                elif (
                    Network.objects.get(name=net).data_vending_medium
                    == "MSORG_DEVELOPED_WEBSITE"
                ):
                    msorg_senddata(
                        config.msorg_web_url,
                        config.msorg_web_api_key,
                        Network.objects.get(name=net).msorg_web_net_id,
                        num,
                        plan.plan_name_id,
                    )
                    status = "successful"

                elif (
                    Network.objects.get(name=net).data_vending_medium
                    == "MSORG_DEVELOPED_WEBSITE_2"
                ):
                    msorg_senddata(
                        config.msorg_web_url_2,
                        config.msorg_web_api_key_2,
                        Network.objects.get(name=net).msorg_web_net_id,
                        num,
                        plan.plan_name_id_2,
                    )
                    status = "successful"

                elif (
                    Network.objects.get(name=net).data_vending_medium
                    == "MSORG_DEVELOPED_WEBSITE_3"
                ):
                    msorg_senddata(
                        config.msorg_web_url_3,
                        config.msorg_web_api_key_3,
                        Network.objects.get(name=net).msorg_web_net_id,
                        num,
                        plan.plan_name_id_3,
                    )
                    status = "successful"

                elif Network.objects.get(name=net).data_vending_medium == "SMS":
                    sendmessage(
                        "myweb",
                        "{0} want to buy {1}{3}  GLO-DATA data on {2} ".format(
                            user.username, plan.plan_size, num, plan.plan_Volume
                        ),
                        f"{config.sms_notification_number}",
                        "02",
                    )

                elif Network.objects.get(name=net).data_vending_medium == "VTUAUTO":
                    VTUAUTO_USSD(
                        f"{ussd}", glo_text.vtu_auto_device_id, glo_text.vtu_sim_slot
                    )
                    status = "successful"

                elif Network.objects.get(name=net).data_vending_medium == "MSPLUG":
                    Msplug_Data_vending(
                        net,
                        plan.msplug_plan_name_id,
                        num,
                        glo_text.msplug_sim_slot,
                        "USSD",
                        glo_text.msplug_device_id,
                    )
                    status = "successful"

                elif Network.objects.get(name=net).data_vending_medium == "SMEIFY":
                    senddatasmeify(
                        net, plan.smeify_plan_name_id, num, plan.month_validate
                    )
                    status = "successful"

            elif net == "AIRTEL":
                airtel_text = SME_text.objects.get(
                    network=Network.objects.get(name="AIRTEL")
                )
                try:
                    ussd = plan.ussd_string.replace("n", num).replace(
                        "p", airtel_text.pin
                    )
                except:
                    ussd = ""

                if plan.plan_type == "CORPORATE GIFTING":
                    if (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "UWS"
                    ):

                        def create_id():
                            random.randint(1, 10)
                            num_2 = random.randint(1, 10)
                            num_3 = random.randint(1, 10)
                            return str(num_2) + str(num_3) + str(uuid.uuid4())

                        ident = create_id()

                        while Data.objects.filter(ident=ident).exists():
                            ident = create_id()

                        url = "https://api.uws.com.ng/api/v1/airtel_coperate_data/purchase"

                        headers = {
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "Authorization": f"Bearer {config.uws_token}",
                        }
                        payload = {
                            "phone": num,
                            "plan_id": str(plan.uws_plan_name_id),
                            "customRef": ident,
                        }

                        response = requests.request(
                            "POST", url, headers=headers, data=json.dumps(payload)
                        )
                        # print(f'-------------------- AIRTEL CG ------------------------')
                        # print(f'payload  = {payload}')
                        # print(f'response.text  = {response.text}')
                        result = json.loads(response.text)

                        if result["status"] == "success":
                            status = "successful"
                        elif result["status"] == "failed":
                            status = "failed"
                        else:
                            status = "processing"

                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "ALAGUSIY"
                    ):

                        def create_id():
                            random.randint(1, 10)
                            num_2 = random.randint(1, 10)
                            num_3 = random.randint(1, 10)
                            return str(num_2) + str(num_3) + str(uuid.uuid4())

                        ident = create_id()

                        while Data.objects.filter(ident=ident).exists():
                            ident = create_id()

                        def sendag(num, plan_id):
                            url = "https://alagusiy.com/api/data"
                            payload = {
                                "token": "api_d1ed83d46ac3eb93e9b944fb36c8f3b0",
                                "mobile": num,
                                "network": "AIRTEL-CG",
                                "plan_code": plan_id,
                                "request_id": ident,
                            }
                            payload = json.dumps(payload)

                            print("payload", payload)
                            response = requests.request("POST", url, data=payload)
                            # response = requests.request("POST", url, headers=headers, data=payload)
                            print(
                                "################### alagusiy new API#########################"
                            )
                            print("response == ", response.text)
                            print(
                                "################### alagusiy new API#########################"
                            )
                            print(response.status_code)

                            print(
                                "################### alagusiy new API#########################"
                            )
                            try:
                                if (
                                    response.status_code == 200
                                    or response.status_code == 201
                                ):
                                    result = json.loads(response.text)
                                    if (
                                        "status" in result
                                        and result["status"] == "success"
                                    ):
                                        return "successful"

                                    else:
                                        return "failed"

                                elif (
                                    response.status_code == 400
                                    or response.status_code == 401
                                ):
                                    return "failed"

                                else:
                                    return "processing"
                            except:
                                return "processing"

                        result = sendag(num, plan.alagusiy_plan_id)
                        status = result
                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "CHEAPESTDATASUB"
                    ):
                        url = "https://cheapestsub.com/account/api/v1/buyairtelcg"

                        payload = json.dumps(
                            {
                                "bundle": f"{int(plan.plan_size)}{plan.plan_Volume}",
                                "mobile": str(num),
                            }
                        )
                        headers = {
                            "Content-Type": "application/json",
                        }

                        response = requests.post(
                            url,
                            headers=headers,
                            data=payload,
                            auth=HTTPBasicAuth("Malikidi", "uGMr4z4J@h5Bq"),
                        )

                        if "status" in response.text:
                            zz = json.loads(response.text)
                            if zz["status"] == "success":
                                status = "successful"
                            else:
                                status = "failed"
                        else:
                            status = "failed"

                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        resp = msorg_senddata(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id,
                        )
                        status = resp

                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        resp = msorg_senddata(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id_2,
                        )
                        status = resp

                    elif (
                        Network.objects.get(name=net).corporate_data_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        resp = msorg_senddata(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id_3,
                        )
                        status = resp

                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "SIM_SERVER"
                    ):

                        def create_id():
                            random.randint(1, 10)
                            num_2 = random.randint(1, 10)
                            num_3 = random.randint(1, 10)
                            return str(num_2) + str(num_3) + str(uuid.uuid4())

                        ident = create_id()

                        def sendsimserver(num, plan_id):
                            url = "https://api.simservers.io"

                            payload = {
                                "process": "buy",
                                "api_key": "7x4ezoqrvuhz4d1a7t7aq8k5opissi0jgxjp4hfyxa8g90dgrkfmzipnndr604u9auuwv9ggwejwgruryhzf0ekp470j2vvb23ko9ulpn03zvdta433bb0rtw3m0otfn",
                                "product_code": plan_id,
                                "amount": "1",
                                "recipient": num,
                                "callback": " ",
                                "user_reference": ident,
                            }

                            payload_data = json.dumps(payload)
                            headers = {
                                "Content-Type": "application/json",
                            }

                            try:
                                response = requests.request(
                                    "POST",
                                    url,
                                    headers=headers,
                                    data=payload_data,
                                    timeout=60,
                                )
                                # print("##########################################################################")
                                # print("payload ==",payload)
                                # print("result =====",response.text)
                                # print("result status =====",response.status_code)
                                # print("##########################################################################")
                                # if response.status_code == 200 or response.status_code == 201:
                                #     result = json.loads(response.text)
                                #     print("print result ===", result)

                                #     if "status" in result and result["status"] == True:
                                #             return 'successful'

                                #     else:
                                #             return "failed"

                                # elif response.status_code == 400 or response.status_code == 401:
                                #     return "failed"

                                # else:
                                #     return "processing"

                                if (
                                    response.status_code == 200
                                    or response.status_code == 201
                                ):
                                    result = json.loads(response.text)
                                    print("print result ===", result)

                                    if (
                                        "status" in result
                                        and result["data"]["text_status"] == "success"
                                    ):
                                        return (
                                            "successful",
                                            result["data"]["true_response"],
                                        )
                                    elif (
                                        "status" in result
                                        and result["data"]["text_status"] == "pending"
                                    ):
                                        return (
                                            "pending",
                                            result["data"]["true_response"],
                                        )
                                    else:
                                        return "failed", result["data"]["true_response"]
                                elif (
                                    response.status_code == 400
                                    or response.status_code == 408
                                    or response.status_code == 502
                                    or response.status_code == 401
                                ):
                                    return "failed", "No Response"

                                else:
                                    return "processing", "Response Not available"

                            except requests.exceptions.HTTPError:
                                return "failed", ""
                            except requests.exceptions.ConnectionError:
                                return "failed", ""
                            except requests.exceptions.Timeout:
                                return "processing", ""
                            except requests.exceptions.RequestException:
                                return "failed", ""

                        result = sendsimserver(num, plan.simserver_plan_id)
                        status = result[0]
                        api_response = result[1]

                    else:
                        status = "processing"

                else:
                    if Network.objects.get(name=net).data_vending_medium == "SIMHOST":
                        senddata_ussdsimhost(
                            f"{ussd}", airtel_text.sim_host_server_id_for_data, "USSD"
                        )
                        senddata_ussdsimhost(
                            "*123#".format(),
                            airtel_text.sim_host_server_id_for_data,
                            "USSD",
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "SIMHOST_NG"
                    ):
                        senddata_simhostng(
                            f"{ussd}",
                            airtel_text.sim_host_server_id_for_data,
                            "USSD",
                            airtel_text.vtu_sim_slot,
                        )
                        status = "successful"

                    elif Network.objects.get(name=net).data_vending_medium == "SMEPLUG":
                        resp = senddatasmeplug("2", plan.smeplug_id, num)
                        status = "successful"

                        try:
                            if resp.status_code == 400 or resp.status_code == 404:
                                status = "failed"
                            else:
                                result = json.loads(resp.text)
                                ident = result["data"]["reference"]

                                if result["transaction"]["status"] == "failed":
                                    status = "failed"
                                else:
                                    pass
                        except:
                            pass

                    elif Network.objects.get(name=net).data_vending_medium == "UWS":
                        # print('--------------------------------- AIRTEL DATA TO UWS')
                        def create_id():
                            random.randint(1, 10)
                            num_2 = random.randint(1, 10)
                            num_3 = random.randint(1, 10)
                            return str(num_2) + str(num_3) + str(uuid.uuid4())

                        ident = create_id()

                        while Data.objects.filter(ident=ident).exists():
                            ident = create_id()

                        url = "https://api.uws.com.ng/api/v1/sme_data/purchase"

                        payload = {
                            "phone": num,
                            "network_id": "1",
                            "plan_id": str(plan.uws_plan_name_id),
                            "customRef": ident,
                        }

                        headers = {
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "Authorization": f"Bearer {config.uws_token}",
                        }

                        response = requests.request(
                            "POST", url, headers=headers, data=json.dumps(payload)
                        )
                        result = json.loads(response.text)
                        # print(payload)
                        # print(response.text)
                        # print(response.status_code)
                        status = "successful"
                        try:
                            if result["status"] == "failed":
                                status = "failed"
                        except:
                            pass

                    elif Network.objects.get(name=net).data_vending_medium == "SMS":
                        sendmessage(
                            "myweb",
                            "{0} want to buy {1}{3}  AIRTEL-DATA data on {2} ".format(
                                user.username, plan.plan_size, num, plan.plan_Volume
                            ),
                            f"{config.sms_notification_number}",
                            "02",
                        )

                    # elif Network.objects.get(name=net).data_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                    #             msorg_senddata(Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                    #             status = "successful"
                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        msorg_senddata(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        msorg_senddata(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id_2,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).data_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        msorg_senddata(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            plan.plan_name_id_3,
                        )
                        status = "successful"

                    elif Network.objects.get(name=net).data_vending_medium == "VTUAUTO":
                        VTUAUTO_USSD(
                            f"{ussd}",
                            airtel_text.vtu_auto_device_id,
                            airtel_text.vtu_sim_slot,
                        )
                        VTUAUTO_USSD(
                            "*123#".format(),
                            airtel_text.vtu_auto_device_id,
                            airtel_text.vtu_sim_slot,
                        )
                        status = "successful"

                    elif Network.objects.get(name=net).data_vending_medium == "MSPLUG":
                        Msplug_Data_vending(
                            net,
                            plan.msplug_plan_name_id,
                            num,
                            airtel_text.msplug_sim_slot,
                            "USSD",
                            airtel_text.msplug_device_id,
                        )
                        status = "successful"

                    elif Network.objects.get(name=net).data_vending_medium == "SMEIFY":
                        senddatasmeify(
                            net, plan.smeify_plan_name_id, num, plan.month_validate
                        )
                        status = "successful"

            elif net == "9MOBILE":
                mobile_text = SME_text.objects.get(
                    network=Network.objects.get(name="9MOBILE")
                )
                try:
                    ussd = plan.ussd_string.replace("n", num)
                except:
                    ussd = ""

                if Network.objects.get(name=net).data_vending_medium == "SIMHOST":
                    senddata_ussdsimhost(
                        f"{ussd}", mobile_text.sim_host_server_id_for_data, "USSD"
                    )
                    senddata_ussdsimhost(
                        "*232#".format(),
                        mobile_text.sim_host_server_id_for_data,
                        "USSD",
                    )
                    status = "successful"

                elif Network.objects.get(name=net).data_vending_medium == "SIMHOST_NG":
                    senddata_simhostng(
                        f"{ussd}",
                        mobile_text.sim_host_server_id_for_data,
                        "USSD",
                        mobile_text.vtu_sim_slot,
                    )
                    status = "successful"

                elif Network.objects.get(name=net).data_vending_medium == "SMEPLUG":
                    resp = senddatasmeplug("3", plan.smeplug_id, num)
                    status = "successful"

                    try:
                        if resp.status_code == 400 or resp.status_code == 404:
                            status = "failed"
                        else:
                            result = json.loads(resp.text)
                            ident = result["data"]["reference"]

                            if result["transaction"]["status"] == "failed":
                                status = "failed"
                            else:
                                pass
                    except:
                        pass

                elif Network.objects.get(name=net).data_vending_medium == "SMS":
                    sendmessage(
                        "myweb",
                        "{0} want to buy {1}{3}  9MOBILE-DATA data on {2} ".format(
                            user.username, plan.plan_size, num, plan.plan_Volume
                        ),
                        f"{config.sms_notification_number}",
                        "02",
                    )

                # elif Network.objects.get(name=net).data_vending_medium  == "MSORG_DEVELOPED_WEBSITE":
                #             msorg_senddata(Network.objects.get(name=net).msorg_web_net_id,num,plan.plan_name_id)
                #             status = "successful"
                elif (
                    Network.objects.get(name=net).data_vending_medium
                    == "MSORG_DEVELOPED_WEBSITE"
                ):
                    msorg_senddata(
                        config.msorg_web_url,
                        config.msorg_web_api_key,
                        Network.objects.get(name=net).msorg_web_net_id,
                        num,
                        plan.plan_name_id,
                    )
                    status = "successful"

                elif (
                    Network.objects.get(name=net).data_vending_medium
                    == "MSORG_DEVELOPED_WEBSITE_2"
                ):
                    msorg_senddata(
                        config.msorg_web_url_2,
                        config.msorg_web_api_key_2,
                        Network.objects.get(name=net).msorg_web_net_id,
                        num,
                        plan.plan_name_id_2,
                    )
                    status = "successful"

                elif (
                    Network.objects.get(name=net).data_vending_medium
                    == "MSORG_DEVELOPED_WEBSITE_3"
                ):
                    msorg_senddata(
                        config.msorg_web_url_3,
                        config.msorg_web_api_key_3,
                        Network.objects.get(name=net).msorg_web_net_id,
                        num,
                        plan.plan_name_id_3,
                    )
                    status = "successful"

                elif Network.objects.get(name=net).data_vending_medium == "VTUAUTO":
                    VTUAUTO_USSD(
                        f"{ussd}",
                        mobile_text.vtu_auto_device_id,
                        mobile_text.vtu_sim_slot,
                    )
                    VTUAUTO_USSD(
                        "*232#".format(),
                        mobile_text.vtu_auto_device_id,
                        mobile_text.vtu_sim_slot,
                    )
                    status = "successful"

                elif Network.objects.get(name=net).data_vending_medium == "MSPLUG":
                    Msplug_Data_vending(
                        net,
                        plan.msplug_plan_name_id,
                        num,
                        mobile_text.msplug_sim_slot,
                        "USSD",
                        mobile_text.msplug_device_id,
                    )
                    status = "successful"

                elif Network.objects.get(name=net).data_vending_medium == "SMEIFY":
                    senddatasmeify(
                        "ETISALAT", plan.smeify_plan_name_id, num, plan.month_validate
                    )
                    status = "successful"

            elif net == "SMILE":

                def create_id():
                    random.randint(1, 10)
                    num_2 = random.randint(1, 10)
                    num_3 = random.randint(1, 10)
                    return str(num_2) + str(num_3) + str(uuid.uuid4())[:4]

                ident = create_id()

                payload = {
                    "billersCode": num,
                    "serviceID": "smile-direct",
                    "request_id": ident,
                    "amount": plan.plan_amount,
                    "variation_code": plan.vtpass_variation_code,
                    "phone": num,
                }
                authentication = (f"{config.vtpass_email}", f"{config.vtpass_password}")

                resp = requests.post(
                    "https://vtpass.com/api/pay", data=payload, auth=authentication
                )
                # print(resp.text)
                status = "successful"

            serializer.save(
                Status=status,
                api_response=api_response,
                ident=ident,
                plan_amount=amount,
                medium="API",
                balance_before=previous_bal,
                balance_after=(previous_bal - amount),
            )

            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


# airtime topup api


class AirtimeTopupAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        try:
            item = AirtimeTopup.objects.filter(user=request.user).get(pk=id)
            serializer = AirtimeTopupSerializer(item)
            return Response(serializer.data)
        except AirtimeTopup.DoesNotExist:
            return Response(status=404)


class AirtimeTopupAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = AirtimeTopup.objects.filter(user=request.user).order_by("-create_date")
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = AirtimeTopupSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        status = "processing"
        fund = 0
        serializer = AirtimeTopupSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            (serializer.validated_data["user"]).username
            num = serializer.validated_data["mobile_number"]
            amt = serializer.validated_data["amount"]
            net = str(serializer.validated_data["network"])
            order_user = serializer.validated_data["user"]
            user = serializer.validated_data["user"]
            previous_bal = order_user.Account_Balance
            airtime_type = serializer.validated_data["airtime_type"]
            errors = {}

            # def create_id():
            #     num = random.randint(1, 10)
            #     num_2 = random.randint(1, 10)
            #     num_3 = random.randint(1, 10)
            #     return str(num_2)+str(num_3)+str(uuid.uuid4())[:4]

            # ident = create_id()

            def create_id():
                num = random.randint(1000, 4999)
                num_2 = random.randint(5000, 8000)
                num_3 = random.randint(111, 999) * 2
                return (
                    str(Mdate.now().strftime("%Y%m%d%H%M%S"))
                    + str(num)
                    + str(num_2)
                    + str(num_3)
                    + str(uuid.uuid4())
                )

            ident = create_id()

            if user.user_type == "Affilliate":
                perc = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)
                ).Affilliate_percent
                perc2 = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)
                ).share_n_sell_affilliate_percent

            elif user.user_type == "API":
                perc = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)
                ).api_percent
                perc2 = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)
                ).share_n_sell_api_percent

            elif user.user_type == "TopUser":
                perc = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)
                ).topuser_percent
                perc2 = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)
                ).share_n_sell_topuser_percent
            else:
                perc = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)
                ).percent
                perc2 = TopupPercentage.objects.get(
                    network=Network.objects.get(name=net)
                ).share_n_sell_percent

            def senddata_ussdsimhost(ussd, servercode, mytype):
                payload = {
                    "ussd": ussd,
                    "servercode": servercode,
                    "token": f"{config.simhost_API_key}",
                    "type": mytype,
                }

                baseurl = "https://ussd.simhosting.ng/api/?"
                response = requests.get(baseurl, params=payload, verify=False)
                logging.error(
                    "---------------------------------------------------- aritime TO USSD SIMHOSTING"
                )
                logging.error(f"payload = {payload}")
                logging.error(response.text)

            def senddata_simhostng(ussd, servercode, sim):
                response = requests.post(
                    f"https://simhostng.com//api/ussd?apikey={config.simhost_API_key}&server={servercode}&sim={sim}&number={urllib.parse.quote(ussd)}"
                )
                print(
                    "-------------------------- Sending Airtime to simhostng.COM ---------------------------"
                )
                print(response.text)

            def sendairtime2(ussd, servercode, sim, msg):
                requests.post(
                    f"https://simhostng.com//api/sms?apikey={config.simhost_API_key}&server={servercode}&sim={sim}&number={ussd}&message={msg}"
                )

            #   #print(response.text)

            def buyairtime(amount, num, code):
                headers = {
                    "email": f"{config.ringo_email}",
                    "password": f"{config.ringo_password}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "serviceCode": "VAR",
                    "amount": amount,
                    "request_id": ident,
                    "msisdn": num,
                    "product_id": code,
                }
                response = requests.post(
                    "https://www.api.ringo.ng/api/agent/p2",
                    headers=headers,
                    data=json.dumps(payload),
                    verify=False,
                )
                return response

            def VTUAUTO_USSD(ussd, device_id, sim):
                payload = {"device_id": device_id, "ussd_string": ussd, "sim": sim}
                requests.post(
                    "https://vtuauto.ng/api/v1/request/ussd",
                    auth=HTTPBasicAuth(
                        f"{config.vtu_auto_email}", f"{config.vtu_auto_password}"
                    ),
                    data=payload,
                )
                # print(response.text)

            def sendairtime(net, num, amount):
                url = "https://smeplug.ng/api/v1/vtu"

                payload = json.dumps(
                    {"network_id": net, "amount": amount, "phone_number": num}
                )

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.sme_plug_secret_key}",
                }

                # print(payload)
                response = requests.request("POST", url, headers=headers, data=payload)
                # print(response.text)
                return response

            def sendairtimeVtpass(net, amount, num):
                authentication = (f"{config.vtpass_email}", f"{config.vtpass_password}")

                payload = {
                    "serviceID": net,
                    "request_id": ident,
                    "amount": amount,
                    "phone": num,
                }

                response = requests.post(
                    "https://vtpass.com/api/pay", data=payload, auth=authentication
                )
                # print(response.text)
                return response.text

            def Msplug_AIRTIME_vending(net, amt, num, sim, rtype, device_id):
                url = "https://www.msplug.com/api/buy-airtime/"
                payload = {
                    "network": net,
                    "amount": str(amt),
                    "phone": num,
                    "device_id": device_id,
                    "sim_slot": sim,
                    "airtime_type": rtype,
                    "webhook_url": "http://www.legitdata.com.ngbuydata/webhook/",
                }
                headers = {
                    "Authorization": f"Token {config.msplug_API_key}",
                    "Content-Type": "application/json",
                }

                requests.post(url, headers=headers, data=json.dumps(payload))
                # print(response.text)

            def sendairtimesmeify(net, amt, num, airtime_type):
                if airtime_type == "Share and Sell":
                    airtime_type = "SAS"
                else:
                    airtime_type = "VTU"

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {SmeifyAuth.objects.first().get_token()}",
                }
                url = "https://api.smeify.com/api/v2/airtime"
                payload = json.dumps(
                    {
                        "network": net,
                        "amount": amt,
                        "phones": str(num),
                        "type": airtime_type,
                    }
                )
                requests.post(url, headers=headers, data=payload)

                # headers = { 'Content-Type': 'application/json', 'Authorization': f'Bearer {SmeifyAuth.objects.first().get_token()}'}
                # url = f"https://auto.smeify.com/api/v1/online/vtu?network={net}&&amount={amt}&&phone={num}"
                # respons = requests.request("POST", url, headers=headers)

                # print(respons.text)

            def msorg_sendairtime(netid, num, amt):
                url = f"{config.msorg_web_url}/api/topup/"

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Token {config.msorg_web_api_key}",
                }
                param = {
                    "network": netid,
                    "mobile_number": num,
                    "amount": amt,
                    "Ported_number": True,
                    "airtime_type": "VTU",
                }
                param_data = json.dumps(param)
                response = requests.post(
                    url, headers=headers, data=param_data, verify=False
                )
                # print(response.text)
                return response

            def msorg_sendairtime2(website, token, netid, num, amt):
                url = f"{website}/api/topup/"

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Token {token}",
                }
                param = {
                    "network": netid,
                    "mobile_number": num,
                    "amount": amt,
                    "Ported_number": True,
                    "airtime_type": "VTU",
                }
                param_data = json.dumps(param)
                response = requests.post(
                    url, headers=headers, data=param_data, verify=False
                )
                return response

            def sendsimserver_airtime(amt, num, plan_id):
                url = "https://api.simservers.io"

                payload = {
                    "process": "buy",
                    "api_key": "7x4ezoqrvuhz4d1a7t7aq8k5opissi0jgxjp4hfyxa8g90dgrkfmzipnndr604u9auuwv9ggwejwgruryhzf0ekp470j2vvb23ko9ulpn03zvdta433bb0rtw3m0otfn",
                    "product_code": plan_id,
                    "amount": amt,
                    "recipient": num,
                    "callback": "https://rpidatang.com/simserver-webhook/",
                    "user_reference": ident,
                }

                payload_data = json.dumps(payload)
                headers = {
                    "Content-Type": "application/json",
                }

                try:
                    response = requests.request(
                        "POST", url, headers=headers, data=payload_data, timeout=60
                    )
                    print(
                        "##########################################################################"
                    )
                    print("payload ==", payload)
                    print("result =====", response.text)
                    print("result status =====", response.status_code)
                    print(
                        "##########################################################################"
                    )

                    if response.status_code == 200 or response.status_code == 201:
                        result = json.loads(response.text)
                        print("print result ===", result)

                        if "status" in result and result["status"] is True:
                            return "successful"

                        else:
                            return "failed"
                    elif response.status_code == 400 or response.status_code == 401:
                        return "failed"

                    else:
                        return "processing"

                except requests.exceptions.HTTPError:
                    return "failed"
                except requests.exceptions.ConnectionError:
                    return "failed"
                except requests.exceptions.Timeout:
                    return "processing"
                except requests.exceptions.RequestException:
                    return "failed"

            if airtime_type == "awuf4U":
                amount = float(amt) * int(perc) / 100
                check = user.withdraw(user.id, amount)
                if check is False:
                    errors["error"] = " insufficient balance "
                    raise serializers.ValidationError(errors)
                fund = amount
                Wallet_summary.objects.create(
                    user=order_user,
                    product="{} {} awuf4u Airtime topup  with {} ".format(
                        net, amt, num
                    ),
                    amount=fund,
                    previous_balance=previous_bal,
                    after_balance=(previous_bal - amount),
                )
                amt = int(amt)

                mtn_text = SME_text.objects.get(network=Network.objects.get(name="MTN"))
                Msplug_AIRTIME_vending(
                    net,
                    amt,
                    num,
                    mtn_text.msplug_sim_slot,
                    "MTN_AWF",
                    mtn_text.msplug_device_id,
                )
                status = "successful"

            elif airtime_type == "VTU":
                amount = float(amt) * int(perc) / 100
                check = user.withdraw(user.id, amount)
                if check is False:
                    errors["error"] = " insufficient balance "
                    raise serializers.ValidationError(errors)
                fund = amount
                Wallet_summary.objects.create(
                    user=order_user,
                    product="{} {} Airtime VTU topup  with {} ".format(net, amt, num),
                    amount=fund,
                    previous_balance=previous_bal,
                    after_balance=(previous_bal - amount),
                )

                amt = int(amt)

                if net == "MTN":
                    mtn_text = SME_text.objects.get(
                        network=Network.objects.get(name="MTN")
                    )

                    if Network.objects.get(name=net).vtu_vending_medium == "SIMHOST":
                        senddata_ussdsimhost(
                            f"*456*1*2*{amt}*{num}*1*{mtn_text.vtu_pin}#",
                            mtn_text.sim_host_server_id_for_airtime,
                            "USSD",
                        )  ## ussd simhosting
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium == "SIM_SERVER"
                    ):
                        status = sendsimserver_airtime(
                            amt, num, "mtn_custom:device:USSD_MTN_FULL"
                        )

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium == "SIMHOST_NG"
                    ):
                        senddata_simhostng(
                            f"*456*1*2*{amt}*{num}*1*{mtn_text.vtu_pin}#",
                            mtn_text.sim_host_server_id_for_airtime,
                            mtn_text.vtu_sim_slot,
                        )
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "RINGO":
                        buyairtime(amt, num, "MFIN-5-OR")
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "SMEPLUG":
                        sendairtime("1", num, amt)
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "SMS":
                        sendmessage(
                            "myweb",
                            f"{user.username} want to buy  {amt} NAIRA  MTN-TOPUP  to {num} ",
                            f"{config.sms_notification_number}",
                            "02",
                        )

                    elif Network.objects.get(name=net).vtu_vending_medium == "VTUAUTO":
                        VTUAUTO_USSD(
                            f"*456*1*2*{amt}*{num}*1*{mtn_text.vtu_pin}#",
                            mtn_text.vtu_auto_device_id,
                            mtn_text.vtu_sim_slot,
                        )
                        status = "successful"
                    elif Network.objects.get(name=net).vtu_vending_medium == "VTPASS":
                        sendairtimeVtpass("mtn", amt, num)
                        status = "successful"
                    elif Network.objects.get(name=net).vtu_vending_medium == "MSPLUG":
                        Msplug_AIRTIME_vending(
                            net,
                            amt,
                            num,
                            mtn_text.msplug_sim_slot,
                            "VTU",
                            mtn_text.msplug_device_id,
                        )
                        status = "successful"
                    elif Network.objects.get(name=net).vtu_vending_medium == "SMEIFY":
                        sendairtimesmeify(net, amt, num, airtime_type)
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                elif net == "GLO":
                    glo_text = SME_text.objects.get(
                        network=Network.objects.get(name="GLO")
                    )

                    if Network.objects.get(name=net).vtu_vending_medium == "SIMHOST":
                        # MULTISTEP
                        def sendussddata(ussd, num, servercode):
                            payload = {
                                "ussd": ussd,
                                "servercode": servercode,
                                "multistep": num,
                                "token": f"{config.simhost_API_key}",
                            }

                            baseurl = "https://ussd.simhosting.ng/api/ussd/?"
                            requests.get(baseurl, params=payload, verify=False)
                            # print(response.text)

                        ussd = "*202*2*{1}*{0}*{2}#".format(amt, num, glo_text.vtu_pin)
                        sendussddata(
                            f"{ussd}", "1", glo_text.sim_host_server_id_for_airtime
                        )
                        status = "successful"

                        # NON-MULTISTEP
                        # senddata_ussdsimhost(ussd,glo_text.sim_host_server_id_for_airtime,'USSD')
                        # status = 'successful'

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium == "SIM_SERVER"
                    ):
                        status = sendsimserver_airtime(
                            amt, num, "glo_custom:device:USSD_GLO_FULL"
                        )

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium == "SIMHOST_NG"
                    ):
                        senddata_simhostng(
                            "*202*2*{1}*{0}*{2}*1#".format(amt, num, glo_text.vtu_pin),
                            glo_text.sim_host_server_id_for_airtime,
                            glo_text.vtu_sim_slot,
                        )
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "RINGO":
                        buyairtime(amt, num, "MFIN-6-OR")
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "SMEPLUG":
                        sendairtime("4", num, amt)
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "SMS":
                        sendmessage(
                            "myweb",
                            f"{user.username} want to buy  {amt} NAIRA  GLO-TOPUP  to {num} ",
                            f"{config.sms_notification_number}",
                            "02",
                        )

                    elif Network.objects.get(name=net).vtu_vending_medium == "VTUAUTO":
                        VTUAUTO_USSD(
                            f"*202*2*{num}*{amt}*{glo_text.vtu_pin}*1#",
                            glo_text.vtu_auto_device_id,
                            glo_text.vtu_sim_slot,
                        )
                        status = "successful"
                    elif Network.objects.get(name=net).vtu_vending_medium == "VTPASS":
                        sendairtimeVtpass("glo", amt, num)
                        status = "successful"
                    elif Network.objects.get(name=net).vtu_vending_medium == "MSPLUG":
                        Msplug_AIRTIME_vending(
                            net,
                            amt,
                            num,
                            glo_text.msplug_sim_slot,
                            "VTU",
                            glo_text.msplug_device_id,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "SMEIFY":
                        sendairtimesmeify(net, amt, num, airtime_type)
                        status = "successful"

                elif net == "AIRTEL":
                    airtel_text = SME_text.objects.get(
                        network=Network.objects.get(name="AIRTEL")
                    )

                    if Network.objects.get(name=net).vtu_vending_medium == "SIMHOST":
                        senddata_ussdsimhost(
                            f"*605*2*1*{num}*{amt}*{airtel_text.vtu_pin}#",
                            airtel_text.sim_host_server_id_for_airtime,
                            "USSD",
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium == "SIMHOST_NG"
                    ):
                        senddata_simhostng(
                            f"*605*2*1*{num}*{amt}*{airtel_text.vtu_pin}#",
                            airtel_text.sim_host_server_id_for_airtime,
                            airtel_text.vtu_sim_slot,
                        )  # USSD

                        # sendairtime2("432",airtel_text.sim_host_server_id_for_airtime,airtel_text.vtu_sim_slot,f'2u {num} {amt} {airtel_text.vtu_pin}')   #SMS
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium == "SIM_SERVER"
                    ):
                        status = sendsimserver_airtime(
                            amt, num, "airtel_custom:device:USSD_AIRTEL_FULL"
                        )

                    elif Network.objects.get(name=net).vtu_vending_medium == "RINGO":
                        buyairtime(amt, num, "MFIN-1-OR")
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "SMEPLUG":
                        sendairtime("2", num, amt)
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "SMS":
                        sendmessage(
                            "myweb",
                            f"{user.username} want to buy  {amt} NAIRA  AIRTEL-TOPUP  to {num} ",
                            f"{config.sms_notification_number}",
                            "02",
                        )

                    elif Network.objects.get(name=net).vtu_vending_medium == "VTUAUTO":
                        VTUAUTO_USSD(
                            f"*605*2*1*{num}*{amt}*{airtel_text.vtu_pin}#",
                            airtel_text.vtu_auto_device_id,
                            airtel_text.vtu_sim_slot,
                        )
                        status = "successful"
                    elif Network.objects.get(name=net).vtu_vending_medium == "VTPASS":
                        sendairtimeVtpass("airtel", amt, num)
                        status = "successful"
                    elif Network.objects.get(name=net).vtu_vending_medium == "MSPLUG":
                        Msplug_AIRTIME_vending(
                            net,
                            amt,
                            num,
                            airtel_text.msplug_sim_slot,
                            "VTU",
                            airtel_text.msplug_device_id,
                        )
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "SMEIFY":
                        sendairtimesmeify(net, amt, num, airtime_type)
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                elif net == "9MOBILE":
                    mobile_text = SME_text.objects.get(
                        network=Network.objects.get(name="9MOBILE")
                    )

                    if Network.objects.get(name=net).vtu_vending_medium == "SIMHOST":
                        senddata_ussdsimhost(
                            f"*224*{amt}*{num}*{mobile_text.vtu_pin}#",
                            mobile_text.sim_host_server_id_for_airtime,
                            "USSD",
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium == "SIM_SERVER"
                    ):
                        status = sendsimserver_airtime(
                            amt, num, "9mobile_custom:device:USSD_9MOBILE_FULL"
                        )

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium == "SIMHOST_NG"
                    ):
                        senddata_simhostng(
                            f"*224*{amt}*{num}*{mobile_text.vtu_pin}#",
                            mobile_text.sim_host_server_id_for_airtime,
                            mobile_text.vtu_sim_slot,
                        )
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "RINGO":
                        buyairtime(amt, num, "MFIN-2-OR")
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "SMEPLUG":
                        sendairtime("3", num, amt)
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "SMS":
                        sendmessage(
                            "myweb",
                            f"{user.username} want to buy  {amt} NAIRA  9MOBILE-TOPUP  to {num} ",
                            f"{config.sms_notification_number}",
                            "02",
                        )

                    elif Network.objects.get(name=net).vtu_vending_medium == "VTUAUTO":
                        VTUAUTO_USSD(
                            f"*224*{amt}*{num}*{mobile_text.vtu_pin}#",
                            mobile_text.vtu_auto_device_id,
                            mobile_text.vtu_sim_slot,
                        )
                        status = "successful"
                    elif Network.objects.get(name=net).vtu_vending_medium == "VTPASS":
                        sendairtimeVtpass("etisalat", amt, num)
                        status = "successful"
                    elif Network.objects.get(name=net).vtu_vending_medium == "MSPLUG":
                        Msplug_AIRTIME_vending(
                            net,
                            amt,
                            num,
                            mobile_text.msplug_sim_slot,
                            "VTU",
                            mobile_text.msplug_device_id,
                        )
                        status = "successful"

                    elif Network.objects.get(name=net).vtu_vending_medium == "SMEIFY":
                        sendairtimesmeify("ETISALAT", amt, num, airtime_type)
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).vtu_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

            else:
                # print(Network.objects.get(name=net).share_and_sell_vending_medium)

                def msorg_sendairtime2(website, token, netid, num, amt):
                    url = f"{website}/api/topup/"

                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Token {token}",
                    }
                    param = {
                        "network": netid,
                        "mobile_number": num,
                        "amount": amt,
                        "Ported_number": True,
                        "airtime_type": "Share and Sell",
                    }
                    param_data = json.dumps(param)
                    response = requests.post(
                        url, headers=headers, data=param_data, verify=False
                    )
                    return response

                amount = float(amt) * int(perc2) / 100
                check = user.withdraw(user.id, amount)
                if check is False:
                    errors["error"] = "Y insufficient balance "
                    raise serializers.ValidationError(errors)

                fund = amount
                Wallet_summary.objects.create(
                    user=order_user,
                    product="{} {} Airtime share and sell topup  with {} ".format(
                        net, amt, num
                    ),
                    amount=fund,
                    previous_balance=previous_bal,
                    after_balance=(previous_bal - amount),
                )

                amt = int(amt)
                if net == "MTN":
                    mtn_text = SME_text.objects.get(
                        network=Network.objects.get(name="MTN")
                    )

                    if (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SIMHOST"
                    ):
                        senddata_ussdsimhost(
                            f"*600*{num}*{amt}*{mtn_text.share_and_sell_pin}#",
                            mtn_text.sim_host_server_id_for_airtime,
                            "USSD",
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SIM_SERVER"
                    ):
                        status = sendsimserver_airtime(
                            amt,
                            num,
                            "mtn_share_and_sell:device:USSD_MTN_SHAREnSELL_FULL",
                        )

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "VTUAUTO"
                    ):
                        VTUAUTO_USSD(
                            f"*600*{num}*{amt}*{mtn_text.share_and_sell_pin}#",
                            mtn_text.vtu_auto_device_id,
                            mtn_text.vtu_sim_slot,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SMS"
                    ):
                        sendmessage(
                            "myweb",
                            f"{user.username} want to buy  {amt} NAIRA  MTN-SHARE AND SELL  to {num} ",
                            f"{config.sms_notification_number}",
                            "02",
                        )

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSPLUG"
                    ):
                        Msplug_AIRTIME_vending(
                            net,
                            amt,
                            num,
                            mtn_text.msplug_sim_slot,
                            "SNS",
                            mtn_text.msplug_device_id,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SMEIFY"
                    ):
                        sendairtimesmeify("MTN", amt, num, airtime_type)
                        status = "successful"

                    else:
                        errors["error"] = "Share and sell not available on this network"
                        raise serializers.ValidationError(errors)

                elif net == "AIRTEL":
                    airtel_text = SME_text.objects.get(
                        network=Network.objects.get(name="AIRTEL")
                    )

                    if (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SIMHOST"
                    ):
                        senddata_ussdsimhost(
                            f"*432*1*{num}*{amt}*{airtel_text.share_and_sell_pin}#",
                            airtel_text.sim_host_server_id_for_airtime,
                            "USSD",
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SIM_SERVER"
                    ):
                        status = sendsimserver_airtime(
                            amt,
                            num,
                            "glo_share_and_sell:device:USSD_Airtel_SHAREnSELL_FULL",
                        )

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SIMHOST_NG"
                    ):
                        senddata_simhostng(
                            f"*432*1*{num}*{amt}*{airtel_text.share_and_sell_pin}#",
                            airtel_text.sim_host_server_id_for_airtime,
                            airtel_text.vtu_sim_slot,
                        )  # USSD

                        # sendairtime2("432",airtel_text.sim_host_server_id_for_airtime,airtel_text.vtu_sim_slot,f'2u {num} {amt} {airtel_text.vtu_pin}')   #SMS
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "VTUAUTO"
                    ):
                        VTUAUTO_USSD(
                            f"*432*1*{num}*{amt}*{airtel_text.share_and_sell_pin}#",
                            airtel_text.vtu_auto_device_id,
                            airtel_text.vtu_sim_slot,
                        )
                        status = "successful"
                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SMS"
                    ):
                        sendmessage(
                            "myweb",
                            f"{user.username} want to buy  {amt} NAIRA  AIRTEL-SHARE AND SELL  to {num} ",
                            f"{config.sms_notification_number}",
                            "02",
                        )

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSPLUG"
                    ):
                        Msplug_AIRTIME_vending(
                            net,
                            amt,
                            num,
                            airtel_text.msplug_sim_slot,
                            "SNS",
                            airtel_text.msplug_device_id,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SMEIFY"
                    ):
                        sendairtimesmeify("AIRTEL", amt, num, airtime_type)
                        status = "successful"
                    else:
                        errors["error"] = "Share and sell not available on this network"
                        raise serializers.ValidationError(errors)

                elif net == "9MOBILE":
                    mobile_text = SME_text.objects.get(
                        network=Network.objects.get(name="9MOBILE")
                    )

                    if (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SIMHOST"
                    ):
                        senddata_ussdsimhost(
                            f"*223*{mobile_text.share_and_sell_pin}*{amt}*{num}*#",
                            mobile_text.sim_host_server_id_for_airtime,
                            "USSD",
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SIM_SERVER"
                    ):
                        status = sendsimserver_airtime(
                            amt,
                            num,
                            "9mobile_share_and_sell:device:USSD_9MOBILE_SHAREnSELL_FULL",
                        )

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "VTUAUTO"
                    ):
                        VTUAUTO_USSD(
                            f"*223*{mobile_text.share_and_sell_pin}*{amt}*{num}*#",
                            mobile_text.vtu_auto_device_id,
                            mobile_text.vtu_sim_slot,
                        )
                        status = "successful"
                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SMS"
                    ):
                        sendmessage(
                            "myweb",
                            f"{user.username} want to buy  {amt} NAIRA  9MOBILE-SHARE AND SELL  to {num} ",
                            f"{config.sms_notification_number}",
                            "02",
                        )

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSPLUG"
                    ):
                        Msplug_AIRTIME_vending(
                            net,
                            amt,
                            num,
                            mobile_text.msplug_sim_slot,
                            "SNS",
                            mobile_text.msplug_device_id,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SMEIFY"
                    ):
                        sendairtimesmeify("ETISALAT", amt, num, airtime_type)
                        status = "successful"
                    else:
                        errors["error"] = "Share and sell not available on this network"
                        raise serializers.ValidationError(errors)

                elif net == "GLO":
                    glo_text = SME_text.objects.get(
                        network=Network.objects.get(name="GLO")
                    )

                    if (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SIMHOST"
                    ):
                        senddata_ussdsimhost(
                            f"*131*{num}*{amt}*{glo_text.share_and_sell_pin}#",
                            glo_text.sim_host_server_id_for_airtime,
                            "USSD",
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SIM_SERVER"
                    ):
                        status = sendsimserver_airtime(
                            amt,
                            num,
                            "glo_share_and_sell:device:USSD_GLO_SHAREnSELL_FULL",
                        )

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SIMHOST_NG"
                    ):
                        senddata_simhostng(
                            f"*131*{num}*{amt}*{glo_text.share_and_sell_pin}#",
                            glo_text.sim_host_server_id_for_airtime,
                            glo_text.vtu_sim_slot,
                        )  # USSD

                        # sendairtime2("432",airtel_text.sim_host_server_id_for_airtime,airtel_text.vtu_sim_slot,f'2u {num} {amt} {airtel_text.vtu_pin}')   #SMS
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "VTUAUTO"
                    ):
                        VTUAUTO_USSD(
                            f"*131*{num}*{amt}*{glo_text.share_and_sell_pin}#",
                            glo_text.vtu_auto_device_id,
                            glo_text.vtu_sim_slot,
                        )
                        status = "successful"
                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SMS"
                    ):
                        sendmessage(
                            "myweb",
                            f"{user.username} want to buy  {amt} NAIRA   GLO-SHARE AND SELL  to {num} ",
                            f"{config.sms_notification_number}",
                            "02",
                        )

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSPLUG"
                    ):
                        Msplug_AIRTIME_vending(
                            net,
                            amt,
                            num,
                            glo_text.msplug_sim_slot,
                            "SNS",
                            glo_text.msplug_device_id,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url,
                            config.msorg_web_api_key,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_2"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_2,
                            config.msorg_web_api_key_2,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "MSORG_DEVELOPED_WEBSITE_3"
                    ):
                        msorg_sendairtime2(
                            config.msorg_web_url_3,
                            config.msorg_web_api_key_3,
                            Network.objects.get(name=net).msorg_web_net_id,
                            num,
                            amt,
                        )
                        status = "successful"

                    elif (
                        Network.objects.get(name=net).share_and_sell_vending_medium
                        == "SMEIFY"
                    ):
                        sendairtimesmeify("GLO", amt, num, airtime_type)
                        status = "successful"
                    else:
                        errors["error"] = "Share and sell not available on this network"
                        raise serializers.ValidationError(errors)

                else:
                    errors[
                        "error"
                    ] = "Share and sell not available on this network currently"
                    raise serializers.ValidationError(errors)

            #            try:
            #                figure = TopupPercentage.objects.filter(network=net).first().commission
            #                figure = float(amt) * figure
            #                if figure > 0:
            #                    if user.referer_username:
            #                        if CustomUser.objects.filter(username__iexact = user.referer_username).exists():
            #                            referer  = CustomUser.objects.get(username__iexact = user.referer_username)
            #
            #                            if  user.user_type == "Smart Earner":
            #                                com =  referer.Referer_Bonus
            #                                referer.ref_deposit(figure)
            #
            #                                Wallet_summary.objects.create(user= referer, product="[Referal bonus] you received N{} commission  from your referal {} Airtime Transaction".format(figure,user.username), amount = figure, previous_balance = com, after_balance= (com + figure))
            #
            #                                notify.send(referer, recipient=referer, verb="[Referal bonus] you received N{} commission from your referal {} Airtime Transaction".format(figure,user.username))
            #
            #            except:
            #                pass

            serializer.save(
                Status=status,
                ident=ident,
                paid_amount=fund,
                medium="API",
                balance_before=previous_bal,
                balance_after=(previous_bal - amount),
            )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# Cable subscriptions api


class CableSubAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        try:
            item = Cablesub.objects.filter(user=request.user).get(pk=id)
            serializer = CablesubSerializer(item)
            return Response(serializer.data)
        except Cablesub.DoesNotExist:
            return Response(status=404)


class CableSubAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Cablesub.objects.filter(user=request.user).order_by("-create_date")
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = CablesubSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        status = "processing"
        serializer = CablesubSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            order_username = serializer.validated_data["user"]
            cableplan = serializer.validated_data["cableplan"]
            cable_name = serializer.validated_data["cablename"]
            num = serializer.validated_data["smart_card_number"]
            cable_plan = serializer.validated_data["cableplan"]
            smart_card_number = serializer.validated_data["smart_card_number"]
            previous_bal = user.Account_Balance
            plan_amount = float(cableplan.plan_amount)
            errors = {}

            service = ServicesCharge.objects.get(service="Cablesub")

            if user.user_type == "Affilliate":
                if service.Affilliate_charge > 0.0:
                    amount = float(plan_amount) + float(service.Affilliate_charge)

                elif service.Affilliate_discount > 0.0:
                    amount = float(plan_amount) - (
                        float(plan_amount) * service.Affilliate_discount / 100
                    )
                else:
                    amount = float(plan_amount)

            elif user.user_type == "TopUser":
                if service.topuser_charge > 0.0:
                    amount = float(plan_amount) + float(service.topuser_charge)

                elif service.topuser_discount > 0.0:
                    amount = float(plan_amount) - (
                        float(plan_amount) * service.topuser_discount / 100
                    )
                else:
                    amount = float(plan_amount)

            elif user.user_type == "API":
                if service.api_charge > 0.0:
                    amount = float(plan_amount) + float(service.api_charge)

                elif service.api_discount > 0.0:
                    amount = float(plan_amount) - (
                        float(plan_amount) * service.api_discount / 100
                    )

                else:
                    amount = float(plan_amount)
            else:
                if service.charge > 0.0:
                    amount = float(plan_amount) + float(service.charge)

                elif service.discount > 0.0:
                    amount = float(plan_amount) - (
                        float(plan_amount) * service.discount / 100
                    )

                else:
                    amount = float(plan_amount)

            # def create_id():
            #     num = random.randint(1, 10)
            #     num_2 = random.randint(1, 10)
            #     num_3 = random.randint(1, 10)

            #     return str(num_2)+str(num_3)+str(uuid.uuid4())[:6]
            # ident = create_id()

            def create_id():
                num = random.randint(1000, 4999)
                num_2 = random.randint(5000, 8000)
                num_3 = random.randint(111, 999) * 2
                return (
                    str(Mdate.now().strftime("%Y%m%d%H%M%S"))
                    + str(num)
                    + str(num_2)
                    + str(num_3)
                    + str(uuid.uuid4())
                )

            ident = create_id()

            if config.Cable_provider == "VTPASS":
                if str(cable_name) == "DSTV":
                    authentication = (
                        f"{config.vtpass_email}",
                        f"{config.vtpass_password}",
                    )

                    payload = {
                        "billersCode": smart_card_number,
                        "serviceID": "dstv",
                        "request_id": ident,
                        "variation_code": cableplan.product_code,
                        "phone": user.Phone,
                    }

                    try:
                        check = user.withdraw(user.id, amount)
                        if check is False:
                            errors["error"] = "Y insufficient balance "
                            raise serializers.ValidationError(errors)

                        Wallet_summary.objects.create(
                            user=user,
                            product="{}  N{} Cable tv Sub with {} ".format(
                                cableplan.package, amount, smart_card_number
                            ),
                            amount=amount,
                            previous_balance=previous_bal,
                            after_balance=(previous_bal - amount),
                        )
                        resp = requests.post(
                            "https://vtpass.com/api/pay",
                            data=payload,
                            auth=authentication,
                        )
                        status = "successful"

                    except:
                        pass

                elif str(cable_name) == "GOTV":
                    authentication = (
                        f"{config.vtpass_email}",
                        f"{config.vtpass_password}",
                    )

                    payload = {
                        "billersCode": smart_card_number,
                        "serviceID": "gotv",
                        "request_id": ident,
                        "variation_code": cableplan.product_code,
                        "phone": user.Phone,
                    }

                    try:
                        check = user.withdraw(user.id, amount)
                        if check is False:
                            errors["error"] = " insufficient balance "
                            raise serializers.ValidationError(errors)
                        Wallet_summary.objects.create(
                            user=user,
                            product="{}  N{} Cable tv Sub with {} ".format(
                                cableplan.package, amount, smart_card_number
                            ),
                            amount=amount,
                            previous_balance=previous_bal,
                            after_balance=(previous_bal - amount),
                        )
                        resp = requests.post(
                            "https://vtpass.com/api/pay",
                            data=payload,
                            auth=authentication,
                        )
                        status = "successful"

                    except:
                        pass

                elif str(cable_name) == "STARTIME":
                    authentication = (
                        f"{config.vtpass_email}",
                        f"{config.vtpass_password}",
                    )

                    payload = {
                        "billersCode": smart_card_number,
                        "serviceID": "startimes",
                        "request_id": ident,
                        "variation_code": cableplan.product_code,
                        "phone": user.Phone,
                    }

                    try:
                        check = user.withdraw(user.id, amount)
                        if check is False:
                            errors["error"] = "Y insufficient balance "
                            raise serializers.ValidationError(errors)
                        Wallet_summary.objects.create(
                            user=user,
                            product="{}  N{} Cable tv Sub with {} ".format(
                                cableplan.package, amount, smart_card_number
                            ),
                            amount=amount,
                            previous_balance=previous_bal,
                            after_balance=(previous_bal - amount),
                        )
                        resp = requests.post(
                            "https://vtpass.com/api/pay",
                            data=payload,
                            auth=authentication,
                        )
                        status = "successful"

                        logging.error("----------CABLE RESPONSE------")
                        logging.error(f"response = {resp.text}")

                    except:
                        pass

            else:
                if str(cable_name) == "DSTV":
                    url = "https://www.api.ringo.ng/api/agent/p2"
                    payload = {
                        "serviceCode": "P-TV",
                        "type": "DSTV",
                        "smartCardNo": num,
                        "name": cable_plan.package,
                        "code": cable_plan.product_code,
                        "period": "1",
                        "request_id": ident,
                        "hasAddon": str(cable_plan.hasAddon),
                        "addondetails": {
                            "name": cable_plan.Addon_name,
                            "addoncode": cable_plan.addoncode,
                        },
                    }

                    headers = {
                        "email": f"{config.ringo_email}",
                        "password": f"{config.ringo_password}",
                        "Content-Type": "application/json",
                    }
                    requests.request(
                        "POST",
                        url,
                        headers=headers,
                        data=json.dumps(payload),
                        verify=False,
                    )

                    try:
                        mb = CustomUser.objects.get(pk=order_username.pk)
                        check = mb.withdraw(mb.id, amount)
                        if check is False:
                            errors["error"] = "Y insufficient balance "
                            raise serializers.ValidationError(errors)

                        requests.request(
                            "POST",
                            url,
                            headers=headers,
                            data=json.dumps(payload),
                            verify=False,
                        )

                    except:
                        pass

                    status = "successful"

                elif str(cable_name) == "GOTV":
                    # print(' ')
                    # print('sending GOTV cable to RINGO .............')

                    url = "https://www.api.ringo.ng/api/agent/p2"
                    payload = {
                        "serviceCode": "P-TV",
                        "type": "GOTV",
                        "smartCardNo": num,
                        "name": cable_plan.package,
                        "code": cable_plan.product_code,
                        "period": "1",
                        "request_id": ident,
                    }
                    payload = json.dumps(payload)
                    headers = {
                        "email": f"{config.ringo_email}",
                        "password": f"{config.ringo_password}",
                        "Content-Type": "application/json",
                    }

                    # try:
                    mb = CustomUser.objects.get(pk=order_username.pk)
                    check = mb.withdraw(mb.id, amount)
                    if check is False:
                        errors["error"] = "Y insufficient balance "
                        raise serializers.ValidationError(errors)

                    requests.request(
                        "POST", url, headers=headers, data=payload, verify=False
                    )
                    # print(headers)
                    # print(payload)
                    # print(response.text)

                    status = "successful"

                elif str(cable_name) == "STARTIME":
                    url = "https://www.api.ringo.ng/api/agent/p2"
                    payload = {
                        "serviceCode": "P-TV",
                        "type": "STARTIMES",
                        "smartCardNo": num,
                        "request_id": ident,
                        "price": cable_plan.plan_amount,
                    }

                    headers = {
                        "email": f"{config.ringo_email}",
                        "password": f"{config.ringo_password}",
                        "Content-Type": "application/json",
                    }

                    # try:
                    mb = CustomUser.objects.get(pk=order_username.pk)
                    check = mb.withdraw(mb.id, amount)
                    if check is False:
                        errors["error"] = "Y insufficient balance "
                        raise serializers.ValidationError(errors)

                    requests.request(
                        "POST",
                        url,
                        headers=headers,
                        data=json.dumps(payload),
                        verify=False,
                    )
                    # print(payload)
                    # print(response.text)

                    status = "successful"

            #            try:
            #                figure = cableplan.commission
            #                if figure > 0:
            #                    if user.referer_username:
            #                        if CustomUser.objects.filter(username__iexact = user.referer_username).exists():
            #                            referer  = CustomUser.objects.get(username__iexact = user.referer_username)
            #
            #                            if  user.user_type == "Smart Earner":
            #                                com =  referer.Referer_Bonus
            #                                referer.ref_deposit(figure)
            #
            #                                Wallet_summary.objects.create(user= referer, product="[Referal bonus] you received N{} commission  from your referal {} CableSub Transaction".format(figure,user.username), amount = figure, previous_balance = com, after_balance= (com + figure))
            #
            #                                notify.send(referer, recipient=referer, verb="[Referal bonus] you received N{} commission from your referal {} CableSub Transaction".format(figure,user.username))
            #
            #            except:
            #                pass

            serializer.save(
                Status=status,
                ident=ident,
                balance_before=previous_bal,
                balance_after=(previous_bal - amount),
                plan_amount=amount,
            )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ValidateIUCAPIView(APIView):
    def get(self, request):
        iuc = request.GET.get("smart_card_number", None)
        cable_id = request.GET.get("cablename", None)

        if config.Cable_provider == "VTPASS":
            if cable_id == "DSTV":
                data = {"billersCode": iuc, "serviceID": "dstv"}

            elif cable_id == "GOTV":
                data = {"billersCode": iuc, "serviceID": "gotv"}

            elif cable_id == "STARTIME" or cable_id == "STARTIMES":
                data = {"billersCode": iuc, "serviceID": "startimes"}

            invalid = False
            authentication = (f"{config.vtpass_email}", f"{config.vtpass_password}")

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
            url = "https://www.api.ringo.ng/api/agent/p2"
            payload = {"serviceCode": "V-TV", "type": cable_id, "smartCardNo": iuc}

            # print(payload)

            headers = {
                "email": f"{config.ringo_email}",
                "password": f"{config.ringo_password}",
                "Content-Type": "application/json",
            }

            response = requests.post(url, headers=headers, data=json.dumps(payload))
            # print(response.text)
            a = json.loads(response.text)

            if response.status_code == 200:
                name = a["customerName"]
                invalid = False
            else:
                name = "INVALID_SMARTCARDNO"
                invalid = True

        data = {"invalid": invalid, "name": name}

        return Response(data)


class ValidateMeterAPIView(APIView):
    def get(self, request):
        meternumber = request.GET.get("meternumber", None)
        disconame = request.GET.get("disconame", None)
        mtype = request.GET.get("mtype", None)

        # disconame = Disco_provider_name.objects.get(id=disconame).name
        if config.Bill_provider == "VTPASS":
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

            invalid = False
            data = {"billersCode": meternumber, "serviceID": disconame, "type": mtype}
            authentication = (f"{config.vtpass_email}", f"{config.vtpass_password}")

            resp = requests.post(
                "https://vtpass.com/api/merchant-verify", data=data, auth=authentication
            )
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
            name = "NO NAME RETURN"
            address = False

            # print("hello")
            # print(disconame)

            url = "https://www.api.ringo.ng/api/agent/p2"
            payload = {
                "serviceCode": "V-ELECT",
                "disco": Disco_provider_name.objects.get(name=disconame).p_id,
                "meterNo": meternumber,
                "type": mtype,
            }

            # print(payload)

            headers = {
                "email": f"{config.ringo_email}",
                "password": f"{config.ringo_password}",
                "Content-Type": "application/json",
            }

            response = requests.post(url, headers=headers, data=json.dumps(payload))
            # print(response.text)
            a = json.loads(response.text)

            status = a["status"]

            if status == "200":
                name = a["customerName"]
                invalid = False
            else:
                name = "NO NAME RETURN"
                invalid = True

        data = {"invalid": invalid, "name": name, "address": address}

        return Response(data)


class BillPaymentAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        try:
            item = Billpayment.objects.filter(user=request.user).get(pk=id)
            serializer = BillpaymentSerializer(item)
            return Response(serializer.data)
        except Billpayment.DoesNotExist:
            return Response(status=404)


class BillPaymentAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Billpayment.objects.filter(user=request.user).order_by("-create_date")
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = BillpaymentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        status = "processing"
        serializer = BillpaymentSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            meter_number = serializer.validated_data["meter_number"]
            mtype = serializer.validated_data["MeterType"]
            disco_name = serializer.validated_data["disco_name"]
            amount = serializer.validated_data["amount"]
            number = serializer.validated_data["Customer_Phone"]
            previous_bal = user.Account_Balance
            token = ""
            errors = {}

            service = ServicesCharge.objects.get(service="Bill")

            if user.user_type == "Affilliate":
                if service.Affilliate_charge > 0.0:
                    paid_amount = float(amount) + float(service.Affilliate_charge)

                elif service.Affilliate_discount > 0.0:
                    paid_amount = float(amount) - (
                        float(amount) * service.Affilliate_discount / 100
                    )
                else:
                    paid_amount = float(amount)

            elif user.user_type == "TopUser":
                if service.topuser_charge > 0.0:
                    paid_amount = float(amount) + float(service.topuser_charge)

                elif service.topuser_discount > 0.0:
                    paid_amount = float(amount) - (
                        float(amount) * service.topuser_discount / 100
                    )
                else:
                    paid_amount = float(amount)
            elif user.user_type == "API":
                if service.api_charge > 0.0:
                    paid_amount = float(amount) + float(service.api_charge)

                elif service.api_discount > 0.0:
                    paid_amount = float(amount) - (
                        float(amount) * service.api_discount / 100
                    )

                else:
                    paid_amount = float(amount)
            else:
                if service.charge > 0.0:
                    paid_amount = float(amount) + float(service.charge)

                elif service.discount > 0.0:
                    paid_amount = float(amount) - (
                        float(amount) * service.discount / 100
                    )

                else:
                    paid_amount = float(amount)

            # def create_id():
            #     num = random.randint(1, 10)
            #     num_2 = random.randint(1, 10)
            #     num_3 = random.randint(1, 10)

            #     return str(num_2)+str(num_3)+str(uuid.uuid4())[:4]
            # ident = create_id()

            def create_id():
                num = random.randint(1000, 4999)
                num_2 = random.randint(5000, 8000)
                num_3 = random.randint(111, 999) * 2
                return (
                    str(Mdate.now().strftime("%Y%m%d%H%M%S"))
                    + str(num)
                    + str(num_2)
                    + str(num_3)
                    + str(uuid.uuid4())
                )

            ident = create_id()

            check = user.withdraw(user.id, paid_amount)
            if check is False:
                errors["error"] = "Y insufficient balance "
                raise serializers.ValidationError(errors)

            Wallet_summary.objects.create(
                user=user,
                product="{}  N{} Electricity Bill Payment  with {} ".format(
                    disco_name.name, amount, meter_number
                ),
                amount=paid_amount,
                previous_balance=previous_bal,
                after_balance=(previous_bal - paid_amount),
            )

            if config.Bill_provider == "VTPASS":
                if disco_name.name == "Ikeja Electric":
                    disconame = "ikeja-electric"

                elif disco_name.name == "Eko Electric":
                    disconame = "eko-electric"

                elif disco_name.name == "Kaduna Electric":
                    disconame = "kaduna-electric"

                elif disco_name.name == "Port Harcourt Electric":
                    disconame = "portharcourt-electric"

                elif disco_name.name == "Jos Electric":
                    disconame = "jos-electric"

                elif disco_name.name == "Ibadan Electric":
                    disconame = "ibadan-electric"

                elif disco_name.name == "Kano Electric":
                    disconame = "kano-electric"

                elif disco_name.name == "Abuja Electric":
                    disconame = "abuja-electric"

                authentication = (f"{config.vtpass_email}", f"{config.vtpass_password}")
                payload = {
                    "billersCode": meter_number,
                    "amount": amount,
                    "serviceID": disconame,
                    "request_id": ident,
                    "variation_code": mtype,
                    "phone": number,
                }
                response = requests.post(
                    "https://vtpass.com/api/pay", data=payload, auth=authentication
                )
                # print(response.text)
                try:
                    if response.status_code == 200 or response.status_code == 201:
                        status = "successful"
                        a = json.loads(response.text)
                        token = a["purchased_code"]

                    else:
                        payload = {"request_id": ident}

                        response = requests.post(
                            "https://vtpass.com/api/requery",
                            data=payload,
                            auth=authentication,
                        )
                        status = "successful"
                        a = json.loads(response.text)
                        token = a["purchased_code"]

                except:
                    pass

            else:
                url = "https://www.api.ringo.ng/api/agent/p2"
                payload = {
                    "serviceCode": "P-ELECT",
                    "disco": disco_name.p_id,
                    "meterNo": meter_number,
                    "type": mtype.upper(),
                    "amount": amount,
                    "phonenumber": number,
                    "request_id": ident,
                }
                headers = {
                    "email": f"{config.ringo_email}",
                    "password": f"{config.ringo_password}",
                    "Content-Type": "application/json",
                }

                response = requests.post(url, headers=headers, data=json.dumps(payload))

                try:
                    if response.status_code == 200 or response.status_code == 201:
                        a = json.loads(response.text)
                        token = a["token"]
                        status = "successful"

                    else:
                        url = "https://www.api.ringo.ng//api/b2brequery"
                        payload = {"request_id": ident}
                        headers = {
                            "email": f"{config.ringo_email}",
                            "password": f"{config.ringo_password}",
                            "Content-Type": "application/json",
                        }

                        response = requests.post(
                            url, headers=headers, data=json.dumps(payload)
                        )

                        # #print(payload)
                        # #print(response.text)
                        a = json.loads(response.text)
                        token = a["token"]
                        status = "successful"

                except:
                    pass

            #            try:
            #                figure = disco_name.commission
            #                if figure > 0:
            #                    if user.referer_username:
            #                        if CustomUser.objects.filter(username__iexact = user.referer_username).exists():
            #                            referer  = CustomUser.objects.get(username__iexact = user.referer_username)
            #
            #                            if  user.user_type == "Smart Earner":
            #                                com =  referer.Referer_Bonus
            #                                referer.ref_deposit(figure)
            #
            #                                Wallet_summary.objects.create(user= referer, product="[Referal bonus] you received N{} commission  from your referal {} BillPayment Transaction".format(figure,user.username), amount = figure, previous_balance = com, after_balance= (com + figure))
            #
            #                                notify.send(referer, recipient=referer, verb="[Referal bonus] you received N{} commission from your referal {} BillPayment Transaction".format(figure,user.username))
            #
            #            except:
            #                pass

            serializer.save(
                Status=status,
                token=token,
                ident=ident,
                balance_before=previous_bal,
                balance_after=(previous_bal - float(amount)),
                paid_amount=paid_amount,
            )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class PINCCHECKAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        pin = request.GET.get("pin", None)
        # print(pin)
        # print(request.user.pin)

        if pin != str(request.user.pin):
            return Response({"error": "  Incorrect pin"}, status=400)

        else:
            data = {"message": "pin correct"}

        return Response(data, status=200)


class PINCHANGEAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        pin1 = request.GET.get("pin1", None)
        pin2 = request.GET.get("pin2", None)
        oldpin = request.GET.get("oldpin", None)
        # print(oldpin)
        # print(request.user.pin)
        if oldpin != str(request.user.pin):
            return Response({"error": "Old pin is incorrect"}, status=400)

        elif pin1 != pin2:
            return Response({"error": "Two Fields are not match"}, status=400)

        elif len(str(pin1)) > 5 or len(str(pin1)) < 5:
            return Response({"error": "Your pin must be 5 digit in length"}, status=400)

        elif len(str(pin2)) > 5 or len(str(pin2)) < 5:
            return Response({"error": "Your pin must be 5 digit in length"}, status=400)

        elif pin1.isdigit() is not True and pin2.isdigit() is not True:
            return Response({"error": "The pin must be Digit"}, status=400)

        elif oldpin == str(request.user.pin):
            return Response(
                {"error": "The old pin must not be the same as the new pin"}, status=400
            )

        else:
            request.user.pin = pin1
            request.user.save()
            data = {"message": "pin Changed successfully"}

        return Response(data, status=200)


class PINRESETAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        pin1 = request.GET.get("pin1", None)
        pin2 = request.GET.get("pin2", None)
        password = request.GET.get("password", None)
        # print(password)
        # print(request.user.password)
        if not request.user.check_password(password):
            return Response({"error": "incorrect password"}, status=400)

        elif pin1 != pin2:
            return Response({"error": "pin1 and pin2  are not match"}, status=400)

        elif len(str(pin1)) > 5 or len(str(pin1)) < 5:
            return Response({"error": "Your pin must be 5 digit in length"}, status=400)

        elif len(str(pin2)) > 5 or len(str(pin2)) < 5:
            return Response({"error": "Your pin must be 5 digit in length"}, status=400)

        elif pin1.isdigit() is not True and pin2.isdigit() is not True:
            return Response({"error": "The pin must be Digit"}, status=400)

        else:
            request.user.pin = pin1
            request.user.save()
            data = {"message": "pin Reset successfully"}

        return Response(data, status=200)


class PINSETUPAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        pin1 = request.GET.get("pin1", None)
        pin2 = request.GET.get("pin2", None)

        if pin1 != pin2:
            return Response({"error": "Two Fields are not match"}, status=400)

        elif len(str(pin1)) > 5 or len(str(pin1)) < 5:
            return Response({"error": "Your pin must be 5 digit in length"}, status=400)

        elif len(str(pin2)) > 5 or len(str(pin2)) < 5:
            return Response({"error": "Your pin must be 5 digit in length"}, status=400)

        elif pin1.isdigit() is not True and pin2.isdigit() is not True:
            return Response({"error": "The pin must be Digit"}, status=400)

        else:
            request.user.pin = pin1
            request.user.save()
            data = {"message": "pin setup successfully"}

        return Response(data, status=200)


class CouponPaymentAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = CouponPayment.objects.filter(user=request.user).order_by("-create_date")
        serializer = CouponPaymentSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        status = "successful"
        serializer = CouponPaymentSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            Code = serializer.validated_data["Code"]

            if Couponcode.objects.filter(Coupon_Code=Code).exists():
                ms = Couponcode.objects.get(Coupon_Code=Code).amount
                amount = Couponcode.objects.get(Coupon_Code=Code).amount
                previous_bal1 = user.Account_Balance
                user.deposit(user.id, float(ms), False, "Coupon payment from API")
                sta = Couponcode.objects.get(Coupon_Code=Code)
                sta.Used = True

                sta.save()
                Wallet_summary.objects.create(
                    user=user,
                    product="Coupon Payment  N{} ".format(amount),
                    amount=amount,
                    previous_balance=previous_bal1,
                    after_balance=(previous_bal1 - float(amount)),
                )

            serializer.save(Status=status, amount=amount)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class Airtime_fundingAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Airtime_funding.objects.filter(user=request.user).order_by(
            "-create_date"
        )
        serializer = Airtime_fundingSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = Airtime_fundingSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            network = serializer.validated_data["network"]
            amount = serializer.validated_data["amount"]
            number = serializer.validated_data["mobile_number"]
            fund_wallet = serializer.validated_data["use_to_fund_wallet"]

            perc = Percentage.objects.get(network=Network.objects.get(name=network))
            Receivece_amount = float(amount) * int(perc.percent) / 100

            def sendmessage(sender, message, to, route):
                baseurl = f"https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}"
                requests.get(baseurl, verify=False)

            sendmessage(
                "Msorg",
                "{0} want to fund his/her account with  airtime transfer network: {1} amount:{2} Phone number:{3} https://www.legitdata.com.ngpage-not-found-error/page/vtuapp/Airtime_funding/".format(
                    user.username, network, amount, number
                ),
                f"{config.sms_notification_number}",
                "03",
            )

            # serializer.save(Receivece_amount=Receivece_amount, AccountName=user.AccountName,
            #                 BankName=user.BankName, AccountNumber=user.AccountNumber)
            serializer.save(
                Receivece_amount=Receivece_amount,
                AccountName=user.AccountName,
                BankName=user.BankName,
                AccountNumber=user.AccountNumber,
                use_to_fund_wallet=fund_wallet,
            )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class WithdrawAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Withdraw.objects.filter(user=request.user).order_by("-create_date")
        serializer = WithdrawSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        status = "successful"
        serializer = WithdrawSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            amount = serializer.validated_data["amount"]
            bankaccount = serializer.validated_data["accountNumber"]
            name = serializer.validated_data["accountName"]
            bankname = serializer.validated_data["bankName"]
            errors = {}

            amt = float(amount) + 100

            def sendmessage(sender, message, to, route):
                baseurl = f"https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}"
                requests.get(baseurl, verify=False)

            previous_bal = user.Account_Balance

            check = user.withdraw(user.id, float(amt))
            if check is False:
                errors["error"] = "Y insufficient balance "
                raise serializers.ValidationError(errors)
            Wallet_summary.objects.create(
                user=user,
                product="Withdraw   N{}  with N100 charge".format(amount),
                amount=amt,
                previous_balance=previous_bal,
                after_balance=(previous_bal - float(amt)),
            )

            sendmessage(
                "datavilla",
                "{0} want to withdraw   amount:{1} to {2} {3} {4}   https://www.datavilla.ng/way/to/vtuapp/admin/app/withdraw/".format(
                    user.username, amount, bankname, bankaccount, name
                ),
                f"{config.sms_notification_number}",
                "2",
            )

            serializer.save(Status=status)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TransferAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Transfer.objects.filter(user=request.user).order_by("-create_date")
        serializer = TransferSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        status = "successful"
        serializer = TransferSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            amount = serializer.validated_data["amount"]
            receiver_username = serializer.validated_data["receiver_username"]
            errors = {}

            mb_2 = CustomUser.objects.get(username__iexact=receiver_username)
            previous_bal1 = user.Account_Balance
            previous_bal2 = mb_2.Account_Balance

            check = user.withdraw(user.id, float(amount))
            if check is False:
                errors["error"] = "Y insufficient balance "
                raise serializers.ValidationError(errors)

            mb_2.deposit(mb_2.id, float(amount), True, "Wallet to Wallet from API")
            notify.send(
                mb_2,
                recipient=mb_2,
                verb="You Received sum of #{} from {} ".format(amount, user.username),
            )

            Wallet_summary.objects.create(
                user=user,
                product="Transfer N{} to {}".format(amount, mb_2.username),
                amount=amount,
                previous_balance=previous_bal1,
                after_balance=(previous_bal1 - float(amount)),
            )

            Wallet_summary.objects.create(
                user=mb_2,
                product="Received sum N{} from {}".format(amount, user.username),
                amount=amount,
                previous_balance=previous_bal2,
                after_balance=(previous_bal2 + float(amount)),
            )

            serializer.save(
                Status=status,
                previous_balance=previous_bal1,
                after_balance=(previous_bal1 + float(amount)),
            )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class bonus_transferAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = bonus_transfer.objects.filter(user=request.user).order_by(
            "-create_date"
        )
        serializer = bonus_transferSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = bonus_transferSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            amount = serializer.validated_data["amount"]

            previous_bal1 = user.Account_Balance

            user.ref_withdraw(float(amount))
            user.deposit(user.id, float(amount), True, "Bonus to wallet from API")
            notify.send(
                user,
                recipient=user,
                verb="#{} referer bonus has been added to your wallet,refer more people to get more bonus".format(
                    amount
                ),
            )

            Wallet_summary.objects.create(
                user=user,
                product="referer bonus to wallet N{} ".format(amount),
                amount=amount,
                previous_balance=previous_bal1,
                after_balance=(previous_bal1 - float(amount)),
            )

            serializer.save()

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


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


# Result_Checker_Pin_order api


class Result_Checker_Pin_orderAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        try:
            item = Result_Checker_Pin_order.objects.filter(user=request.user).get(pk=id)
            serializer = Result_Checker_Pin_orderSerializer(item)
            return Response(serializer.data)
        except Result_Checker_Pin_order.DoesNotExist:
            return Response(status=404)


class Result_Checker_Pin_orderAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Result_Checker_Pin_order.objects.filter(user=request.user).order_by(
            "-create_date"
        )
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = Result_Checker_Pin_orderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = Result_Checker_Pin_orderSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            (serializer.validated_data["user"]).username
            exam = serializer.validated_data["exam_name"]
            quantity = serializer.validated_data["quantity"]
            exam_name = exam
            errors = {}
            control = Result_Checker_Pin.objects.get(exam_name=exam)

            provider_amount = round(control.provider_amount)
            # print(provider_amount)

            if request.user.user_type == "Affilliate":
                amount = Result_Checker_Pin.objects.get(exam_name=exam).Affilliate_price

            elif request.user.user_type == "TopUser":
                amount = Result_Checker_Pin.objects.get(exam_name=exam).TopUser_price

            elif request.user.user_type == "API":
                amount = Result_Checker_Pin.objects.get(exam_name=exam).api_price
            else:
                amount = Result_Checker_Pin.objects.get(exam_name=exam).amount

            amt = amount * quantity
            user = serializer.validated_data["user"]
            previous_bal = user.Account_Balance
            errors = {}
            data = {}

            def create_id():
                random.randint(1, 10070)
                num_2 = random.randint(1, 1056500)
                num_3 = random.randint(1, 1000)
                return str(num_2) + str(num_3) + str(uuid.uuid4())[:8]

            ident = create_id()

            if config.ResultCheckerSource == "API":
                if exam_name == "WAEC":
                    if quantity == 1:
                        q = "WRCONE"

                    elif quantity == 2:
                        q = "WRCTWO"
                    elif quantity == 3:
                        q = "WRCTHR"
                    elif quantity == 4:
                        q = "WRCFOU"
                    elif quantity == 5:
                        q = "WRCFIV"

                    if control.provider_api == "MOBILENIG":
                        # print('hi')
                        # print(f"https://mobilenig.com/API/bills/waec?username={config.mobilenig_username}&api_key={config.mobilenig_api_key}&product_code={q}&price={provider_amount*quantity}&trans_id={ident}")
                        # try:

                        check = user.withdraw(user.id, float(amt))
                        if check is False:
                            errors["error"] = " insufficient balance "
                            raise serializers.ValidationError(errors)

                        Wallet_summary.objects.create(
                            user=user,
                            product="{} WAEC EPIN GENERATED  N{} ".format(
                                quantity, amt
                            ),
                            amount=amt,
                            previous_balance=previous_bal,
                            after_balance=(previous_bal + float(amt)),
                        )

                        resp = requests.get(
                            f"https://mobilenig.com/API/bills/waec_test?username={config.mobilenig_username}&api_key={config.mobilenig_api_key}&product_code={q}&price={provider_amount*quantity}&trans_id={ident}"
                        )
                        # print(resp.text)
                        ab = json.loads(resp.text)
                        data = resp.text
                        # print(data)

                    elif control.provider_api == "EASYACCESS":
                        try:
                            if quantity > 10:
                                errors[
                                    "error"
                                ] = "you can only generate up to 10 pins at a time"
                                raise serializers.ValidationError(errors)

                            else:
                                check = user.withdraw(user.id, float(amt))
                                if check is False:
                                    errors["error"] = " insufficient balance "
                                    raise serializers.ValidationError(errors)

                                Wallet_summary.objects.create(
                                    user=user,
                                    product="{} WAEC EPIN GENERATED  N{} ".format(
                                        quantity, amt
                                    ),
                                    amount=amt,
                                    previous_balance=previous_bal,
                                    after_balance=(previous_bal + float(amt)),
                                )

                                url = "https://easyaccess.com.ng/api/waec_v2.php"
                                payload = {"no_of_pins": quantity}
                                files = []
                                headers = {"AuthorizationToken": ""}
                                headers.update(
                                    {
                                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
                                    }
                                )

                                response = requests.request(
                                    "POST",
                                    url,
                                    headers=headers,
                                    data=payload,
                                    files=files,
                                )
                                data = response.text

                        except:
                            errors = {}
                            errors["error"] = "Service is not currently available"
                            raise serializers.ValidationError(errors)

                    else:
                        check = user.withdraw(user.id, float(amt))
                        if check is False:
                            errors["error"] = " insufficient balance "
                            raise serializers.ValidationError(errors)

                        Wallet_summary.objects.create(
                            user=user,
                            product="{} WAEC EPIN GENERATED  N{} ".format(
                                quantity, amt
                            ),
                            amount=amt,
                            previous_balance=previous_bal,
                            after_balance=(previous_bal + float(amt)),
                        )

                        data = {
                            "variation_code": "waecdirect",
                            "serviceID": "waec",
                            "phone": request.user.Phone,
                            "request_id": ident,
                            "quantity": quantity,
                        }
                        # print(data)
                        authentication = (
                            f"{config.vtpass_email}",
                            f"{config.vtpass_password}",
                        )
                        resp = requests.post(
                            "https://vtpass.com/api/pay", data=data, auth=authentication
                        )
                        # print(resp.text)

                        try:
                            a = json.loads(resp.text)
                            data = a["purchased_code"]
                        except:
                            try:
                                url = "https://vtpass.com/api/requery"
                                data = {"request_id": ident}
                                authentication = (
                                    f"{config.vtpass_email}",
                                    f"{config.vtpass_password}",
                                )
                                resp = requests.post(
                                    url, data=data, auth=authentication
                                )

                                a = json.loads(resp.text)
                                data = a["purchased_code"]
                            except:
                                pass

                elif exam_name == "NECO":
                    if quantity == 1:
                        q = "NECONE"

                    elif quantity == 2:
                        q = "NECTWO"
                    elif quantity == 3:
                        q = "NECTHR"
                    elif quantity == 4:
                        q = "NECFOU"
                    elif quantity == 5:
                        q = "NECFIV"
                    if control.provider_api == "MOBILENIG":
                        # try:

                        check = user.withdraw(user.id, float(amt))
                        if check is False:
                            errors["error"] = "Y insufficient balance "
                            raise serializers.ValidationError(errors)
                        Wallet_summary.objects.create(
                            user=user,
                            product="{} NECO EPIN GENERATED  N{} ".format(
                                quantity, amt
                            ),
                            amount=amt,
                            previous_balance=previous_bal,
                            after_balance=(previous_bal + float(amt)),
                        )

                        resp = requests.get(
                            f"https://mobilenig.com/API/bills/neco?username={config.mobilenig_username}&api_key={config.mobilenig_api_key}&product_code={q}&price={provider_amount*quantity}&trans_id={ident}"
                        )

                        # print(resp.text)
                        ab = json.loads(resp.text)
                        # data = resp.text
                        data = ab["details"]["tokens"]
                        # print(data)

                    elif control.provider_api == "EASYACCESS":
                        try:
                            if quantity > 10:
                                errors[
                                    "error"
                                ] = "you can only generate up to 10 pins at a time"
                                raise serializers.ValidationError(errors)

                            else:
                                check = user.withdraw(user.id, float(amt))

                                if check is False:
                                    errors["error"] = "Y insufficient balance "
                                    raise serializers.ValidationError(errors)

                                Wallet_summary.objects.create(
                                    user=user,
                                    product="{} NECO EPIN GENERATED  N{} ".format(
                                        quantity, amt
                                    ),
                                    amount=amt,
                                    previous_balance=previous_bal,
                                    after_balance=(previous_bal + float(amt)),
                                )

                                url = "https://easyaccess.com.ng/api/neco_v2.php"

                                payload = {"no_of_pins": quantity}
                                files = []
                                headers = {"AuthorizationToken": ""}
                                headers.update(
                                    {
                                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
                                    }
                                )

                                response = requests.request(
                                    "POST",
                                    url,
                                    headers=headers,
                                    data=payload,
                                    files=files,
                                )
                                data = response.text

                        except:
                            errors = {}
                            errors["error"] = "Service is not currently available"
                            raise serializers.ValidationError(errors)

                    else:
                        errors = {}
                        errors["error"] = "Service is not currently available"
                        raise serializers.ValidationError(errors)

                elif exam_name == "NABTEB":
                    try:
                        if quantity > 10:
                            errors[
                                "error"
                            ] = "you can only generate up to 10 pins at a time"
                            raise serializers.ValidationError(errors)

                        else:
                            check = user.withdraw(user.id, float(amt))
                            if check is False:
                                errors["error"] = " insufficient balance "
                                raise serializers.ValidationError(errors)

                            Wallet_summary.objects.create(
                                user=user,
                                product="{} NABTEB EPIN GENERATED  N{} ".format(
                                    quantity, amt
                                ),
                                amount=amt,
                                previous_balance=previous_bal,
                                after_balance=(previous_bal + float(amt)),
                            )

                            url = "https://easyaccess.com.ng/api/nabteb_v2.php"

                            payload = {"no_of_pins": quantity}
                            files = []
                            headers = {"AuthorizationToken": ""}
                            headers.update(
                                {
                                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
                                }
                            )

                            response = requests.request(
                                "POST", url, headers=headers, data=payload, files=files
                            )
                            data = response.text

                    except:
                        errors = {}
                        errors["error"] = "Service is not currently available"
                        raise serializers.ValidationError(errors)

            else:
                check = user.withdraw(user.id, float(amt))
                if check is False:
                    errors["error"] = "Y insufficient balance "
                    raise serializers.ValidationError(errors)

                Wallet_summary.objects.create(
                    user=user,
                    product="{} {} EPIN GENERATED  N{} ".format(
                        exam_name, quantity, amt
                    ),
                    amount=amt,
                    previous_balance=previous_bal,
                    after_balance=(previous_bal - float(amt)),
                )

                if exam_pin.objects.filter(exam=exam).filter(available=True):
                    qs = exam_pin.objects.filter(exam=exam).filter(available=True)[
                        :quantity
                    ]
                    jsondata = seria2.serialize("json", qs)
                    data = jsondata
                    for x in qs:
                        x.available = False
                        x.save()

                    print(jsondata)

                else:
                    errors["error"] = "Education Pin is not Available for {}".format(
                        exam
                    )
                    raise serializers.ValidationError(errors)

            serializer.save(
                data=data,
                amount=amt,
                previous_balance=previous_bal,
                after_balance=(previous_bal - amt),
            )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# Result_Checker_Pin_order api


##################################################### MANUAL RESULT CHECKER START ########################################
"""
class Result_Checker_Pin_orderAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, id, format=None):
        try:
            item =Result_Checker_Pin_order.objects.filter(user=request.user).get(pk=id)
            serializer = Result_Checker_Pin_orderSerializer(item)
            return Response(serializer.data)
        except Result_Checker_Pin_order.DoesNotExist:
            return Response(status=404)


class Result_Checker_Pin_orderAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Result_Checker_Pin_order.objects.filter(user=request.user).order_by('-create_date')
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = Result_Checker_Pin_orderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        status = "processing"
        fund = 0
        serializer = Result_Checker_Pin_orderSerializer(data=request.data,context={'request': request})

        if serializer.is_valid():
                       user = (serializer.validated_data["user"])
                       exam = serializer.validated_data["exam_name"]
                       quantity = serializer.validated_data["quantity"]
                       exam_name = exam



                       if request.user.user_type == "Affilliate":
                                amount = Exam_pin_price.objects.get(exam_name=exam).Affilliate_price
                       elif request.user.user_type == "TopUser":
                                amount = Exam_pin_price.objects.get(exam_name=exam).TopUser_price

                       elif request.user.user_type == "API":
                                amount = Exam_pin_price.objects.get(exam_name=exam).api_price
                       else:
                                amount = Exam_pin_price.objects.get(exam_name=exam).amount

                       amt = amount * quantity


                       user = (serializer.validated_data["user"])
                       previous_bal = user.Account_Balance
                       errors = {}
                       data = {}

                       def create_id():
                                num = random.randint(1,10070)
                                num_2 = random.randint(1,1056500)
                                num_3 = random.randint(1,1000)
                                return str(num_2)+str(num_3)+str(uuid.uuid4())[:8]

                       ident = create_id()


                       check = user.withdraw(user.id, float(amt))
                       if check == False:
                            errors['error'] = u'Y insufficient balance '
                            raise serializers.ValidationError(errors)

                       print(' ')
                       print('---------------------')
                       print(f"amt = {amt}")

                       Wallet_summary.objects.create(user= user, product="{} {} EPIN GENERATED  N{} ".format(exam_name,quantity,amt), amount = amt, previous_balance = previous_bal, after_balance= (previous_bal + float(amt)))


                       if Result_Checker_Pin.objects.filter(exam_name = exam).filter(Buy = False):
                              qs = Result_Checker_Pin.objects.filter(exam_name = exam).filter(Buy = False)[:quantity]
                              jsondata = seria2.serialize('json', qs)
                              data = jsondata
                              for x in qs:
                                  x.Buy = True
                                  x.save()


                              print(jsondata)
                       else:
                               errors['error'] = u'Education Pin is not Available for {}'.format(exam)
                               raise serializers.ValidationError(errors)



                       serializer.save(data=data ,amount=amt,previous_balance = previous_bal, after_balance =(previous_bal - amt) )

                       return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

"""
##################################################### MANUAL RESULT CHECKER END ########################################


class Recharge_pin_orderAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, format=None):
        try:
            item = Recharge_pin_order.objects.filter(user=request.user).get(pk=id)
            serializer = Recharge_pin_orderSerializer(item)
            return Response(serializer.data)
        except Recharge_pin_order.DoesNotExist:
            return Response(status=404)


class Recharge_pin_orderAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Recharge_pin_order.objects.filter(user=request.user).order_by(
            "-create_date"
        )
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = Recharge_pin_orderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = Recharge_pin_orderSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            (serializer.validated_data["user"]).username
            network = serializer.validated_data["network"]
            network_amount = serializer.validated_data["network_amount"]
            quantity = serializer.validated_data["quantity"]
            # amount = Result_Checker_Pin.objects.get(exam_name=exam).amount
            # amt = network_amount.amount_to_pay * quantity
            user = serializer.validated_data["user"]
            previous_bal = user.Account_Balance
            errors = {}

            # #print('............RECHARGE PRNGINTI ORDER............')
            # #print(f"network = {network}")
            # #print(f"network_amount = {network_amount}")

            myamount = network_amount.amount

            if request.user.user_type == "Affilliate":
                amt = network_amount.Affilliate_price * quantity

            elif request.user.user_type == "TopUser":
                amt = network_amount.TopUser_price * quantity

            elif request.user.user_type == "API":
                amt = network_amount.api_price * quantity
            else:
                amt = network_amount.amount_to_pay * quantity

            def create_id():
                random.randint(1, 10070)
                num_2 = random.randint(1, 1056500)
                num_3 = random.randint(1, 1000)
                return str(num_2) + str(num_3) + str(uuid.uuid4())[:8]

            create_id()

            if (
                Recharge_pin.objects.filter(network=Network.objects.get(name=network))
                .filter(available=True)
                .filter(amount=myamount)
            ):
                check = user.withdraw(user.id, float(amt))
                if check is False:
                    errors["error"] = "Y insufficient balance "
                    raise serializers.ValidationError(errors)
                Wallet_summary.objects.create(
                    user=user,
                    product="{} {}  N{} Airtime pin Generated".format(
                        network.name, quantity, myamount
                    ),
                    amount=amt,
                    previous_balance=previous_bal,
                    after_balance=(previous_bal - amt),
                )

                qs = (
                    Recharge_pin.objects.filter(
                        network=Network.objects.get(name=network)
                    )
                    .filter(available=True)
                    .filter(amount=network_amount.amount)[:quantity]
                )
                jsondata = seria2.serialize("json", qs)
                data = jsondata
                for x in qs:
                    x.available = False
                    x.save()

                # print(jsondata)
            else:
                errors[
                    "error"
                ] = "Airtime Pin is not Available on this network currently"
                raise serializers.ValidationError(errors)

            serializer.save(
                data=data,
                amount=amt,
                previous_balance=previous_bal,
                after_balance=(previous_bal - amt),
            )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ReferalListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Referal_list.objects.filter(user=request.user).order_by("id")
        serializer = Referal_listSerializer(items, many=True)
        return Response(serializer.data)


# class KYCCreate(generic.CreateView):
#     form_class = KYCForm
#     template_name = "kyc_form.html"

#     def form_valid(self, form):
#         form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList(
#             ["use updated browser and retry"]
#         )
#         return self.form_invalid(form)

#         return super(KYCCreate, self).form_valid(form)

class KYCAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = KYC.objects.filter(user=request.user)
        serializer = KYCSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = KYCSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            errors = {}
            (serializer.validated_data["First_Name"])
            (serializer.validated_data["Middle_Name"])
            (serializer.validated_data["Last_Name"])
            (serializer.validated_data["DOB"])
            (serializer.validated_data["Gender"])
            (serializer.validated_data["State_of_origin"])
            (serializer.validated_data["Local_gov_of_origin"])
            (serializer.validated_data["BVN"])
            (serializer.validated_data["passport_photogragh"])
            verify = False

            previous_bal = user.Account_Balance
            if 100 > user.Account_Balance:
                errors["error"] = "Y insufficient balance "
                raise serializers.ValidationError(errors)

            check = user.withdraw(user.id, 100)

            if check is False:
                errors["error"] = " insufficient balance "
                raise serializers.ValidationError(errors)

            Wallet_summary.objects.create(
                user=user,
                product="BVN VERIFY  N{}  ".format(100),
                amount=100,
                previous_balance=previous_bal,
                after_balance=(previous_bal - float(100)),
            )

            if KYC.objects.filter(user=user).exists():
                KYC.objects.filter(user=user).delete()
                comment = "KYC submitted successfully"
                message = "Information submitted successful ,Your account verification in process"
                serializer.save(
                    comment=comment, dump="", primary_details_verified=verify
                )
                return Response({"message": message}, status=201)

            else:
                comment = "KYC submitted successfully"
                message = "Information submitted successful ,Your account verification in process"
                serializer.save(
                    comment=comment, dump="", primary_details_verified=verify
                )
                return Response({"message": message}, status=201)

        return Response(serializer.errors, status=400)


"""
class KYCAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = KYC.objects.filter(user=request.user)
        serializer = KYCSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = KYCSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            user = (serializer.validated_data["user"])
            errors = {}
            First_Name = (serializer.validated_data["First_Name"])
            Middle_Name = (serializer.validated_data["Middle_Name"])
            Last_Name = (serializer.validated_data["Last_Name"])
            DOB = (serializer.validated_data["DOB"])
            Gender = (serializer.validated_data["Gender"])
            State_of_origin = (serializer.validated_data["State_of_origin"])
            Local_gov_of_origin = (
                serializer.validated_data["Local_gov_of_origin"])
            BVN = (serializer.validated_data["BVN"])
            passport_photogragh = (
                serializer.validated_data["passport_photogragh"])
            verify = False

            previous_bal = user.Account_Balance
            if 100 > user.Account_Balance:
                errors['error'] = u'Y insufficient balance '
                raise serializers.ValidationError(errors)


            def create_id():
                num = random.randint(1, 10)
                num_2 = random.randint(1, 10)
                num_3 = random.randint(80, 10000)
                return str(num_2)+str(num_3) + str(uuid.uuid4())[:8]

            url = "https://www.idchecker.com.ng/bvn_verify/"

            payload = {"bvn": BVN}

            headers = {
                'Authorization': f'Token {config.idchecker_api_key}',
                'Content-Type': 'application/json',
            }
            #print(config.idchecker_api_key)

            abd = datetime.strptime(str(DOB), '%Y-%m-%d').strftime('%d-%b-%Y')
            response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            #print(response.text)
            if response.status_code == 200 or  response.status_code == 201 :
                    check = user.withdraw(user.id, 100)

                    if check == False:
                        errors['error'] = u' insufficient balance '
                        raise serializers.ValidationError(errors)

                    Wallet_summary.objects.create(user=user, product="BVN VERIFY  N{}  ".format( 100), amount=100, previous_balance=previous_bal, after_balance=(previous_bal - float(100)))
                    mydata = json.loads(response.text)
                    #print(mydata['response']['data'])

                    if mydata["response"]["responsecode"]  == "00":
                            if KYC.objects.filter(user=user).exists():
                                ab = KYC.objects.filter(user=user).first()
                                if First_Name.upper() == mydata['response']['data']['firstName'].upper() and Middle_Name.upper() == mydata['response']['data']['middleName'].upper() and Last_Name.upper() == mydata['response']['data']['lastName'].upper() and abd == mydata['response']['data']['dateOfBirth'] and Gender == mydata['response']['data']['gender'].upper():
                                    message = "Information submitted successful ,Your account verification in process"
                                    ab.First_Name = First_Name
                                    ab.Middle_Name = Middle_Name
                                    ab.Last_Name = Last_Name
                                    ab.DOB = DOB
                                    ab.Gender = Gender
                                    ab.State_of_origin = State_of_origin
                                    ab.Local_gov_of_origin = Local_gov_of_origin
                                    ab.BVN = BVN
                                    ab.passport_photogragh = passport_photogragh
                                    ab.comment = "BVN MATCHED WITH DETAILS"
                                    ab.dump = response.text
                                    ab.primary_details_verified = True
                                    ab.status= "processing"
                                    ab.save()
                                    return Response({"message": message}, status=201)
                                else:
                                    ab.dump = response.text
                                    ab.comment = "BVN NOT MATCH WITH DEATILS SUPPLIED"


                                    ab.save()
                                    comment = "BVN NOT MATCH WITH DEATILS"
                                    return Response({"message": "BVN NOT MATCH WITH DETAILS SUPPLIED"}, status=400)
                            else:
                                if First_Name.upper() == mydata['response']['data']['firstName'].upper() and Middle_Name.upper() == mydata['response']['data']['middleName'].upper() and Last_Name.upper() == mydata['response']['data']['lastName'].upper() and abd == mydata['response']['data']['dateOfBirth'] and Gender == mydata['response']['data']['gender'].upper():
                                    message = "Information submitted successful ,Your account verification in process"
                                    comment = "BVN MATCHED WITH DETAILS SUPPLIED"
                                    verify = True

                                else:
                                    comment = "BVN MATCHED WITH DETAILS SUPPLIED"
                                    message = "BVN MATCHED WITH DETAILS SUPPLIED"
                                    serializer.save(comment=comment, dump=response.text, primary_details_verified=verify)
                                    return Response({"response": message}, status=400)


                    else:
                                data = json.loads(response.text)
                                return Response(data,status = 400)

            elif  response.status_code == 500:
                            data = {
                                "status":"error",
                                "message": "something went wrong, please try again",
                                }
                            return Response(data,status = 500)
            else:
                        data = json.loads(response.text)
                        return Response(data,status = 400)

            serializer.save(comment=comment, dump=response.text, primary_details_verified=verify)

            return Response({"message": message}, status=201)
        return Response(serializer.errors, status=400)

"""


class GetNetworkAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        mtn = Network.objects.get(name="MTN")
        glo = Network.objects.get(name="GLO")
        airtel = Network.objects.get(name="AIRTEL")
        etisalat = Network.objects.get(name="9MOBILE")
        smile = Network.objects.get(name="SMILE")

        net_1 = NetworkSerializer(mtn)
        net_2 = NetworkSerializer(glo)
        net_3 = NetworkSerializer(airtel)
        net_4 = NetworkSerializer(etisalat)
        net_5 = NetworkSerializer(smile)

        mtn_plans = Plan.objects.filter(network=mtn).order_by("plan_amount").values()
        glo_plans = Plan.objects.filter(network=glo).order_by("plan_amount").values()
        airtel_plans = (
            Plan.objects.filter(network=airtel).order_by("plan_amount").values()
        )
        mobile_plans = (
            Plan.objects.filter(network=etisalat).order_by("plan_amount").values()
        )
        smile_plans = (
            Plan.objects.filter(network=smile).order_by("plan_amount").values()
        )

        return JsonResponse(
            {
                "MTN": {"network_info": net_1.data, "data_plans": list(mtn_plans)},
                "GLO": {"network_info": net_2.data, "data_plans": list(glo_plans)},
                "AIRTEL": {
                    "network_info": net_3.data,
                    "data_plans": list(airtel_plans),
                },
                "9MOBILE": {
                    "network_info": net_4.data,
                    "data_plans": list(mobile_plans),
                },
                "SMILE": {"network_info": net_5.data, "data_plans": list(smile_plans)},
            },
            status=200,
        )


class GetCablePlanAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        startime = (
            CablePlan.objects.filter(cablename__name="STARTIME")
            .order_by("plan_amount")
            .values()
        )
        gotv = (
            CablePlan.objects.filter(cablename__name="GOTV")
            .order_by("plan_amount")
            .values()
        )
        dstv = (
            CablePlan.objects.filter(cablename__name="DSTV")
            .order_by("plan_amount")
            .values()
        )

        return JsonResponse(
            {
                "GOTV": {
                    "cable_id": Cable.objects.get(name="GOTV").id,
                    "plans": list(gotv),
                },
                "DSTV": {
                    "cable_id": Cable.objects.get(name="DSTV").id,
                    "plans": list(dstv),
                },
                "STARTIME": {
                    "cable_id": Cable.objects.get(name="STARTIME").id,
                    "plans": list(startime),
                },
            },
            status=200,
        )


class GetDiscoAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        disco = Disco_provider_name.objects.all().values()

        return JsonResponse(
            {
                "plans": list(disco),
            },
            status=200,
        )


class available_recharge(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        info = ""
        if Info_Alert.objects.all():
            info = [x.message for x in Info_Alert.objects.all()[:1]][0]

        data = {
            "mtn": Recharge_pin.objects.filter(network=Network.objects.get(name="MTN"))
            .filter(available=True)
            .count(),
            "glo": Recharge_pin.objects.filter(network=Network.objects.get(name="GLO"))
            .filter(available=True)
            .count(),
            "airtel": Recharge_pin.objects.filter(
                network=Network.objects.get(name="AIRTEL")
            )
            .filter(available=True)
            .count(),
            "9mobile": Recharge_pin.objects.filter(
                network=Network.objects.get(name="9MOBILE")
            )
            .filter(available=True)
            .count(),
            "balance": request.user.Account_Balance,
            "info": info,
        }

        return Response(data)


def Faqs(request):
    faq_question = frequentlyAskedQuestion.objects.order_by("pk")
    context = {"question": faq_question}
    return render(request, "faq.html", context)


def RetailWebFaqs(request):
    faq_question = RetailWebFrequentlyAskedQuestion.objects.order_by("pk")
    context = {"question": faq_question}
    return render(request, "faq2.html", context)


def selfCenter(request):
    if request.is_ajax():
        transaction_type = request.GET["type"]
        reference = request.GET["ref"]

        status = False
        reciept_id = None

        if transaction_type.upper() == "AIRTIME":
            qs = AirtimeTopup.objects.filter(ident=reference, user=request.user)
            if qs.exists():
                resp = "weldone hameed"
                status = True
                reciept_id = qs.first().id
            else:
                resp = f"Airtime TopUp Transaction matching query(id: {reference}) does not exist"

        elif transaction_type.upper() == "DATA":
            qs = Data.objects.filter(ident=reference, user=request.user)
            if qs.exists():
                resp = "weldone hameed"
                status = True
                reciept_id = qs.first().id
            else:
                resp = (
                    f"Data Transaction matching query(id: {reference}) does not exist"
                )

        elif transaction_type.upper() == "CABLE":
            qs = Cablesub.objects.filter(ident=reference, user=request.user)
            if qs.exists():
                resp = "weldone hameed"
                status = True
                reciept_id = qs.first().id
            else:
                resp = f"Cable Subscription Transaction matching query(id: {reference}) does not exist"

        elif transaction_type.upper() == "BILL":
            qs = Billpayment.objects.filter(ident=reference, user=request.user)
            if qs.exists():
                resp = "weldone hameed"
                status = True
                reciept_id = qs.first().id
            else:
                resp = f"Bill Payment Transaction matching query(id: {reference}) does not exist"
        else:
            resp = f"Transaction matching query(id: {reference}) does not exist"

        data = {"message": resp, "valid": status, "id": reciept_id}
        return JsonResponse(data)

    else:
        return render(request, "selfhelp.html")


class UpgradeUserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        package = request.GET.get("package", None)

        if request.user.user_type == "Affilliate":
            amount = 500
            bonus = 250
        elif package == "Affilliate":
            amount = 1500
            bonus = 500
        else:
            amount = 1500
            bonus = 500

        if package == request.user.user_type:
            data = {"message": "You cannot upgrade to your current package"}
            return Response(data, status=400)

        elif request.user.user_type == "TopUser" and package == "Affilliate":
            data = {
                "message": "You cannot upgrade to lower package to your current package"
            }
            return Response(data, status=400)

        elif amount > request.user.Account_Balance:
            data = {
                "message": "Insufficient Balance please fund your wallet and try to upgrade"
            }
            return Response(data, status=400)

        previous_bal = request.user.Account_Balance
        p_level = request.user.user_type
        request.user.user_type = package
        request.user.save()
        withdraw = request.user.withdraw(request.user.id, float(amount))
        if withdraw is False:
            data = {
                "message": "Insufficient Balance please fund your wallet and try to upgrade"
            }
            return Response(data, status=400)

        # try:
        Upgrade_user.objects.create(
            user=request.user,
            from_package=p_level,
            to_package=package,
            amount=f"{amount}",
            previous_balance=previous_bal,
            after_balance=(previous_bal - amount),
        )
        if request.user.referer_username:
            if CustomUser.objects.filter(
                username__iexact=request.user.referer_username
            ).exists():
                referer = CustomUser.objects.get(
                    username__iexact=request.user.referer_username
                )
                referer.ref_deposit(bonus)
                notify.send(
                    referer,
                    recipient=referer,
                    verb="N{} {} Upgarde Bonus from  {} your referal has been added to your referal bonus wallet".format(
                        bonus, package, request.user.username
                    ),
                )

        # except:
        #     data = {'message': "Something went wrong"}
        #     return Response(data,status=400)

        message = f"Your account has beeen succesfully upgraded from {p_level} to {package} package, balance before upgrade N{previous_bal} and balance after upgrade N{previous_bal - amount}"
        Wallet_summary.objects.create(
            user=request.user,
            product=f"Your account has beeen succesfully upgraded from {p_level} to Affilliate package, balance before upgrade N{previous_bal} and balance after upgrade N{previous_bal - amount}",
            amount=amount,
            previous_balance=previous_bal,
            after_balance=previous_bal - amount,
        )

        data = {
            "message": message,
        }
        return Response(data, status=200)


class Wallet_summaryListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Wallet_summary.objects.filter(user=request.user).order_by(
            "-create_date"
        )
        serializer = Wallet_summarySerializer(items, many=True)
        return Response(serializer.data)


class ReferalListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Referal_list.objects.filter(user=request.user).order_by("id")
        serializer = Referal_listSerializer(items, many=True)
        return Response(serializer.data)


class BankpaymentAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Bankpayment.objects.filter(user=request.user).order_by("-create_date")
        serializer = seria2.serialize("json", items)

        data = [x["fields"] for x in json.loads(serializer)]
        return Response(data)

    def post(self, request, format=None):
        user = request.user
        bank_paid_to = request.data["bank_paid_to"]
        Reference = request.data["Reference"]
        amount = request.data["amount"]

        Bankpayment.objects.create(
            user=user, Bank_paid_to=bank_paid_to, Reference=Reference, amount=amount
        )

        try:
            sendmessage(
                "Msorg",
                "{} want to fund his/her account with  bank payment  amount:{}  bank paid to {} https://www.legitdata.com.ng404/page-not-found-error/page/vtuapp/bankpayment/".format(
                    user.username, amount, bank_paid_to
                ),
                f"{config.sms_notification_number}",
                "2",
            )

        except:
            pass
        return Response(
            {"message": "Bank Notification submitted successful"}, status=200
        )


class RetailerWebsiteAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        print(request.body)
        domain = request.data["domain"]
        address = request.data["address"]
        phone = request.data["phone"]
        amount = 40000
        print(domain)

        if amount > request.user.Account_Balance:
            return Response({"error": "insufficient balance"}, status=400)

        else:
            withdraw = request.user.withdraw(request.user.id, amount)
            if withdraw is False:
                return Response({"error": "insufficient balance"}, status=400)

            request.user.user_type = "TopUser"
            request.user.save()

            try:
                Wallet_summary.objects.create(
                    user=request.user,
                    product="Affillite Website  ",
                    amount=amount,
                    previous_balance=request.user.Account_Balance,
                    after_balance=request.user.Account_Balance - amount,
                )
            except:
                pass

            try:
                if request.user.referer_username:
                    if CustomUser.objects.filter(
                        username__iexact=request.user.referer_username
                    ).exists():
                        referer = CustomUser.objects.get(
                            username__iexact=request.user.referer_username
                        )
                        referer.ref_deposit(3000)
                        notify.send(
                            referer,
                            recipient=referer,
                            verb="N3000 TopUser Upgarde Bonus from  {} your referal has been added to your referal bonus wallet".format(
                                request.user.username
                            ),
                        )

            except:
                pass

            try:
                TopuserWebsite.objects.create(
                    user=request.user,
                    Domain_name=domain,
                    amount=amount,
                    Offices_Address=address,
                    Website_Customer_Care_Number=phone,
                    SSL_Security=True,
                )
            except:
                return Response(
                    {"error": "something went wrong pls contact admin "}, status=400
                )

        return Response(
            {
                "success": "Your website order has submitted successful will contact you when the website is ready"
            },
            status=200,
        )


class BulkSmsAPIListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = Bulk_Message.objects.all()
        data = serializers.serialize("json", queryset)
        return Response(data)


class BulkSmsAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        items = Bulk_Message.objects.filter(user=request.user).order_by("-create_date")
        serializer = Bulk_MessageSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        numbers = request.data.get("recetipient")
        message = request.data.get("message")
        sendername = request.data.get("sender")
        DND = request.data.get("DND")

        num = numbers.split(",")
        invalid = 0
        unit = 0
        numberlist = []
        page = 1
        previous_bal = request.user.Account_Balance
        charge = 1.8

        def sendmessage(sender, message, to, route):
            baseurl = f"https://sms.hollatags.com/api/send/?user={config.hollatag_username}&pass={config.hollatag_password}&to={to}&from={sender}&msg={urllib.parse.quote(message)}"
            response = requests.get(baseurl, verify=False)
            return response

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
        total = len(numberlist)

        if DND is True:
            charge = 3.5

        if len(message) >= 1 and len(message) <= 160:
            page = 1
        elif len(message) >= 161 and len(message) <= 304:
            page = 2
        elif len(message) >= 305 and len(message) <= 454:
            page = 3
        elif len(message) >= 455 and len(message) <= 605:
            page = 4
        elif len(message) >= 606 and len(message) <= 755:
            page = 5
        elif len(message) >= 756 and len(message) <= 905:
            page = 6
        else:
            message = message[:905]
            page = 6

        if numberset == "" or numberset is None:
            return Response({"error": "No valid Number found"}, status=400)

        elif Disable_Service.objects.get(service="Bulk sms").disable is True:
            return Response(
                {"error": "This Service is not currently available please check back"},
                status=400,
            )

        else:
            if total * charge * page > request.user.Account_Balance:
                return Response(
                    {"error": "You can't send bulk sms  due to insufficientr balance"},
                    status=400,
                )

            else:
                response = sendmessage(sendername, message, numberset, "03")
                if response.text != "sent":
                    return Response({"error": "Message could not be sent "}, status=400)

                else:
                    amount = total * charge * page

                    withdraw = request.user.withdraw(request.user.id, amount)
                    if withdraw is False:
                        return Response(
                            {
                                "error": "You can't send bulk sms  due to insufficientr balance"
                            },
                            status=400,
                        )

                    Wallet_summary.objects.create(
                        user=request.user,
                        product="bulk sms service charge  N{} ".format(amount),
                        amount=amount,
                        previous_balance=previous_bal,
                        after_balance=(previous_bal - amount),
                    )

                    Bulk_Message.objects.create(
                        user=request.user,
                        unit=unit,
                        invalid=invalid,
                        total=total,
                        page=page,
                        amount=amount,
                        sendername=sendername,
                        message=message,
                        to=numberset,
                        DND=DND,
                    )
                    return Response({"error": "Message succesfully sent "}, status=200)


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
