"""
Orbs Game: Set your name and see the scores
"""
___name___         = "Orbs Game"
___license___      = "MIT"
___dependencies___ = ["app", "dialogs", "sim800", "ugfx_helper"]
___categories___   = ["Games"]
___bootstrapped___ = False

from app import *
from dialogs import *
import utime
import ugfx
import ugfx_helper
from orbs.umqtt.simple import MQTTClient
import network
from machine import mem32
import wifi
wifi.connect()

ugfx_helper.init()
ugfx.clear()
broker='151.216.207.139'
mqtt_username='orbs'
mqtt_password='orbs123'
scoretext=""

MACAddress=str(mem32[0x400fef20]) + str(mem32[0x400fef24]) + str(mem32[0x400fef28]) + str(mem32[0x400fef2C])
regOK=False
regFAILED=False

def mqtt_connect():
  client = MQTTClient(MACAddress,broker, user=mqtt_username, password=mqtt_password)
  client.set_callback(sub_cb)
  connected=False
  try:
    client.connect()
    connected=True
  except Exception as err:
    connected=False
  if (connected):
    return client
  else:
    return False

def sub_cb(topic,msg):
  global regOK
  global regFAILED
  global scoretext
  try:
      (t1,t2,t3,targetBadge,messageType)=topic.decode('utf-8').split('/')
      strmsg=msg.decode('utf-8')
      if messageType=="regok":
        regOK=True
      if messageType=="regerror":
        regFAILED=True
      if messageType=="scores":
        scoretext=msg
  except:
    return
  

def update_token(token):
   lb=open("token.txt","w")
   lb.write(token)
   lb.close()
    
def do_gettoken():
   notice("Enter your RFID token ID digits only. Get it right!", title="Orbs Game")
   token=prompt_text("Enter token:")
   if len(token)==8 or len(token)==14 or len(token)==20:
     return token
   else:
     notice("Invalid token", title="Orbs Game")
     return ""   
    
def do_register(client):
  playername=prompt_text("Enter name:")
  playername=playername.replace(",",".")
  regOK==False
  regFAILED==False
  if len(playername)>3:
    client.publish("/registration/from/" + MACAddress + "/name",mytoken + "," + playername)
    notice("Name request sent")
    client.check_msg()
    if regOK==True:
      notice("Registration completed")
    if regFAILED==True:
      notice("Registration failed")    
  else:
    notice("Name too short")  
    
def get_token():
  try:
    lb=open("token.txt","r")
    token=lb.readline()
    lb.close()
    if token=="":
      token=do_gettoken()
  except:
    token=""
  if token=="":
    token=do_gettoken()
  return token

def do_showscores(client):
  client.publish("/registration/from/" + MACAddress + "/score",mytoken)
  notice("Requested scores")
  client.check_msg()
  if len(scoretext)>0:
    (playername,playerscore,rank,redscore,greenscore,bluescore)=scoretext.decode('utf-8').split(',')  
    notice("Player: " + playername + chr(13) + "Score: " + playerscore + chr(13) + "Rank: " + rank)
    notice("Red Score: " + redscore + chr(13) + "Green Score: " + greenscore + chr(13) + "Blue Score: " + bluescore)
  else:
    notice("Failed to get scores")
  
mqttclient=mqtt_connect()
while (not mqttclient):
    utime.sleep(2)
    mqttclient=mqtt_connect()
mqttclient.subscribe(topic='/badge/to/' + MACAddress + '/#')
#mqttclient.subscribe(topic='/scoreboard/to/all/#')
mytoken=get_token()
if len(mytoken)==0:
  notice("Token required",title="Orbs Game")
  try:
    mqttclient.close()
  except:
    restart_to_default()
  restart_to_default()
update_token(mytoken)
  

menuset = []
menuset.append({ "title" : "Register", "index" : 1 })
menuset.append({ "title" : "Scores", "index" : 2 })

while True:
    selection = prompt_option(menuset, text="Orbs Game", select_text="Select", none_text="Exit")
    if (not selection):
        restart_to_default()
    elif (selection["index"]==1):
        do_register(mqttclient)
    elif (selection["index"]==2):
        do_showscores(mqttclient)
