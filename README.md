# BizCard-Visualization

## Objective
To build a streamlit application which allows users to upload and the scan business cards. The scanned data should be stored in a database and should be accessible on the streamlit UI for the user to update or delete the entries easily.

## Project pre-requisites
To execute this app on your machine, ensure to have the following configured in your machine.
1. Install Python virtual environment in desired folder  (https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
2. Python latest version (https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe)
3. Once you have the venv environment configured,go to installed path and access virtual environment by executing the following in windows command line

           'venv\Scripts\activate.bat'
4. Once you have activated virtual environment, install python packagages highlighted below using the syntax 

   
        pip install os
        pip install PIL 
        pip install streamlit_js_eval
        pip install streamlit
        pip install easyocr
        pip install re
        pip install mysql.connector
        pip install pandas
5. As I have used MySQL workbench as DB, I would recommend installing the same. Although you may install DB of your choice but you may need to alter the sql based on the DB's syntax. (https://dev.mysql.com/downloads/installer/)

## Code walkthrough
1. First we import required packages as shown below

                                 from os.path import isfile
                                 from PIL import Image
                                 from streamlit_js_eval import streamlit_js_eval
                                 import streamlit as st
                                 import easyocr
                                 import re
                                 import mysql.connector as mysql
                                 import pandas as pd
                                 import os

2. Enter the path where you have the business card images in the "filepath" variable and path where modified images need to be stored in "filepath_mod" variable.

                                    filepath='../data/ocr/'
                                    filepath_mod='../data/ocr/modified/'
   
4. The following functions  will create the required MySQL DB objects.

                         def create_db_objects():
                          connection=mysql.connect(
                                                  host='localhost',
                                                  user='root',
                                                  password='12345678',
                                                  port=3306,
                                                  auth_plugin='mysql_native_password'
                                                  )
                          cursor=connection.cursor(buffered=True)
                      
                      
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
                                                                     `ID` BIGINT NOT NULL AUTO_INCREMENT,
                                                                      COMPANY_NAME  varchar(100),
                                                                      CARD_HOLDER   varchar(100),
                                                                      DESIGNATION   varchar(100),
                                                                      MOBILE_NUMBER varchar(100),
                                                                      EMAIL         varchar(100),
                                                                      WEBSITE       varchar(100),
                                                                      AREA          varchar(100),
                                                                      CITY          varchar(100),
                                                                      STATE         varchar(100),
                                                                      PINCODE       varchar(100),
                                                                      MODIFIER TINYINT NOT NULL DEFAULT 0 ,
                                                                      PRIMARY KEY (`ID`)
                                                                      );
                                    '''
                              cursor.execute(query)
                              connection.commit()
                              st.success('MySQL table created')
                          except:
                              st.info('MySQL table already exists')
                              pass

5. The following functions scan the business card images and queries the database.

           def scan_and_read_image(file):
               data=filepath+file
               img=Image.open(data)
               img=img.resize((500,300)) # Resizing the image
               img.save(filepath_mod+file)
               reader=easyocr.Reader(['en'],gpu=False) 
               result_para=reader.readtext(filepath_mod+file,decoder='greedy',min_size=2,paragraph=True) # Scan the image
               result=reader.readtext(filepath_mod+file,decoder='greedy',min_size=2,beamWidth=15,paragraph=False) # Scan the image
               # Variables for data storage
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
               
           #    for data in result_para:
           #        st.write('para',data[1])
               
               for data in result:
           #        st.write(data[1])
                   if re.search('[0-9]+-{1}[0-9]{3}-{1}[0-9]{4}',data[1]):
                       if re.search('[+]',data[1]):
                           MOBILE_NUMBER.append(data[1]) ## mobile number
                       else:
                           MOBILE_NUMBER.append('+'+data[1])
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
                   elif re.search('St',data[1]):
                       try:
                           AREA=data[1] #area 
                           if re.search('\s',data[1]):
                               try:
                                   temp=re.split(' ',data[1])
                                   STATE=temp[len(temp)-1] #state
                               except:
                                   pass  
                           if re.search(',',data[1]):
                               try:
                                   data[1]=data[1].replace(' ',',')
                                   temp=re.split(',',data[1])
                                   city=temp[len(temp)-2] # city
                               except:
                                   pass                                        
                       except:
                           pass   
                   elif re.search('[0-9]{6}',data[1]):
                       temp=re.split(' ',data[1])
                       PINCODE=[x for x in temp if x.isdigit()] #pin code.                
                       if re.search('\s',data[1]):
                           try:
                               temp=re.split('\s',data[1])
                               STATE=temp[0] #state
                           except:
                               pass
           
               value=(COMPANY_NAME,CARD_HOLDER,DESIGNATION,','.join(MOBILE_NUMBER),EMAIL,WEBSITE,AREA,CITY,STATE,''.join(PINCODE),0)
               # Insert data into bizcard table
               query=''' INSERT INTO bizcard.bizcards (COMPANY_NAME,CARD_HOLDER,DESIGNATION,MOBILE_NUMBER,EMAIL,WEBSITE,AREA,CITY,STATE,PINCODE,MODIFIER) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); '''
               df,query_status=query_db(query,value)
               st.success(f'Card holder {CARD_HOLDER}\'s details have been scanned')
               return query_status
           
               def query_db(query,data=None):
               if data is None:
                   data=[]
               connection=mysql.connect(
                                       host='localhost',
                                       user='root',
                                       password='12345678',
                                       port=3306,
                                       database='bizcard'
                                       )
               cursor=connection.cursor(buffered=True)
               cursor.execute(query,data)
               row_count=cursor.rowcount
               connection.commit()
               cursor.execute(''' select * FROM bizcard.bizcards where ID is not null;''')
               connection.commit()
               return pd.DataFrame(cursor.fetchall()),row_count

6.The following code will define the streamlit app and its components like tabs , columns ,buttons , dataframe.

           ## Streamlit part
           st.set_page_config(layout="wide")
           st.title(':green[BizCard Scanner]')
           st.divider()
           try:
           #    with st.container(height=500):
               tab1,tab2=st.tabs(['1.Upload and Scan BizCard','2.View and Modify Details'])
               with tab1: 
                   st.write('\n\n')
                   if tab1:        
                       uploaded_files = st.file_uploader("Browse image file(s) to upload and scan", accept_multiple_files=True)
                       if uploaded_files:
                           create_db_objects()
                           for file in uploaded_files:
                               query_status=scan_and_read_image(file.name)
                           streamlit_js_eval(js_expressions="parent.window.location.reload()") # Refresh page after executing query
               
           
               with tab2:
           #            with st.container(height=350):
                   st.write('\n\n')
                   st.subheader('MySQL data')
                   query1=''' SELECT * FROM bizcard.bizcards;'''
                   df,query_status=query_db(query1)
                   df.rename(columns={0:'ROW_ID',1:'COMPANY_NAME', 2:'CARD_HOLDER', 3:'DESIGNATION', 4:'MOBILE_NUMBER', 5:'EMAIL', 6:'WEBSITE', 7:'AREA', 8:'CITY', 9:'STATE', 10:'PINCODE', 11:'MODIFIER'},inplace=True)
                   df['MODIFIER']=df['MODIFIER'].astype({'MODIFIER': 'bool'})
                   st.data_editor(df[['COMPANY_NAME','CARD_HOLDER','DESIGNATION','MOBILE_NUMBER','EMAIL','WEBSITE','AREA','CITY','STATE','PINCODE','MODIFIER']],
                   column_config={
                       "MODIFIER": st.column_config.CheckboxColumn(
                           "Delete",
                           help="check the box if you want delete the row",
                           default=False
                       )
                   },
                   
                   num_rows="dynamic",
                   key='id_key',
                   hide_index=True)
                   col1,col2,col3=st.columns(3)
                   with col1:
                       update=st.button('Submit Changes')
                       if update:
           #                st.write(st.session_state['id_key'])
                           edits=st.session_state['id_key']
           #                st.write('Edits made by user:',edits)
                           for item in edits["edited_rows"]:
                               modification=[]
                               deletes=[]                    
                               mod_row=df.loc[item]['ROW_ID']           
                               # 1 get company name
                               try:
                                   modification.append(' COMPANY_NAME=\''+edits["edited_rows"][item]['COMPANY_NAME']+'\'')
                               except:
                                   pass
                               # 2 get CARD_HOLDER
                               try:
                                   modification.append(' CARD_HOLDER=\''+edits["edited_rows"][item]['CARD_HOLDER']+'\'') 
                               except:
                                   pass                 
                               # 3 get DESIGNATION
                               try:
                                   modification.append(' DESIGNATION=\''+edits["edited_rows"][item]['DESIGNATION']+'\'') 
                               except:
                                   pass                                    
                               # 2 get MOBILE_NUMBER
                               try:
                                   modification.append(' MOBILE_NUMBER=\''+edits["edited_rows"][item]['MOBILE_NUMBER']+'\'') 
                               except:
                                   pass                                 
                               # 5 get EMAIL
                               try:
                                   modification.append(' EMAIL=\''+edits["edited_rows"][item]['EMAIL']+'\'') 
                               except:
                                   pass                                 
                               # 6 get WEBSITE
                               try:
                                   modification.append(' WEBSITE=\''+edits["edited_rows"][item]['WEBSITE']+'\'') 
                               except:
                                   pass                                 
                               # 8 get AREA
                               try:
                                   modification.append(' AREA=\''+edits["edited_rows"][item]['AREA']+'\'') 
                               except:
                                   pass                                 
                               # 9 get CARD_HOLDER
                               try:
                                   modification.append(' CITY=\''+edits["edited_rows"][item]['CITY']+'\'') 
                               except:
                                   pass   
                               # 10 get STATE
                               try:
                                   modification.append(' STATE=\''+edits["edited_rows"][item]['STATE']+'\'') 
                               except:
                                   pass                       
                               # 10 get PINCODE
                               try:
                                   modification.append(' PINCODE=\''+edits["edited_rows"][item]['PINCODE']+'\'') 
                               except:
                                   pass  
                               # delete rows
                               try:
                                   delete=edits["edited_rows"][item]['MODIFIER']             
                                   if delete==True:
                                       del_row=df.loc[item]['ROW_ID']
                                       query='delete from bizcard.bizcards WHERE ID='+str(del_row)+';'
                                       df_out,status=query_db(query)                        
                               except:
                                   pass  
                               ## Update rows    
                               try:    
                                   query='UPDATE bizcard.bizcards SET '+','.join(modification)+' WHERE ID='+str(mod_row)+';'
                                   df_out,status=query_db(query)
                               except:
                                   pass
                               
                   with col2:
                       refresh=st.button('Refresh')
                       if refresh:
           #                streamlit_js_eval(js_expressions="parent.window.location.reload()") # Refresh page after executing query
                           pass
                   with col3:
                       if st.button('Remove duplicates'):
                           query=''' WITH DATASET AS (SELECT ROW_NUMBER() OVER(PARTITION BY COMPANY_NAME,CARD_HOLDER,DESIGNATION,MOBILE_NUMBER,EMAIL,WEBSITE,AREA,CITY,STATE,PINCODE)ROW_NUM,
                                   `bizcards`.`ID`,
                                   `bizcards`.`COMPANY_NAME`,
                                   `bizcards`.`CARD_HOLDER`,
                                   `bizcards`.`DESIGNATION`,
                                   `bizcards`.`MOBILE_NUMBER`,
                                   `bizcards`.`EMAIL`,
                                   `bizcards`.`WEBSITE`,
                                   `bizcards`.`AREA`,
                                   `bizcards`.`CITY`,
                                   `bizcards`.`STATE`,
                                   `bizcards`.`PINCODE`,
                                   `bizcards`.`MODIFIER`
                                                       FROM `bizcard`.`bizcards`)
                                   DELETE FROM `bizcard`.`bizcards`
                                   WHERE ID IN  
                                   (SELECT ID FROM DATASET A WHERE ROW_NUM>1);
                                    '''
                           query_db(query)
                           streamlit_js_eval(js_expressions="parent.window.location.reload()") # Refresh page after executing query
           except:
               pass

## Application walkthrough
1. Once the pre-requisites are achieved activate the virtual environment and run the following command.

                                 Streamlit run BizCard.py
2. The default browser will open and display the app as shown below

![image](https://github.com/karthik-guruparan/BizCard-Visualization/assets/77478705/2c71b28e-06b3-4bb2-9b95-b5549b2f159c)

3. Click on the browse file option and select the business card image files and click open.

![image](https://github.com/karthik-guruparan/BizCard-Visualization/assets/77478705/1239316f-258b-457c-8d92-274240e03521)

4. The application will attempt to create MySQL DB objects (schema and table) followed by insertion of card holder details.

![image](https://github.com/karthik-guruparan/BizCard-Visualization/assets/77478705/be4afe42-0182-46dd-97e2-f52e90d4b7e7)

5. Once the scanned data is inserted, click on the second tab '2.View and Modify Details'. The scanned details will be visible as seen below.
![image](https://github.com/karthik-guruparan/BizCard-Visualization/assets/77478705/f03b245e-f9a2-4cf0-aa2f-d68de7184f26)

6. The user can edit the cells as required and can even delete the rows by checking the checkboxes on the delete column as shown below.
![image](https://github.com/karthik-guruparan/BizCard-Visualization/assets/77478705/97d5ea81-f503-4207-b76c-0d2086a45603)

![image](https://github.com/karthik-guruparan/BizCard-Visualization/assets/77478705/5adbe67b-b828-4ef8-905b-68ebebbbeaee)

7. Once the changes have been made , click on the submit button and then the refresh button.

![image](https://github.com/karthik-guruparan/BizCard-Visualization/assets/77478705/f40d82d2-0f34-40d1-b0f9-093124e057e4)

8. If there are duplicate entries the user can clear the duplicates by clicking the 'Remove duplicates' button.

   ![image](https://github.com/karthik-guruparan/BizCard-Visualization/assets/77478705/bbaadc41-680c-4601-acfb-7a360113e528)

![image](https://github.com/karthik-guruparan/BizCard-Visualization/assets/77478705/cbace5a9-f390-4afb-a417-1be67fbdc3a6)



   
