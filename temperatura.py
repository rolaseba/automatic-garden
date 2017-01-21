# Garden project from Sebastian Rolando.
# The programming languaje is Python 3

import os
import glob
import time
import sqlite3
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(24,GPIO.OUT) # red Led <-- out of range
GPIO.setup(23,GPIO.OUT) # green Led

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
       # temp_f = temp_c * 9.0 / 5.0 + 32.0   # we don´t use Fahrenheit grades
        return temp_c

conn = sqlite3.connect('dbase.db')
c = conn.cursor()

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS stuffToPlot(id INTEGER PRIMARY KEY AUTOINCREMENT, temp REAL, alarm_hi REAL, alarm_low REAL, datestamp TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS parameters(id INTEGER PRIMARY KEY AUTOINCREMENT, palarm_hi REAL, palarm_low REAL)")


class parametros(object):
    def __init__(self, alarm_hi, alarm_low):
        self.alarm_hi = alarm_hi
        self.alarm_low = alarm_low
    

try:
    create_table()  # create database tables

    tempold = read_temp()
    print(tempold,' °C <- sensor andando') #sensor working

    x = parametros(28,16) #seteo por defecto
        
    set=input('Modificar parámetros? [S/N]')
    if (set == 'S' or set == 's'):
        x.alarm_hi = float(input('Ingresar Temperatura Máxima [°C] = '))       
        x.alarm_low = float(input('Ingresar Temperatura Mínima [°C] = '))
        # guardo parametros en tabla
        c.execute("INSERT INTO parameters(id, palarm_hi, palarm_low) VALUES (null,?,?)",
                  (x.alarm_hi, x.alarm_low))
        conn.commit()
    else:
        c.execute('SELECT max(id) FROM parameters')
        max_id = c.fetchone()[0]
        #print('max_id =', max_id)
        print(' Los valores por defecto son =')
        c.execute('SELECT * FROM parameters WHERE id=?',(max_id,))
        a = c.fetchone()
        print('a =', a)
       
              
    
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
            

