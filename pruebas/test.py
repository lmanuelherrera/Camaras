import time
import locale
import datetime

ahora = time.strftime("%c")

## Muestra fecha y hora actual a partir de la variable 
print ("Fecha y hora de la variable %s"  % ahora )


locale.setlocale(locale.LC_ALL, '')
today = datetime.datetime.utcnow()
print(today)


fecha_actual = datetime.datetime.now()
print(fecha_actual)
print(fecha_actual.strftime('\n inicio: %A, %d de %B de %Y a las %H:%M:%S \n'))

time.sleep(2)

today = datetime.datetime.now()
fecha = today.strftime('%A, %d de %B de %Y a las %I:%M:%S %p')
print(fecha)

url="https://www.youtube.com/"


