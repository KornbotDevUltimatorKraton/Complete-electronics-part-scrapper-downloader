import os
import json 
import socket 
import pickle
import subprocess
import multiprocessing
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#Client side to receive the command to acticate restart loop 
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
address = ("127.0.0.1",5080) 
sock.bind(address)

username = str(subprocess.check_output("uname -a",shell=True)) # Get the the username of the computer reading from the client computer 
Getusername = username.split("-")[0].split(" ")[1]  #Get the username
HOME_PATH = "/home/"+str(Getusername)+"/Automaticsoftware/"
#running the downloader application to start and reset the loop download
os.system("python3 "+HOME_PATH+"tibreakout_control_download.py")
while True: 
      data,addr = sock.recvfrom(1024)
      print(data.decode()) # Getting the string data back 
      if data.decode() == "Finished Downloading": 
                 print("Restart software")
                 os.system("python3 "+HOME_PATH+"tibreakout_control_download.py")
      #received  = pickle.loads(data)
      #message = json.loads(received)
      #print(received,type(received),addr)
      #print(message,type(message),addr)   
