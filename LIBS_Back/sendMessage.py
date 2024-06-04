# from twilio.rest import Client
# userSID="USa91e2fe590706cd9eef845883b3a8bf4"
#
# # les credentials sont lues depuis les variables d'environnement TWILIO_ACCOUNT_SID et AUTH_TOKEN
# client = Client()
# # c'est le numéro de test de la sandbox WhatsApp
# from_whatsapp_number='whatsapp:+14155238886'
# # remplacez ce numéro avec votre propre numéro WhatsApp
# to_whatsapp_number='whatsapp:+330630307144'
# client.messages.create(body='La batterie a finit de charger !',from_=from_whatsapp_number,to=to_whatsapp_number)


import pywhatkit

def send_message():

    import time
    time = time.localtime()
    hour = time.tm_hour
    minute = time.tm_min +2
    pywhatkit.sendwhatmsg("+55 92 8129-5256","🤖 The bot says : 'Battery test is finished !'", hour, minute, 30, tab_close=True, close_time=20)
