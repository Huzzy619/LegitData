from django.urls import path
from . import views

urlpatterns = [
    path("validateiuc/", views.ValidateIUCAPIView.as_view()),
    path("validatemeter/", views.ValidateMeterAPIView.as_view()),
    path("data/<int:id>", views.DataAPIView.as_view()),
    path("data/", views.DataAPIListView.as_view()),
    path("topup/<int:id>", views.AirtimeTopupAPIView.as_view()),
    path("cablesub/", views.CableSubAPIListView.as_view()),
    path("cablesub/<int:id>", views.CableSubAPIView.as_view()),
    path("epin/<int:id>", views.Result_Checker_Pin_orderAPIView.as_view()),
    path("epin/", views.Result_Checker_Pin_orderAPIListView.as_view()),
    path("rechargepin/", views.Recharge_pin_orderAPIListView.as_view()),
    path("pin/", views.PINSETUPAPIView.as_view()),
    path("changepin/", views.PINCHANGEAPIView.as_view()),
    path("checkpin/", views.PINCCHECKAPIView.as_view()),
    path("resetpin/", views.PINRESETAPIView.as_view()),
    path("billpayment/", views.BillPaymentAPIListView.as_view()),
    path("billpayment/<int:id>", views.BillPaymentAPIView.as_view()),
    path("topup/", views.AirtimeTopupAPIListView.as_view()),
    path("couponpayment/", views.CouponPaymentAPIView.as_view()),
    path("Airtime_funding/", views.Airtime_fundingAPIView.as_view()),
    path("users/", views.UserListView.as_view()),
    path("history/", views.Api_History.as_view()),
    path("user/", views.UserAPIView.as_view()),
    path("kyc/", views.KYCAPIView.as_view()),
    path("transfer/", views.TransferAPIView.as_view()),
    path("bonus_transfer/", views.bonus_transferAPIView.as_view()),
    # new urls
    path("withdraw/", views.WithdrawAPIView.as_view()),
    path("Wallet_summary/", views.Wallet_summaryListView.as_view()),
    path("referal/", views.ReferalListView.as_view()),
    path("alert/", views.AlertAPIView.as_view()),
    path("network/", views.NetworkAPIView.as_view()),
    path("cable/", views.CablenameAPIView.as_view()),
    path("disco/", views.DiscoAPIView.as_view()),
    path("registration/", views.CustomUserCreate.as_view()),
    path("passwordchange/", views.PasswordChangeAPIView.as_view()),
    path("get/network/", views.GetNetworkAPIView.as_view()),
    path("upgrade/", views.UpgradeUserAPIView.as_view()),
    path("bank_notification/", views.BankpaymentAPIView.as_view()),
    path("rta/", views.RetailerWebsiteAPI.as_view()),
    path("available_recharge", views.available_recharge.as_view()),
    path("verification", views.VerificationEmailAPIView.as_view()),
    path("sendsms/", views.BulkSmsAPIView.as_view()),
    path("sms/", views.BulkSmsAPIListView.as_view()),

]