import pywhatkit

def send_message():

    import time
    time = time.localtime()
    hour = time.tm_hour
    if time.tm_min<56:
        minute = time.tm_min +2
    else :
        hour = hour+1
        minute=2
    pywhatkit.sendwhatmsg("+55 92 8129-5256","🤖 The bot says : 'Battery test is finished !'", hour, minute, 30, tab_close=True, close_time=20)
    #pywhatkit.sendwhatmsg("+33 0630307144","🤖 The bot says : 'Battery test is finished !'", hour, minute, 30, tab_close=True, close_time=20)