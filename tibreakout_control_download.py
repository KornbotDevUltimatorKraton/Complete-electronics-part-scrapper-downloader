import re
from re import search
import os 
import sys
import bs4 # Getting the beautiful soup request data 
import json 
import urllib.request
from urllib import request
import requests
from PyPDF2 import PdfFileWriter, PdfFileReader
from requests.structures import CaseInsensitiveDict
import getpass 
import socket
import pickle
import difflib # Getting the difflib to find the matching sequence 
from pathlib import Path

username = getpass.getuser() 
#curl = 'curl -X POST "https://api.mouser.com/api/v1/search/partnumber?apiKey=cf621336-fea9-4734-81dd-a8442ed3e05c" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"SearchByPartRequest\": { \"mouserPartNumber\": \"LM324\", \"partSearchOptions\": \"1\" }}"'
#curl1 = 'curl -X POST "https://api.mouser.com/api/v1/search/keyword?apiKey=cf621336-fea9-4734-81dd-a8442ed3e05c" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"SearchByKeywordRequest\": { \"keyword\": \"DC motor driver IC\", \"records\": 0, \"startingRecord\": 0, \"searchOptions\": \"1\", \"searchWithYourSignUpLanguage\": \"English\" }}"'
sock1  = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # Streaming back the json data of the pakage name 
address_send = "127.0.0.1"  
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
address = ("127.0.0.1",5000)  #communication address to talking with the local server  
#Recieving the command key word from the main control 
sock.bind(address)
mode = 0o777 # Getting permission create the directory 
HOME_PATH = "/home/"+username+"/Automaticsoftware/" # Gettig the home path to point the file downloaded into the list 
Document = HOME_PATH+"Downloadedpackage/"   # Manage the directory to download the file into the path 
try:
   os.mkdir(Document) #Create the document 
except: 
   pass
CONFIG   = "/home/"+username+"/Automaticsoftware/Configuresearch" # Config file
headers = CaseInsensitiveDict()
headers["acccept"] = "application/json"
headers["Content-Type"] = "application/json"
mem_keys_word = []
category_manage = {}
Write_category_mem = {}
#Insert requirement inside the data json here for search capabiity 
 
configure_search = {'motor':"Motor/Motion/Ignition Controllers & Drivers"} 
list_config = os.listdir(CONFIG)
config= list_config[0] #Select the config file in the list of the directory 
Data_package_name = {} 
Price_package = {} 
Before_update_packname = {} 
Prices_fil_pack = {} 
Partitioning_data = {} # Getting the dictionary of partitioning data 
title_Package_data = {} # Getting all title data 
#Finding the intersection of the list 
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3   

def Configure(configfile): 
     try: 
       data = open(CONFIG+"/"+str(configfile),'r') #Open the configuretion file for the path 
       datas = data.readline()
       transfer = json.loads(datas)
       return transfer
     except:
        print("Not found the configure file please check again")
config_data = Configure(config)
def Getpackage_all_link(dataout,config_data):
      for ig in list(dataout): 
        try:
            print("header list",ig)
            datajson = dataout.get(list(dataout)[1])
            #print(datajson)
            #print(list(datajson))
            #print(datajson.get(list(datajson)[1]))
            getpart = datajson.get(list(datajson)[1]) 
            #print('getpart',getpart)
            print(list(getpart)[0])
        except: 
            print("Out of range")
     
      for ij in range(0,len(list(getpart))): 
                 Product_info = list(list(getpart)[ij]) 
                 #for rt in range(0,len(Product_info)): 
                 #print(list(getpart)[ij].get(Product_info[2]))
                 print(list(getpart)[ij].get(Product_info[16]),list(getpart)[ij].get(Product_info[5])) 
                 category_manage[list(getpart)[ij].get(Product_info[5])+"_"+str(ij)] = list(getpart)[ij].get(Product_info[16])
                 Write_category_mem[list(getpart)[ij].get(Product_info[5])] = ij
                 plen = list(getpart)[ij].get(Product_info[16]).split("https://")[1].split("/")
                 split_price = list(getpart)[ij].get(Product_info[16]).split("https://")[1].split("/")[len(plen)-1].split("?")[0]
                 Price_package[split_price] = list(getpart)[ij].get(Product_info[14])
      print(category_manage)  # using the category to create the new directory calssify in the list of ti_product
      print("Category data",list(Write_category_mem))
      #Writing the Category data into the directory 
      for pr in list(category_manage): 
               print(pr)
       
      #Generate the category data inside the list 
      jsonstring = json.dumps(Write_category_mem) 
      components_write = open("category_components.json",'w')
      #Writing the json file into the home path directory to running the api data
      components_write.write(jsonstring)  
      components_write.close()     
      for ir in range(0,len(category_manage)):
           components = category_manage.get(list(category_manage)[ir])
           Manufacturer = components.split("https://")[1].split("/")[2]
           compackage = components.split("https://")[1].split("/")[3].split("?")[0]
           #price = Price_package.get(compackage)
           #print(Price_package)
           drawing_pack = config_data.get('package').get('packagesdrawing')
           #replace and remove drawing package from the list 
           for re in range(0,len(drawing_pack)): 
                  try:
            
                    if search(drawing_pack[re],str(compackage)):
                                              
                      output_package = compackage.replace(str(drawing_pack[re]),"",1) 
                      Before_update_packname[compackage] = output_package
                      Data_package_name[output_package] = drawing_pack[re]
                      
                      print("Found drawing pakage",output_package,drawing_pack[re])

                  except:
                      pass  
      
      return Data_package_name
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def extract_pdf_page(keys_data): 
       input1 = PdfFileReader(open(Document+keys_data, "rb"))  #using oslist dir readding the file and extract all the value in the loop 
       info = input1.getDocumentInfo()
       number_of_pages = input1.getNumPages()
       print("Total page number ", number_of_pages) # Getting all number of total pages
       print(info)
       #print(author,creator,producer,subject,title)
       return info  # Geatting the header info of the pdf data 

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#Processing the data of the category extraction 

def Gen_prices_match(Before_update_packname): 
          for ry in list(Before_update_packname): 
                prices_data = re.sub(r'\D+$', '', str(Before_update_packname.get(ry)))
                prices_stock = Price_package.get(ry) 
                Prices_fil_pack[prices_data.lower()] = prices_stock 
          return Prices_fil_pack

def Google_search_package(Pack_drawing_json): 

      for p in list(Pack_drawing_json):   
          list_exsist_data = os.listdir(Document) #Checking the document download path 
          text= p.lower()  #insert the search data here 
          print(text)
          if text not in list_exsist_data:
              url = 'https://google.com/search?q=' + text  #Select google as search engine 

              check_menufac = ['ti','nxp','st']
              # Fetch the URL data using requests.get(url),
              # store it in a variable, request_result.
              request_result=requests.get(url)
              # Creating soup from the fetched request
              soup = bs4.BeautifulSoup(request_result.text,"html.parser")
              #print(soup)
              #print(type(soup))
              for a in soup.find_all('a', href=True):
                       #print("Found the URL:", a['href'])
                       try:
                           if len(a['href'].split('/url?q=')) == 2:
                                  print("Manufacturer",a['href'].split('/url?q=')[1].split('&')[0].split("https://")[1].split("/")[0].split(".")[1])
                                  data_link_menufac = a['href'].split('/url?q=')[1].split('&')[0].split("https://")[1].split("/")[0].split(".")[1]
                                  if data_link_menufac in check_menufac[0]:
                                      try:
                                                  print(a['href'].split('/url?q=')[1].split('&')[0])
                                                  length = len(a['href'].split('/url?q=')[1].split('&')[0].split("/")) -1
                                                  url_link = a['href'].split('/url?q=')[1].split('&')[0].split("/")[length].lower()
                                                  #Making download hear 
                                                  url = 'https://www.ti.com/lit/ds/symlink/'+url_link+".pdf" 
                                                  getname = url.split(".pdf")[0].split("/")[len(url.split(".pdf")[0].split("/"))-1]
                                                  print(getname)
                                                  filename = Path(Document+text+'.pdf')
                                                  r = requests.get(url)
                                                  if int(r.status_code) == 200:
                                                         print(r.status_code) 
                                                         filename.write_bytes(r.content) 
                                                         
                                                         break 
                                      except: 
                                          print("Out of range data match")
                                                                        
                       except:
                            pass
          else: 
              print("The file is already exist in the ", Document)  
def Google_filter_search(text,keys_data): 
     
          list_exsist_data = os.listdir(Document) #Checking the document download path 
          #.lower()  #insert the search data here 
          print(text,keys_data)
          print(text,Prices_fil_pack.get(keys_data))
          if keys_data not in list_exsist_data:
              url = 'https://google.com/search?q=' + keys_data  #Select google as search engine 

              check_menufac = ['ti','nxp','st']
              # Fetch the URL data using requests.get(url),
              # store it in a variable, request_result.
              request_result=requests.get(url)
              # Creating soup from the fetched request
              soup = bs4.BeautifulSoup(request_result.text,"html.parser")
              #print(soup)
              #print(type(soup))
              for a in soup.find_all('a', href=True):
                       #print("Found the URL:", a['href'])
                       try:
                           if len(a['href'].split('/url?q=')) == 2:
                                  print("Manufacturer",a['href'].split('/url?q=')[1].split('&')[0].split("https://")[1].split("/")[0].split(".")[1])
                                  data_link_menufac = a['href'].split('/url?q=')[1].split('&')[0].split("https://")[1].split("/")[0].split(".")[1]
                                  if data_link_menufac in check_menufac[0]:
                                      try:
                                                  print(a['href'].split('/url?q=')[1].split('&')[0])
                                                  length = len(a['href'].split('/url?q=')[1].split('&')[0].split("/")) -1
                                                  url_link = a['href'].split('/url?q=')[1].split('&')[0].split("/")[length].lower()
                                                  #Making download hear 
                                                  url = 'https://www.ti.com/lit/ds/symlink/'+url_link+".pdf" 
                                                  getname = url.split(".pdf")[0].split("/")[len(url.split(".pdf")[0].split("/"))-1]
                                                  print(getname)
                                                  list_partion =  Category_partitioner(config_data,category_manage)
                                                  get_partition = "TI_"+list_partion.get(keys_data).split("_")[0]
                                                  filename = Path(HOME_PATH+"TI_product/"+get_partition+"/"+keys_data+'.pdf')
                                                  filename1 = Path(Document+keys_data+'.pdf')  # Setting the category name for the directory 

                                                  r = requests.get(url)
                                                  if int(r.status_code) == 200:
                                                         print(r.status_code) 
                                                         filename.write_bytes(r.content) 
                                                         filename1.write_bytes(r.content)
                                                         del Data_package_name[text]
                                                         break 
                                      except: 
                                          print("Out of range data match")
                                                                        
                       except:
                            pass
          else: 
              print("The file is already exist in the ", Document) 
#Category partitioner 
def Category_partitioner(config_data,category_manage):
         cat_keys  = list(category_manage.keys())
         cat_vavs  = list(category_manage.values())
         drawing_pack = config_data.get('package').get('packagesdrawing')
         for ryi in range(0,len(category_manage)):
                     len_link = cat_vavs[ryi].split("https://")[1].split("/")
                     packagename =   cat_vavs[ryi].split("https://")[1].split("/")[len(len_link)-1].split("?")[0] #Getting the package name as the keys of the partition to search data in the partioning category
                     #remove_drawing = Pack_drawing_remover(packagename,config_data)
                     for rey in range(0,len(drawing_pack)): 
                             try:
            
                                    if search(drawing_pack[rey],str(packagename)):
                                             output_package = str(packagename).replace(str(drawing_pack[rey]),"",1).lower()
                                             key_category = re.sub(r'\D+$', '', output_package)
                                             Partitioning_data[key_category] = cat_keys[ryi] 

                             except:
                                 pass   
         return Partitioning_data 

#Un filter algorithm to collect more data 
def Filter_collection(Pack_drawing_json): # For TI algorithm
    list_partion =  Category_partitioner(config_data,category_manage)
    for iy in range(0,len(list_partion)):
              try:
                    os.mkdir(HOME_PATH+"TI_product/"+"TI_"+list_partion.get(list(list_partion)[iy]).spit("_")[0].split("/")[len(list_partion.get(list(list_partion)[iy]).spit("_")[0].split("/"))-1],mode) # Create the category folder automatically
              except: 
                    try:
                        os.mkdir(HOME_PATH+"TI_product/"+"TI_"+list_partion.get(list(list_partion)[iy]).split("_")[0],mode) # Create the category folder automatically
                    except: 
                         pass 
    for p in range(0,len(Pack_drawing_json)):
      list_exist_data = os.listdir(Document)      
      text  = list(Pack_drawing_json)[p].lower()
      #print(list_exsist_data)
      keys_data = re.sub(r'\D+$', '', text) # split the text after the number in the string 
      print("Now filtering ",text+" ======>  "+keys_data)
         
    
      if str(keys_data)+".pdf" not in list_exist_data: 
          try:
              #Making download hear 
              
              get_partition = "TI_"+list_partion.get(keys_data).split("_")[0]
              url = 'https://www.ti.com/lit/ds/symlink/'+keys_data+".pdf" 
              filename = Path(HOME_PATH+"TI_product/"+get_partition+"/"+keys_data+'.pdf')  # Setting the category name for the directory 
              filename1 = Path(Document+keys_data+'.pdf')  # Setting the category name for the directory 

              r = requests.get(url)
              if int(r.status_code) == 200:
                    print(r.status_code) 
                    filename.write_bytes(r.content) 
                    filename1.write_bytes(r.content)                                     
                    print(text,Prices_fil_pack.get(keys_data))
                    del Data_package_name[text] 
              elif int(r.status_code) != 200: 
                     print("Filtering search file with the google search")
                     Google_filter_search(text,keys_data) # using the filtering google search 
          except: 
              print("Out of range data match")
      else: 
           print("Already downloaded inside the list")
      
#Running the function of search algorithm
#Google_search_package(Pack_drawing_json)
#Running filter rethrieving data 
#while True:
data,addr = sock.recvfrom(1024)
key_words = " Texas instrument "+data.decode()       #Sensor Magnetic sensor #motor Dc motor BLDC motor driver RF chip 
all_lowercase = key_words.islower()
convert_lowercase = "" 
if all_lowercase == False: 
    convert_lowercase = key_words.lower()   
data = { 

        'SearchByKeywordRequest': {
        'keyword': key_words,
        'records': 0,
        'startingRecord': 0,
        'searchOptions':1,
        'searchWithYourSignUpLanguage':'English', 
       }
    }
r = requests.post('https://api.mouser.com/api/v1/search/keyword?apiKey=cf621336-fea9-4734-81dd-a8442ed3e05c', headers=headers, json=data)
print(r.status_code)
dataout = r.json()
Pack_drawing_json = Getpackage_all_link(dataout,config_data)
print(Pack_drawing_json)
print("Before update package name",Before_update_packname)
Price_stock_data = Gen_prices_match(Before_update_packname) 
print(Price_stock_data)
mem_keys_word.append(key_words)    
Filter_collection(Pack_drawing_json) #These are the data for TI product collected pdf datasheet downloaded
print("Category list ", category_manage) # Getting the list of the category data of the component
print("category_data ",list(Write_category_mem)) # Getting the category directory management 
#Getting the pdf header extraction 
for keys_Data in os.listdir(Document):
    try:
           info = extract_pdf_page(keys_Data)
           print(keys_Data,info)
           try:
                title_Package_data[keys_Data.split(".")[0]] = info.get(list(info)[2]).decode() 
           except:
                title_Package_data[keys_Data.split(".")[0]] = info.get(list(info)[2])
    except: 
        print("Fail to load the file in the directory may be downloader is fail please check software")
print(title_Package_data) # Reading the topic as reference for the package name 
jsonstring = json.dumps(title_Package_data) 
components_write = open(HOME_PATH+"Component_title.json",'w') 
#Writing the json file into the home path directory to running the api data
components_write.write(jsonstring)  
components_write.close() 
try:
    #json_data = json.dumps(Data_package_name)
    #message = pickle.dumps(json_data)
    print("Finish downloading datasheet.......(^_^)")
    sock1.sendto("Finished Downloading".encode('utf-8'),(address_send,5080)) # Sending the process          
    
except:
    pass  
     