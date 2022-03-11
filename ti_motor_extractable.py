from email.header import Header
from importlib.resources import Package
from inspect import getfullargspec
import io
import os 
import json
import socket
from struct import pack
from zipfile import Path 
import camelot 
import difflib 
import subprocess
import numpy as np 
import pandas as pd
import psycopg2 # postgres database 
from PyPDF2 import PdfFileWriter, PdfFileReader

username = str(subprocess.check_output("uname -a",shell=True)) # Get the the username of the computer reading from the client computer 
Getusername = username.split("-")[0].split(" ")[1]  #Get the username
HOME_PATH = "/home/"+str(Getusername)+"/Automaticsoftware/"
EXTRACT  = "/home/"+str(Getusername)+"/Automaticsoftware/tempolarydocextract" #Tempolary read the file extraction from the pdf specification function
PATHMAIN = "/home/"+str(Getusername)+"/Automaticsoftware/ComponentDoc"   # Getting the document page 
CONFIG   = "/home/"+str(Getusername)+"/Automaticsoftware/Configuresearch" # Config file
TI_product  = "/home/"+str(Getusername)+"/Automaticsoftware/TI_product"
NXP_product = "/home/"+str(Getusername)+"/Automaticsoftware/NXP_product"
ST_product = "/home/"+str(Getusername)+"/Automaticsoftware/ST_product"

TI_motor_drive  = "/home/"+str(Getusername)+"/Automaticsoftware/TIpro/TI_motordriver"
TI_bms  = "/home/"+str(Getusername)+"/Automaticsoftware/TIpro/TI_BMS"
TI_sensor  = "/home/"+str(Getusername)+"/Automaticsoftware/TIpro/TI_sensor"

NXP_interfaces = "/home/"+str(Getusername)+"/Automaticsoftware/NXPpro/NXP_interface"
NXP_multiplexer = "/home/"+str(Getusername)+"/Automaticsoftware/NXPpro/NXP_multiplexer"

ST_motordriver = "/home/"+str(Getusername)+"/Automaticsoftware/STpro/ST_motordriver"
ST_sensor =  "/home/"+str(Getusername)+"/Automaticsoftware/STpro/ST_sensor"
ST_microcontroller  =  "/home/"+str(Getusername)+"/Automaticsoftware/STpro/ST_mcus"

directcreate = ['tempolarydocextract','ComponentDoc','Configuresearch','TI_product','NXP_product','ST_product'] #list of the directory to create file
print("Create directory and give permission.....")
mode = 0o777
listdir_data = os.listdir(EXTRACT)
print(listdir_data)
listConfig = os.listdir(CONFIG)
cluster_class = {}
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
PinsNamepack = []
PinsNumpack  = []
IONamepack = [] # Getting the io name pack 
Packagingdata = {} 
PackagewithIO = {} 
completepack = {} 
completeioname = {} 
check_datatype = {}
Check_Packagename = []  # Checking the list of the package name inside the list 
Generate_Pinspack = []
Generate_Numpack = [] 
Generate_iopack = [] 
completeNumpack = {} # Getting the new pins name append into the dictionary 
completePinspack = {} #Getting the complete pins pack data
check_pack_order = {}   
check_pins_table = {} #Getting the pins table inside the list 
Pack_data = {}

Pins_page_intersec = [] 
Pins_subpage_intersec = []
Order_page_internsec = []
Pins_Page_regroup  = {} 
Order_page_regroup = {} 
mem_pins_info = []
all_pins_info = {} 
pins_mem_pack = []
pins_reorder = {}
pack_map = {}
num_rc_map = {} 
mem_pack_frame = []
pack_subpackframe = {}
#Static parameters 
n = 1
n1 = 0
n2 = 2
n3 = 3
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Swap string 
new_str=""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Classified_package = {'Multipackage':['NAME', 'NO.', 'nan', 'nan', 'nan'],'Singlepackage':['NAME', 'NO.', 'nan', 'nan']}
False_package_check = {'True':'Singlepackage','False':'Multiplepackage'} # Getting the True Single package data ad false multipackage
listConfig = os.listdir(CONFIG)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#Writing the json file into the cloud database 
#using the roboreactorpart database cloud   
DATABASE_URL = "postgres://deblnijnzpwins:0b338cb6d067f909fa72de09359f40e8a3089c76a216192a3ae1355c58d71f5e@ec2-3-229-127-203.compute-1.amazonaws.com:5432/d43p77fjhmtuf2"
Host = "ec2-3-229-127-203.compute-1.amazonaws.com"
Database = "d43p77fjhmtuf2"
Password = "0b338cb6d067f909fa72de09359f40e8a3089c76a216192a3ae1355c58d71f5e"
Port = "5432"


#Specific function to classify data of the clusterring
def Configure(configfile): 
     try: 
       data = open(CONFIG+"/"+str(configfile),'r') #Open the configuretion file for the path 
       datas = data.readline()
       transfer = json.loads(datas)
       return transfer
     except:
        print("Not found the configure file please check again")
def max_index_cal(dictdatakeys,dictdatavav):

         cal_max = list(dictdatavav)
         keys_cal_max = list(dictdatakeys)
         try: 
           max_index = max(cal_max)
           print(max_index,'Choosing',keys_cal_max[cal_max.index(max_index)])
           return max_index,keys_cal_max[cal_max.index(max_index)] 

         except:
             pass
def Matchingdata_cal(checkpackage,listheader): 
                percent=difflib.SequenceMatcher(None,checkpackage,listheader)
                #print("Match found:"+str(percent.ratio()*100)+"%") #Getting the percent matching 
                prob = percent.ratio()*100 # Calculate the percentage inside the list to find the max value in possibility detection 
                return  prob

def Get_fullPinpage_cal(configdata,pathselec,inputcomp):
                       
                                  Orderableoackage = configdata.get("Orderablepackage").get("Orderable") #Getting the package data from the search intersection                  
                                  Pinstable = configdata.get("Specific_pins").get("Pins_header")
                                  print("Getting the file path ",pathselec+inputcomp)  # file path           
                                  
                                  df = pd.read_csv(pathselec+inputcomp+".csv") 
                                  print("Header files",df.columns)
                                  probpinsdata = Matchingdata_cal(Pinstable,df.columns) # checking the columns matching data of the pins table inside the list 
                                  print("Matching prob",probpinsdata) # Checking the matching prob of the pins datatable   
                                  if probpinsdata >=40 and probpinsdata <= 100: # Checking if the data pins correct 100 percent inside the list
                                                check_pins_table[inputcomp] = probpinsdata # Getting the data of the page to calculate the right page to extract all pins to concatinate data together
                                                #Checking the orderlist
                                                probdata = Matchingdata_cal(Orderableoackage,df.columns)  
                                                print("Matching prob ",probdata)
                                                check_pack_order[inputcomp] = probdata # Getting the data of the page to calculate the right page matching probability 
                                                
for directr in range(0,len(directcreate)):
      try:
           os.mkdir(directcreate[directr],mode)
      except: 
          pass
for directr in directcreate:
          print("Give permission to directory =====> ",directr)
          os.system("echo 'Rkl3548123#' | sudo -S "+"sudo chmod -R 777 "+str(directr))  
list_path = ['TI_product','NXP_product','ST_product']
list_subpath = ['TI_motor_drive','TI_bms','TI_sensor','NXP_interfaces','NXP_multiplexer','ST_motordriver','ST_sensor','ST_microcontroller']
dict_manufacture = {'TI':'TI_product','NXP':'NXP_product','ST':'ST_product'}
dict_menudoct = {'TI_product':'TI_comdoc','NXP_product':'NXP_comdoc','ST_product':'ST_comdoc'} #component doct
part_select = {'motor':['TI_motor_drive','ST_motordriver']}
sub_doctpart = {'TI_motor_driver':['TI_BLDC_motor','TI_Stepper_motor','TI_DC_motor'],'TI_sensor':['TI_Encoder']}
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#Select PATH here ]
#example 
Comp_directory =  list(dict_manufacture)[0]

PATH_SELECT = HOME_PATH+dict_manufacture.get(list(dict_manufacture)[0]) + "/"+ list_subpath[0]+"/"
print("Path selected for manufacturer ",PATH_SELECT)
PATH_SUBSELECT =  HOME_PATH+dict_manufacture.get(list(dict_manufacture)[0]) + "/" 
print("Path sub select for components generated ",PATH_SUBSELECT) # Getting the path sub select file 
getdoct = dict_manufacture.get(list(dict_manufacture)[0])
create_comdoc = PATH_SUBSELECT+dict_menudoct.get(getdoct)+"/"
print("Create component_doct ", create_comdoc)

config_data = Configure(listConfig[0])
try: 
     print("Creating .....===>",create_comdoc)
     os.mkdir(create_comdoc,mode)
except: 
    pass
for ret in range(0,len(list_path)): 
     try:
         os.mkdir(list_path[ret],mode)
     except: 
         pass

for ret in range(0,len(list_subpath)): 
    try:
       verify = list_subpath[ret].split("_")[0]
         
       os.mkdir(dict_manufacture.get(verify)+"/"+list_subpath[ret],mode)
       
    except: 
        pass
for directr in list_path:
          print("Give permission to directory =====> ",directr)
          os.system("echo 'Rkl3548123#' | sudo -S "+"sudo chmod -R 777 "+str(directr))        

#listdir_data = os.listdir(EXTRACT)
#print(listdir_data)
listConfig = os.listdir(CONFIG)
print(listConfig[0])
#list docfile 
list_pdfdoc = os.listdir(PATH_SELECT)
print("Check path document",list_pdfdoc) #Using the list of the doc on processing the data 
Orderableoackage = config_data.get("Orderablepackage").get("Orderable") #Getting the package data from the search intersection                  
print("Order config data ",Orderableoackage)
configdata = Configure(listConfig[0])
Pinstable = configdata.get("Specific_pins").get("Pins_header")  # Getting the specific pins to classify the data matching 
for et in range(0,len(list_pdfdoc)):
                            
         pdf_list = list_pdfdoc[et].split(".")
         pdf_class = list_pdfdoc[et].split(".")[1]
         list_check_com = os.listdir(create_comdoc)
         print("Check the list in",Comp_directory+" ",list_check_com)
         print("Document docfile",list_pdfdoc[et]) 
         if list_pdfdoc[et].split(".")[0] not in list_check_com:
            
            if pdf_class == 'pdf': 
                  print(list_pdfdoc[et].split(".")[0]) # Create the document 
                  component_path_csv = create_comdoc+pdf_list[0]
                  try: 
                      print("Create component_path ",create_comdoc+pdf_list[0])
                      os.mkdir(component_path_csv,mode)   # Create the directory name here
                    
                  except: 
                      pass
                  #Running the loop of the total pdf file classification function 
                  try:
                     input1 = PdfFileReader(open(PATH_SELECT+"/"+pdf_list[0]+".pdf", "rb"))  #using oslist dir readding the file and extract all the value in the loop 
                  except:
                     input1 = PdfFileReader(open(PATH_SELECT+"/"+pdf_list[0].split("/")[1]+".pdf", "rb"))
                  print(pdf_list[0]+".pdf has %d pages." % input1.getNumPages())  # Getting the total pins of th page component 
                  total_page = input1.getNumPages()
                  for pagess in range(0,total_page): 
                      tables = camelot.read_pdf(PATH_SELECT+"/"+str(list_pdfdoc[et].split(".")[0])+".pdf",pages=str(pagess)) # Getting the pdf doc
                      print(list_pdfdoc[et].split(".")[0],len(tables)) # Getting the pdf file name and len(tables)
                      
                      if len(tables) > 0: 
                          for table in range(0,len(tables)): 
                                 print("Tables "+list_pdfdoc[et].split(".")[0]+"_"+str(pagess)+"_"+str(len(tables))) # Getting the page of the file and number list 
                                 #Naming the file name of the data 
                                 file_extract_name = list_pdfdoc[et].split(".")[0]+"_"+str(pagess)+"_"+str(len(tables)) # Getting the file name 
                                 #Now clreate the directory to generate the file into the components directory 
                                 print("Check sub select ",component_path_csv+"/"+file_extract_name) # Getting the file extract
                                 print(tables[table].df)
                                 tables[table].to_csv(component_path_csv+"/"+file_extract_name+".csv")
                                 
                      #Checking if the file is already done created directory and complete extracted csv file 
                      # If all requirement are done then created the function for running the pins extraction here   
                      if pagess+1 == total_page: 
                                 print("End of data sheet beginning extraction process......",str(pagess)+" pages") 
                                 print("Preparing new process........")
                                 file_ext = open('listerase.py','r')
                                 datafile = file_ext.readlines()
                                 
                                 #clear_check = ['check_pins_table','check_pack_order']
                                 #for re in clear_check:
                                         #print("Clearing list ====> ",re.split("=")[0]) 
                                         #exec(str(re)+".clear()") 
                                 
                                 #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                 #Doing the file extraction here 
                                 for table in range(0,len(tables)):
                                          try:
                                              Path_to_Expins = component_path_csv+"/" #+list_pdfdoc[et].split(".")[0]
                                              print("Extract Path",Path_to_Expins)
                                              list_expins = os.listdir(Path_to_Expins)
                                              #sorted_expins = sorted(list_expins,reverse=True) # reverse the list in the sort list to ordering the page data
                                              print("Sort list pages ",list_expins)
                                              for files_ex in range(0,len(list_expins)): 
                                                      print('Extract matching file data',list_expins[files_ex],list_expins[files_ex].split("_")[1]) 
                                                      Orderableoackage = config_data.get("Orderablepackage").get("Orderable") #Getting the package data from the search intersection                  
                                                      Pinstable = config_data.get("Specific_pins").get("Pins_header")
                                                      print("Getting the file path ",Path_to_Expins+list_expins[files_ex])  # file path           
                                                      df = pd.read_csv(Path_to_Expins+list_expins[files_ex].split(".")[0]+".csv")
                                                      print("Header",df.columns)
                                                      probpinsdata = Matchingdata_cal(Pinstable,df.columns) 
                                                      print("Matching probabilty: ",probpinsdata) 
                                                      #if probpinsdata >=40 and probpinsdata <= 100: # Checking if the data pins correct 100 percent inside the list
                                                      check_pins_table[list_expins[files_ex].split(".")[0]] = probpinsdata # Getting the data of the page to calculate the right page to extract all pins to concatinate data together
                                                      #Checking the orderlist
                                                      probdata = Matchingdata_cal(Orderableoackage,df.columns)  
                                                      print("Matching prob ",probdata)
                                                      check_pack_order[list_expins[files_ex].split(".")[0]] = probdata # Getting the data of the page to calculate the right page matching probability 
                                                      #Get_fullPinpage_cal(config_data,Path_to_Expins,list_expins[files_ex]) # Getting the full pins page 
                                          
                                          except:
                                              pass
                                 #Pins page calculation percentage
                                 
                                 print("List Pins ",check_pins_table)
                                 print("List Order ",check_pack_order)
                                 #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                 
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.
#Create the matching data after complete processing 

for r in range(0,len(check_pins_table)): 
                    #print("Checking the percentage of the data in array")
                    #print(list(check_pins_table)[r], check_datatype.get(list(check_pins_table)[r]))
                    matching_pins_percent = check_pins_table.get(list(check_pins_table)[r])
                    if matching_pins_percent > 40 and matching_pins_percent <= 100:
                                print("List pins percentage ",list(check_pins_table)[r].split("_")[0],list(check_pins_table)[r]) # Getting the pins percentage of the of the data extraction                              
                                Pins_Page_regroup[list(check_pins_table)[r]] = list(check_pins_table)[r].split("_")[0]
                               
for k in range(0,len(check_pack_order)):
                    #print("Checking the percentage of the data in array")
                    #print(list(check_pack_order)[k], check_pack_order.get(list(check_pack_order)[k]))
                    matching_order_percent = check_pack_order.get(list(check_pack_order)[k])
                    if matching_order_percent > 40 and matching_order_percent <= 100: 
                                      print("List order percentage ",list(check_pack_order)[k].split("_")[0],list(check_pack_order)[k]) # Getting the package order percentage of the data extraction 
                                      Order_page_regroup[list(check_pack_order)[k].split("_")[0]] = list(check_pack_order)[k]


print("Pins page regroup ", Pins_Page_regroup)
print("Order page regroup ", Order_page_regroup)  
print("Pins page regroup list fix")
for rt in range(0,len(Pins_Page_regroup)): 
            pins_mem_pack.append([])
            pins_mem_pack[rt].append(list(Pins_Page_regroup)[rt])
            #print(Pins_Page_regroup.get(list([Pins_Page_regroup])[rt]))
            #pins_reorder[Pins_Page_regroup.get(list([Pins_Page_regroup])[rt])] = pins_mem_pack[rt]

print(pins_mem_pack) # Getting the list of the page data             

#print(pins_reorder)
# Processing the table classification to select the type of the table classifiation management system 
#1.) First get the number of the pins of package to calculate the len of the column for ore pins needed on the list and adjust the pins porportionally 
#2.) Second calculate the table type and getting the data from the table 
#3.) Processing the data of the Pins classification like pins name pins I/O pins description and matching them 
#4.) Processing the data of the 
#for packs in range(0,len(Order_page_regroup)):
#          print("Componentname and Page",list(Order_page_regroup)[packs],Order_page_regroup.get(list(Order_page_regroup)[packs]))


#'''
for packs in range(0,len(Order_page_regroup)):
        print("Getting the component name from the page input") 
        mem_pins_info.append([])
        #print("Componentname and Page",list(Order_page_regroup)[packs],Order_page_regroup.get(list(Order_page_regroup)[packs]))
        #Calculate the package pins 
        #print("Path Package number ",Path_to_Expins+Order_page_regroup.get(list(Order_page_regroup)[packs])+".csv")
        Path_pack_read = create_comdoc+"/"+list(Order_page_regroup)[packs]+"/"+Order_page_regroup.get(list(Order_page_regroup)[packs])
        df = pd.read_csv(Path_pack_read+".csv") # Getting the columns in path 
        #print("Header",df.columns)
        #print("Split header",df.columns[0].split("\n"))
        Header_list_selector = df.columns[0].split("\n") # Getting the header list selector
        #print(list(Order_page_regroup)[packs]," Number of packaages ",len(df.values.tolist()))
        for ri in range(0,len(df.values.tolist())): 
             try:
                     Package_info = df.values.tolist()[ri][0].split("\n")
                     #print("Package ",str(ri)+" ",df.values.tolist()[ri][0].split("\n"),Package_info[0],Package_info[1],Package_info[2],Package_info[3],Package_info[4]) 
                     inputpackage = Package_info[0]
                     #Convert the upper_case to lower_case
                     for i in range (len(inputpackage)):
                          if inputpackage[i].isupper():
                                new_str =inputpackage[i].lower()
                          elif inputpackage[i].islower():
                                new_str =inputpackage[i].upper()
                          else:
                              new_str =inputpackage[i]
                     #Getting the string function to processing in the matching page of pins classification
                     
                     lower_case_package = new_str 
                     #Processing the pins classification and classify from all columns 
                     Path_pins_read = create_comdoc+list(Order_page_regroup)[packs]
                     for pins in range(0,len(Pins_Page_regroup)):  # Only get the pins package from the found list in the Order package list if not this will only actracted the package with the name in the order package list                                  
                           
                           print(Pins_Page_regroup.get(list(Pins_Page_regroup)[pins]))
                           
                           if Pins_Page_regroup.get(list(Pins_Page_regroup)[pins]) == list(Order_page_regroup)[packs]:
                                      
                                      print("Page pins match ", list(Pins_Page_regroup)[pins]) # Getting the page pins map data
                                      
                                      
                                      #Getting the data from the pins classification header 
                                      Getpath = Path_pins_read+"/"+list(Pins_Page_regroup)[pins]+".csv"
                                      print(Getpath)
                                      df = pd.read_csv(Getpath) #Getting the data frame 
                                      print("Columns header of Pins",df.columns,type(df.columns)) # Getting the data of columns header in the pins
                                      all_info_pack = df.values.tolist()
                                      row,col = df.shape 
                                      num_rc_map[list(Order_page_regroup)[packs]] = row,col 
                                      for io_dat in range(0,len(df.values.tolist())): 
                                                  #Getting the header pattern classifications
                                                  #try:
                                                        l_new=['missing' if x is np.nan else x for x in all_info_pack[io_dat]]
                                                        mynewlist = [s for s in l_new if s.isdigit()] # Getting the list of data pack by getting only the pins values 
                                                        if mynewlist != []:
                                                            print('Row scanning',list(Order_page_regroup)[packs],list(Pins_Page_regroup)[pins],df.values.tolist()[io_dat])
                                                            mem_pins_info[packs].append(df.values.tolist()[io_dat]) 
                                                            all_pins_info[list(Order_page_regroup)[packs]] = mem_pins_info[packs]
                                                            #print("Colum scanning",df.columns.values[io_dat],df[df.columns.values[io_dat]].values.tolist())
                                                        
                                                        #print("Pins data in table is lesser than package for ", str(int(Package_info[4])-len(df[df.columns.values[io_dat]].values.tolist()))," Package pins amount ",Package_info[4])
                                                  #except:
                                                  #      print("All data in the list are string beginning collect extraction")
             except:
                pass  
#print(all_pins_info)
print("#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
for pins in range(0,len(all_pins_info)): 
           print(list(all_pins_info)[pins],mem_pins_info[pins])
print("Getting the pins name data with page number")
print("Lenght of pins info ",len(mem_pins_info))
print("Lenght of page map ", len(all_pins_info))
try:
     print("Testing extraction data",list(all_pins_info)[pins],mem_pins_info[0])
except: 
     print("The file is complete extracted please update new datasheet")
print("Testing extract the data of package pins from the first list") 
try:
   Path_doc = create_comdoc+"/"+list(Order_page_regroup)[0]+"/"+Order_page_regroup.get(list(Order_page_regroup)[0])
   df = pd.read_csv(Path_doc+".csv")
   print(df.values.tolist()[0]) 
   print("Pack order detected ",check_pack_order)# Getting the list of the page where detected
   print("Order regroup ",Order_page_regroup)
except: 
    pass 
for pack_order in range(0,len(Order_page_regroup)): 
        print(list(Order_page_regroup)[pack_order])
        values = list(Order_page_regroup)[pack_order]
        print(values)

for t in range(0,len(mem_pins_info)):
   print(list(Order_page_regroup)[t],Order_page_regroup.get(list(Order_page_regroup)[t])) #Getting the page of the Order package data 
   print("Processing the number of each package pins") 
   Path_doc = create_comdoc+"/"+list(Order_page_regroup)[t]+"/"+Order_page_regroup.get(list(Order_page_regroup)[t])
   df = pd.read_csv(Path_doc+".csv")
   Header_list_selector = df.columns[0].split("\n") # Getting the header list selector
   print(Header_list_selector)
   row,col = df.shape # Getting the len of row and columns
   print("Row len ",df.shape)
   package_info = df.values.tolist()
   print(package_info)
   for ty in range(0,len(package_info)):        
           pack_list_info  = package_info[ty][0].split("\n")
           #print(pack_list_info)
           print(pack_list_info[0],pack_list_info[1],pack_list_info[2],pack_list_info[3],pack_list_info[4])
           packagename = pack_list_info[0]
           status = pack_list_info[1]
           packagetype = pack_list_info[2]     
           drawing = pack_list_info[3] 
           pinsnumber = pack_list_info[4]
           pack_map[list(Order_page_regroup)[t]] = pack_list_info
print(pack_map)
print("Number of row and columns reference data from each package")
print(num_rc_map)
for sub_t in range(0,len(mem_pins_info)):
   mem_pack_frame.append([])
   pack_map_data = pack_map.get(list(Order_page_regroup)[sub_t])
   print("Package information ",pack_map_data)  # Getting the package information 
   
   for r in range(0,len(mem_pins_info[sub_t])): 
        
        print(list(Order_page_regroup)[sub_t]," Pins NO. ",pack_map_data[0],pack_map_data[4]," List len ",len(mem_pins_info[sub_t]),mem_pins_info[sub_t][r])
        
        if int(len(mem_pins_info[sub_t])) == int(pack_map_data[4]):       
               print("Generated the data for pins I/O and description data into the dictionary")
               print("Generated package", list(Order_page_regroup)[sub_t],mem_pins_info[sub_t])  
               pack_subpackframe[list(Order_page_regroup)[sub_t]] = mem_pins_info[sub_t]
               break 
        if int(len(mem_pins_info[sub_t])) > int(pack_map_data[4]): 
                   print(list(Order_page_regroup)[sub_t]," Number of pins in pack lesser than ",int(pack_map_data[4])-int(len(mem_pins_info[sub_t])) ) 
                   for q in range(0,int(pack_map_data[4])): 
                            print(mem_pins_info[sub_t][q])
                            mem_pack_frame[sub_t].append(mem_pins_info[sub_t][q])
                   pack_subpackframe[list(Order_page_regroup)[sub_t]] = mem_pack_frame[sub_t]                             
        if int(len(mem_pins_info[sub_t])) < int(pack_map_data[4]): 
                   print(list(Order_page_regroup)[sub_t]," Number of pins in pack lesser than ",int(len(mem_pins_info[sub_t]))- int(pack_map_data[4])) 
   
   print("#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.") 
  
print(pack_subpackframe)
for rwe in range(0,len(pack_subpackframe)):
         #print(list(pack_subpackframe)[rwe],pack_subpackframe.get(list(pack_subpackframe)[rwe]))
         print(list(pack_subpackframe)[rwe])
#for rwe in range(0,len(pack_subpackframe)):
         #print(list(pack_subpackframe)[rwe],pack_subpackframe.get(list(pack_subpackframe)[rwe]))
#         data_pin_len = len(list(pack_subpackframe)[rwe][0]) 
#         for pins_name in range(0,len(list(pack_subpackframe)[rwe])):
#                  print(pack_subpackframe.get(list(pack_subpackframe)[rwe])[pins_name][0]) # Getting the first name of the pin in each device on the list data
jsonstring = json.dumps(pack_subpackframe) 
components_write = open(HOME_PATH+"e_components.json",'w') 
#Writing the json file into the home path directory to running the api data
components_write.write(jsonstring)  
components_write.close()                 
#'''
#for pins in range(0,len(Pins_Page_regroup)):
#        print("Getting the component name from the page input") 
#        print("Componentname and Page",list(Pins_Page_regroup)[pins],Pins_Page_regroup.get(list(Pins_Page_regroup)[pins]))
      
