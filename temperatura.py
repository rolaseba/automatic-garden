import os
import glob
import time
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
    print(tempold,' °C') #unica vez
    
    file = open("datos.txt", "w")
    
    while True:
        temp = read_temp()
        if temp != tempold:
            file.write(str (temp)+' °C'+time.strftime('   %a %b %d %H:%M:%S %Y')+'\n') # grabo temp en archivo txt
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
            tempold = temp
            time.sleep(1)
        
    # Interrumpe con control+c 
except KeyboardInterrupt:
    pass
finally:
    file.close()
    GPIO.cleanup()  #clean exit
            

