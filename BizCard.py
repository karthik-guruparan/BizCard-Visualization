
from os.path import isfile
from PIL import Image
import easyocr
import re
import mysql.connector as mysql
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import pandas as pd
import os

filepath='../data/ocr/'
filepath_mod='../data/ocr/modified/'

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

def scan_and_read_image(file):
    data=filepath+file
    img=Image.open(data)
    img=img.resize((500,300))
    img.save(filepath_mod+file)
    reader=easyocr.Reader(['en'],gpu=False)
    result_para=reader.readtext(filepath_mod+file,decoder='greedy',min_size=2,paragraph=True)
    result=reader.readtext(filepath_mod+file,decoder='greedy',min_size=2,beamWidth=15,paragraph=False)

    # # to browse all image files in a location , resize then store in modified location
    # files=os.listdir(filepath)
    # for file in files:
    #     data=filepath+file
    #     if isfile(data): 
    #         img=Image.open(data)
    #         img=img.resize((800,500))
    #         img.save(filepath_mod+file)

    # record={'COMPANY_NAME':[],'CARD_HOLDER':[],'DESIGNATION':[],'MOBILE_NUMBER':[],'EMAIL':[],'WEBSITE':[],'AREA':[],'CITY':[],'STATE':[],'PINCODE':[]}
    # ## Scan biz card and Store info from image into data frame
    # new_files=os.listdir(filepath_mod)
    # for file in new_files:
    #     data=filepath_mod+file
    #     reader=easyocr.Reader(['en'],gpu=False)
    #     result_para=reader.readtext(filepath_mod+file,decoder='greedy',min_size=2,paragraph=True)
    #     result=reader.readtext(filepath_mod+file,decoder='greedy',min_size=2,beamWidth=15,paragraph=False)
    #     record['COMPANY_NAME'].append(result_para[len(result_para)-1][1]) ## Company name
    #     record['CARD_HOLDER'].append(result[0][1])## Cardholder name
    #     record['DESIGNATION'].append(result[1][1])## designation
        
    #     for data in result:
    #         if re.search('[0-9]+-{1}[0-9]{3}-{1}[0-9]{4}',data[1]):
    #             record['MOBILE_NUMBER'].append(data[1]) ## mobile number 
    #         elif re.search('@',data[1]):
    #             record['EMAIL'].append(data[1]) ## email address
            # elif re.search('[.]com',data[1]):
    #             if re.search('^[wW]{3}',data[1]):
    #                 record['WEBSITE'].append(data[1]) #website URL
    #             else:
    #                 record['WEBSITE'].append('www.'+data[1])       
    #         elif len(re.findall(',',data[1]))>1:
    #             location=[]
    #             location=re.split(',',data[1])
    #             location.remove('')
    #             record['AREA'].append(location[0]) #area 
    #             record['CITY'].append(location[1]) #city
    #             record['STATE'].append(location[2]) #state
    #         elif re.search('^[0-9]{6}',data[1]):
    #             record['PINCODE'].append((data[1])) #pin code.
    # df=pd.DataFrame(record)


    # for data in result:
        # print(data[1])

#   for data in result_para:
#       print(data[1])

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
        elif re.search('[0-9]{6}',data[1]):
            temp=re.split(' ',data[1])
            PINCODE=[x for x in temp if x.isdigit()] #pin code.
    value=(COMPANY_NAME,CARD_HOLDER,DESIGNATION,','.join(MOBILE_NUMBER),EMAIL,WEBSITE,AREA,CITY,STATE,''.join(PINCODE),0)
    # Insert data into bizcard table
    st.write(value)
    query=''' INSERT INTO bizcard.bizcards (COMPANY_NAME,CARD_HOLDER,DESIGNATION,MOBILE_NUMBER,EMAIL,WEBSITE,AREA,CITY,STATE,PINCODE,MODIFIER) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); '''
    df,query_status=query_db(query,value)
    return query_status

## Streamlit part
st.set_page_config(layout="wide")
st.title(':green[BizCard Scanner]')
st.divider()
tab1,tab2,tab3=st.tabs(['1.Upload and Scan BizCard','2.View Details','3.Modify Details'])
with tab1: 
    st.write('\n\n')
    uploaded_files = st.file_uploader("Browse image file(s) to upload and scan", accept_multiple_files=True)
    if uploaded_files:
        create_db_objects()
        for file in uploaded_files:
            query_status=scan_and_read_image(file.name)
            st.write(f'Rows affected:{query_status}')
with tab2:
    st.write('\n\n')
    st.subheader('Data in MySQL')
    if tab2:
        query1=''' SELECT ID,COMPANY_NAME,CARD_HOLDER,DESIGNATION,MOBILE_NUMBER,EMAIL,WEBSITE,AREA,CITY,STATE,PINCODE FROM bizcard.bizcards;'''
        df1,query_status=query_db(query1)
        df1.rename(columns={0:'ROW_ID',1:'COMPANY_NAME', 2:'CARD_HOLDER', 3:'DESIGNATION', 4:'MOBILE_NUMBER', 5:'EMAIL', 6:'WEBSITE', 7:'AREA', 8:'CITY', 9:'STATE', 10:'PINCODE'},inplace=True)
        st.write(df1[df1.columns[0:-1]])

with tab3:
    st.write('\n\n')
    st.subheader('Modify Data in MySQL')
    query1=''' SELECT * FROM bizcard.bizcards;'''
    df,query_status=query_db(query1)
#    st.write('data from function:',df)
    df.rename(columns={0:'ROW_ID',1:'COMPANY_NAME', 2:'CARD_HOLDER', 3:'DESIGNATION', 4:'MOBILE_NUMBER', 5:'EMAIL', 6:'WEBSITE', 7:'AREA', 8:'CITY', 9:'STATE', 10:'PINCODE', 11:'MODIFIER'},inplace=True)
#    st.write('df:',df)
    df['MODIFIER']=df['MODIFIER'].astype({'MODIFIER': 'bool'})
    st.data_editor(df,
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
    col1,col2=st.columns(2)
    with col1:
        update=st.button('Update details')
        if update:
#            st.write(st.session_state['id_key'])
            modification=[]
            deletes=[]
            edits=st.session_state['id_key']
#            st.write('Edits made by user:',edits)
            for item in edits["edited_rows"]:
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
                # 11 MODIFIER
                try:
                    delete=edits["edited_rows"][item]['MODIFIER']             
                    if delete==True:
                        del_row=df.loc[item]['ROW_ID']  
                except:
                    pass  
                query='UPDATE bizcard.bizcards SET '+','.join(modification)+' WHERE ID='+str(mod_row)+';'
                df_out,status=query_db(query)
                streamlit_js_eval(js_expressions="parent.window.location.reload()") # Refresh page after executing query
