import notifications.urls
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
from .views_list import managementviews  
 
urlpatterns = [
    path("", views.WelcomeView.as_view(), name="home"),
    path(
        "activate/(P<uidb64>[0-9A-Za-z_\-]+)/(P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/",
        views.activate,
        name="activate",
    ),
    path("admin2/", TemplateView.as_view(template_name="admin.html")),
    path("super-admin/", TemplateView.as_view(template_name="admin2.html")),
    path("500/server-error/page/", TemplateView.as_view(template_name="500.html")),
    path("403/bad-request-error/page/", TemplateView.as_view(template_name="403.html")),
    path("404/page-not-found-error/page/", TemplateView.as_view(template_name="admin.html")),
    
    path("uws/webhook/", views.UWS_Webhook),
    path("vtpass/webhook/", views.Vtpass_Webhook),
    path("smeplug/webook/", views.Smeplug_Webhook),

    path("csv/", views.user_csv, name="csv"),
    path(
        "Data_History_new/",
        login_required(views.Data_History_new),
        name="data_history_new",
    ),
    # path('retailer_faq/',login_required(TemplateView.as_view(template_name='faq2.html')),name='faq2'),
    path("retailer_faq/", login_required(views.RetailWebFaqs), name="faq2"),
    path(
        "topuser/", login_required(views.TopuserWebsiteview.as_view()), name="topuser"
    ),
    path(
        "Recharge-Pin-order/",
        login_required(views.Recharge_pin_order_view.as_view()),
        name="recharge",
    ),
    path(
        "Recharge-Pin-order/<int:pk>/",
        login_required(views.Recharge_pin_order_success.as_view()),
        name="recharge_success",
    ),
    path("paymentpage/", login_required(views.Paymentpage), name="paymentpage"),
    path("kyc/", login_required(views.KYCCreate.as_view()), name="kyc"),
    # path('ajax/Generate_Result_checker/', login_required(views.Generate_Result_checker), name='generate_pin'),
    path("ajax/validate_iuc/", views.validate_iuc, name="validate_iuc"),
    path(
        "ajax/validate_meter_number/",
        views.validate_meter_number,
        name="validate_meter_number",
    ),
    path("payonlinedone/", views.payonlinedone, name="payonlinedone"),
    path("replybot/", views.replybot, name="replybot"),
    path("ussdcallback/", views.ussdcallback, name="ussdcallback"),
    path("ajax/Affilliate/", login_required(views.Affilliate), name="Affilliate"),
    path("ajax/Topuser/", login_required(views.Topuser), name="Topuser"),
    path("payonline/", login_required(views.paymentrave), name="pay"),
    path("flutterwavepaymentdone/", views.flutterwavepaymentdone, name="ravepaydone"),
    path(
        "flutterwavepayment/", login_required(views.flutterwavepayment), name="payrave"
    ),
    path("documentation/", login_required(views.ApiDoc.as_view()), name="doc"),
    path("autobank/", login_required(views.monnifypage), name="monnifypage"),
    # path('ajax/validate_username/', views.validate_iuc_number, name='validate_iuc_number'),
    path(
        "transfer-bonus/",
        login_required(views.bonus_transferCreate.as_view()),
        name="bonus",
    ),
    path("ebook-library/", views.BookList.as_view(), name="book_list_by_category"),
    path(
        "ebook-library/<slug:slug>/",
        login_required(views.BookDetail.as_view()),
        name="book_detail",
    ),
    path(
        "Result-Checker-Pin-order/",
        login_required(views.Result_Checker_Pin_order_view.as_view()),
        name="Result_Checker",
    ),
    path(
        "Result-Checker-Pin-order/<int:pk>/",
        login_required(views.Result_Checker_Pin_order_success.as_view()),
        name="checker_pin",
    ),
    path("newpost/", login_required(views.Postcreateview.as_view()), name="post"),
    path(
        "postedit/<slug:slug>/",
        login_required(views.Post_Edit.as_view()),
        name="post_edit",
    ),
    path("blog", views.PostList.as_view(), name="blog"),
    path("blog/<slug:slug>/", views.PostDetail.as_view(), name="post_detail"),
    path(
        "privacy/",
        login_required(TemplateView.as_view(template_name="privacy.html")),
        name="privacy",
    ),
    path("pricing/", login_required(views.PricingView.as_view()), name="pricing"),
    path("ravepaymentdone/", login_required(views.ravepaymentdone), name="rave"),
    path(
        "Cablesub_success/<int:pk>/",
        login_required(views.Cablesub_success.as_view()),
        name="cablesub_success",
    ),
    path(
        "Cablesub/", login_required(views.Cablesubscription.as_view()), name="cablesub"
    ),
    path(
        "bill_success/<int:pk>/",
        login_required(views.BillPayment_success.as_view()),
        name="bill_success",
    ),
    path("billpayment/", login_required(views.BillpaymentView.as_view()), name="bill"),
    path(
        "ajax/loadcableplans/",
        login_required(views.loadcableplans),
        name="ajax_loadcableplans",
    ),
    path("Bulk/", login_required(views.BulkCreate.as_view()), name="bulksms"),
    path(
        "Bulk_success/<int:pk>/",
        login_required(views.Bulk_success.as_view()),
        name="Bulk_success",
    ),
    # path('pay/',login_required(views.paymentgatewayCreate.as_view()),name ='pay'),
    path("referal/", login_required(views.referalView.as_view()), name="referal"),
    path("articles/comments/", include("django_comments.urls")),
    path("Users_Testimonial/", views.TestimonialView.as_view(), name="Testimonials"),
    path(
        "Notify_user/", login_required(views.Notify_User.as_view()), name="notify_user"
    ),
    path(
        "inbox/notifications/", include(notifications.urls, namespace="notifications")
    ),
    # path('FAQ/',TemplateView.as_view(template_name='faq.html'),name='faq'),
    path("FAQ/", login_required(views.Faqs), name="faq"),
    path("terms/", TemplateView.as_view(template_name="terms.html"), name="terms"),
    path(
        "Notifications/",
        login_required(views.NotificationView.as_view()),
        name="notification",
    ),
    path(
        "succesmessage/",
        TemplateView.as_view(template_name="succesmessage.html"),
        name="succesmessage.",
    ),
    path(
        "user-detail/",
        login_required(TemplateView.as_view(template_name="userdetails.html")),
        name="userdetails",
    ),
    path(
        "contact/", TemplateView.as_view(template_name="contact.html"), name="contact"
    ),
    path("about/", TemplateView.as_view(template_name="About.html"), name="about"),
    path(
        "Developer/", TemplateView.as_view(template_name="developer.html"), name="dev"
    ),
    path("signup/", views.SignUp.as_view(), name="signup"),
    path("EditProfile/", login_required(views.UserEdit.as_view()), name="Editprofile"),
    path(
        "airtime_create/", login_required(views.airtimeCreate.as_view()), name="airtime"
    ),
    path("airtime_list/", login_required(views.AirlisView.as_view()), name="airlist"),
    path(
        "Coupon_Payment/",
        login_required(views.CouponCodePayment.as_view()),
        name="Coupon",
    ),
    path("User/account_pin/", views.PinView.as_view(), name="pin"),
    path(
        "Airtime_funding/",
        login_required(views.Airtime_fundingCreate.as_view()),
        name="Airtime_funding",
    ),
    path(
        "withdraw_Create/",
        login_required(views.withdrawCreate.as_view()),
        name="withdraw",
    ),
    path("pay_with_monnify/", login_required(views.monnify_payment), name="monnify"),
    path(
        "monnify_payment_done/", views.monnify_payment_done, name="monnify_payment_done"
    ),
    path(
        "Wallet_Summary/", login_required(views.WalletSummaryView.as_view()), name="wallet"
    ),
    path("history/", login_required(views.History.as_view()), name="history"),
    path(
        "check-user-history/",
        login_required(views.UserHistory.as_view()),
        name="check_user_history",
    ),
    path("data_Create/", login_required(views.dataCreate.as_view()), name="data"),
    path(
        "Airtime_to_Data_tranfer/",
        login_required(views.Airtime_to_Data_tranfer_Create.as_view()),
        name="Airtime_to_Data_tranfer",
    ),
    path(
        "Airtime_to_Data/",
        login_required(views.Airtime_to_Data_Create.as_view()),
        name="Airtime_to_data",
    ),
    path(
        "Testimonial/",
        login_required(views.TestimonialCreate.as_view()),
        name="testimonial",
    ),
    path(
        "Testimonial_details/<int:pk>/",
        views.Testimonial_Detail.as_view(),
        name="testimonialdetail",
    ),
    path(
        "Testimonial_details/<int:pk>/new",
        login_required(views.TestimonialReply.as_view()),
        name="testimonialreply",
    ),
    path(
        "Testimonial/<int:pk>/reply/",
        login_required(views.add_comment_to_testimonial),
        name="add_comment_to_testimonial",
    ),
    path(
        "TransferCreate/",
        login_required(views.TransferCreate.as_view()),
        name="transfer",
    ),
    path(
        "AirtimeTopupCreate/",
        login_required(views.AirtimeTopupCreate.as_view()),
        name="topup",
    ),
    path(
        "AirtimeswapCreate/",
        login_required(views.AirtimeswapCreate.as_view()),
        name="swap",
    ),
    path("ajax/load_plans/", login_required(views.loadplans), name="ajax_load_plans"),
    path(
        "ajax/loadrechargeplans/",
        login_required(views.loadrechargeplans),
        name="ajax_loadrechargeplans",
    ),
    path(
        "ajax/load_plans_2/",
        login_required(views.loadplans_2),
        name="ajax_load_plans_2",
    ),
    path("profile/", login_required(views.Profile.as_view()), name="profile"),
    path(
        "Airtime_funding_success/<int:pk>/",
        login_required(views.Airtime_funding_success.as_view()),
        name="airtime_detail",
    ),
    path(
        "Coupon_success/<int:pk>/",
        login_required(views.Coupon_success.as_view()),
        name="Coupon_detail",
    ),
    path(
        "airtime_success/<int:pk>/",
        login_required(views.airtime_success.as_view()),
        name="airtime_success",
    ),
    path(
        "Airtimeswap_success/<int:pk>/",
        login_required(views.Airtimeswap_success.as_view()),
        name="Airtimeswap_success",
    ),
    path(
        "AirtimeTopup_success/<int:pk>/",
        login_required(views.AirtimeTopup_success.as_view()),
        name="AirtimeTopup_success",
    ),
    path(
        "Transfer_success/<int:pk>/",
        login_required(views.Transfer_success.as_view()),
        name="Transfer_detail",
    ),
    path(
        "Airtime_to_Data__success/<int:pk>/",
        login_required(views.Airtime_to_Data__success.as_view()),
        name="Airtime_to_Data_pin_success",
    ),
    path(
        "Data_success/<int:pk>/",
        login_required(views.Data_success.as_view()),
        name="Data_success",
    ),
    path(
        "Airtime_to_Data_tranfer_success/<int:pk>/",
        login_required(views.Airtime_to_Data_tranfer_success.as_view()),
        name="Airtime_to_Data_tranfer_success",
    ),
    path(
        "Withdraw_success/<int:pk>/",
        login_required(views.Withdraw_success.as_view()),
        name="Withdraw_success",
    ),
    path(
        "Coupon_success/<int:pk>/",
        login_required(views.Coupon_success.as_view()),
        name="Coupon_success",
    ),
    path(
        "Bankpayment/",
        login_required(views.BankpaymentCreate.as_view()),
        name="BankCreate",
    ),
    path(
        "Bankpayment/<int:pk>/",
        login_required(views.Bankpaymentsuccess.as_view()),
        name="Banksuccess",
    ),
    path("Buybitcoin/", login_required(views.BuybtcCreate.as_view()), name="buybtc"),
    path("sellbitcoin/", login_required(views.SellbtcCreate.as_view()), name="sellbtc"),
    path(
        "Sellbitcoin/<int:pk>/success/",
        login_required(views.Sellbtc_success.as_view()),
        name="sell_btc_success",
    ),
    path(
        "Buybitcoin/<int:pk>/success/",
        login_required(views.Buybtc_success.as_view()),
        name="buy_btc_success",
    ),
    ########################MANAGEMENT VIEWS########################################
    path(
        "ajax/sales/account/",
        login_required(managementviews.salesAccount),
        name="sales-accounting",
    ),
    path(
        "verifyemail/",
        login_required(TemplateView.as_view(template_name="confirm_email.html")),
        name="confirmemail",
    ),
    path(
        "sendverificationlink/",
        login_required(views.sendverificationlink),
        name="sendverificationlink",
    ),
    path("self-service/", login_required(views.selfCenter), name="selfhelp"),
]


admin.site.site_title = "LegitData"
admin.site.site_header = "Welcome To LegitData Admin Panel"
