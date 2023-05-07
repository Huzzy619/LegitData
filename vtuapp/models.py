import datetime
import json

# Create your models here.
import random
import uuid

import requests
from colorfield.fields import ColorField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.db import models
from django.db.models import Sum
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from notifications.signals import notify
from requests.auth import HTTPBasicAuth

Bank = (
    ("Access Bank", "Access Bank"),
    ("Access(Diamond) Bank", "Access (Diamond) Bank"),
    ("ECO Bank", "ECO Bank"),
    ("First Bank of Nigeria", "First Bank of Nigeria"),
    ("FCMBank", "FCMBank"),
    ("FIdelity Bank", "FIdelity Bank"),
    ("GTBank", "GTBank"),
    ("Heritage Bank", "Heritage Bank"),
    ("Kuda Bank", "Kuda Bank"),
    ("Opay", "Opay"),
    ("Palmpay", "Palmpay"),
    ("Polarise Bank", "Polarise Bank"),
    ("Stanbic IBTC", "Stanbic IBTC"),
    ("Sterling Bank", "Sterling Bank"),
    ("UBA", "UBA"),
    ("Union Bank", "Union Bank"),
    ("Unity Bank", "Unity Bank"),
    ("Wema Bank", "Wema Bank"),
    ("Zenith Bank", "Zenith Bank"),
)

User = settings.AUTH_USER_MODEL

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




status = (
    ("processing", "processing"),
    ("failed", "Failed"),
    ("successful", "Successful"),
)

Netstatus = (
    ("Fair", "Fair"),
    ("Bad", "Bad"),
    ("Strong", "Strong"),
)

service = (
    ("Data", "Data"),
    ("Airtime", "Airtime"),
    ("Cablesub", "Cablesub"),
    ("Bill", "Bill"),
    ("Withdraw", "Withdraw"),
    ("Recharge PRINTING", "Recharge PRINTING"),
    ("Bulk SMS", "Bulk SMS"),
    ("AIRTIME TO CASH ", "AIRTIME TO CASH "),
    ("RESULT CHECKER SERVICES", "RESULT CHECKER SERVICES"),
)

plan_type = (
    ("SME", "SME"),
    ("GIFTING", "GIFTING"),
    ("CORPORATE GIFTING", "CORPORATE GIFTING"),
)


Mtn_Tran_Plan = (
    ("600", "1Gb  = #600"),
    ("1200", "2Gb  = #1200"),
    ("2900", "5Gb  = #2900"),
)

Network_2 = (
    ("MTN", "MTN"),
    ("AIRTEL", "AIRTEL"),
)


mtype = (
    ("Prepaid", "Prepaid"),
    ("Postpaid", "Postpaid"),
)

Network_3 = (("MTN", "MTN"),)

api_medium = (
    ("MSORG_DEVELOPED_WEBSITE", "MSORG Developed Website 1"),
    ("MSORG_DEVELOPED_WEBSITE_2", "MSORG Developed Website 2"),
    ("MSORG_DEVELOPED_WEBSITE_3", "MSORG Developed Website 3"),
    ("MSPLUG", "MSPLUG"),
    ("SIM_SERVER", "SIM_SERVER"),
    ("RINGO", "RINGO"),
    ("MYSIMHOSTING", "MYSIMHOSTING"),
    ("SIMHOST", "USSD.SIMHOSTING"),
    ("SIMHOST_NG", "SIMHOSTNG.COM"),
    ("SMEPLUG", "SMEPLUG"),
    ("SMEIFY", "SMEIFY"),
    ("SMS", "SMS"),
    ("VTPASS", "VTPASS"),
    ("VTUAUTO", "VTUAUTO"),
    ("OGDAMS", "OGDAMS"),
    ("OGDAMS2", "OGDAMS2"),
    ("OGDAMS_DOUBLE", "OGDAMS_DOUBLE"),
)


cop_api_medium = {
    ("MSORG_DEVELOPED_WEBSITE", "MSORG Developed Website 1"),
    ("MSORG_DEVELOPED_WEBSITE_2", "MSORG Developed Website 2"),
    ("MSORG_DEVELOPED_WEBSITE_3", "MSORG Developed Website 3"),
    ("QTopUp", "QTopUp"),
    ("SMEPLUG", "SMEPLUG"),
    ("ALAGUSIY", "ALAGUSIY"),
    ("SIMHOST", "USSD.SIMHOSTING"),
    ("SIMHOST_NG", "SIMHOSTNG.COM"),
    ("SMS", "SMS"),
    ("SMEIFY", "SMEIFY"),
    ("CHEAPESTDATASUB", "CHEAPESTDATASUB"),
    ("UWS", "UWS"),
    ("SIM_SERVER", "SIM_SERVER"),
}


api_medium2 = (
    ("MSORG_DEVELOPED_WEBSITE", "MSORG Developed Website 1"),
    ("MSORG_DEVELOPED_WEBSITE_2", "MSORG Developed Website 2"),
    ("MSORG_DEVELOPED_WEBSITE_3", "MSORG Developed Website 3"),
    ("MSPLUG", "MSPLUG"),
    ("SIM_SERVER", "SIM_SERVER"),
    ("SIMHOST", "USSD.SIMHOSTING"),
    ("SIMHOST_NG", "SIMHOSTNG.COM"),
    ("SMEIFY", "SMEIFY"),
    ("SMS", "SMS"),
    ("VTUAUTO", "VTUAUTO"),
)


Netchoice = (
    ("MTN", "MTN"),
    ("GLO", "GLO"),
    ("AIRTEL", "AIRTEL"),
    ("9MOBILE", "9MOBILE"),
    ("SMILE", "SMILE"),
    ("SPECTRANET", "SPECTRANET"),
    ("SWIFT", "SWIFT"),
)

result = (
    ("WAEC", "WAEC"),
    ("NECO", "NECO"),
    ("NABTEB", "NABTEB"),
)

Air_choice = (
    ("100", "#100"),
    ("200", "#200"),
    ("400", "#400"),
    ("500", "#500"),
    ("1000", "#1000"),
)

service = (
    ("Data", "Data"),
    ("Airtime", "Airtime"),
    ("Cablesub", "Cablesub"),
    ("Bill", "Bill"),
    ("Bankpayment", "Bankpayment"),
    ("Monnify ATM", "Monnify ATM"),
    ("Monnfy bank", "Monnify bank"),
    ("paystack", "paystack"),
    ("Result_checker", "Result_checker"),
    ("Recharge_Printing", "Recharge_Printing"),
    ("Bulk sms", "Bulk sms"),
    ("Airtime_Funding", "Airtime_Funding"),
)

airtype = (
    ("VTU", "VTU"),
    ("Share and Sell", "Share and Sell"),
    ("awuf4U", "awuf4U"),
)

Volchoice = (
    ("MB", "MB"),
    ("GB", "GB"),
    ("TB", "TB"),
)

ratechoice = (
    ("Selling_rate", "Selling_rate"),
    ("Buying_rate", "Buying_rate"),
)


Multichoice = (
    ("GOTV", "GOTV"),
    ("DSTV", "DSTV"),
    ("STARTIME", "STARTIME"),
    ("TSTV", "TSTV"),
)

STATUS = ((0, "Draft"), (1, "Publish"))


status2 = (
    ("Pending", "Pending"),
    ("Processing", "processing"),
    ("Delivered", "Delivered"),
)


def create_id():
    num = random.randint(100, 2000)
    num_2 = random.randint(1, 1000)
    num_3 = random.randint(60, 1000)
    return str(num) + str(num_2) + str(num_3) + str(uuid.uuid4())[:8]

    # +str(num_2)+str(num_3)+str(uuid.uuid4())[:7]


vericate = (
    ("processing", "processing"),
    ("Approved", "Approved"),
    ("Not_Appprove", "Not_Approve"),
)


def validate_file_size(value):
    filesize = value.size

    if filesize > 1024 * 50:
        raise ValidationError("The maximum file size that can be uploaded is 50kb")
    else:
        return value


class WebsiteConfiguration(models.Model):
    primary_color = ColorField(default="#132563")
    secondary_color = ColorField(
        null=True,
        blank=True,
        help_text="add this color if you want to use color mixure or gradient else leave blank to use single color",
    )
    intro_message = models.TextField(
        default="Refer people to legitdata and earn N500 immediately the person upgrade his/her account to affiliate or topuser",
        null=True,
        blank=True,
    )
    sms_notification_number = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter the phone number to recieve SMS notifications on",
    )
    support_phone_number = models.CharField(
        max_length=13,
        null=True,
        blank=True,
        help_text="Customer support phone number ,Whatsapp number  (start with 234)",
    )
    whatsapp_group_link = models.URLField(
        null=True, blank=True, help_text="Support group link if any"
    )
    gmail = models.EmailField(
        null=True, blank=True, help_text="Email to get notification on"
    )

    ######## PAYMENT GATEWAYS
    manual_bank_funding_limit = models.PositiveIntegerField(
        default=5000,
        help_text="minimum amount allowed for FUND WITH MANUAL BANK TRANSFER",
    )
    manual_bank_funding_info_message = models.TextField(
        default="Your account will be suspended if you submit without transfer \n Please note that there is a charge of N50 if the amount greater than N9,999.",
        null=True,
        blank=True,
    )
    Paystack_secret_key = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your Paystack SCRET API KEY here if you are using Paystack, else leave blank",
    )
    monnify_API_KEY = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your monnify  API_KEY here if you are using monnify  else leave blank",
    )
    monnify_SECRET_KEY = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your monnify Secret Key here if you are using monnify else leave blank",
    )
    monnify_contract_code = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your monnify contarct code here if you are using monnify else leave blank",
    )

    ########### API/AUTOMATION
    ringo_email = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your RINGO Email here if you are using VTpass else leave blank",
    )
    ringo_password = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your RINGO password here if you are using VTpass else leave blank",
    )

    vtpass_email = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your Vtpass Email here if you are using VTpass else leave blank",
    )
    vtpass_password = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your Vtpass password here if you are using VTpass else leave blank",
    )

    hollatag_username = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your hollatag username here if you are using hollatag else leave blank",
    )
    hollatag_password = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your hollatag  password here if you are using hollatag else leave blank",
    )

    sme_plug_secret_key = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your SMEPLUG SCRET API KEY here if you are using SMEplug else leave blank",
    )

    simhost_API_key = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your simhost APIKEY here if you are using simhost else leave blank",
    )

    msplug_API_key = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your msplug APIKEY here if you are using msplug else leave blank",
    )

    vtu_auto_email = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your vtuauto Email here if you are using vtuauto else leave blank",
    )
    vtu_auto_password = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your vtuauto Password here if you are using vtuauto else leave blank",
    )

    mobilenig_username = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your mobilenig username here if you are using mobilenig else leave blank",
    )
    mobilenig_api_key = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your mobilenig APIKEY here if you are using mobilenig else leave blank",
    )
    idchecker_api_key = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your idchecker APIKEY here if you are using idchecker else leave blank",
    )
    uws_token = models.TextField(
        null=True,
        blank=True,
    )
    qtopup_api_key = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your qtopup APIKEY here if you are using qtopup else leave blank",
    )

    ########## MSORD WEB API
    msorg_web_url = models.URLField(
        null=True,
        blank=True,
    )
    msorg_web_api_key = models.TextField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your MSORG website APIKEY here if you are using website developed by MSORG else leave blank",
    )
    msorg_web_url_2 = models.URLField(
        null=True,
        blank=True,
    )
    msorg_web_api_key_2 = models.TextField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your APIKEY for your 2nd MSORG WEBSITE here if you are using website developed by MSORG else leave blank",
    )
    msorg_web_url_3 = models.URLField(
        null=True,
        blank=True,
    )
    msorg_web_api_key_3 = models.TextField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter your APIKEY for your 3rd choice MSORG WEBSITE here if you are using website developed by MSORG else leave blank",
    )

    ############## ACCOUNT UPGRADE
    affiliate_upgrade_fee = models.IntegerField(
        default=2000, blank=True, null=True, verbose_name="Upgrade to Affiliate charge"
    )
    affiliate_to_topuser_upgrade_fee = models.IntegerField(
        default=3000,
        blank=True,
        null=True,
        verbose_name="Upgrade from Affiliate to TopUser charge",
    )
    topuser_upgrade_fee = models.IntegerField(
        default=5000, blank=True, null=True, verbose_name="Upgrade to TopUser charge"
    )

    ############## REFERRAL BONUS
    affiliate_referral_bonus = models.IntegerField(
        default=500,
        blank=True,
        null=True,
        help_text="set amount upline/referee earns when downline/referral upgrades to Affiliate package",
    )
    affiliate_to_topuser_referral_bonus = models.IntegerField(
        default=500,
        blank=True,
        null=True,
        help_text="set amount upline/referee earns when downline/referral upgrades from Affiliate to TopUser package",
    )
    topuser_referral_bonus = models.IntegerField(
        default=1000,
        blank=True,
        null=True,
        help_text="set amount upline/referee earns when downline/referral upgrades to TopUser package",
    )

    ############## CONTROLLER
    ResultCheckerSource = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="API",
        choices=(
            ("API", "API"),
            ("MANUAL", "MANUAL"),
        ),
    )
    Cable_provider = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="VTPASS",
        choices=(
            ("VTPASS", "VTPASS"),
            ("RINGO", "RINGO"),
        ),
    )
    Bill_provider = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="VTPASS",
        choices=(
            ("VTPASS", "VTPASS"),
            ("RINGO", "RINGO"),
        ),
    )
    disable_Transaction_limit = models.BooleanField(
        max_length=50,
        default=False,
        choices=(
            (True, "YES"),
            (False, "NO"),
        ),
        verbose_name="Disable Transaction limit for unverified user",
    )

    ############## UNVERIFIED USER LIMITS
    # unverified_users_data_TopUp_limit =  models.PositiveIntegerField(default=10000, help_text="maximum amount of data TopUp allowed for unverified users DAILY")
    # unverified_users_airtime_TopUp_limit =  models.PositiveIntegerField(default=10000, help_text="maximum amount of Airtime TopUp allowed for unverified users DAILY")
    unverified_users_daily_withdraws_limit = models.PositiveIntegerField(
        default=5000,
        help_text="maximum amount of withdrawal allowed for unverified users DAILY",
    )
    unverified_users_transfer_limit = models.PositiveIntegerField(
        default=5000,
        help_text="total amount of transfer allowed for unverified users DAILY",
    )
    unverified_users_daily_transation_limit = models.PositiveIntegerField(
        default=30000,
        help_text="total amount of transaction allowed for unverified users DAILY",
    )

    # def save(self, *args, **kwargs):
    #     if WebsiteConfiguration.objects.all():
    #         WebsiteConfiguration.objects.all().delete()

    #     super(WebsiteConfiguration, self).save(*args, **kwargs)

    def __str__(self):
        return "Website Configuration"

    class Meta:
        verbose_name_plural = "WEBSITE CONFIGURATIONS"


config = ""
# config = WebsiteConfiguration.objects.all().first()


class TopuserWebsite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    Domain_name = models.CharField(max_length=500)
    amount = models.CharField(max_length=10)
    Offices_Address = models.CharField(max_length=800)
    Website_Customer_Care_Number = models.CharField(max_length=15)
    SSL_Security = models.BooleanField(
        default=False, help_text="Additional ₦5000 for SSL Certificate"
    )
    status = models.CharField(max_length=30, choices=status2, default="processing")

    def __str__(self):
        return self.user.username


class user_upgrade_amount(models.Model):
    top_user_amount = models.CharField(max_length=10)
    affilliate_user_amount = models.CharField(max_length=10)

    def __str__(self):
        return "Upgrade price"

    def save(self, *args, **kwargs):
        if user_upgrade_amount.objects.all():
            user_upgrade_amount.objects.all().delete()
        super(user_upgrade_amount, self).save(*args, **kwargs)


class WalletFunding(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        editable=False,
        blank=False,
        null=True,
        related_name="wallet_funding",
    )
    medium = models.CharField(
        max_length=500,
        blank=True,
        editable=False,
    )
    amount = models.CharField(
        max_length=30,
        blank=True,
        editable=False,
    )
    previous_balance = models.CharField(
        max_length=30,
        blank=True,
        editable=False,
    )
    after_balance = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        editable=False,
    )
    create_date = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )
    ident = models.CharField(default=create_id, editable=False, max_length=30)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name_plural = "WALLET FUNDING TRACKING"

    def save(self, *args, **kwargs):
        # REFERRAL BONUS FOR FUNDING
        """
        user = self.user
        chek =  Wallet_Funding.objects.filter(user=user).count()
        if user.referer_username and chek == 0:
            if User.objects.filter(username__iexact=user.referer_username).exists():
               referer = User.objects.get(username__iexact=user.referer_username)
               ref_previous_bal = referer.Account_Balance

               # amt_to_earn = 200
               amt_to_earn = round(int(self.amount) * 0.02)
               print(f'amt_to_earn = {amt_to_earn}')
               if amt_to_earn > 100:
                   amt_to_earn = 100

               amt_to_earn = int(amt_to_earn)
               referer.ref_deposit(int(amt_to_earn))

               notify.send(referer, recipient=referer, verb=f'you Earned N{amt_to_earn} Bonus from your referal: {user.username} first funding and has been added to your referal bonus wallet')
               Wallet_summary.objects.create(user=referer, product=f"Earned N{amt_to_earn} referral bonus from {user} first funding", amount=amt_to_earn, previous_balance=ref_previous_bal, after_balance=(ref_previous_bal + amt_to_earn))
        """
        # REFERRAL BONUS FOR FUNDING
        return super(WalletFunding, self).save(*args, **kwargs)


class Black_List_Phone_Number(models.Model):
    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    def __str__(self):
        return str(self.phone)

    class Meta:
        verbose_name_plural = "BLACKLIST PHONE NUMBER"


class Transactions(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    amount = models.FloatField()
    balance_before = models.FloatField(blank=True, null=True)
    balance_after = models.FloatField(blank=True, null=True)
    transaction_type = models.CharField(max_length=30, blank=True)
    create_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "WALLET TRANSACTIONS"

    def __str__(self):
        return str(self.transaction_type)

    def today_credit_transaction(self):
        today = datetime.date.today()
        return Transactions.objects.filter(
            create_date__gt=today, transaction_type="CREDIT"
        ).aggregate(Sum("amount"))["amount__sum"]

    def today_debit_transaction(self):
        today = datetime.date.today()
        return Transactions.objects.filter(
            create_date__gt=today, transaction_type="DEBIT"
        ).aggregate(Sum("amount"))["amount__sum"]

    def this_month_credit_transaction(self):
        current_month = datetime.datetime.now().month
        return Transactions.objects.filter(
            create_date__month=current_month, transaction_type="CREDIT"
        ).aggregate(Sum("amount"))["amount__sum"]

    def this_month_debit_transaction(self):
        current_month = datetime.datetime.now().month
        return Transactions.objects.filter(
            create_date__month=current_month, transaction_type="DEBIT"
        ).aggregate(Sum("amount"))["amount__sum"]

    def total_credit_transaction(self):
        return Transactions.objects.filter(transaction_type="CREDIT").aggregate(
            Sum("amount")
        )["amount__sum"]

    def total_debit_transaction(self):
        return Transactions.objects.filter(transaction_type="DEBIT").aggregate(
            Sum("amount")
        )["amount__sum"]


class WalletSummary(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        editable=False,
        blank=False,
        null=True,
        related_name="wallet",
    )
    product = models.CharField(max_length=500, blank=True)
    amount = models.CharField(max_length=30, blank=True)
    previous_balance = models.CharField(max_length=30, blank=True)
    after_balance = models.CharField(max_length=30, blank=True, null=True)
    Status = models.CharField(max_length=30, choices=status, default="successful")
    create_date = models.DateTimeField(default=timezone.now)
    ident = models.CharField(default=create_id, editable=False, max_length=30)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        try:
            sendmail(
                "Transaction Notification ",
                f"{self.product} \n Amount : {self.amount} \n Previous Balance : {self.previous_balance} \n New Balance: {self.after_balance} \n Date {self.create_date.strftime('%d, %b %Y') }",
                self.user.email,
                self.user.username,
            )
        except:
            pass
        super(WalletSummary, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "USERS WALLET SUMMARY"


class bonus_transfer(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    amount = models.CharField(max_length=30, blank=True)
    create_date = models.DateTimeField(default=timezone.now)
    Current_bonus = models.CharField(max_length=30, blank=True)
    ident = models.CharField(default=create_id, editable=False, max_length=30)

    def __str__(self):
        return self.amount


class BankAccount(models.Model):
    bank_name = models.CharField(max_length=500, null=True, blank=True)
    account_name = models.CharField(max_length=500, null=True, blank=True)
    account_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.bank_name

    class Meta:
        verbose_name_plural = "ADMIN BANK ACCOUNT"


class Referal_list(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    username = models.CharField(max_length=30)
    referal_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        editable=False,
        blank=False,
        null=True,
        related_name="referal",
    )
    create_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return str(self.username)

    def save(self, *args, **kwargs):
        mb = User.objects.get(username__iexact=self.username)
        self.referal_user = mb

        super(Referal_list, self).save(*args, **kwargs)


class Network(models.Model):
    name = models.CharField(max_length=30, choices=Netchoice, unique=True)
    # status = models.CharField(max_length=30, choices=Netstatus)
    data_vending_medium = models.CharField(max_length=30, choices=api_medium)
    gifting_vending_medium = models.CharField(
        max_length=30, choices=cop_api_medium, blank=True, null=True
    )
    corporate_data_vending_medium = models.CharField(
        max_length=30, choices=cop_api_medium, blank=True, null=True
    )
    vtu_vending_medium = models.CharField(max_length=30, choices=api_medium, null=True)
    msorg_web_net_id = models.CharField(max_length=5, blank=True, null=True)
    share_and_sell_vending_medium = models.CharField(
        max_length=30, choices=api_medium2, null=True
    )
    # convertion_parcentage = models.IntegerField(blank=True, null=True)
    sme_disable = models.BooleanField(default=False, blank=True, null=True)
    gifting_disable = models.BooleanField(default=False, blank=True, null=True)
    corporate_gifting_disable = models.BooleanField(
        default=False, blank=True, null=True
    )
    airtime_disable = models.BooleanField(default=False, blank=True, null=True)
    data_disable = models.BooleanField(default=False, blank=True, null=True)
    recharge_pin_disable = models.BooleanField(default=False, blank=True, null=True)
    share_and_sell_disable = models.BooleanField(default=False, blank=True, null=True)
    awuf4u_disable = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "NETWORKS"


class Network_1(models.Model):
    name = models.CharField(max_length=30, choices=Network_2, unique=True)
    status = models.CharField(max_length=30, choices=Netstatus)

    def __str__(self):
        return str(self.name)


class New_order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    name = models.CharField(max_length=30)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return str(self.name)


class ChargeUser(models.Model):
    username = models.CharField(max_length=100, null=True)
    amount = models.IntegerField()

    balance_before = models.FloatField(
        null=True, blank=True, help_text="leave blank sytem automatic set this"
    )
    balance_after = models.FloatField(
        null=True, blank=True, help_text="leave blank sytem automatic set this"
    )
    comment = models.TextField()
    pending_amount = models.IntegerField(
        default=0,
        help_text="leave blank sytem automatic set this,if the amount you want to with not upto user wallet, pending amount wait till when user fund next",
    )

    def __str__(self):
        return str(self.username)

    def save(self, *args, **kwargs):
        try:
            mb = User.objects.get(username=self.username)
        except:
            raise ValidationError("Invalid user, enter correct username")
        if not self.id:
            if self.amount > mb.Account_Balance:
                self.pending_amount = self.amount - mb.Account_Balance
                self.balance_before = mb.Account_Balance
                mb.withdraw(mb.id, mb.Account_Balance)

                self.balance_after = 0

                try:
                    WalletSummary.objects.create(
                        user=mb,
                        product=f"Admin Charge your account for {self.comment} ",
                        amount=self.amount,
                        previous_balance=self.balance_before,
                        after_balance=self.balance_after,
                    )
                except:
                    pass

            else:
                self.balance_before = mb.Account_Balance
                withdraw = mb.withdraw(mb.id, self.amount)
                if withdraw is False:
                    raise ValidationError(
                        f"Insufficient fund ,{self.username} wallet balance is {mb.Account_Balance}"
                    )
                self.balance_after = mb.Account_Balance - self.amount

                try:
                    WalletSummary.objects.create(
                        user=mb,
                        product=f"Admin Charge your account for {self.comment} ",
                        amount=self.amount,
                        previous_balance=self.balance_before,
                        after_balance=self.balance_after,
                    )
                except:
                    pass

        super(ChargeUser, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "WITHDRAW FROM USER WALLET"


class Fund_User(models.Model):
    username = models.CharField(max_length=100, null=True)
    amount = models.IntegerField()
    balance_before = models.FloatField(
        null=True, blank=True, help_text="leave blank sytem automatic set this"
    )
    balance_after = models.FloatField(
        null=True, blank=True, help_text="leave blank sytem automatic set this"
    )

    def __str__(self):
        return str(self.username)

    def save(self, *args, **kwargs):
        try:
            mb = User.objects.get(username=self.username)
        except:
            raise ValidationError("Invalid user, enter correct username")

        self.balance_before = mb.Account_Balance
        mb.deposit(mb.id, self.amount, False, "ADMIN WALLET FUNDING")
        self.balance_after = mb.Account_Balance + self.amount

        try:
            WalletSummary.objects.create(
                user=mb,
                product=f"Admin  Funding your wallet with sum of {self.amount}",
                amount=self.amount,
                previous_balance=self.balance_before,
                after_balance=(self.balance_after),
            )
        except:
            pass

        super(Fund_User, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "FUND USER WALLET"


class Plan(models.Model):
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    plan_size = models.FloatField()
    plan_Volume = models.CharField(max_length=30, choices=Volchoice)
    plan_amount = models.PositiveIntegerField()
    ussd_string = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="put small letter n in place of number and p in place of pin i.e*141*6*2*3*3*1*n*p#",
    )
    sms_command = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="put small letter n in place of number and p in place of pin i.e SMEB n 1000 p",
    )

    plan_name_id = models.CharField(max_length=500, null=True, blank=True)
    plan_name_id_2 = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter plan ID for your 2nd MSORG WEBSITE API",
    )
    plan_name_id_3 = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter plan ID for your 3rd MSORG WEBSITE API",
    )
    ogdams_plan_id = models.CharField(max_length=500, null=True, blank=True)
    alagusiy_plan_id = models.CharField(max_length=500, null=True, blank=True)
    simserver_plan_id = models.CharField(max_length=500, null=True, blank=True)
    mysimhosting_plan_id = models.CharField(max_length=500, null=True, blank=True)
    Affilliate_price = models.PositiveIntegerField(default=100000)
    TopUser_price = models.PositiveIntegerField(default=100000)
    api_price = models.PositiveIntegerField(default=100000)
    smeplug_id = models.CharField(max_length=500, null=True, blank=True)
    vtpass_variation_code = models.CharField(max_length=500, null=True, blank=True)
    smeify_plan_name_id = models.CharField(max_length=30, blank=True, null=True)
    uws_plan_name_id = models.CharField(max_length=500, blank=True, null=True)
    msplug_plan_name_id = models.CharField(max_length=30, blank=True, null=True)
    qtopup_id = models.CharField(max_length=30, blank=True, null=True)

    plan_type = models.CharField(
        max_length=30, choices=plan_type, blank=True, help_text="Data plan  type only ."
    )
    month_validate = models.CharField(max_length=30)
    #    commission = models.PositiveIntegerField(default=0)

    def __str__(self):
        return (
            str(self.plan_size)
            + str(self.plan_Volume)
            + "----"
            + "N"
            + str(self.plan_amount)
        )

    def plan_name(self):
        return str(self.plan_size) + str(self.plan_Volume)

    def plan_net(self):
        return str(self.network)

    def plan_amt(self):
        return str(self.plan_amount)

    def plan_amt2(self):
        return str(self.Affilliate_price)

    def plan_amt3(self):
        return str(self.TopUser_price)

    def plan_id(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "DATA PLANS"


class Disable_Service(models.Model):
    service = models.CharField(
        max_length=50,
        choices=service,
        unique=True,
    )
    disable = models.BooleanField(
        default=False,
        help_text="Check this box to disable this service, uncheck to unable it back",
    )

    def save(self, *args, **kwargs):
        if Disable_Service.objects.filter(service=service):
            Disable_Service.objects.filter(service=service).delete()

        super(Disable_Service, self).save(*args, **kwargs)

    def __str__(self):
        return self.service

    class Meta:
        verbose_name_plural = "DISABLE SERVICES"


class SmeifyAuth(models.Model):
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    token = models.TextField(null=True, blank=True)
    expire_date = models.DateTimeField(null=True, blank=True)
    re_auth = models.BooleanField(default=True, blank=True, null=True)

    def get_token(self):
        try:
            url = "https://api.smeify.com/api/v2/auth"
            payload = {"identity": f"{self.username}", "password": f"{self.password}"}
            response = requests.post(url, data=payload)
            rdata = json.loads(response.text)
            tok = rdata["token"]
            self.token = tok

            return tok

        except:
            return self.token

        """
            if timezone.now() >= self.expire_date:

                try:
                    url = f"https://auto.smeify.com/api/v1/auth/login?identity={self.username}&&password={self.password}"
                    response = requests.request("POST", url)
                    rdata = json.loads(response.text)
                    self.token = rdata["token"]
                    self.expire_date = dateparse.parse_datetime(f"{rdata['expires']}")

                    self.save()
                    return rdata["token"]
                except:
                     return self.token
            else:

                 return self.token
            """

    def save(self, *args, **kwargs):
        if self.username and self.password and self.re_auth is True:
            try:
                url = "https://api.smeify.com/api/v2/auth"
                payload = {
                    "identity": f"{self.username}",
                    "password": f"{self.password}",
                }
                response = requests.post(url, data=payload)
                rdata = json.loads(response.text)
                self.token = rdata["token"]
                # self.expire_date = dateparse.parse_datetime(f"{rdata['expires_in']}")

                # url = f"https://auto.smeify.com/api/v1/auth/login?identity={self.username}&&password={self.password}"
                # response = requests.request("POST", url)
                # rdata = json.loads(response.text)
                # self.token = rdata["token"]
                # self.expire_date = dateparse.parse_datetime(f"{rdata['expires']}")

                self.re_auth = False
                self.save()

            except:
                pass

        super(SmeifyAuth, self).save(*args, **kwargs)


class Info_Alert(models.Model):
    message = models.TextField()
    image = models.ImageField(upload_to="alert_images", blank=True, null=True)

    class Meta:
        verbose_name_plural = "CREATE ALERT NOTIFICATION"

    def save(self, *args, **kwargs):
        try:
            Info_Alert.objects.first().delete()
            self.save()
        except:
            pass
        super(Info_Alert, self).save(*args, **kwargs)

    def __str__(self):
        return self.message


class Upgrade_user(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    from_package = models.CharField(max_length=50, blank=True)
    to_package = models.CharField(max_length=50, blank=True)
    amount = models.CharField(max_length=30, blank=True)
    previous_balance = models.CharField(max_length=30, blank=True)
    after_balance = models.CharField(max_length=30, blank=True, null=True)
    Status = models.CharField(max_length=30, choices=status, default="successful")
    create_date = models.DateTimeField(default=timezone.now)
    ident = models.CharField(default=create_id, editable=False, max_length=30)

    def __str__(self):
        return str(self.user.username)

    class Meta:
        verbose_name_plural = "UPGRADE USER"


class Percentage(models.Model):
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    percent = models.IntegerField()

    def __str__(self):
        return str(self.network) + "-----" + str(self.percent)

    class Meta:
        verbose_name_plural = "AIRTIME TO CASH PERCENTAGE"


class TopupPercentage(models.Model):
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    percent = models.IntegerField()
    Affilliate_percent = models.IntegerField(default=100)
    topuser_percent = models.IntegerField(default=100)
    api_percent = models.IntegerField(default=100)
    share_n_sell_percent = models.IntegerField(default=100)
    share_n_sell_api_percent = models.IntegerField(default=100)
    share_n_sell_affilliate_percent = models.IntegerField(default=100)
    share_n_sell_topuser_percent = models.IntegerField(default=100)
    awuf4u_percent = models.IntegerField(default=100)
    awuf4u_api_percent = models.IntegerField(default=100)
    awuf4u_affilliate_percent = models.IntegerField(default=100)
    awuf4u_topuser_percent = models.IntegerField(default=100)
    commission = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = "AIRTIME TOPUP PERCENTAGE"

    def __str__(self):
        return str(self.network) + "-----" + str(self.percent)


class ServicesCharge(models.Model):
    service = models.CharField(choices=service, max_length=100, unique=True)
    charge = models.FloatField(
        default=0.0,
        help_text="Note: Extra charge , you can either set charge or Discount dont set both at once",
    )
    Affilliate_charge = models.FloatField(
        default=0.0,
        help_text="Note: Extra charge , you can either set charge or Discount dont set both at once",
    )
    topuser_charge = models.FloatField(
        default=0.0,
        help_text="Note: Extra charge , you can either set charge or Discount dont set both at once",
    )
    api_charge = models.FloatField(
        default=0.0,
        help_text="Note: Extra charge , you can either set charge or Discount dont set both at once",
    )
    discount = models.FloatField(
        default=0.0, help_text="set charge to 0 to set discount"
    )
    Affilliate_discount = models.FloatField(
        default=0.0, help_text="set charge to 0 to set discount for affillitae users"
    )
    topuser_discount = models.FloatField(
        default=0.0, help_text="set charge to 0 to set discount for topuser"
    )
    api_discount = models.FloatField(
        default=0.0, help_text="set charge to 0 to set discountfor api user"
    )

    def __str__(self):
        return str(self.service)

    def save(self, *args, **kwargs):
        if self.charge > 0.0 and self.discount > 0.0:
            self.discount = 0.0

        super(ServicesCharge, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "SERVICE CHARGE"


class Airtime_to_data_Plan(models.Model):
    network = models.ForeignKey(Network_1, on_delete=models.CASCADE)
    plan_size = models.FloatField()
    plan_Volume = models.CharField(max_length=30, choices=Volchoice)
    plan_amount = models.PositiveIntegerField()
    month_validate = models.CharField(max_length=30)

    def __str__(self):
        return (
            str(self.plan_size)
            + str(self.plan_Volume)
            + "----"
            + "#"
            + str(self.plan_amount)
            + "#"
        )


class Admin_number(models.Model):
    network = models.CharField(max_length=30, choices=Netchoice, unique=True)
    phone_number = models.CharField(max_length=30, blank=True, unique=True)

    def __str__(self):
        return str(self.network) + str(self.phone_number)

    class Meta:
        verbose_name_plural = "AIRTIME TO CASH NUMBER"


class Airtime_funding(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    network = models.ForeignKey(Network, on_delete=models.SET_NULL, null=True)
    mobile_number = models.CharField(max_length=30, blank=True)
    amount = models.FloatField()
    Receivece_amount = models.FloatField(null=True)
    Status = models.CharField(
        max_length=30,
        choices=status,
        default="processing",
        help_text="Select Succesful and save to fund user",
    )
    create_date = models.DateTimeField(default=timezone.now)
    ident = models.CharField(default=create_id, editable=False, max_length=30)
    fund = models.BooleanField(default=False, blank=True, null=True)
    BankName = models.CharField(max_length=100, blank=True)
    AccountNumber = models.CharField(max_length=10, blank=True)
    AccountName = models.CharField(max_length=200, blank=True)
    use_to_fund_wallet = models.BooleanField(
        default=False,
        help_text="Note : if this is not check the user want to withdraw it to his bank kindly transfer to the account above after comfirm the airtime and change status to successful",
    )

    def get_absolute_url(self):
        return reverse("airtime_detail", args=[str(self.id)])

    def __str__(self):
        return self.mobile_number

    def save(self, *args, **kwargs):
        if (
            self.Status == "successful"
            and self.fund is False
            and self.use_to_fund_wallet is True
        ):
            previous_bal = self.user.Account_Balance
            self.user.deposit(
                self.user.id,
                float(self.Receivece_amount),
                False,
                "AIRTIME WALLET FUNDING",
            )
            self.fund = True
            WalletSummary.objects.create(
                user=self.user,
                product="Airtime  share Funding",
                amount=self.Receivece_amount,
                previous_balance=previous_bal,
                after_balance=(previous_bal + float(self.Receivece_amount)),
            )

        super(Airtime_funding, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "AIRTIME TO CASH TRANSACTIONS"


class Airtime(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    network = models.ForeignKey(Network, on_delete=models.SET_NULL, null=True)
    pin = models.CharField(max_length=30, blank=True)
    amount = models.CharField(max_length=30, choices=Air_choice, default="#100")
    Receivece_amount = models.FloatField(null=True)
    Status = models.CharField(max_length=30, choices=status, default="processing")
    create_date = models.DateTimeField(default=timezone.now)
    ident = models.CharField(default=create_id, editable=False, max_length=300)
    fund = models.BooleanField(default=False, blank=True, null=True)

    def get_absolute_url(self):
        return reverse("airtime_success", args=[str(self.id)])

    def __str__(self):
        return self.Status

    def save(self, *args, **kwargs):
        if self.Status == "successful" and self.fund is False:
            previous_bal = self.user.Account_Balance
            self.user.deposit(
                self.user.id,
                self.user.id,
                float(self.Receivece_amount),
                False,
                "AIRTIME WALLET FUNDING",
            )
            self.fund = True
            WalletSummary.objects.create(
                user=self.user,
                product="Airtime  pin Funding",
                amount=self.Receivece_amount,
                previous_balance=previous_bal,
                after_balance=(previous_bal - float(self.Receivece_amount)),
            )

        super(Airtime, self).save(*args, **kwargs)


class Result_Checker_Pin(models.Model):
    exam_name = models.CharField(max_length=15, choices=result, unique=True)
    provider_amount = models.FloatField(
        help_text="amount your API provider are selling it", default=1700
    )
    disable_this_exam = models.BooleanField(default=False, blank=True, null=True)
    provider_api = models.CharField(
        max_length=30,
        default="MOBILENIG",
        choices=(
            ("MOBILENIG", "MOBILENIG"),
            ("VTPASS", "VTPASS"),
            ("EASYACCESS", "EASYACCESS.COM.NG"),
        ),
    )
    amount = models.FloatField(default="1800")
    Affilliate_price = models.FloatField(default=1750)
    TopUser_price = models.FloatField(default=1750)
    api_price = models.FloatField(default=1750)

    def __str__(self):
        return str(self.exam_name) + " - N" + str(self.provider_amount)

    class Meta:
        verbose_name_plural = "RESULT CHECKER CONTROL"


class Result_Checker_Pin_order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    exam_name = models.CharField(max_length=15, choices=result)
    create_date = models.DateTimeField(default=timezone.now)
    quantity = models.PositiveIntegerField(
        default=1,
    )
    data = models.TextField(null=True)
    amount = models.FloatField(default=0)
    previous_balance = models.CharField(max_length=30, blank=True)
    after_balance = models.CharField(max_length=30, blank=True, null=True)
    Status = models.CharField(max_length=30, choices=status, default="successful")

    def __str__(self):
        return self.exam_name

    def data_pin(self):
        if self.data:
            return json.loads(self.data)

    def get_absolute_url(self):
        return reverse("checker_pin", args=[str(self.id)])

    class Meta:
        verbose_name_plural = "RESULT CHECKER TRANSACTIONS"


class Recharge_pin(models.Model):
    network = models.ForeignKey(
        Network, on_delete=models.CASCADE, related_name="pin_net"
    )
    available = models.BooleanField(default=True)
    amount = models.FloatField(default=100)
    pin = models.CharField(max_length=20, unique=False, null=True)
    serial = models.CharField(max_length=100, unique=False, null=True)
    load_code = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.network.name) + "  " + str(self.pin) + "  " + str(self.serial)


class Load_Recharge_pin(models.Model):
    network = models.ForeignKey(
        Network, on_delete=models.CASCADE, related_name="Loadpin_net"
    )
    dump_pin = models.TextField()
    amount = models.FloatField(default=0)
    load_code = models.CharField(max_length=100, null=True)
    total_pin_loaded = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Leave blank, system automatic return it",
    )

    def save(self, *args, **kwargs):
        data = self.dump_pin.split("\n")
        self.total_pin_loaded = len(data)
        if Recharge_pin.objects.all():
            last_id = int(Recharge_pin.objects.all().last().serial)
        else:
            last_id = 0

        for x in data:
            last_id += 1
            Recharge_pin.objects.create(
                pin=x,
                network=self.network,
                amount=self.amount,
                serial=last_id,
                load_code=self.load_code,
            )
        super(Load_Recharge_pin, self).save(*args, **kwargs)

    def __str__(self):
        return " set  " + str(self.id)

    class Meta:
        verbose_name_plural = "LOAD RECHARGE PIN"


class Recharge(models.Model):
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)
    amount = models.FloatField(default=0)
    amount_to_pay = models.FloatField(default=0)
    Affilliate_price = models.FloatField(default=100)
    TopUser_price = models.FloatField(default=100)
    api_price = models.FloatField(default=100)

    class Meta:
        verbose_name_plural = "RECHARGE CARD PRINTING PRICE"

    def __str__(self):
        return str(self.amount_to_pay)

    def netname(self):
        return str(self.network.name)


class Recharge_pin_order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    network = models.ForeignKey(Network, on_delete=models.CASCADE, null=True)
    network_amount = models.ForeignKey(Recharge, on_delete=models.CASCADE, null=True)
    data = models.TextField(blank=False, null=True)
    name_on_card = models.CharField(max_length=200, blank=False, null=True)
    amount = models.FloatField(default=0)
    previous_balance = models.CharField(max_length=30, blank=True)
    after_balance = models.CharField(max_length=30, blank=True, null=True)
    quantity = models.PositiveIntegerField(null=True)
    create_date = models.DateTimeField(default=timezone.now)
    Status = models.CharField(max_length=30, choices=status, default="successful")

    class Meta:
        verbose_name_plural = "RECHARGE CARD PRINTING TRANSACTIONS"

    def __str__(self):
        return (
            str(self.create_date)
            + "> Batch "
            + str(self.id)
            + str(self.amount)
            + str(self.quantity)
        )

    def Batch(self):
        return (
            str(self.create_date)
            + "> Batch "
            + str(self.id)
            + str(self.amount)
            + str(self.quantity)
        )

    def net_work(self):
        return str(self.network.name)

    def data_pin(self):
        if self.data:
            return json.loads(self.data)

    def loadcode(self):
        if self.network.name == "MTN":
            return str("Dial *555*pin# to load")
        elif self.network.name == "GLO":
            return str("Dial *123*pin# to load")
        elif self.network.name == "AIRTEL":
            return str("Dial *126*pin# to load")
        elif self.network.name == "9MOBILE":
            return str("Dial *222*pin# to load")

    def get_absolute_url(self):
        return reverse("recharge_pin", args=[str(self.id)])


class Couponcode(models.Model):
    Coupon_Code = models.CharField(max_length=15, unique=True)
    amount = models.CharField(max_length=15)
    create_date = models.DateTimeField(default=timezone.now)
    ident = models.CharField(default=create_id, editable=False, max_length=30)
    Used = models.BooleanField()

    def __str__(self):
        return self.Coupon_Code

    class Meta:
        verbose_name_plural = "COUPON CODES"


class CouponPayment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    Code = models.CharField(max_length=15)
    amount = models.IntegerField(editable=False, null=True)
    create_date = models.DateTimeField(default=timezone.now)
    ident = models.CharField(default=create_id, editable=False, max_length=30)
    Status = models.CharField(max_length=30, choices=status, default="successful")

    def get_absolute_url(self):
        return reverse("Coupon_success", args=[str(self.id)])

    def __str__(self):
        return self.Code

    class Meta:
        verbose_name_plural = "COUPON PAYMENTS"


class Withdraw(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    accountNumber = models.CharField(max_length=30, blank=True)
    accountName = models.CharField(max_length=30, blank=True)
    bankName = models.CharField(max_length=100, choices=Bank, blank=True)
    amount = models.CharField(max_length=30, blank=True)
    previous_balance = models.CharField(max_length=30, blank=True)
    after_balance = models.CharField(max_length=30, blank=True, null=True)
    Status = models.CharField(
        max_length=30,
        choices=status,
        default="processing",
        help_text="Select failed and save to refund user",
    )
    create_date = models.DateTimeField(default=timezone.now)
    Current_balance = models.CharField(max_length=30, blank=True)
    ident = models.CharField(default=create_id, editable=False, max_length=30)
    refund = models.BooleanField(default=False, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.Status == "failed" and self.refund is False:
            previous_bal = self.user.Account_Balance
            self.user.deposit(
                self.user.id, float(self.amount), False, "Wallet Withdraw Refund"
            )
            self.refund = True
            WalletSummary.objects.create(
                user=self.user,
                product="Wallet Withdraw Refund",
                amount=self.amount,
                previous_balance=previous_bal,
                after_balance=(previous_bal + float(self.amount)),
            )
        super(Withdraw, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("Withdraw_success", args=[str(self.id)])

    def __str__(self):
        return self.accountName

    class Meta:
        verbose_name_plural = "WITHDRAW TRANSACTIONS"


class Data(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    network = models.ForeignKey(Network, on_delete=models.SET_NULL, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    data_type = models.CharField(
        max_length=30,
        choices=plan_type,
        blank=True,
        null=True,
        help_text="Select Plan Type SME, GIFTING or CORPORATE GIFTING",
    )
    mobile_number = models.CharField(max_length=30, blank=True)
    Status = models.CharField(
        max_length=30,
        choices=status,
        default="processing",
        help_text="Select failed and save to refund user",
    )
    medium = models.CharField(max_length=30, default="website")
    create_date = models.DateTimeField(default=timezone.now)
    balance_before = models.CharField(max_length=30, blank=True)
    balance_after = models.CharField(max_length=30, blank=True, null=True)
    plan_amount = models.CharField(max_length=30, blank=True)
    Ported_number = models.BooleanField(default=False, blank=True, null=True)
    refund = models.BooleanField(default=False, blank=True, null=True)
    ident = models.CharField(
        default=create_id, editable=False, max_length=100, verbose_name="Reference ID"
    )
    provider_source = models.CharField(max_length=100, blank=True, null=True)
    api_response = models.TextField(default="", blank=True)

    class Meta:
        verbose_name_plural = "DATA TOP-UP TRANSACTIONS"

    def __str__(self):
        return str(self.plan)

    def requery(self):
        # if self.provider_source == "VTPASS":
        # query provider endpoint.....

        result = "data successful"
        return str(result)

    def data_amount(self):
        return str(self.plan_amount)

    def save(self, *args, **kwargs):
        self.data_type = self.plan.plan_type

        if self.Status == "failed" and self.refund is False:
            self.user.deposit(
                self.user.id, float(self.plan_amount), False, "FAILED DATA TOPUP REFUND"
            )
            self.refund = True

            previous_bal = float(self.user.Account_Balance)
            after_bal = previous_bal + float(self.plan_amount)

            WalletSummary.objects.create(
                user=self.user,
                product="FAILED DATA TOPUP REFUND for {} {}{}   N{}  with {} ".format(
                    self.network.name,
                    self.plan.plan_size,
                    self.plan.plan_Volume,
                    self.plan_amount,
                    self.mobile_number,
                ),
                amount=self.plan_amount,
                previous_balance=previous_bal,
                after_balance=after_bal,
            )

            # Wallet_summary.objects.create(user=self.user, product="{} {}{}   N{}  DATA topup Refund for {} ".format(self.network.name, self.plan.plan_size, self.plan.plan_Volume,  self.plan_amount, self.mobile_number), amount=self.plan_amount, previous_balance=previous_bal, after_balance=(previous_bal + float(self.plan_amount)))

            try:
                if self.user.referer_username:
                    if User.objects.filter(
                        username__iexact=self.user.referer_username
                    ).exists():
                        referer = User.objects.get(
                            username__iexact=self.user.referer_username
                        )
                        # if  self.user.user_type == "Smart Earner":
                        com = referer.Referer_Bonus
                        if com > 0:
                            referer.ref_withdraw(self.plan.commission)

                            WalletSummary.objects.create(
                                user=referer,
                                product="[Referal bonus] refund  N{} commission for your referal {} DATA order".format(
                                    self.plan.commission, self.user.username
                                ),
                                amount=self.plan.commission,
                                previous_balance=com,
                                after_balance=(com - self.plan.commission),
                            )
                            notify.send(
                                referer,
                                recipient=referer,
                                verb="[Referal bonus] refund N{}commission  for your referal {} DATA order ".format(
                                    self.plan.commission, self.user.username
                                ),
                            )
            except:
                pass

        super(Data, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("Data_success", args=[str(self.id)])


class Transfer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        editable=False,
        blank=False,
        null=True,
        related_name="Airtime_tranfere",
    )
    receiver_username = models.CharField(max_length=30, blank=True)
    amount = models.CharField(max_length=30, blank=True)
    previous_balance = models.CharField(max_length=30, blank=True)
    after_balance = models.CharField(max_length=30, blank=True, null=True)
    Status = models.CharField(max_length=30, choices=status, default="successful")
    create_date = models.DateTimeField(default=timezone.now)
    Current_balance = models.CharField(max_length=30, blank=True)
    ident = models.CharField(default=create_id, editable=False, max_length=30)

    def __str__(self):
        return self.receiver_username

    def get_absolute_url(self):
        return reverse("Transfer_detail", args=[str(self.id)])

    class Meta:
        verbose_name_plural = "WALLET-WALLET TRANSFER TRANSACTIONS"


class AirtimeTopup(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    network = models.ForeignKey(Network, on_delete=models.SET_NULL, null=True)
    mobile_number = models.CharField(max_length=30, blank=True)
    airtime_type = models.CharField(
        max_length=30, choices=airtype, default="VTU", help_text="VTU or share and Sell"
    )
    amount = models.CharField(max_length=30, blank=True)
    paid_amount = models.CharField(max_length=30, blank=True)
    Status = models.CharField(
        max_length=30,
        choices=status,
        default="processing",
        help_text="Select failed and save to refund user",
    )
    create_date = models.DateTimeField(default=timezone.now)
    balance_before = models.CharField(max_length=30, blank=True)
    balance_after = models.CharField(max_length=30, blank=True)
    Ported_number = models.BooleanField(default=False, blank=True, null=True)
    medium = models.CharField(max_length=30, default="website")
    refund = models.BooleanField(default=False, blank=True, null=True)
    ident = models.CharField(
        default=create_id, editable=False, max_length=100, verbose_name="Reference ID"
    )
    provider_source = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.mobile_number

    def get_absolute_url(self):
        return reverse("AirtimeTopup_success", args=[str(self.id)])

    def plan_net(self):
        return str(self.network)

    def plan_amt(self):
        return str(self.amount)

    def save(self, *args, **kwargs):
        if self.Status == "failed" and self.refund is False:
            previous_bal = self.user.Account_Balance
            self.user.deposit(
                self.user.id, float(self.paid_amount), False, "AIRTIME TOPUP Refund"
            )
            self.refund = True
            WalletSummary.objects.create(
                user=self.user,
                product="{} {} Airtime topup Refund for {} ".format(
                    self.network.name, self.amount, self.mobile_number
                ),
                amount=self.paid_amount,
                previous_balance=previous_bal,
                after_balance=(previous_bal + float(self.paid_amount)),
            )

            try:
                figure = (
                    TopupPercentage.objects.filter(network=self.network)
                    .first()
                    .commission
                )
                figure = float(self.paid_amount) * figure
                if figure > 0:
                    if self.user.referer_username:
                        if User.objects.filter(
                            username__iexact=self.user.referer_username
                        ).exists():
                            referer = User.objects.get(
                                username__iexact=self.user.referer_username
                            )

                            if self.user.user_type == "Smart Earner":
                                com = referer.Referer_Bonus
                                if com > 0:
                                    referer.ref_withdraw(figure)

                                    WalletSummary.objects.create(
                                        user=referer,
                                        product="[Referal bonus] refund  N{} commission for your referal {} AIRTIME failed order".format(
                                            figure, self.user.username
                                        ),
                                        amount=figure,
                                        previous_balance=com,
                                        after_balance=(com - figure),
                                    )
                                    notify.send(
                                        referer,
                                        recipient=referer,
                                        verb="[Referal bonus] refund N{}commission  for your referal {} AIRTIME failed order".format(
                                            figure, self.user.username
                                        ),
                                    )
            except:
                pass

        super(AirtimeTopup, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "AIRTIME TOPUP TRANSACTIONS"


class SME_text(models.Model):
    network = models.OneToOneField(
        Network, on_delete=models.SET_NULL, null=True, unique=True
    )
    number = models.CharField(max_length=100, null=True, blank=True)
    pin = models.CharField(
        max_length=10, help_text="DATA PIN if any", null=True, blank=True
    )
    data_vending_medium_for_500_mb_under_ogdams_double_account = models.CharField(
        max_length=100,
        choices=(("OGDAMS1", "OGDAMS1"), ("OGDAMS2", "OGDAMS2")),
        null=True,
        blank=True,
    )
    data_vending_medium_for_1_gb_under_ogdams_double_account = models.CharField(
        max_length=100,
        choices=(("OGDAMS1", "OGDAMS1"), ("OGDAMS2", "OGDAMS2")),
        null=True,
        blank=True,
    )
    data_vending_medium_for_2_gb_under_ogdams_double_account = models.CharField(
        max_length=100,
        choices=(("OGDAMS1", "OGDAMS1"), ("OGDAMS2", "OGDAMS2")),
        null=True,
        blank=True,
    )
    data_vending_medium_for_3_gb_under_ogdams_double_account = models.CharField(
        max_length=100,
        choices=(("OGDAMS1", "OGDAMS1"), ("OGDAMS2", "OGDAMS2")),
        null=True,
        blank=True,
    )
    data_vending_medium_for_5_gb_under_ogdams_double_account = models.CharField(
        max_length=100,
        choices=(("OGDAMS1", "OGDAMS1"), ("OGDAMS2", "OGDAMS2")),
        null=True,
        blank=True,
    )
    data_vending_medium_for_10_gb_under_ogdams_double_account = models.CharField(
        max_length=100,
        choices=(("OGDAMS1", "OGDAMS1"), ("OGDAMS2", "OGDAMS2")),
        null=True,
        blank=True,
    )
    sim_host_server_id_for_airtime = models.CharField(
        max_length=500, help_text="If you are using simhost", null=True, blank=True
    )
    sim_host_server_id_for_data = models.CharField(
        max_length=500, help_text="If you are using simhost", null=True, blank=True
    )
    vtu_sim_slot = models.IntegerField(
        help_text="Enter 1 for sim1 or 2 for sim2", null=True, blank=True
    )
    data_sim_slot = models.IntegerField(
        help_text="Enter 1 for sim1 or 2 for sim2", null=True, blank=True
    )
    mtn_sme_route = models.CharField(
        max_length=500,
        help_text="Select either SMS  to 131 or USSD  ",
        choices=(("SMS", "SMS"), ("USSD", "USSD")),
        null=True,
        blank=True,
    )
    msplug_device_id = models.CharField(
        max_length=500, help_text="If you are using MSPLUG ", null=True, blank=True
    )
    msplug_sim_slot = models.CharField(
        max_length=5,
        choices=(("sim1", "sim1"), ("sim2", "sim2")),
        help_text="If you are using MSPLUG i.e enter sim1 for sim1, sim2 for sim2",
        null=True,
        blank=True,
    )
    vtu_pin = models.CharField(max_length=10, null=True, blank=True)
    share_and_sell_pin = models.CharField(max_length=10, null=True, blank=True)
    vtu_auto_device_id = models.CharField(
        max_length=500, help_text="If you are using VTU AUTO", null=True, blank=True
    )

    def __str__(self):
        return self.network.name

    def save(self, *args, **kwargs):
        if SME_text.objects.filter(network=self.network):
            SME_text.objects.filter(network=self.network).delete()

        super(SME_text, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "SIM MANAGEMENT"


class Airtimeswap(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    swap_from_network = models.ForeignKey(
        Network, on_delete=models.SET_NULL, null=True, related_name="network_swap_from"
    )
    swap_to_network = models.ForeignKey(
        Network, on_delete=models.SET_NULL, null=True, related_name="network_swap_to"
    )
    amount = models.CharField(max_length=30, blank=True)
    mobile_number = models.CharField(max_length=30, blank=True)
    Status = models.CharField(max_length=30, choices=status, default="processing")
    create_date = models.DateTimeField(default=timezone.now)
    Receivece_amount = models.FloatField(null=True)
    Ported_number = models.BooleanField(default=False, blank=True, null=True)
    ident = models.CharField(default=create_id, editable=False, max_length=30)

    def __str__(self):
        return str(self.amount)

    def get_absolute_url(self):
        return reverse("Airtimeswap_success", args=[str(self.id)])


class PinCode(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    pin = models.IntegerField(unique=True)

    def get_absolute_url(self):
        return reverse("Transfer_detail", args=[str(self.id)])


class Btc_rate(models.Model):
    rate = models.CharField(max_length=50, choices=ratechoice)
    btc_wallet_address = models.CharField(max_length=200, default="abcdef")
    amount = models.FloatField()

    def __str__(self):
        return str(self.rate)


class Buybtc(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    Btc = models.FloatField(blank=False, null=True)
    amount = models.FloatField(blank=False, null=True)
    Btc_address = models.CharField(max_length=200)
    create_date = models.DateTimeField(default=timezone.now)
    ident = models.CharField(default=create_id, editable=False, max_length=30)
    Status = models.CharField(max_length=30, choices=status, default="processing")

    def __str__(self):
        return str(self.Btc)

    def get_absolute_url(self):
        return reverse("buy_btc_success", args=[str(self.id)])


class SellBtc(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    Btc = models.FloatField(blank=False, null=True)
    amount = models.FloatField(blank=False, null=True)
    create_date = models.DateTimeField(default=timezone.now)
    ident = models.CharField(default=create_id, editable=False, max_length=30)
    Status = models.CharField(max_length=30, choices=status, default="processing")

    def __str__(self):
        return str(self.Btc)

    def get_absolute_url(self):
        return reverse("sell_btc_success", args=[str(self.id)])


class Bulk_Message(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    unit = models.IntegerField(null=True)
    invalid = models.IntegerField(null=True)
    total = models.IntegerField(null=True)
    page = models.FloatField(null=True)
    amount = models.FloatField(null=True)
    sendername = models.CharField(max_length=12, blank=True)
    message = models.TextField(blank=True)
    to = models.TextField(blank=True)
    create_date = models.DateTimeField(default=timezone.now)
    DND = models.BooleanField(default=False, blank=True, null=True)
    ident = models.CharField(default=create_id, editable=False, max_length=30)

    def get_absolute_url(self):
        return reverse("Bulk_success", args=[str(self.id)])

    class Meta:
        verbose_name_plural = "BULK SMS"


class Testimonial(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    message = models.TextField()
    create_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.message


class Comment(models.Model):
    testimonial = models.ForeignKey(Testimonial, blank=True, on_delete=models.CASCADE)
    Reply = models.TextField()
    create_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.Reply


class Notify_user(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    username = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    create_date = models.DateTimeField(default=timezone.now)
    send_email = models.BooleanField(null=True, blank=True, default=False)
    ident = models.CharField(default=create_id, editable=False, max_length=30)

    def __str__(self):
        return self.username


class Airtime_to_Data_pin(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    network = models.ForeignKey(Network_1, on_delete=models.CASCADE)
    plan = models.ForeignKey(Airtime_to_data_Plan, on_delete=models.SET_NULL, null=True)
    mobile_number = models.CharField(max_length=30, blank=True)
    Status = models.CharField(max_length=30, choices=status, default="processing")
    create_date = models.DateTimeField(default=timezone.now)
    pin = models.CharField(max_length=30, blank=True)
    Ported_number = models.BooleanField(default=False, blank=True, null=True)
    ident = models.CharField(default=create_id, editable=False, max_length=30)

    def __str__(self):
        return str(self.plan)

    def save(self, *args, **kwargs):
        if self.Status == "failed":
            mb = User.objects.get(id=self.user.id)
            mb.deposit(mb.id, float(self.plan.plan_amount))
        super(Airtime_to_Data_pin, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("Airtime_to_Data_pin_success", args=[str(self.id)])


class Airtime_to_Data_tranfer(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    plan = models.CharField(choices=Mtn_Tran_Plan, max_length=30, null=True)
    network = models.CharField(choices=Network_3, max_length=30, null=True)
    Transfer_number = models.CharField(max_length=30, blank=True)
    mobile_number = models.CharField(max_length=30, blank=True)
    Status = models.CharField(max_length=30, choices=status, default="processing")
    create_date = models.DateTimeField(default=timezone.now)
    Ported_number = models.BooleanField(default=False, blank=True, null=True)
    ident = models.CharField(default=create_id, editable=False, max_length=30)

    def __str__(self):
        return str(self.plan)

    def save(self, *args, **kwargs):
        if self.Status == "failed":
            mb = User.objects.get(id=self.user.id)
            mb.deposit(mb.id, float(self.plan.plan_amount))
        super(Airtime_to_Data_tranfer, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("Airtime_to_Data_tranfer_success", args=[str(self.id)])


class Automation_control(models.Model):
    Network_good = models.BooleanField(default=False)
    network_name = models.OneToOneField(
        Network, on_delete=models.SET_NULL, null=True, unique=True, blank=True
    )

    def __str__(self):
        return str(self.network_name)


class Airtime_automation_control(models.Model):
    Network_good = models.BooleanField(default=False)
    network_name = models.OneToOneField(
        Network, on_delete=models.SET_NULL, null=True, unique=True, blank=True
    )

    def __str__(self):
        return str(self.network_name)


class Bankpayment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )

    Bank_paid_to = models.CharField(max_length=15, blank=True, null=True)
    Reference = models.CharField(max_length=15, blank=True, null=True)
    amount = models.CharField(max_length=30, blank=True, null=True)
    create_date = models.DateTimeField(default=timezone.now)
    ident = models.CharField(default=create_id, editable=False, max_length=30)
    Status = models.CharField(max_length=30, choices=status, default="processing")
    fund = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse("Banksuccess", args=[str(self.id)])

    def save(self, *args, **kwargs):
        amount = self.amount
        if self.Status == "successful" and self.fund is False:
            previous_bal = self.user.Account_Balance

            self.user.deposit(self.user.id, float(amount), False, "Manual Bank Funding")
            self.fund = True
            WalletSummary.objects.create(
                user=self.user,
                product="Manual Bank Funding",
                amount=amount,
                previous_balance=previous_bal,
                after_balance=(previous_bal + float(amount)),
            )

        super(Bankpayment, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "MANUAL BANK FUNDING"


class paymentgateway(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    reference = models.CharField(null=True, blank=True, max_length=50)
    amount = models.FloatField(blank=True, null=True)
    Status = models.CharField(max_length=30, choices=status, default="processing")
    gateway = models.CharField(max_length=30, default="Paystack")
    created_on = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = "PAYMENT GATEWAY TRANSACTIONS"


class Cable(models.Model):
    name = models.CharField(max_length=30, choices=Multichoice, unique=True)
    status = models.CharField(max_length=30, choices=Netstatus)
    vending_api = models.CharField(
        max_length=50,
        default="VTPASS",
        choices=(("VTPASS", "VTPASS"), ("RINGO", "RINGO")),
        blank=True,
        null=True,
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "CABLE COMPANY"


class CablePlan(models.Model):
    cablename = models.ForeignKey(Cable, on_delete=models.CASCADE)
    plan_amount = models.PositiveIntegerField()
    product_code = models.CharField(max_length=200, blank=True, null=True)
    package = models.CharField(max_length=200, help_text="package(ie GOTV Plus)")
    hasAddon = models.BooleanField(default=False)
    Addon_name = models.CharField(
        max_length=200, help_text="package(ie Asian Add-on)", blank=True, null=True
    )
    addoncode = models.CharField(max_length=200, blank=True, null=True)
    commission = models.PositiveIntegerField(default=0)

    def __str__(self):
        return (
            str(self.package)
            + str(self.Addon_name)
            + "----"
            + "#"
            + str(self.plan_amount)
        )

    def plan_name(self):
        return str(self.package)

    def cableplanname(self):
        return str(self.cablename)

    def plan_amt(self):
        return str(self.plan_amount)

    def plan_id(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "CABLE SUBSCRIPTION PLAN"


class Cablesub(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    cablename = models.ForeignKey(Cable, on_delete=models.SET_NULL, null=True)
    cableplan = models.ForeignKey(CablePlan, on_delete=models.SET_NULL, null=True)
    smart_card_number = models.CharField(max_length=30, blank=True)
    balance_before = models.CharField(max_length=30, blank=True)
    balance_after = models.CharField(max_length=30, blank=True)
    plan_amount = models.CharField(max_length=30, blank=True)
    Status = models.CharField(
        max_length=30,
        choices=status,
        default="processing",
        help_text="Select failed and save to refund user",
    )
    create_date = models.DateTimeField(default=timezone.now)
    refund = models.BooleanField(default=False, blank=True, null=True)
    customer_name = models.CharField(max_length=70, blank=True, null=True)
    ident = models.CharField(
        default=create_id, editable=False, max_length=300, verbose_name="Reference ID"
    )
    provider_source = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.cableplan)

    def get_absolute_url(self):
        return reverse("cablesub_success", args=[str(self.id)])

    def save(self, *args, **kwargs):
        if self.Status == "failed" and self.refund is False:
            previous_bal = self.user.Account_Balance
            self.user.deposit(
                self.user.id, float(self.plan_amount), False, "Cablesub Refund"
            )
            self.refund = True
            WalletSummary.objects.create(
                user=self.user,
                product="{} N{} Cablesub Refund for {} ".format(
                    self.cableplan.package, self.plan_amount, self.smart_card_number
                ),
                amount=self.plan_amount,
                previous_balance=previous_bal,
                after_balance=(previous_bal + float(self.plan_amount)),
            )

        super(Cablesub, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "CABLE SUBSCRIPTION TRANSACTIONS"


class Disco_provider_name(models.Model):
    name = models.CharField(max_length=150, unique=True)
    p_id = models.CharField(max_length=150, unique=True, null=True, blank=False)
    commission = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "DISCO PROVIDER NAMES"


class KYC(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        editable=False,
        blank=False,
        null=True,
        related_name="Customer",
    )
    First_Name = models.CharField(max_length=50, null=True, help_text="Your name here")
    Middle_Name = models.CharField(
        max_length=50,
        null=True,
    )
    Last_Name = models.CharField(max_length=50, null=True, help_text="Your Surname")
    DOB = models.DateField(null=True)
    Gender = models.CharField(
        max_length=6,
        null=True,
    )
    State_of_origin = models.CharField(
        max_length=100,
        null=True,
    )
    Local_gov_of_origin = models.CharField(
        max_length=100,
        null=True,
    )
    BVN = models.CharField(
        max_length=50,
        null=True,
    )
    passport_photogragh = models.ImageField(
        upload_to="passport_images",
        null=True,
        help_text="Maximum of 50kb in size",
        validators=[validate_file_size],
    )

    status = models.CharField(
        max_length=20, null=True, choices=vericate, default="processing"
    )
    dump = models.TextField()
    comment = models.TextField()
    primary_details_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "KYC"

    def save(self, *args, **kwargs):
        if self.status == "Approved":
            self.user.verify = True
            self.user.FullName = (
                self.First_Name + " " + self.Middle_Name + " " + self.Last_Name
            )
            self.user.DOB = self.DOB
            self.user.BVN = self.BVN
            self.user.passport_photogragh = self.passport_photogragh
            self.user.State_of_origin = self.State_of_origin
            self.user.Local_gov_of_origin = self.Local_gov_of_origin
            self.user.Gender = self.Gender
            self.user.save()

            try:
                body = {"bvn": self.BVN}
                data = json.dumps(body)
                ad = requests.post(
                    "https://api.monnify.com/api/v1/auth/login",
                    auth=HTTPBasicAuth(
                        f"{config.monnify_API_KEY}", f"{config.monnify_SECRET_KEY}"
                    ),
                )
                mydata = json.loads(ad.text)
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(
                        mydata["responseBody"]["accessToken"]
                    ),
                }
                requests.post(
                    f"https://api.monnify.com/api/v1/bank-transfer/reserved-accounts/update-customer-bvn/{self.user.reservedaccountReference}",
                    headers=headers,
                    data=data,
                )

            except:
                pass

            try:
                sendmail(
                    "KYC Approved Notification ",
                    f"Dear {self.user.username} , your KYC varification has been Approved. your account daily transactions is now unlimited",
                    self.user.email,
                    self.user.username,
                )
            except:
                pass

        if not self.id:
            try:
                sendmail(
                    "User KYC Verification Notification ",
                    f" {self.user.username} Just submitted his details for KYC verification",
                    config.email,
                    "Admin",
                )
            except:
                pass

        super(KYC, self).save(*args, **kwargs)

    def __str__(self):
        return '<img src="https://www.legitdata.com.ngmedia/{}" height="150"/>'.format(
            self.passport_photogragh.url
        )

    def upload_passport(self):
        from django.utils.html import mark_safe

        return mark_safe(
            '<img src="https://www.legitdata.com.ngmedia/%s" width="150" height="150" />'
            % (self.passport_photogragh)
        )

    upload_passport.short_description = "Uploaded Passport"

    def bvn_passport(self):
        from django.utils.html import mark_safe

        data = json.loads(self.dump)
        img = data["response"]["base64Image"]
        img = "data:image/jpeg;base64," + img
        # print(img)
        return mark_safe('<img src="%s" width="150" height="150" />' % (img))

    bvn_passport.short_description = "BVN Passport"

    def __str__(self):
        return str(self.user)


class Billpayment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    disco_name = models.ForeignKey(
        Disco_provider_name, on_delete=models.SET_NULL, null=True
    )
    amount = models.CharField(max_length=30)
    paid_amount = models.CharField(max_length=30, blank=True)
    balance_before = models.CharField(max_length=30, blank=True)
    balance_after = models.CharField(max_length=30, blank=True)
    meter_number = models.CharField(max_length=30, blank=True)
    token = models.CharField(max_length=200, blank=True, null=True)
    Customer_Phone = models.CharField(max_length=15, null=True)
    MeterType = models.CharField(max_length=30, choices=mtype, null=True)
    Status = models.CharField(
        max_length=30,
        choices=status,
        default="processing",
        help_text="Select failed and save to refund user",
    )
    create_date = models.DateTimeField(default=timezone.now)
    refund = models.BooleanField(default=False, blank=True, null=True)
    customer_name = models.CharField(max_length=250, blank=True, null=True)
    customer_address = models.CharField(max_length=500, blank=True, null=True)
    ident = models.CharField(
        default=create_id, editable=False, max_length=300, verbose_name="Reference ID"
    )
    provider_source = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.disco_name)

    def get_absolute_url(self):
        return reverse("bill_success", args=[str(self.id)])

    def save(self, *args, **kwargs):
        if self.Status == "failed" and self.refund is False:
            previous_bal = self.user.Account_Balance
            self.user.deposit(
                self.user.id, float(self.amount), False, "Bill Payment Refund"
            )
            self.refund = True
            WalletSummary.objects.create(
                user=self.user,
                product="{} {}Bill Payment Refund for {} ".format(
                    self.disco_name.name, self.amount, self.meter_number
                ),
                amount=self.amount,
                previous_balance=previous_bal,
                after_balance=(previous_bal + float(self.amount)),
            )

        elif self.token:

            def sendmessage(sender, message, to, route):
                baseurl = "https://sms.hollatags.com/api/send/?user=oluwole1&pass=Pstsegunsss@c1&to={0}&from={1}&msg={2}".format(
                    to, sender, message
                )
                requests.get(baseurl, verify=False)

            sendmessage(
                "BILLTOKEN",
                "From legitdata your Bill Token is {0} ".format(self.token),
                self.Customer_Phone,
                "02",
            )

        super(Billpayment, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "BILL PAYMENT TRANSACTIONS"


class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    updated_on = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="blogimage", null=True, blank=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ["-created_on"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return '<img src="{}" height="150"/>'.format(self.image.url)
        Post.allow_tags = True

    def get_absolute_url(self):
        return reverse("post_detail", args=[self.slug])


class Category(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("book_list_by_category", args=[self.slug])


class Book(models.Model):
    category = models.ForeignKey(
        Category, related_name="books", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100, db_index=True)
    author = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="books/%Y/%m/%d", blank=True)

    class Meta:
        ordering = ("name",)
        index_together = (("id", "slug"),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("book_detail", args=[self.id, self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Book, self).save(*args, **kwargs)


class Book_order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, editable=False, blank=False, null=True
    )
    book_name = models.ForeignKey(Book, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class frequentlyAskedQuestion(models.Model):
    question = models.CharField(max_length=100, null=True, blank=True)
    answer = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.question}"

    class Meta:
        verbose_name_plural = "FREQUENTLY ASKED QUESTIONS"


class RetailWebFrequentlyAskedQuestion(models.Model):
    question = models.CharField(max_length=100, null=True, blank=True)
    answer = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.question}"

    class Meta:
        verbose_name_plural = "FREQUENTLY ASKED QUESTIONS(Retailer Website)"


######################################################### HAMEED
"""
class exam_pin(models.Model):
    exam = models.CharField(max_length=30, choices=result, default='WAEC')
    available = models.BooleanField(default=True)
    pin = models.CharField(max_length=100, unique=True, null=True)
    serial = models.CharField(max_length=100, unique=True, null=True)

    def __str__(self):
        return str(self.exam) + "  " + str(self.pin) + "  " + str(self.serial)
 
    class Meta:
        verbose_name_plural = "EXAM PINS GENERATED"


class Load_exam_pin(models.Model):
    exam = models.CharField(max_length=30, choices=result, default='WAEC')
    dump_pin = models.TextField()
    total_pin_loaded = models.CharField(max_length=100, null=True, blank=True, help_text="Leave blank, system automatic return it")

    def save(self, *args, **kwargs):
        data = self.dump_pin.split("\n")
        self.total_pin_loaded = len(data)

        if exam_pin.objects.all():
            last_id = int(exam_pin.objects.all().last().serial)
        else:
            last_id = 0

        
        for x in data:
            last_id += 1
            exam_pin.objects.create(pin=x, exam=self.exam, serial=last_id)
        super(Load_exam_pin, self).save(*args, **kwargs)

    def __str__(self):
        return " set  " + str(self.id)

    class Meta:
        verbose_name_plural = 'GENERATE EXAM PIN'

"""


class AppAdsImage(models.Model):
    banner = models.ImageField(
        upload_to="adsbanner",
        null=True,
        help_text="Dimensions:400 by 250 in pixel. width by height",
    )
    route = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        help_text="i.e /datanet for buy data page other route /datanet =  buy data page \n /airtimenet = buy airtime page \n /cablename = cable sub page \n /bill = billpayment page \n /referal = referal page",
    )

    def __str__(self):
        return self.route

    class Meta:
        verbose_name_plural = "APP ADS BANNERS"


class Charge_referral_bonus(models.Model):
    username = models.CharField(max_length=100, null=True)
    amount = models.IntegerField()

    balance_before = models.FloatField(
        null=True, blank=True, help_text="leave blank sytem automatic set this"
    )
    balance_after = models.FloatField(
        null=True, blank=True, help_text="leave blank sytem automatic set this"
    )
    comment = models.TextField()
    pending_amount = models.IntegerField(
        default=0,
        help_text="leave blank sytem automatic set this,if the amount you want to with not upto user wallet, pending amount wait till when user fund next",
    )

    def __str__(self):
        return str(self.username)

    def save(self, *args, **kwargs):
        try:
            mb = User.objects.get(username=self.username)
        except:
            raise ValidationError("Invalid user, enter correct username")
        if not self.id:
            if self.amount > mb.Referer_Bonus:
                self.pending_amount = self.amount - mb.Referer_Bonus
                self.balance_before = mb.Referer_Bonus
                mb.ref_withdraw(mb.Referer_Bonus)

                self.balance_after = 0

                try:
                    WalletSummary.objects.create(
                        user=mb,
                        product=f"Admin Charge your referral bonus wallet for {self.comment} ",
                        amount=self.amount,
                        previous_balance=self.balance_before,
                        after_balance=self.balance_after,
                    )
                except:
                    pass

            else:
                self.balance_before = mb.Referer_Bonus
                withdraw = mb.ref_withdraw(self.amount)
                if withdraw is False:
                    raise ValidationError(
                        f"Insufficient fund ,{self.username} referral bonus balance is {mb.Referer_Bonus}"
                    )
                self.balance_after = mb.Referer_Bonus

                try:
                    WalletSummary.objects.create(
                        user=mb,
                        product=f"Admin Charge your referral bonus wallet for {self.comment} ",
                        amount=self.amount,
                        previous_balance=self.balance_before,
                        after_balance=self.balance_after,
                    )
                except:
                    pass

        super(Charge_referral_bonus, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "WITHDRAW FROM USER BONUS WALLET"


class Fund_User_Bonus(models.Model):
    username = models.CharField(max_length=100, null=True)
    amount = models.IntegerField()
    balance_before = models.FloatField(
        null=True, blank=True, help_text="leave blank sytem automatic set this"
    )
    balance_after = models.FloatField(
        null=True, blank=True, help_text="leave blank sytem automatic set this"
    )

    def __str__(self):
        return str(self.username)

    def save(self, *args, **kwargs):
        try:
            mb = User.objects.get(username=self.username)
        except:
            raise ValidationError("Invalid user, enter correct username")

        self.balance_before = mb.Referer_Bonus
        mb.ref_deposit(self.amount)
        self.balance_after = mb.Referer_Bonus

        try:
            WalletSummary.objects.create(
                user=mb,
                product=f"Admin  Funding your REFERRAL BONUS wallet with sum of {self.amount}",
                amount=self.amount,
                previous_balance=self.balance_before,
                after_balance=(self.balance_after),
            )
        except:
            pass

        super(Fund_User_Bonus, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "FUND USER REFERRAL BONUS WALLET"
