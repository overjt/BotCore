from pyquery import PyQuery as pq
import requests
import re

selectors = [
    'div._eF',  # Fecha nacimiento, lugar de nacimiento
    '#cwos',  # Calculos
    'div.kpd-ans',  # tasas de desempleo
    '#wob_tm',  # temperatura
    'div.vk_bk.vk_ans',  # conversion de monedas por ejemplo, hora tambien
    'span._Tgc',
    'ol.lr_dct_wd_ol',  # que es
    'div.vk_sh.vk_gy',  # ubicacion, donde estoy
    # Span wikipedia julian assange testing, hernan botbol, barra a la derecha
    'div.kno-rdesc span',
    '#tw-target-text',  # traducciones
    'div._mr.kno-fb-ctx'
]


def findResponse(body):
    response = ""
    d = pq(body)
    for selector in selectors:
        response = d(selector).eq(0).text()
        if response != "":
            if selector == '#wob_tm':
                temp = "Temperatura: " + response + " °C"
                city = d("#wob_loc").eq(0).text()
                humidity = "Humedad: " + d("#wob_hm").eq(0).text()
                wind = "Viento: " + d("#wob_ws").eq(0).text()
                response = "▪️ " + city + " ▫️\n" + temp + "\n" + humidity + "\n" + wind
            break
    return response


def googleQuestion(message):
    url = "http://www.google.{tld}/search?hl={lang}&q={query}&start={start}&sa=N&num={num}&ie=UTF-8&oe=UTF-8&nfpr=1&gws_rd=ssl".format(
        tld="com.co",
        lang='es',
        query=message,
        start="0",
        num="25"
    )

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-419,es;q=0.8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36',
        'Connection': 'keep-alive',
        'DNT': '1'
    }

    r = requests.get(url, headers=headers)
    return findResponse(r.text)


def process_message(message, msg_sender, msg_to, msg_type, connector, bot):
    regex = "{bot_name},? (.*?)\?$".format(bot_name=bot.name)
    try:
        found = re.search(regex, message, re.IGNORECASE).group(1)
    except AttributeError:
        found = ''
    if found != '':
        response = googleQuestion(found)
        if response:
            connector.send_message(msg_to, response)
