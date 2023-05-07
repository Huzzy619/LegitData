from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from core.models import CustomUser, ChargeUser
import json
from .forms import *

 

# Register your models here.

class CustomUserAdmin(UserAdmin):
    
    list_display =['username',"FullName",'email','user_type','Phone','Account_Balance','referer_username','referals','Referer_Bonus','id','last_login','date_joined','verify']
    search_fields = ('username','email','Phone','referer_username','id','user_type')

    def referals(self, obj):
        a = CustomUser.objects.get(id = obj.id)
        return Referal_list.objects.filter(user=a).count()

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('user_type','reservedaccountNumber','verify','email_verify')}),
             ("Profile", {'fields': ('image_tag',"FullName",'Phone',"Account_Balance",'referer_username','Referer_Bonus',"BVN","DOB",'BankName','AccountNumber','AccountName',"Gender","State_of_origin","Local_gov_of_origin")}),
    )

    readonly_fields = ('image_tag','FullName','Address',"Account_Balance",'referer_username','Referer_Bonus','BankName','AccountNumber','AccountName',"BVN","DOB","Gender","State_of_origin","Local_gov_of_origin")


class AirtimeAdmin(admin.ModelAdmin):
    add_form=airtimeform
    list_display =['user','network','pin','amount','id','ident','Status','create_date']
    search_fields = ('id','ident')



class DataAdmin(admin.ModelAdmin):
    add_form=dataform
    list_display =['user','network','mobile_number','plan','data_type','id','api_response','ident','Status','medium','create_date']
    search_fields = ('user__username','mobile_number','ident')
    list_filter =['network__name']

class Airtime_fundingAdmin(admin.ModelAdmin):
    add_form=Airtime_fundingform
    list_display =['user',"use_to_fund_wallet",'network','mobile_number','amount',"BankName",'AccountNumber','AccountName','id','ident','Status','create_date']
    search_fields = ('user__username','id','ident')


class WithdrawAdmin(admin.ModelAdmin):
    add_form=withdrawform
    list_display =['user','accountNumber','accountName','bankName','amount','id','ident','Status','create_date']
    search_fields = ('user__username','id','ident')

class Admin_number_Admin(admin.ModelAdmin):
    list_display =['network','phone_number']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class NetworkAdmin(admin.ModelAdmin):
    list_display =['name', 'msorg_web_net_id','data_vending_medium','vtu_vending_medium','airtime_disable', 'data_disable', 'sme_disable','gifting_disable']

class PlanAdmin(admin.ModelAdmin):
    list_display =['network', 'plan_type','plansize','ussd_string','planamount','Affilliateprice','TopUserprice','apiprice']
    ordering = ['network','plan_size']
    list_filter =['network__name']

    def plansize(self, obj):
        
        return  str(obj.plan_size) + str(obj.plan_Volume)

    def planamount(self, obj):
        
        return  "₦" + str(obj.plan_amount)

    def Affilliateprice(self, obj):
        
        return  "₦" + str(obj.Affilliate_price)

    def TopUserprice(self, obj):
        
        return  "₦" + str(obj.TopUser_price)

    def apiprice(self, obj):
        
        return  "₦" + str(obj.api_price)


class TransferAdmin(admin.ModelAdmin):
    add_form=Transferform
    list_display =['user','receiver_username','amount','id','ident','Status','create_date']
    search_fields = ('user__username','id','ident')

class AirtimeTopupAdmin(admin.ModelAdmin):
    add_form=AirtimeTopupform
    list_display =['user','network','mobile_number','amount','id','ident','Status','medium','create_date']
    search_fields = ('user__username','mobile_number','ident')
    list_filter =['network__name']

class AirtimeswapAdmin(admin.ModelAdmin):
    add_form=Airtimeswapform
    list_display =['user','swap_from_network','swap_to_network','mobile_number','amount','Status','id','ident','create_date']
    search_fields = ('id','ident')

class CouponCodeAdmin(admin.ModelAdmin):
    list_display =['Coupon_Code','amount','Used']

class CouponPaymentAdmin(admin.ModelAdmin):
    list_display =['user','Code','amount','id','ident']
    search_fields = ('user__username','id','ident')

class TestimonialAdmin(admin.ModelAdmin):
    list_display =['user','message']

class CommentAdmin(admin.ModelAdmin):
    list_display =['Reply']

class Airtime_To_Data_Pin_Admin(admin.ModelAdmin):

    list_display =['user','network','mobile_number','pin','plan','id','ident','Status','create_date']
    search_fields = ('id','ident')

class Airtime_To_Data_PlanAdmin(admin.ModelAdmin):
    list_display =['network','plan_amount','plan_size']
    search_fields = ('id','ident')


class Automation_control_Admin(admin.ModelAdmin):
    list_display =['network_name','Network_good','id']


class Airtime_to_data_Network_Admin(admin.ModelAdmin):
    list_display =['name']


class Airtime_to_data_Plan_Admin(admin.ModelAdmin):
    list_display =['network','plan_amount','plan_size']
    search_fields = ('id','ident')

class Airtime_to_Data_tranfer_Admin(admin.ModelAdmin):
    list_display =['user','network','plan','Transfer_number','mobile_number','Status','id','ident','create_date']
    search_fields = ('id','ident')


class Bank_payment_admin(admin.ModelAdmin):
     list_display =['user','amount','ident','Status','create_date']
     search_fields = ('user__username','id','ident')


class Cable_Admin(admin.ModelAdmin):
    list_display =['name']

class CablePlan_Admin(admin.ModelAdmin):
    list_display =['cablename','package']



class Cablesub_Admin(admin.ModelAdmin):
    list_display =['user','cablename','cableplan','smart_card_number','Status','create_date','id']
    search_fields = ('user__username','id','ident')


class Billpayment_Admin(admin.ModelAdmin):
    list_display =['user','disco_name','amount','meter_number','Status','create_date','id']
    search_fields = ('user__username','id','ident')


class Percentage_Admin(admin.ModelAdmin):
    list_display =['network','percent','id']

class Topup_Percentage_Admin(admin.ModelAdmin):
    list_display =['network','percent','id']

class New_order_admin(admin.ModelAdmin):
     list_display = ['user','name','amount']
     search_fields = ('user__username','id','ident')



class Btc_rate_admin(admin.ModelAdmin):
     list_display = ['rate','amount']

class Bulk_sms_admin(admin.ModelAdmin):
     list_display = ['user','sendername','message','to','total','amount','create_date']
     search_fields = ('user__username','id','ident')


class Result_Checker_Pin_admin(admin.ModelAdmin):
     list_display = ['exam_name','amount']

class Result_Checker_Pin_order_admin(admin.ModelAdmin):
     list_display = ['user','exam_name','create_date']

class BuyBtc_admin(admin.ModelAdmin):
     list_display = ['user','Btc','amount','Btc_address','ident','Status','create_date']

class paymentgateway_admin(admin.ModelAdmin):
     list_display = ['user','reference','amount','gateway','Status','created_on']
     search_fields = ('user__username','id',)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status','image','created_on')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}

class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'amount','previous_balance',"after_balance",'create_date')

    search_fields = ['user__username','product',]



class upgradeuserAdmin(admin.ModelAdmin):
    list_display = ('user', 'from_package', "to_package",'amount','previous_balance',"after_balance",'create_date')
    search_fields = ['user__username',]

class RechargeAdmin(admin.ModelAdmin):
    list_display = ('network', 'amount', 'amount_to_pay')
    search_fields = ['user__username',]

class KYCAdmin(admin.ModelAdmin):
    list_display = ('user','First_Name', 'Middle_Name', 'Last_Name', 'DOB', 'Gender', 'State_of_origin', 'status')
    search_fields = ['user__username',]

    fieldsets =  (
        ("INFORMATION SUBMITED", {'fields': ('upload_passport','BVN','First_Name', 'Middle_Name', 'Last_Name', 'DOB', 'Gender', 'State_of_origin','Local_gov_of_origin',)}),
       ("BVN INFORMATION", {'fields': ("bvn_passport","FirsName",'middleName','lastName','dateOfBirth','gender')}),
        ("VERIFICATION REMARK", {'fields': ("comment","status")}),

    )
    readonly_fields =('Local_gov_of_origin',"FirsName",'dateOfBirth','gender','middleName','lastName','upload_passport',"bvn_passport",'First_Name', 'Middle_Name', 'Last_Name', 'BVN','DOB', 'Gender', 'State_of_origin')



    def FirsName(self, obj):
        print(obj.dump)
        print("musa")
        return  str(json.loads(obj.dump)["response"]["data"]["firstName"])

    def lastName(self, obj):
        print(obj.dump)
        print("musa")
        return  str(json.loads(obj.dump)["response"]["data"]["lastName"])
    def middleName(self, obj):
        print(obj.dump)
        print("musa")
        return  str(json.loads(obj.dump)["response"]["data"]["middleName"])

    def dateOfBirth(self, obj):
        print(obj.dump)
        print("musa")
        return  str(json.loads(obj.dump)["response"]["data"]["dateOfBirth"])

    def gender(self, obj):
        print(obj.dump)
        print("musa")
        return  str(json.loads(obj.dump)["response"]["data"]["gender"])

  
class Recharge_pin_orderadmin(admin.ModelAdmin):
    list_display =    ('user','network','network_amount','name_on_card','quantity','data_pin','id','Status',"previous_balance","after_balance","amount",'create_date' )
    search_fields = ['user__username',]

class Load_Recharge_pinAdmin(admin.ModelAdmin):
    list_display = ('dump_pin','amount','total_pin_loaded','load_code')

class Charge_userAdmin(admin.ModelAdmin):
    list_display = ('username','amount','pending_amount','balance_before','balance_after')
    search_fields = ['user__username',]

class Fund_userAdmin(admin.ModelAdmin):
    list_display = ('username','amount','balance_before','balance_after')
    search_fields = ['username',]

class Wallet_Funding_Admin(admin.ModelAdmin):
    list_display = ('user','medium','amount','previous_balance','after_balance','create_date')
    search_fields = ['user__username',]

class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('user','amount','transaction_type','balance_before','balance_after')
    search_fields = ['user__username',]

class TopuserWebsiteAdmin(admin.ModelAdmin):
    list_display = ('user','Domain_name','amount','Offices_Address','Website_Customer_Care_Number',"SSL_Security")


class SmeifyAuth_admin(admin.ModelAdmin):
    list_display = ['username','password','expire_date',"token"]
    
    def has_add_permission(self, request):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False

class Recharge_pin_Admin(admin.ModelAdmin):
     list_display = ['network','amount','pin',"serial", 'load_code', 'available']
     list_filter = ['network','available']

from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from django_otp.admin import OTPAdminSite



class OTPAdmin(OTPAdminSite):
    pass


admin_site = OTPAdmin(name='OTPAdmin')


# admin_site.register(TOTPDevice, TOTPDeviceAdmin) 
admin_site.site_title = "UFARDATA"
admin_site.site_header = "Welcome To UFARDATA Admin Panel"

admin_site.register(SmeifyAuth,SmeifyAuth_admin)
admin_site.register(TopuserWebsite,TopuserWebsiteAdmin)
admin_site.register(Load_Recharge_pin,Load_Recharge_pinAdmin)
admin_site.register(Upgrade_user,upgradeuserAdmin)
admin_site.register(Result_Checker_Pin, Result_Checker_Pin_admin)
admin_site.register(Result_Checker_Pin_order, Result_Checker_Pin_order_admin)
admin_site.register(Post, PostAdmin)
admin_site.register( paymentgateway, paymentgateway_admin)
admin_site.register(Transactions,TransactionsAdmin)
admin_site.register(Bulk_Message,Bulk_sms_admin)
admin_site.register(CustomUser,CustomUserAdmin)
admin_site.register(Info_Alert)
admin_site.register(Btc_rate,Btc_rate_admin)
admin_site.register(Airtime,AirtimeAdmin)
admin_site.register(Data,DataAdmin)
admin_site.register(ServicesCharge)
admin_site.register(Airtimeswap, AirtimeswapAdmin)
admin_site.register(AirtimeTopup,AirtimeTopupAdmin)
admin_site.register(Transfer,TransferAdmin)
admin_site.register(Plan,PlanAdmin)
admin_site.register(BankAccount)
admin_site.register(Network,NetworkAdmin)
admin_site.register(Withdraw, WithdrawAdmin)
admin_site.register(Couponcode, CouponCodeAdmin)
admin_site.register(CouponPayment,CouponPaymentAdmin)
admin_site.register(Admin_number,Admin_number_Admin)
admin_site.register(Airtime_funding,Airtime_fundingAdmin)
admin_site.register(Disable_Service)
admin_site.register(Airtime_to_Data_tranfer,Airtime_to_Data_tranfer_Admin)
admin_site.register(Airtime_to_Data_pin,Airtime_To_Data_Pin_Admin)
admin_site.register(Automation_control,Automation_control_Admin)
admin_site.register(Recharge_pin_order,Recharge_pin_orderadmin)
admin_site.register(Bankpayment,Bank_payment_admin)
admin_site.register(Cablesub,Cablesub_Admin)
admin_site.register(CablePlan,CablePlan_Admin)
admin_site.register(Cable,Cable_Admin)
admin_site.register(Percentage,Percentage_Admin)
admin_site.register(ChargeUser, Charge_userAdmin)
admin_site.register(Fund_User, Fund_userAdmin)
admin_site.register(WalletSummary,WalletAdmin)
admin_site.register(Recharge,RechargeAdmin)
admin_site.register(SME_text)
admin_site.register(Disco_provider_name)
admin_site.register(TopupPercentage,Topup_Percentage_Admin)
admin_site.register(Billpayment,Billpayment_Admin)
admin_site.register(KYC,KYCAdmin)
admin_site.register(Black_List_Phone_Number)
admin_site.register(WalletFunding,Wallet_Funding_Admin)
# admin_site.register(Site)
# admin_site.register(LogEntry) 


@admin.register(frequentlyAskedQuestion)
class FAQ_Admin(admin.ModelAdmin):
    # list_display =['']
    search_fields = ['*']


@admin.register(RetailWebFrequentlyAskedQuestion)
class RetailWebFAQ_Admin(admin.ModelAdmin):
    search_fields = ['*']


# @admin.register(exam_pin)
# class exam_pinAdmin(admin.ModelAdmin):
#     list_display = ('exam','available', 'serial',)
#     search_fields = ['exam','serial']


# @admin.register(Load_exam_pin)
# class Load_exam_pin(admin.ModelAdmin):
#     list_display = ('exam','total_pin_loaded', 'dump_pin',)


@admin.register(WebsiteConfiguration)
class WebConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, 
            {'fields': ('primary_color', 'secondary_color', 'support_phone_number', 'whatsapp_group_link', 'gmail','sms_notification_number', 'intro_message')} 
        ),
        # ('Advanced options', {
        #     'classes': ('collapse',),
        #     'fields': ('registration_required', 'template_name'),
        # }),
        ('USERS ACCOUNT UPGRADE SETTING', {
            'fields': ('affiliate_upgrade_fee', 'affiliate_to_topuser_upgrade_fee', 'topuser_upgrade_fee'),
        }),
        ('REFERRAL BONUS', {
            'fields': ('affiliate_referral_bonus', 'affiliate_to_topuser_referral_bonus', 'topuser_referral_bonus'),
        }),
        ('CONTROLLER', {
            'fields': ('Cable_provider', 'Bill_provider', 'disable_Transaction_limit', 'ResultCheckerSource'),
        }),
        ('UNVERIFIED USER LIMITS', {
            'fields': ( 
                'unverified_users_daily_withdraws_limit', 'unverified_users_transfer_limit','unverified_users_daily_transation_limit'
            ),
        }),
        ('PAYMENT GATEWAYS', {
            'fields': (
                'manual_bank_funding_limit', 'manual_bank_funding_info_message', 'Paystack_secret_key','monnify_API_KEY', 'monnify_SECRET_KEY', 'monnify_contract_code'
            ),
        }),
        ('MSORG WEBSITE API/AUTOMATION', {
            'fields': ('msorg_web_url', 'msorg_web_api_key', 'msorg_web_url_2', 'msorg_web_api_key_2', 'msorg_web_url_3', 'msorg_web_api_key_3'),
        }),
        ('API/AUTOMATION', {
            'fields': 
            ('ringo_email', 'ringo_password', 'vtpass_email', 'vtpass_password', 'vtu_auto_email', 'vtu_auto_password', 'hollatag_username', 'hollatag_password', 'sme_plug_secret_key', 'simhost_API_key', 'msplug_API_key', 'mobilenig_username', 'mobilenig_api_key', 'idchecker_api_key','qtopup_api_key','uws_token'),
        }),
    )

    from django.forms import Textarea
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
                attrs={
                    'rows': 20,
                    'cols': 100,
                    'style': 'height: 2.5em;'
                }
            )
        },
    }


    
    def has_add_permission(self, request):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False

   
@admin.register(Referal_list)
class Referal_list_Admin(admin.ModelAdmin):
    list_display = ('user', 'referal_user', 'create_date')
    search_fields = ['user__username']
     

@admin.register(Fund_User_Bonus)
class Fund_User_BonusAdmin(admin.ModelAdmin):
    list_display = ('username','amount','balance_before','balance_after')
    search_fields = ['username',]

@admin.register(Charge_referral_bonus)
class Charge_referral_bonusAdmin(admin.ModelAdmin):
    list_display = ('username','amount','pending_amount','balance_before','balance_after')
    search_fields = ['user__username',]


@admin.register(AppAdsImage)
class AppAdsImage_Admin(admin.ModelAdmin):
    list_display = ('route',)
    