import time
import json
import locale
import logging
import sqlite3
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

locale.setlocale(locale.LC_ALL, '')
today = datetime.datetime.now() #antes datetime.datetime.utcnow()
day_access = datetime.date.today() + datetime.timedelta(days=10)
day_refresh = datetime.date.today() + datetime.timedelta(days=85)
client_id = "Cecfb8c11e92e732d13e78d528a7714432820859b0ddd1b7238779709f611d98c"
client_secret = "0f04b932a98e6e7d54a57514605b7198208331264a7cc4d28c74cf4e66239d32"

def code():
    url = 'https://webexapis.com/v1/authorize?client_id=Cecfb8c11e92e732d13e78d528a7714432820859b0ddd1b7238779709f611d98c&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A4200&scope=spark%3Akms%20spark%3Amessages_write&state=set_state_here'
    
    #Configuración web driver
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    #Pagina de inicio Webex
    username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'IDToken1')))
    username_input.send_keys("luis.herrera@axity.com")
    button_login = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'IDButton2')))
    button_login.click()
    password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'IDToken2')))
    password_input.send_keys("Covid2021*")
    login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'Button1')))
    login_button.click()
    url_retorno = driver.current_url
    code_param = url_retorno.split("code=")[1]
    
    # Obtener el código de autorización
    codigo_autorizacion = code_param.split("&")[0]
    
    # Imprimir el código de autorización
    print("Código de autorización:", codigo_autorizacion)
    time.sleep(10)
    driver.quit()
    return codigo_autorizacion

#Atenticacion del token
def _get_webex_refresh_token(refresh_token):
    url = "https://webexapis.com/v1/access_token"
    payload = 'grant_type=refresh_token&client_id='+client_id + \
        '&client_secret='+client_secret+'&refresh_token='+refresh_token
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    dictionary = response.json()
    [dictionary.pop(key, None) for key in ['expires_in', 'refresh_token',
                    'refresh_token_expires_in', 'token_type', 'scope']]
    print("nuevo access token expira el",day_access)
    return dictionary

def _get_webex_access_token(code):
    url = "https://webexapis.com/v1/access_token"
    payload = 'code='+code+'&client_id='+client_id+'&client_secret='+client_secret+\
        f'&grant_type=authorization_code&redirect_uri=http%3A%2F%2Flocalhost%3A4200'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    print("payload: ",payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    print("response: ",response.text)
    dictionary = response.json()
    print("dictionary: ",dictionary)
    [dictionary.pop(key, None) for key in ['expires_in',
                    'refresh_token_expires_in', 'token_type', 'scope']]
    print("El nuevo access token expira el:",day_access)
    print("El nuevo refresh token expira el:",day_refresh)
    print("dictionary: ",dictionary)
    print("access_token:",dictionary["access_token"])
    print("refresh_token:",dictionary["refresh_token"])
    return dictionary["access_token"], dictionary["refresh_token"]

def validaciones_token():
    db = sqlite3.connect('datos.db')
    connection = db.cursor()
    connection.execute("""CREATE TABLE IF NOT EXISTS access_token(
                id_access INTEGER PRIMARY KEY AUTOINCREMENT,
                access_token VARCHAR NOT NULL,
                access_expire VARCHAR NOT NULL,
                refresh_token VARCHAR NOT NULL,
                refresh_expire VARCHAR NOT NULL)""")
    db.commit()
    connection.execute("SELECT access_token, access_expire, refresh_token, refresh_expire FROM access_token ORDER BY id_access DESC LIMIT 1")
    result = connection.fetchone()  #print(result)
    today = datetime.datetime.now() #antes datetime.datetime.utcnow()
    date_access = datetime.date.today() + datetime.timedelta(days=10)
    print("date_access:", date_access)
    date_refresh = datetime.date.today() + datetime.timedelta(days=85)
    print("date_refresh:",date_refresh)
    if result:
        print("access token actual", result[1])
        print("refresh token actual", result[3])
        expire_access = datetime.datetime.strptime(str(result[1]), '%Y-%m-%d')
        expire_refresh = datetime.datetime.strptime(str(result[3]), '%Y-%m-%d')
        print("hoy",today)
        if today >= expire_refresh:
            access_token, refresh_token = _get_webex_access_token(code())
            connection.execute("UPDATE access_token SET access_token=:token, access_expire=:date, refresh_token=:refresh, refresh_expire=:expire",
                                {"token": access_token, "date": date_access, "refresh": refresh_token, "expire": date_refresh})        
            db.commit()
            logging.warning("access_token y refresh_token actualizados por vencimiento mayor a 85 dias")
        else:
            if today >= expire_access:
                webex_response = _get_webex_refresh_token(result[2])
                token = webex_response["access_token"]
                connection.execute("UPDATE access_token SET access_token=:token, access_expire=:date",
                                    {"token": token, "date": date_access})
                db.commit()
                logging.warning("Token vencido por mas de 10 dias, se ha actualizado correctamente")
                access_token = token
            else:
                print("El Token aun no ha vencido")
                access_token = result[0]  # Token not expired
    else:
        access_token, refresh_token = _get_webex_access_token(code())
        print("access_token: ",access_token) #nueva linea
        print("refresh_token: ",refresh_token)#nueva linea
        connection.execute("INSERT INTO access_token VALUES (NULL, ?, ?, ?, ?)",
                            (access_token, date_access, refresh_token, date_refresh))
        db.commit()
        logging.warning("access_token y refresh_token creados por primera vez")
    db.close()

def get_access_token():
    db = sqlite3.connect('datos.db')
    connection = db.cursor()
    connection.execute("SELECT access_token FROM access_token ORDER BY id_access DESC LIMIT 1")
    result = connection.fetchone()
    access_token = result[0]
    return access_token

validaciones_token()

Camaras = {
    "Camara_Frontera":"Q2GV-HY57-H937",
    "MV22_Camara_1":"Q2HV-FU4B-5CRT",
    "MV32_Camara_1":"Q2PV-AUAR-4K3G",
    "MV32_Camara_2":"Q2PV-TNTC-G8TZ",
    "MV32_Camara_3":"Q2PV-YHGR-9HGY",
    "MV32_Camara_4":"Q2PV-64NS-7G4F",
    "MV32_Camara_5":"Q2PV-C7SJ-ERD7",
    "MV32_Camara_6":"Q2PV-ZEE6-RRXG",
}

for x in Camaras:
    print(x)
    print(Camaras[x])
    print("")
    
    serial = Camaras[x]
    
    ## Live API
    print('MV Sense Live API')
    meraki_live_url = 'https://api.meraki.com/api/v1/devices/'+serial+'/camera/analytics/live'
    meraki_headers = {'X-Cisco-Meraki-API-Key': '8f7fae459f872d4a64493ec0df5d28c2152d68e3'}
    meraki_live_response = requests.get(meraki_live_url, headers=meraki_headers)
    meraki_live_response_json=json.loads(meraki_live_response.text)
    num_of_person_detected=meraki_live_response_json['zones']['0']['person']
    print(num_of_person_detected)
    
    ##Get Device
    print('Get Device')
    nombre_device = x
    
    ## Snapshot API
    print('Snapshot API')
    meraki_snapshot_url='https://api.meraki.com/api/v1/devices/'+serial+'/camera/generateSnapshot'
    meraki_snapshot_response = requests.post(meraki_snapshot_url, headers=meraki_headers)
    time.sleep(5)
    meraki_snapshot_response_json=json.loads(meraki_snapshot_response.text)
    snapshot_url=meraki_snapshot_response_json['url']
    print(snapshot_url)
    
    ## Webex API
    print('Sending Message via WebEx API')
    
    WEBEX_API_URL = 'https://webexapis.com/v1/messages'
    #WEBEX_ACCESS_TOKEN = 'NzYwNzA3NDctN2U2Zi00YTc0LThlY2YtNzM4ODU3MTc3ZjgwNmUzZTA3ZWYtM2Uy_PF84_b4e50a79-b7de-4ee2-940a-a983d1e5c35b'
    WEBEX_ACCESS_TOKEN = get_access_token() #ojo revisar... consultas innecesarias en ciclos...
    print(WEBEX_ACCESS_TOKEN)
    
    httpHeaders = {'Authorization': f'Bearer {WEBEX_ACCESS_TOKEN}'}
    texto = nombre_device +", personas: "+ str(num_of_person_detected)
    body = {'roomId': 'Y2lzY29zcGFyazovL3VzL1JPT00vYTc1YTgzOTAtNTYzMC0xMWVlLTk2MTEtMDU3YWFkYjZhNWM3', 'text':texto,'files':snapshot_url}
    print(texto)
    
    response = requests.post(url=WEBEX_API_URL, headers=httpHeaders, json=body)
    print(response.status_code)
    print(json.dumps(response.json(), indent=2))
