import os
import glob
import time
import sqlite3
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(24,GPIO.OUT) # Led Rojo
GPIO.setup(23,GPIO.OUT) # Led Verde

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
       # temp_f = temp_c * 9.0 / 5.0 + 32.0   # usado en C
        return temp_c

conn = sqlite3.connect('base.db')
c = conn.cursor()

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS stuffToPlot(id INTEGER PRIMARY KEY AUTOINCREMENT, temp REAL, alarm_hi REAL, alarm_low REAL, datestamp TEXT)")




class parametros(object):
    def __init__(self, alarm_hi, alarm_low):
        self.alarm_hi = alarm_hi
        self.alarm_low = alarm_low

try:

   
   
    x = parametros(28,16) #seteo por defecto
        
    set=input('Modificar parámetros? [S/N]')
    if (set == 'S' or set == 's'):
        x.alarm_hi = float(input('Ingresar Temperatura Máxima [°C] = '))       
        x.alarm_low = float(input('Ingresar Temperatura Mínima [°C]= '))
    else:
       print(' Los valores por defecto son 28°C y 23°C')

    
    tempold = read_temp()
    print(tempold,' °C <- sensor andando') #unica vez
    
  
    create_table()
    
    while True:
        temp = read_temp()
            
        if (temp < x.alarm_hi) & (temp > x.alarm_low):
            print(temp,' °C')
            GPIO.output(23,1)
            GPIO.output(24,0)
        elif temp > x.alarm_hi:
            print (temp,' °C ---> Muy Caliente')
            GPIO.output(23,0)
            GPIO.output(24,1)
        elif temp < x.alarm_low:
            print (temp,' °C ---> Muy Frio')
            GPIO.output(23,0)
            GPIO.output(24,1)
         
        date = time.strftime('%y-%m-%d - %H:%M:%S')
        c.execute("INSERT INTO stuffToPlot (id, temp, alarm_hi, alarm_low, datestamp) VALUES (null,?,?,?,?)",
                      (temp, x.alarm_hi, x.alarm_low, date))
        conn.commit()
    
        time.sleep(2)
        
    # Interrumpe con control+c 
except KeyboardInterrupt:
    pass
finally:
    c.close()
    conn.close()
    GPIO.cleanup()  #clean exit
            

