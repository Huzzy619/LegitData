
from django.db.models import Sum
from django.http import JsonResponse

from vtuapp.forms import *
from vtuapp.models import *
from nelly_api.serializers import *

# new import for webhook



def salesAccount(request):
    form_data = request.POST
    start_date = form_data["start_date"]
    end_date = form_data["end_date"]

    # Network.objects.get(name="MTN")
    # Network.objects.get(name="GLO")
    # Network.objects.get(name="9MOBILE")
    # Network.objects.get(name="AIRTEL")

    #######################################

    mtn_dataSold_total_SE_sme = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="MTN",
            plan__plan_type="SME",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    mtn_dataSold_total_AF_sme = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="MTN",
            plan__plan_type="SME",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    mtn_dataSold_total_TU_sme = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="MTN",
            plan__plan_type="SME",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    # mtn_dataSold_total_GO_sme = Data.objects.filter(user__user_type="Gold", network__name="MTN", plan__plan_type="SME",Status = "successful", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan_amount'))['plan_amount__sum'] or 0
    # mtn_dataSold_total_SI_sme = Data.objects.filter(user__user_type="Silver", network__name="MTN", plan__plan_type="SME",Status = "successful", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan_amount'))['plan_amount__sum'] or 0
    mtn_dataSold_total_API_sme = (
        Data.objects.filter(
            user__user_type="API",
            network__name="MTN",
            plan__plan_type="SME",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )

    mtn_dataSold_total_SE_gift = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="MTN",
            plan__plan_type="GIFTING",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    mtn_dataSold_total_AF_gift = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="MTN",
            plan__plan_type="GIFTING",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    mtn_dataSold_total_TU_gift = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="MTN",
            plan__plan_type="GIFTING",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    # mtn_dataSold_total_GO_gift = Data.objects.filter(user__user_type="Gold", network__name="MTN", plan__plan_type="GIFTING",Status = "successful", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan_amount'))['plan_amount__sum'] or 0
    # mtn_dataSold_total_SI_gift = Data.objects.filter(user__user_type="Silver", network__name="MTN", plan__plan_type="GIFTING",Status = "successful", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan_amount'))['plan_amount__sum'] or 0
    mtn_dataSold_total_API_gift = (
        Data.objects.filter(
            user__user_type="API",
            network__name="MTN",
            plan__plan_type="GIFTING",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )

    mtn_dataSold_total_SE_cg = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="MTN",
            plan__plan_type="CORPORATE GIFTING",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    mtn_dataSold_total_AF_cg = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="MTN",
            plan__plan_type="CORPORATE GIFTING",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    mtn_dataSold_total_TU_cg = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="MTN",
            plan__plan_type="CORPORATE GIFTING",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    # mtn_dataSold_total_GO_cg = Data.objects.filter(user__user_type="Gold", network__name="MTN", plan__plan_type="CORPORATE GIFTING",Status = "successful", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan_amount'))['plan_amount__sum'] or 0
    # mtn_dataSold_total_SI_cg = Data.objects.filter(user__user_type="Silver", network__name="MTN", plan__plan_type="CORPORATE GIFTING",Status = "successful", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan_amount'))['plan_amount__sum'] or 0
    mtn_dataSold_total_API_cg = (
        Data.objects.filter(
            user__user_type="API",
            network__name="MTN",
            plan__plan_type="CORPORATE GIFTING",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )

    airtel_dataSold_total_SE = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="AIRTEL",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    airtel_dataSold_total_AF = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="AIRTEL",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    airtel_dataSold_total_TU = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="AIRTEL",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    # airtel_dataSold_total_GO = Data.objects.filter(user__user_type="Gold", network__name="AIRTEL",Status = "successful", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan_amount'))['plan_amount__sum'] or 0
    # airtel_dataSold_total_SI = Data.objects.filter(user__user_type="Silver", network__name="AIRTEL",Status = "successful", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan_amount'))['plan_amount__sum'] or 0
    airtel_dataSold_total_API = (
        Data.objects.filter(
            user__user_type="API",
            network__name="AIRTEL",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )

    glo_dataSold_total_SE = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="GLO",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    glo_dataSold_total_AF = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="GLO",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    glo_dataSold_total_TU = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="GLO",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    # glo_dataSold_total_GO = Data.objects.filter(user__user_type="Gold", network__name="GLO",Status = "successful", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan_amount'))['plan_amount__sum'] or 0
    # glo_dataSold_total_SI = Data.objects.filter(user__user_type="Silver", network__name="GLO",Status = "successful", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan_amount'))['plan_amount__sum'] or 0
    glo_dataSold_total_API = (
        Data.objects.filter(
            user__user_type="API",
            network__name="GLO",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )

    eti_dataSold_total_SE = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="9MOBILE",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    eti_dataSold_total_AF = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="9MOBILE",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    eti_dataSold_total_TU = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="9MOBILE",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    # eti_dataSold_total_GO = Data.objects.filter(user__user_type="Gold", network__name="9MOBILE",Status = "successful", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan_amount'))['plan_amount__sum'] or 0
    # eti_dataSold_total_SI = Data.objects.filter(user__user_type="Silver", network__name="9MOBILE",Status = "successful", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan_amount'))['plan_amount__sum'] or 0
    eti_dataSold_total_API = (
        Data.objects.filter(
            user__user_type="API",
            network__name="9MOBILE",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )

    ###########################################

    mtn_dataSold_total = (
        Data.objects.filter(
            network__name="MTN",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    airtel_dataSold_total = (
        Data.objects.filter(
            network__name="AIRTEL",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    glo_dataSold_total = (
        Data.objects.filter(
            network__name="GLO",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    eti_dataSold_total = (
        Data.objects.filter(
            network__name="9MOBILE",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    smile_dataSold_total = (
        Data.objects.filter(
            network__name="SMILE",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )

    mtn_dataSold_total2 = (
        Data.objects.filter(
            network__name="MTN",
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    airtel_dataSold_total2 = (
        Data.objects.filter(
            network__name="AIRTEL",
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    glo_dataSold_total2 = (
        Data.objects.filter(
            network__name="GLO",
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    eti_dataSold_total2 = (
        Data.objects.filter(
            network__name="9MOBILE",
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    smile_dataSold_total2 = (
        Data.objects.filter(
            network__name="SMILE",
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )

    mtn_dataSold_total3 = (
        Data.objects.filter(
            network__name="MTN",
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    airtel_dataSold_total3 = (
        Data.objects.filter(
            network__name="AIRTEL",
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    glo_dataSold_total3 = (
        Data.objects.filter(
            network__name="GLO",
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    eti_dataSold_total3 = (
        Data.objects.filter(
            network__name="9MOBILE",
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    smile_dataSold_total3 = (
        Data.objects.filter(
            network__name="SMILE",
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )

    mtn_airtimeSold_total2 = (
        AirtimeTopup.objects.filter(
            network__name="MTN",
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    airtel_airtimeSold_total2 = (
        AirtimeTopup.objects.filter(
            network__name="AIRTEL",
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    glo_airtimeSold_total2 = (
        AirtimeTopup.objects.filter(
            network__name="GLO",
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    eti_airtimeSold_total2 = (
        AirtimeTopup.objects.filter(
            network__name="9MOBILE",
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )

    mtn_airtimeSold_total3 = (
        AirtimeTopup.objects.filter(
            network__name="MTN",
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    airtel_airtimeSold_total3 = (
        AirtimeTopup.objects.filter(
            network__name="AIRTEL",
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    glo_airtimeSold_total3 = (
        AirtimeTopup.objects.filter(
            network__name="GLO",
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    eti_airtimeSold_total3 = (
        AirtimeTopup.objects.filter(
            network__name="9MOBILE",
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )

    mtn_airtimeSold_total = (
        AirtimeTopup.objects.filter(
            network__name="MTN",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    airtel_airtimeSold_total = (
        AirtimeTopup.objects.filter(
            network__name="AIRTEL",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    glo_airtimeSold_total = (
        AirtimeTopup.objects.filter(
            network__name="GLO",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    eti_airtimeSold_total = (
        AirtimeTopup.objects.filter(
            network__name="9MOBILE",
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )

    (
        CustomUser.objects.all().aggregate(Sum("Account_Balance"))[
            "Account_Balance__sum"
        ]
        or 0
    )
    (
        CustomUser.objects.all().aggregate(Sum("Referer_Bonus"))["Referer_Bonus__sum"]
        or 0
    )
    total_bank_payments = (
        Bankpayment.objects.filter(
            Status="successful", create_date__date__range=[start_date, end_date]
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
    total_atm_payments = (
        paymentgateway.objects.filter(
            created_on__date__range=[start_date, end_date]
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
    total_coupon_payments = (
        CouponPayment.objects.all()
        .filter(create_date__date__range=[start_date, end_date])
        .aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
    bill_payment = (
        Billpayment.objects.filter(
            Status="successful", create_date__date__range=[start_date, end_date]
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    Cable_payment = (
        Cablesub.objects.filter(
            Status="successful", create_date__date__range=[start_date, end_date]
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    recharge_card = (
        Recharge_pin_order.objects.filter(
            create_date__date__range=[start_date, end_date]
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
    result_checker = (
        Result_Checker_Pin_order.objects.filter(
            create_date__date__range=[start_date, end_date]
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
    credit = (
        Transactions.objects.filter(
            create_date__date__range=[start_date, end_date], transaction_type="CREDIT"
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
    debit = (
        Transactions.objects.filter(
            create_date__date__range=[start_date, end_date], transaction_type="DEBIT"
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )

    gotv = (
        Cablesub.objects.filter(
            cablename=Cable.objects.get(name="GOTV"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    dstv = (
        Cablesub.objects.filter(
            cablename=Cable.objects.get(name="DSTV"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    startime = (
        Cablesub.objects.filter(
            cablename=Cable.objects.get(name="STARTIME"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )

    gotv2 = (
        Cablesub.objects.filter(
            cablename=Cable.objects.get(name="GOTV"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    dstv2 = (
        Cablesub.objects.filter(
            cablename=Cable.objects.get(name="DSTV"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    startime2 = (
        Cablesub.objects.filter(
            cablename=Cable.objects.get(name="STARTIME"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )

    gotv3 = (
        Cablesub.objects.filter(
            cablename=Cable.objects.get(name="GOTV"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    dstv3 = (
        Cablesub.objects.filter(
            cablename=Cable.objects.get(name="DSTV"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )
    startime3 = (
        Cablesub.objects.filter(
            cablename=Cable.objects.get(name="STARTIME"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan_amount"))["plan_amount__sum"]
        or 0
    )

    d1 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="IKEDC"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    d2 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="EKEDC"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    d3 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="AEDC"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    d4 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="IBEDC"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    d5 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="KEDC"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    d6 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="EEDC"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    d7 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="PHEDC"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    d8 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="KAEDC"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    d9 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="JEDC"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    d10 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="BEDC"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    d11 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="YEDC"),
            Status="successful",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )

    e1 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="IKEDC"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    e2 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="EKEDC"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    e3 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="AEDC"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    e4 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="IBEDC"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    e5 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="KEDC"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    e6 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="EEDC"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    e7 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="PHEDC"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    e8 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="KAEDC"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    e9 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="JEDC"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    e10 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="BEDC"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    e11 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="YEDC"),
            Status="processing",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )

    f1 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="IKEDC"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    f2 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="EKEDC"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    f3 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="AEDC"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    f4 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="IBEDC"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    f5 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="KEDC"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    f6 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="EEDC"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    f7 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="PHEDC"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    f8 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="KAEDC"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    f9 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="JEDC"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    f10 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="BEDC"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )
    f11 = (
        Billpayment.objects.filter(
            disco_name=Disco_provider_name.objects.get(p_id="YEDC"),
            Status="failed",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("paid_amount"))["paid_amount__sum"]
        or 0
    )

    ##########################
    SE_sme_data_mtn_obj = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="MTN",
            plan__plan_type="SME",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    SE_sme_data_mtn_obj_2 = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="MTN",
            plan__plan_type="SME",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    AF_sme_data_mtn_obj = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="MTN",
            plan__plan_type="SME",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    AF_sme_data_mtn_obj_2 = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="MTN",
            plan__plan_type="SME",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    TU_sme_data_mtn_obj = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="MTN",
            plan__plan_type="SME",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    TU_sme_data_mtn_obj_2 = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="MTN",
            plan__plan_type="SME",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    # GO_sme_data_mtn_obj = Data.objects.filter(user__user_type="Gold", network__name="MTN", plan__plan_type="SME", Status = "successful",plan__plan_Volume = "GB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # GO_sme_data_mtn_obj_2 = Data.objects.filter(user__user_type="Gold", network__name="MTN", plan__plan_type="SME", Status = "successful", plan__plan_Volume = "MB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0

    # SI_sme_data_mtn_obj = Data.objects.filter(user__user_type="Silver", network__name="MTN", plan__plan_type="SME", Status = "successful",plan__plan_Volume = "GB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # SI_sme_data_mtn_obj_2 = Data.objects.filter(user__user_type="Silver", network__name="MTN", plan__plan_type="SME", Status = "successful", plan__plan_Volume = "MB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0

    API_sme_data_mtn_obj = (
        Data.objects.filter(
            user__user_type="API",
            network__name="MTN",
            plan__plan_type="SME",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    API_sme_data_mtn_obj_2 = (
        Data.objects.filter(
            user__user_type="API",
            network__name="MTN",
            plan__plan_type="SME",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    SE_gift_data_mtn_obj = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="MTN",
            plan__plan_type="GIFTING",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    SE_gift_data_mtn_obj_2 = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="MTN",
            plan__plan_type="GIFTING",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    AF_gift_data_mtn_obj = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="MTN",
            plan__plan_type="GIFTING",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    AF_gift_data_mtn_obj_2 = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="MTN",
            plan__plan_type="GIFTING",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    TU_gift_data_mtn_obj = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="MTN",
            plan__plan_type="GIFTING",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    TU_gift_data_mtn_obj_2 = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="MTN",
            plan__plan_type="GIFTING",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    # GO_gift_data_mtn_obj = Data.objects.filter(user__user_type="Gold", network__name="MTN", plan__plan_type="GIFTING", Status = "successful",plan__plan_Volume = "GB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # GO_gift_data_mtn_obj_2 = Data.objects.filter(user__user_type="Gold", network__name="MTN", plan__plan_type="GIFTING", Status = "successful", plan__plan_Volume = "MB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0

    # SI_gift_data_mtn_obj = Data.objects.filter(user__user_type="Silver", network__name="MTN", plan__plan_type="GIFTING", Status = "successful",plan__plan_Volume = "GB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # SI_gift_data_mtn_obj_2 = Data.objects.filter(user__user_type="Silver", network__name="MTN", plan__plan_type="GIFTING", Status = "successful", plan__plan_Volume = "MB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0

    API_gift_data_mtn_obj = (
        Data.objects.filter(
            user__user_type="API",
            network__name="MTN",
            plan__plan_type="GIFTING",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    API_gift_data_mtn_obj_2 = (
        Data.objects.filter(
            user__user_type="API",
            network__name="MTN",
            plan__plan_type="GIFTING",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    SE_cg_data_mtn_obj = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="MTN",
            plan__plan_type="CORPORATE GIFTING",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    SE_cg_data_mtn_obj_2 = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="MTN",
            plan__plan_type="CORPORATE GIFTING",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    AF_cg_data_mtn_obj = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="MTN",
            plan__plan_type="CORPORATE GIFTING",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    AF_cg_data_mtn_obj_2 = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="MTN",
            plan__plan_type="CORPORATE GIFTING",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    TU_cg_data_mtn_obj = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="MTN",
            plan__plan_type="CORPORATE GIFTING",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    TU_cg_data_mtn_obj_2 = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="MTN",
            plan__plan_type="CORPORATE GIFTING",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    # GO_cg_data_mtn_obj = Data.objects.filter(user__user_type="Gold", network__name="MTN", plan__plan_type="CORPORATE GIFTING", Status = "successful",plan__plan_Volume = "GB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # GO_cg_data_mtn_obj_2 = Data.objects.filter(user__user_type="Gold", network__name="MTN", plan__plan_type="CORPORATE GIFTING", Status = "successful", plan__plan_Volume = "MB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0

    # SI_cg_data_mtn_obj = Data.objects.filter(user__user_type="Silver", network__name="MTN", plan__plan_type="CORPORATE GIFTING", Status = "successful",plan__plan_Volume = "GB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # SI_cg_data_mtn_obj_2 = Data.objects.filter(user__user_type="Silver", network__name="MTN", plan__plan_type="CORPORATE GIFTING", Status = "successful", plan__plan_Volume = "MB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0

    API_cg_data_mtn_obj = (
        Data.objects.filter(
            user__user_type="API",
            network__name="MTN",
            plan__plan_type="CORPORATE GIFTING",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    API_cg_data_mtn_obj_2 = (
        Data.objects.filter(
            user__user_type="API",
            network__name="MTN",
            plan__plan_type="CORPORATE GIFTING",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    SE_data_airtel_obj = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="AIRTEL",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    SE_data_airtel_obj_2 = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="AIRTEL",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    AF_data_airtel_obj = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="AIRTEL",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    AF_data_airtel_obj_2 = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="AIRTEL",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    TU_data_airtel_obj = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="AIRTEL",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    TU_data_airtel_obj_2 = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="AIRTEL",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    # GO_data_airtel_obj = Data.objects.filter(user__user_type="Gold", network__name="AIRTEL", Status = "successful",plan__plan_Volume = "GB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # GO_data_airtel_obj_2 = Data.objects.filter(user__user_type="Gold", network__name="AIRTEL", Status = "successful", plan__plan_Volume = "MB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # SI_data_airtel_obj = Data.objects.filter(user__user_type="Silver", network__name="AIRTEL", Status = "successful",plan__plan_Volume = "GB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # SI_data_airtel_obj_2 = Data.objects.filter(user__user_type="Silver", network__name="AIRTEL", Status = "successful", plan__plan_Volume = "MB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    API_data_airtel_obj = (
        Data.objects.filter(
            user__user_type="API",
            network__name="AIRTEL",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    API_data_airtel_obj_2 = (
        Data.objects.filter(
            user__user_type="API",
            network__name="AIRTEL",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    SE_data_glo_obj = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="GLO",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    SE_data_glo_obj_2 = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="GLO",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    AF_data_glo_obj = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="GLO",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    AF_data_glo_obj_2 = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="GLO",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    TU_data_glo_obj = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="GLO",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    TU_data_glo_obj_2 = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="GLO",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    # GO_data_glo_obj = Data.objects.filter(user__user_type="Gold", network__name="GLO", Status = "successful",plan__plan_Volume = "GB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # GO_data_glo_obj_2 = Data.objects.filter(user__user_type="Gold", network__name="GLO", Status = "successful", plan__plan_Volume = "MB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # SI_data_glo_obj = Data.objects.filter(user__user_type="Silver", network__name="GLO", Status = "successful",plan__plan_Volume = "GB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # SI_data_glo_obj_2 = Data.objects.filter(user__user_type="Silver", network__name="GLO", Status = "successful", plan__plan_Volume = "MB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    API_data_glo_obj = (
        Data.objects.filter(
            user__user_type="API",
            network__name="GLO",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    API_data_glo_obj_2 = (
        Data.objects.filter(
            user__user_type="API",
            network__name="GLO",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    SE_data_9mobile_obj = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="9MOBILE",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    SE_data_9mobile_obj_2 = (
        Data.objects.filter(
            user__user_type="Smart Earner",
            network__name="9MOBILE",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    AF_data_9mobile_obj = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="9MOBILE",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    AF_data_9mobile_obj_2 = (
        Data.objects.filter(
            user__user_type="Affilliate",
            network__name="9MOBILE",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    TU_data_9mobile_obj = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="9MOBILE",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    TU_data_9mobile_obj_2 = (
        Data.objects.filter(
            user__user_type="TopUser",
            network__name="9MOBILE",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    # GO_data_9mobile_obj = Data.objects.filter(user__user_type="Gold", network__name="9MOBILE", Status = "successful",plan__plan_Volume = "GB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # GO_data_9mobile_obj_2 = Data.objects.filter(user__user_type="Gold", network__name="9MOBILE", Status = "successful", plan__plan_Volume = "MB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # SI_data_9mobile_obj = Data.objects.filter(user__user_type="Silver", network__name="9MOBILE", Status = "successful",plan__plan_Volume = "GB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    # SI_data_9mobile_obj_2 = Data.objects.filter(user__user_type="Silver", network__name="9MOBILE", Status = "successful", plan__plan_Volume = "MB", create_date__date__range=[start_date, end_date]).aggregate(Sum('plan__plan_size'))['plan__plan_size__sum'] or 0
    API_data_9mobile_obj = (
        Data.objects.filter(
            user__user_type="API",
            network__name="9MOBILE",
            Status="successful",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    API_data_9mobile_obj_2 = (
        Data.objects.filter(
            user__user_type="API",
            network__name="9MOBILE",
            Status="successful",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    ##########################

    data_mtn_obj = (
        Data.objects.filter(
            Status="successful",
            network__name="MTN",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    data_mtn_obj_2 = (
        Data.objects.filter(
            Status="successful",
            network__name="MTN",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    data_glo_obj = (
        Data.objects.filter(
            Status="successful",
            network__name="GLO",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    data_glo_obj_2 = (
        Data.objects.filter(
            Status="successful",
            network__name="GLO",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    data_9mobile_obj = (
        Data.objects.filter(
            Status="successful",
            network__name="9MOBILE",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    data_9mobile_obj_2 = (
        Data.objects.filter(
            Status="successful",
            network__name="9MOBILE",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    data_airtel_obj = (
        Data.objects.filter(
            Status="successful",
            network__name="AIRTEL",
            plan__plan_Volume="GB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )
    data_airtel_obj_2 = (
        Data.objects.filter(
            Status="successful",
            network__name="AIRTEL",
            plan__plan_Volume="MB",
            create_date__date__range=[start_date, end_date],
        ).aggregate(Sum("plan__plan_size"))["plan__plan_size__sum"]
        or 0
    )

    total_SE_sme = str(
        "{:,}".format(round(mtn_dataSold_total_SE_sme, 2))
        + " ( "
        + str(round((SE_sme_data_mtn_obj) + (SE_sme_data_mtn_obj_2 / 1000), 2))
    )
    total_AF_sme = str(
        "{:,}".format(round(mtn_dataSold_total_AF_sme, 2))
        + " ( "
        + str(round((AF_sme_data_mtn_obj) + (AF_sme_data_mtn_obj_2 / 1000), 2))
    )
    total_TU_sme = str(
        "{:,}".format(round(mtn_dataSold_total_TU_sme, 2))
        + " ( "
        + str(round((TU_sme_data_mtn_obj) + (TU_sme_data_mtn_obj_2 / 1000), 2))
    )
    # total_GO_sme = str("{:,}".format(round(mtn_dataSold_total_GO_sme,2))+ " ( " + str (round((GO_sme_data_mtn_obj) + (GO_sme_data_mtn_obj_2/1000),2)))
    # total_SI_sme = str("{:,}".format(round(mtn_dataSold_total_SI_sme,2))+ " ( " + str (round((SI_sme_data_mtn_obj) + (SI_sme_data_mtn_obj_2/1000),2)))
    total_API_sme = str(
        "{:,}".format(round(mtn_dataSold_total_API_sme, 2))
        + " ( "
        + str(round((API_sme_data_mtn_obj) + (API_sme_data_mtn_obj_2 / 1000), 1))
    )

    mtnprice_sme = "{:,}".format(
        round(
            mtn_dataSold_total_SE_sme
            + mtn_dataSold_total_AF_sme
            + mtn_dataSold_total_TU_sme
            + mtn_dataSold_total_API_sme,
            2,
        )
    )
    mtnsize_sme = (
        round((SE_sme_data_mtn_obj) + (SE_sme_data_mtn_obj_2 / 1000), 2)
        + round((AF_sme_data_mtn_obj) + (AF_sme_data_mtn_obj_2 / 1000), 2)
        + round((TU_sme_data_mtn_obj) + (TU_sme_data_mtn_obj_2 / 1000), 2)
        + round((API_sme_data_mtn_obj) + (API_sme_data_mtn_obj_2 / 1000), 2)
    )

    # mtnprice_sme = "{:,}".format(round(mtn_dataSold_total_SE_sme + mtn_dataSold_total_AF_sme + mtn_dataSold_total_TU_sme + mtn_dataSold_total_GO_sme + mtn_dataSold_total_SI_sme + mtn_dataSold_total_API_sme,2))
    # mtnsize_sme = round((SE_sme_data_mtn_obj) + (SE_sme_data_mtn_obj_2/1000),2) + round((AF_sme_data_mtn_obj) + (AF_sme_data_mtn_obj_2/1000),2) + round((TU_sme_data_mtn_obj) + (TU_sme_data_mtn_obj_2/1000),2) + round((GO_sme_data_mtn_obj) + (GO_sme_data_mtn_obj_2/1000),2) + round((SI_sme_data_mtn_obj) + (SI_sme_data_mtn_obj_2/1000),2) + round((API_sme_data_mtn_obj) + (API_sme_data_mtn_obj_2/1000),2)

    total_SE_gift = (
        str(
            "{:,}".format(round(mtn_dataSold_total_SE_gift, 2))
            + " ( "
            + str(round((SE_gift_data_mtn_obj) + (SE_gift_data_mtn_obj_2 / 1000), 2))
        ),
    )
    total_AF_gift = (
        str(
            "{:,}".format(round(mtn_dataSold_total_AF_gift, 2))
            + " ( "
            + str(round((AF_gift_data_mtn_obj) + (AF_gift_data_mtn_obj_2 / 1000), 2))
        ),
    )
    total_TU_gift = (
        str(
            "{:,}".format(round(mtn_dataSold_total_TU_gift, 2))
            + " ( "
            + str(round((TU_gift_data_mtn_obj) + (TU_gift_data_mtn_obj_2 / 1000), 2))
        ),
    )
    # total_GO_gift = str("{:,}".format(round(mtn_dataSold_total_GO_gift,2))+ " ( " + str (round((GO_gift_data_mtn_obj) + (GO_gift_data_mtn_obj_2/1000),2))),
    # total_SI_gift = str("{:,}".format(round(mtn_dataSold_total_SI_gift,2))+ " ( " + str (round((SI_gift_data_mtn_obj) + (SI_gift_data_mtn_obj_2/1000),2))),
    total_API_gift = (
        str(
            "{:,}".format(round(mtn_dataSold_total_API_gift, 2))
            + " ( "
            + str(round((API_gift_data_mtn_obj) + (API_gift_data_mtn_obj_2 / 1000), 2))
        ),
    )

    mtnprice_gift = "{:,}".format(
        round(
            mtn_dataSold_total_SE_gift
            + mtn_dataSold_total_AF_gift
            + mtn_dataSold_total_TU_gift
            + mtn_dataSold_total_API_gift,
            2,
        )
    )
    mtnsize_gift = (
        round((SE_gift_data_mtn_obj) + (SE_gift_data_mtn_obj_2 / 1000), 2)
        + round((AF_gift_data_mtn_obj) + (AF_gift_data_mtn_obj_2 / 1000), 2)
        + round((TU_gift_data_mtn_obj) + (TU_gift_data_mtn_obj_2 / 1000), 2)
        + round((API_gift_data_mtn_obj) + (API_gift_data_mtn_obj_2 / 1000), 2)
    )

    # mtnprice_gift = "{:,}".format(round(mtn_dataSold_total_SE_gift + mtn_dataSold_total_AF_gift + mtn_dataSold_total_TU_gift + mtn_dataSold_total_GO_gift + mtn_dataSold_total_SI_gift + mtn_dataSold_total_API_gift,2))
    # mtnsize_gift = round((SE_gift_data_mtn_obj) + (SE_gift_data_mtn_obj_2/1000),2) + round((AF_gift_data_mtn_obj) + (AF_gift_data_mtn_obj_2/1000),2) + round((TU_gift_data_mtn_obj) + (TU_gift_data_mtn_obj_2/1000),2) + round((GO_gift_data_mtn_obj) + (GO_gift_data_mtn_obj_2/1000),2) + round((SI_gift_data_mtn_obj) + (SI_gift_data_mtn_obj_2/1000),2) + round((API_gift_data_mtn_obj) + (API_gift_data_mtn_obj_2/1000),2)

    total_SE_cg = (
        str(
            "{:,}".format(round(mtn_dataSold_total_SE_cg, 2))
            + " ( "
            + str(round((SE_cg_data_mtn_obj) + (SE_cg_data_mtn_obj_2 / 1000), 2))
        ),
    )
    total_AF_cg = (
        str(
            "{:,}".format(round(mtn_dataSold_total_AF_cg, 2))
            + " ( "
            + str(round((AF_cg_data_mtn_obj) + (AF_cg_data_mtn_obj_2 / 1000), 2))
        ),
    )
    total_TU_cg = (
        str(
            "{:,}".format(round(mtn_dataSold_total_TU_cg, 2))
            + " ( "
            + str(round((TU_cg_data_mtn_obj) + (TU_cg_data_mtn_obj_2 / 1000), 2))
        ),
    )
    # total_GO_cg = str("{:,}".format(round(mtn_dataSold_total_GO_cg,2))+ " ( " + str (round((GO_cg_data_mtn_obj) + (GO_cg_data_mtn_obj_2/1000),2))),
    # total_SI_cg = str("{:,}".format(round(mtn_dataSold_total_SI_cg,2))+ " ( " + str (round((SI_cg_data_mtn_obj) + (SI_cg_data_mtn_obj_2/1000),2))),
    total_API_cg = (
        str(
            "{:,}".format(round(mtn_dataSold_total_API_cg, 2))
            + " ( "
            + str(round((API_cg_data_mtn_obj) + (API_cg_data_mtn_obj_2 / 1000), 2))
        ),
    )

    mtnprice_cg = "{:,}".format(
        round(
            mtn_dataSold_total_SE_cg
            + mtn_dataSold_total_AF_cg
            + mtn_dataSold_total_TU_cg
            + mtn_dataSold_total_API_cg,
            2,
        )
    )
    mtnsize_cg = (
        round((SE_cg_data_mtn_obj) + (SE_cg_data_mtn_obj_2 / 1000), 2)
        + round((AF_cg_data_mtn_obj) + (AF_cg_data_mtn_obj_2 / 1000), 2)
        + round((TU_cg_data_mtn_obj) + (TU_cg_data_mtn_obj_2 / 1000), 2)
        + round((API_cg_data_mtn_obj) + (API_cg_data_mtn_obj_2 / 1000), 2)
    )

    # mtnprice_cg = "{:,}".format(round(mtn_dataSold_total_SE_cg + mtn_dataSold_total_AF_cg + mtn_dataSold_total_TU_cg + mtn_dataSold_total_GO_cg + mtn_dataSold_total_SI_cg + mtn_dataSold_total_API_cg,2))
    # mtnsize_cg = round((SE_cg_data_mtn_obj) + (SE_cg_data_mtn_obj_2/1000),2) + round((AF_cg_data_mtn_obj) + (AF_cg_data_mtn_obj_2/1000),2) + round((TU_cg_data_mtn_obj) + (TU_cg_data_mtn_obj_2/1000),2) + round((GO_cg_data_mtn_obj) + (GO_cg_data_mtn_obj_2/1000),2) + round((SI_cg_data_mtn_obj) + (SI_cg_data_mtn_obj_2/1000),2) + round((API_cg_data_mtn_obj) + (API_cg_data_mtn_obj_2/1000),2)

    if request.method == "POST":
        return JsonResponse(
            {
                #####################
                "mtn_dataSold_total_SE_sme": total_SE_sme,
                "mtn_dataSold_total_AF_sme": total_AF_sme,
                "mtn_dataSold_total_TU_sme": total_TU_sme,
                # "mtn_dataSold_total_GO_sme": total_GO_sme,
                # "mtn_dataSold_total_SI_sme": total_SI_sme,
                "mtn_dataSold_total_API_sme": total_API_sme,
                "mtn_dataSold_total_TOTAL_sme": f"{mtnprice_sme} ({mtnsize_sme})",
                "mtn_dataSold_total_SE_gift": total_SE_gift,
                "mtn_dataSold_total_AF_gift": total_AF_gift,
                "mtn_dataSold_total_TU_gift": total_TU_gift,
                # "mtn_dataSold_total_GO_gift": total_GO_gift,
                # "mtn_dataSold_total_SI_gift": total_SI_gift,
                "mtn_dataSold_total_API_gift": total_API_gift,
                "mtn_dataSold_total_TOTAL_gift": f"{mtnprice_gift} ({mtnsize_gift})",
                "mtn_dataSold_total_SE_cg": total_SE_cg,
                "mtn_dataSold_total_AF_cg": total_AF_cg,
                "mtn_dataSold_total_TU_cg": total_TU_cg,
                # "mtn_dataSold_total_GO_cg": total_GO_cg,
                # "mtn_dataSold_total_SI_cg": total_SI_cg,
                "mtn_dataSold_total_API_cg": total_API_cg,
                "mtn_dataSold_total_TOTAL_cg": f"{mtnprice_cg} ({mtnsize_cg})",
                "airtel_dataSold_total_SE": str(
                    "{:,}".format(round(airtel_dataSold_total_SE, 2))
                    + " ( "
                    + str(
                        round((SE_data_airtel_obj) + (SE_data_airtel_obj_2 / 1000), 2)
                    )
                ),
                "airtel_dataSold_total_AF": str(
                    "{:,}".format(round(airtel_dataSold_total_AF, 2))
                    + " ( "
                    + str(
                        round((AF_data_airtel_obj) + (AF_data_airtel_obj_2 / 1000), 2)
                    )
                ),
                "airtel_dataSold_total_TU": str(
                    "{:,}".format(round(airtel_dataSold_total_TU, 2))
                    + " ( "
                    + str(
                        round((TU_data_airtel_obj) + (TU_data_airtel_obj_2 / 1000), 2)
                    )
                ),
                # "airtel_dataSold_total_GO": str("{:,}".format(round(airtel_dataSold_total_GO,2))+ " ( " + str (round((GO_data_airtel_obj) + (GO_data_airtel_obj_2/1000),2))),
                # "airtel_dataSold_total_SI": str("{:,}".format(round(airtel_dataSold_total_SI,2))+ " ( " + str (round((SI_data_airtel_obj) + (SI_data_airtel_obj_2/1000),2))),
                "airtel_dataSold_total_API": str(
                    "{:,}".format(round(airtel_dataSold_total_API, 2))
                    + " ( "
                    + str(
                        round((API_data_airtel_obj) + (API_data_airtel_obj_2 / 1000), 2)
                    )
                ),
                "glo_dataSold_total_SE": str(
                    "{:,}".format(round(glo_dataSold_total_SE, 2))
                    + " ( "
                    + str(round((SE_data_glo_obj) + (SE_data_glo_obj_2 / 1000), 2))
                ),
                "glo_dataSold_total_AF": str(
                    "{:,}".format(round(glo_dataSold_total_AF, 2))
                    + " ( "
                    + str(round((AF_data_glo_obj) + (AF_data_glo_obj_2 / 1000), 2))
                ),
                "glo_dataSold_total_TU": str(
                    "{:,}".format(round(glo_dataSold_total_TU, 2))
                    + " ( "
                    + str(round((TU_data_glo_obj) + (TU_data_glo_obj_2 / 1000), 2))
                ),
                # "glo_dataSold_total_GO": str("{:,}".format(round(glo_dataSold_total_GO,2))+ " ( " + str (round((GO_data_glo_obj) + (GO_data_glo_obj_2/1000),2))),
                # "glo_dataSold_total_SI": str("{:,}".format(round(glo_dataSold_total_SI,2))+ " ( " + str (round((SI_data_glo_obj) + (SI_data_glo_obj_2/1000),2))),
                "glo_dataSold_total_API": str(
                    "{:,}".format(round(glo_dataSold_total_API, 2))
                    + " ( "
                    + str(round((API_data_glo_obj) + (API_data_glo_obj_2 / 1000), 2))
                ),
                "eti_dataSold_total_SE": str(
                    "{:,}".format(round(eti_dataSold_total_SE, 2))
                    + " ( "
                    + str(
                        round((SE_data_9mobile_obj) + (SE_data_9mobile_obj_2 / 1000), 2)
                    )
                ),
                "eti_dataSold_total_AF": str(
                    "{:,}".format(round(eti_dataSold_total_AF, 2))
                    + " ( "
                    + str(
                        round((AF_data_9mobile_obj) + (AF_data_9mobile_obj_2 / 1000), 2)
                    )
                ),
                "eti_dataSold_total_TU": str(
                    "{:,}".format(round(eti_dataSold_total_TU, 2))
                    + " ( "
                    + str(
                        round((TU_data_9mobile_obj) + (TU_data_9mobile_obj_2 / 1000), 2)
                    )
                ),
                # "eti_dataSold_total_GO":  str("{:,}".format(round(eti_dataSold_total_GO,2))+ " ( " + str (round((GO_data_9mobile_obj) + (GO_data_9mobile_obj_2/1000),2))) ,
                # "eti_dataSold_total_SI":  str("{:,}".format(round(eti_dataSold_total_SI,2))+ " ( " + str (round((SI_data_9mobile_obj) + (SI_data_9mobile_obj_2/1000),2))) ,
                "eti_dataSold_total_API": str(
                    "{:,}".format(round(eti_dataSold_total_API, 2))
                    + " ( "
                    + str(
                        round(
                            (API_data_9mobile_obj) + (API_data_9mobile_obj_2 / 1000), 2
                        )
                    )
                ),
                #####################
                "mtn_dataSold_total": str(
                    "{:,}".format(round(mtn_dataSold_total, 2))
                    + " ( "
                    + str(round((data_mtn_obj) + (data_mtn_obj_2 / 1000), 2))
                ),
                "glo_dataSold_total": str(
                    "{:,}".format(round(glo_dataSold_total, 2))
                    + " ( "
                    + str(round((data_glo_obj) + (data_glo_obj_2 / 1000), 2))
                ),
                "airtel_dataSold_total": str(
                    "{:,}".format(round(airtel_dataSold_total, 2))
                    + " ("
                    + str(round((data_airtel_obj) + (data_airtel_obj_2 / 1000), 2))
                ),
                "eti_dataSold_total": str(
                    "{:,}".format(round(eti_dataSold_total, 2))
                    + " ("
                    + str(round((data_9mobile_obj) + (data_9mobile_obj_2 / 1000), 2))
                ),
                #############
                "mtn_airtimeSold_total": "{:,}".format(round(mtn_airtimeSold_total, 2)),
                "glo_airtimeSold_total": "{:,}".format(round(glo_airtimeSold_total, 2)),
                "airtel_airtimeSold_total": "{:,}".format(
                    round(airtel_airtimeSold_total, 2)
                ),
                "eti_airtimeSold_total": "{:,}".format(round(eti_airtimeSold_total, 2)),
                ###########
                "total_bank_payments": "{:,}".format(round(total_bank_payments, 2)),
                "bill_payment": "{:,}".format(round(bill_payment, 2)),
                "Cable_payment": "{:,}".format(round(Cable_payment, 2)),
                "total_atm_payments": "{:,}".format(round(total_atm_payments, 2)),
                "total_coupon_payments": "{:,}".format(round(total_coupon_payments, 2)),
                "smile_dataSold_total": "{:,}".format(round(smile_dataSold_total, 2)),
                "result_checker": "{:,}".format(round(result_checker, 2)),
                "recharge_card": "{:,}".format(round(recharge_card, 2)),
                "debit": "{:,}".format(round(debit, 2)),
                "credit": "{:,}".format(round(credit, 2)),
                "data_list": [
                    mtn_dataSold_total,
                    glo_dataSold_total,
                    airtel_dataSold_total,
                    eti_dataSold_total,
                    smile_dataSold_total,
                ],
                "data_list2": [
                    mtn_dataSold_total2,
                    glo_dataSold_total2,
                    airtel_dataSold_total2,
                    eti_dataSold_total2,
                    smile_dataSold_total2,
                ],
                "data_list3": [
                    mtn_dataSold_total3,
                    glo_dataSold_total3,
                    airtel_dataSold_total3,
                    eti_dataSold_total3,
                    smile_dataSold_total3,
                ],
                "airtime_list": [
                    mtn_airtimeSold_total,
                    glo_airtimeSold_total,
                    airtel_airtimeSold_total,
                    eti_airtimeSold_total,
                ],
                "airtime_list2": [
                    mtn_airtimeSold_total2,
                    glo_airtimeSold_total2,
                    airtel_airtimeSold_total2,
                    eti_airtimeSold_total2,
                ],
                "airtime_list3": [
                    mtn_airtimeSold_total3,
                    glo_airtimeSold_total3,
                    airtel_airtimeSold_total3,
                    eti_airtimeSold_total3,
                ],
                "cable_list": [gotv, dstv, startime],
                "bill_list": [d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11],
                "cable_list2": [gotv2, dstv2, startime2],
                "bill_list2": [e1, e2, e3, e4, e5, e6, e7, e8, e9, e10, e11],
                "cable_list3": [gotv3, dstv3, startime3],
                "bill_list3": [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11],
            },
            status=200,
        )

    else:
        SalesAccountingForm()
        return JsonResponse({"message": "an error occured"}, status=400)
