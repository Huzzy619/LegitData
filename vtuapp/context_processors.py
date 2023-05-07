from .models import BankAccount, Disable_Service, Network, WebsiteConfiguration




def categories_processor(request):
    config = WebsiteConfiguration.objects.first()
    net = Network.objects.all()
    checkbank = Disable_Service.objects.filter(service="Bankpayment").first()
    monnifybank = Disable_Service.objects.filter(service="Monnfy bank").first()
    monnifyATM = Disable_Service.objects.filter(service="Monnify ATM").first()
    paystack = Disable_Service.objects.filter(service="paystack").first()
    aircash = Disable_Service.objects.filter(service="Airtime_Funding").first()

    return {
        "banks": BankAccount.objects.all(),
        "networks": net,
        "whatsapp_group_link": config.whatsapp_group_link,
        "support_phone": config.support_phone_number,
        "air2cash": aircash.disable if aircash else None,
        "bank2": checkbank.disable if checkbank else None,
        "monnifyatm2": monnifyATM.disable if monnifyATM else None,
        "paystack2": paystack.disable if paystack else None,
        "monnifybank2": monnifybank.disable if monnifybank else None,
        "config": config,
    }
