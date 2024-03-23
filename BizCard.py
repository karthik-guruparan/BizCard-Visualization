
from os.path import isfile
from PIL import Image
import easyocr
import re
import mysql.connector as mysql
import streamlit as st
import pandas as pd
import os

def create_db_objects():
    connection=mysql.connect(
                            host='localhost',
                            user='root',
                            password='12345678',
                            port=3306,
                            auth_plugin='mysql_native_password'
                            )
    cursor=connection.cursor()

# DB CREATION
    try:
        query='''
                  CREATE DATABASE bizcard;
              '''
        cursor.execute(query)
        connection.commit()
        st.success('MySQL DB created')
    except:
        st.info('MySQL DB already exists')

# Table creation
    try:
        query='''
                  CREATE TABLE bizcard.bizcards(
                                                COMPANY_NAME  varchar(100),
                                                CARD_HOLDER   varchar(100),
                                                DESIGNATION   varchar(100),
                                                MOBILE_NUMBER varchar(100),
                                                EMAIL         varchar(100),
                                                WEBSITE       varchar(100),
                                                AREA          varchar(100),
                                                CITY          varchar(100),
                                                STATE         varchar(100),
                                                PINCODE       varchar(100)
                                                );
              '''
        cursor.execute(query)
        connection.commit()
        st.success('MySQL table created')
    except:
        st.info('MySQL table already exists')
        

def mysql_connect(query,data=None):
    if data is None:
        data=[]
    connection=mysql.connect(
                            host='localhost',
                            user='root',
                            password='12345678',
                            port=3306,
                            database='bizcard'
                            )
    cursor=connection.cursor()
    cursor.execute(query,data)
    connection.commit()
    return pd.DataFrame(cursor.fetchall())

filepath='../data/ocr/'
filepath_mod='../data/ocr/modified/'
file='2.png'
### to browse all image files in a location , resize then store in modified location
# files=os.listdir(filepath)
# for file in files:
#     data=filepath+file
#     if isfile(data): 
#         img=Image.open(data)
#         img=img.resize((800,500))
#         img.save(filepath_mod+file)
# img

data=filepath+file
img=Image.open(data)
img=img.resize((500,300))
img.save(filepath_mod+file)
reader=easyocr.Reader(['en'],gpu=False)
result_para=reader.readtext(filepath_mod+file,decoder='greedy',min_size=2,paragraph=True)
result=reader.readtext(filepath_mod+file,decoder='greedy',min_size=2,beamWidth=15,paragraph=False)

##Store info from image into data frame

# record={'COMPANY_NAME':[],'CARD_HOLDER':[],'DESIGNATION':[],'MOBILE_NUMBER':[],'EMAIL':[],'WEBSITE':[],'AREA':[],'CITY':[],'STATE':[],'PINCODE':[]}
# record['COMPANY_NAME'].append(result_para[len(result_para)-1][1]) ## Company name
# record['CARD_HOLDER'].append(result[0][1])## Cardholder name
# record['DESIGNATION'].append(result[1][1])## designation

# for data in result:
#     if re.search('[0-9]+-{1}[0-9]{3}-{1}[0-9]{4}',data[1]):
#         record['MOBILE_NUMBER'].append(data[1]) ## mobile number 
#     elif re.search('@',data[1]):
#         record['EMAIL'].append(data[1]) ## email address
#     elif re.search('[.]com',data[1]):
#         if re.search('^[wW]{3}',data[1]):
#             record['WEBSITE'].append(data[1]) #website URL
#         else:
#             record['WEBSITE'].append('www.'+data[1])       
#     elif len(re.findall(',',data[1]))>1:
#         location=[]
#         location=re.split(',',data[1])
#         location.remove('')
#         record['AREA'].append(location[0]) #area 
#         record['CITY'].append(location[1]) #city
#         record['STATE'].append(location[2]) #state
#     elif re.search('^[0-9]{6}',data[1]):
#         record['PINCODE'].append((data[1])) #pin code.
# df=pd.DataFrame(record)


for data in result:
    print(data[1])

for data in result_para:
    print(data[1])

COMPANY_NAME='' 
CARD_HOLDER='' 
DESIGNATION='' 
MOBILE_NUMBER=[]
EMAIL='' 
WEBSITE='' 
AREA='' 
CITY='' 
STATE='' 
PINCODE='' 

COMPANY_NAME=result_para[len(result_para)-1][1] ## Company name
CARD_HOLDER=result[0][1]## Cardholder name
DESIGNATION=result[1][1]## designation

for data in result:
    if re.search('[0-9]+-{1}[0-9]{3}-{1}[0-9]{4}',data[1]):
        MOBILE_NUMBER.append(data[1]) ## mobile number 
    elif re.search('@',data[1]):
        EMAIL=data[1] ## email address
    elif re.search('com',data[1]) :
        if re.search('^[wW]{3}',data[1].lower().replace('www','')):
            WEBSITE=data[1] #website URL
        else:
            WEBSITE='www.'+data[1].lower().replace('www','').replace(' ','')      
    elif len(re.findall(',',data[1]))>1:
        location=[]
        try:
            location=re.split(',',data[1])
            location.remove('')
            AREA=location[0] #area 
        except:
            pass
        try:
            CITY=location[1] #city
        except:
            pass 
        try:
            STATE=location[2] #state
        except:
            pass
    elif re.search('^[0-9]{6}',data[1]):
        PINCODE=data[1] #pin code.
value=(COMPANY_NAME,CARD_HOLDER,DESIGNATION,','.join(MOBILE_NUMBER),EMAIL,WEBSITE,AREA,CITY,STATE,PINCODE)
value

create_db_objects()
# Insert data into bizcard table
query=''' INSERT INTO bizcard.bizcards (COMPANY_NAME,CARD_HOLDER,DESIGNATION,MOBILE_NUMBER,EMAIL,WEBSITE,AREA,CITY,STATE,PINCODE) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); '''
OUTPUT=mysql_connect(query,value)

