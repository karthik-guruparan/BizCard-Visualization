import easyocr
import re
import mysql.connector as mysql
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_js_eval import streamlit_js_eval


FILEPATH = '../data/ocr/'
FILEPATH_MOD = '../data/ocr/modified/'


def create_db_objects():
    connection = mysql.connect(
        host='localhost',
        user='root',
        password='12345678',
        port=3306,
        auth_plugin='mysql_native_password'
    )
    cursor = connection.cursor(buffered=True)


# DB CREATION
    try:
        query1 = '''
                  CREATE DATABASE bizcard;
              '''
        cursor.execute(query1)
        connection.commit()
        st.success('MySQL DB created')
    except Exception:
        st.info('MySQL DB already exists')

# Table creation
    try:
        query2 = '''
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
        cursor.execute(query2)
        connection.commit()
        st.success('MySQL table created')
    except Exception:
        st.info('MySQL table already exists')


def query_db(query, data=None):
    if data is None:
        data = []
    connection = mysql.connect(
        host='localhost',
        user='root',
        password='12345678',
        port=3306,
        database='bizcard'
    )
    cursor = connection.cursor(buffered=True)
    cursor.execute(query, data)
    row_count = cursor.rowcount
    connection.commit()
    cursor.execute(''' select * FROM bizcard.bizcards where ID is not null;''')
    connection.commit()
    sql_output = cursor.fetchall()
    return pd.DataFrame(sql_output), row_count, sql_output


def scan_and_read_image(file):
    data = FILEPATH+file
    img = Image.open(data)
    img = img.resize((500, 300))  # Resizing the image
    img.save(FILEPATH_MOD+file)
    reader = easyocr.Reader(['en'], gpu=False)
    result_para = reader.readtext(
        FILEPATH_MOD+file, decoder='greedy', min_size=2, paragraph=True)  # Scan the image
    result = reader.readtext(FILEPATH_MOD+file, decoder='greedy',
                             min_size=2, beamWidth=15, paragraph=False)  # Scan the image
    # Variables for data storage
    COMPANY_NAME = ''
    CARD_HOLDER = ''
    DESIGNATION = ''
    MOBILE_NUMBER = []
    EMAIL = ''
    WEBSITE = ''
    AREA = ''
    CITY = ''
    STATE = ''
    PINCODE = ''

    COMPANY_NAME = result_para[len(result_para)-1][1]  # COMPany name
    CARD_HOLDER = result[0][1]  # Cardholder name
    DESIGNATION = result[1][1]  # DESIGNATION

#    for data in result_para:
#        st.write('para',data[1])

    for data in result:
        #        st.write(data[1])
        if re.search('[0-9]+-{1}[0-9]{3}-{1}[0-9]{4}', data[1]):
            if re.search('[+]', data[1]):
                MOBILE_NUMBER.append(data[1])  # mobile number
            else:
                MOBILE_NUMBER.append('+'+data[1])
        elif re.search('@', data[1]):
            EMAIL = data[1]  # email address
        elif re.search('com', data[1]):
            if re.search('^[wW]{3}', data[1].lower().replace('www', '')):
                WEBSITE = data[1]  # website URL
            else:
                WEBSITE = 'www.' + \
                    data[1].lower().replace('www', '').replace(' ', '')
        elif len(re.findall(',', data[1])) > 1:
            location = []
            try:
                location = re.split(',', data[1])
                location.remove('')
                AREA = location[0]  # area
            except Exception:
                pass
            try:
                CITY = location[1]  # city
            except Exception:
                pass
            try:
                STATE = location[2]  # state
            except Exception:
                pass
        elif re.search('St', data[1]):
            try:
                AREA = data[1]  # area
                if re.search('\s', data[1]):
                    try:
                        temp = re.split(' ', data[1])
                        STATE = temp[len(temp)-1]  # state
                    except Exception:
                        pass
                if re.search(',', data[1]):
                    try:
                        data[1] = data[1].replace(' ', ',')
                        temp = re.split(',', data[1])
                        city = temp[len(temp)-2]  # city
                    except Exception:
                        pass
            except Exception:
                pass
        elif re.search('[0-9]{6}', data[1]):
            temp = re.split(' ', data[1])
            PINCODE = [x for x in temp if x.isdigit()]  # pin code.
            if re.search('\s', data[1]):
                try:
                    temp = re.split('\s', data[1])
                    STATE = temp[0]  # state
                except Exception:
                    pass

    value = (COMPANY_NAME, CARD_HOLDER, DESIGNATION, ','.join(
        MOBILE_NUMBER), EMAIL, WEBSITE, AREA, CITY, STATE, ''.join(PINCODE), 0)
    # Insert data into bizcard table
    query = ''' INSERT INTO bizcard.bizcards (COMPANY_NAME,CARD_HOLDER,DESIGNATION,MOBILE_NUMBER,EMAIL,WEBSITE,AREA,CITY,STATE,PINCODE,MODIFIER) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); '''
    df, query_status, output = query_db(query, value)
    query = ''' select * FROM bizcard.bizcards where ID is not null;'''
    df, query_status, output = query_db(query)
    st.success(f'Card holder {CARD_HOLDER}\'s details have been scanned')
    return query_status


def refresh():
    pass


# Streamlit part
st.set_page_config(layout="wide")
st.title(':green[BizCard Scanner]')
st.divider()
try:
    #    with st.container(height=500):
    tab1, tab2, tab3 = st.tabs(['1.Upload and Scan BizCard',
                                '2.Form layout', '3.Table Layout'])
    with tab1:
        st.write('\n\n')
        if tab1:
            uploaded_files = st.file_uploader(
                "Browse image file(s) to upload and scan", accept_multiple_files=True)
            if uploaded_files:
                create_db_objects()
                for file in uploaded_files:
                    query_status = scan_and_read_image(file.name)
                # Refresh page after executing query
                streamlit_js_eval(
                    js_expressions="parent.window.location.reload()")
    
    with tab2:
        #            with st.container(height=350):
        st.write('\n\n')
        st.subheader('MySQL data')
        query1 = 'SELECT * FROM bizcard.bizcards where id is not null;'
        df2, query_status, output = query_db(query1)
        user = st.selectbox('User details', df2[2])
    
        if user:
            query1 = f'''SELECT * FROM (SELECT * FROM bizcard.bizcards where id is not null )a where CARD_HOLDER='{user}' ;'''
            connection = mysql.connect(
                host='localhost',
                user='root',
                password='12345678',
                port=3306,
                database='bizcard'
            )
            cursor = connection.cursor(buffered=True)
            cursor.execute(query1)
            connection.commit()
            output = cursor.fetchall()
            df, output = pd.DataFrame(output), output
            st.session_state.rowid = output[0][0]
        with st.form('form'):
            st.text_input('COMPany', str(output[0][1]), key='COMP')
            st.text_input('DESIGNATION', str(output[0][3]), key='DESIGNATION')
            st.text_input('MobileNumber', str(output[0][4]), key='Mobile')
            st.text_input('Email', str(output[0][5]), key='Email')
            st.text_input('Website', str(output[0][6]), key='Website')
            st.text_input('Area', str(output[0][7]), key='Area')
            st.text_input('City', str(output[0][8]), key='City')
            st.text_input('State', str(output[0][9]), key='State')
            st.text_input('Pincode', str(output[0][10]), key='Pincode')
    
            #       Capture session state as variables
            COMP = str(st.session_state.COMP).replace('\'', '')
            DESIGNATION = str(st.session_state.DESIGNATION).replace('\'', '')
            Mobile = st.session_state.Mobile
            Email = st.session_state.Email
            Website = st.session_state.Website
            Area = st.session_state.Area
            City = st.session_state.City
            State = st.session_state.State
            Pincode = st.session_state.Pincode
            row_id = st.session_state.rowid
    
            update_query = f'''update bizcards set COMPANY_NAME  ='{COMP}'
                            ,DESIGNATION   ='{DESIGNATION}'
                            ,MOBILE_NUMBER ='{Mobile}'
                            ,EMAIL         ='{Email}'
                            ,WEBSITE       ='{Website}'
                            ,AREA          ='{Area}'
                            ,CITY          ='{City}'
                            ,STATE         ='{State}'
                            ,PINCODE       ='{Pincode}'   
                            where ID={row_id};'''
    
            col1, col2, col3 = st.columns(3)
            with col1:
                submitted = st.form_submit_button("Submit")
                if submitted:
                    query_db(update_query)
                    refresh()
            with col2:
                refresh = st.form_submit_button('Refresh')
                if refresh:
                    pass
    
            with col3:
                delete_query = f'''DELETE FROM `bizcard`.`bizcards` WHERE ID={row_id};'''
                delete = st.form_submit_button('Delete details')
                if delete:
                    query_db(delete_query)
    
    with tab3:
        #            with st.container(height=350):
        st.write('\n\n')
        st.subheader('MySQL data')
        query1 = ''' SELECT * FROM bizcard.bizcards;'''
        df, query_status, output = query_db(query1)
        df.rename(columns={0: 'ROW_ID', 1: 'COMPANY_NAME', 2: 'CARD_HOLDER', 3: 'DESIGNATION', 4: 'MOBILE_NUMBER',
                        5: 'EMAIL', 6: 'WEBSITE', 7: 'AREA', 8: 'CITY', 9: 'STATE', 10: 'PINCODE', 11: 'MODIFIER'}, inplace=True)
        df['MODIFIER'] = df['MODIFIER'].astype({'MODIFIER': 'bool'})
        st.data_editor(df[['COMPANY_NAME', 'CARD_HOLDER', 'DESIGNATION', 'MOBILE_NUMBER', 'EMAIL', 'WEBSITE', 'AREA', 'CITY', 'STATE', 'PINCODE', 'MODIFIER']],
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
        col1, col2, col3 = st.columns(3)
    #    st.write(edits)
        with col1:
            update = st.button('Submit Changes')
            if update:
                edits = st.session_state['id_key']
                for item in edits["edited_rows"]:
                    modification = []
                    deletes = []
                    mod_row = df.loc[item]['ROW_ID']
                    # 1 get COMPany name
                    try:
                        modification.append(
                            ' COMPANY_NAME=\''+edits["edited_rows"][item]['COMPANY_NAME']+'\'')
                    except Exception:
                        pass
                    # 2 get CARD_HOLDER
                    try:
                        modification.append(
                            ' CARD_HOLDER=\''+edits["edited_rows"][item]['CARD_HOLDER']+'\'')
                    except Exception:
                        pass
                    # 3 get DESIGNATION
                    try:
                        modification.append(
                            ' DESIGNATION=\''+edits["edited_rows"][item]['DESIGNATION']+'\'')
                    except Exception:
                        pass
                    # 2 get MOBILE_NUMBER
                    try:
                        modification.append(
                            ' MOBILE_NUMBER=\''+edits["edited_rows"][item]['MOBILE_NUMBER']+'\'')
                    except Exception:
                        pass
                    # 5 get EMAIL
                    try:
                        modification.append(
                            ' EMAIL=\''+edits["edited_rows"][item]['EMAIL']+'\'')
                    except Exception:
                        pass
                    # 6 get WEBSITE
                    try:
                        modification.append(
                            ' WEBSITE=\''+edits["edited_rows"][item]['WEBSITE']+'\'')
                    except Exception:
                        pass
                    # 8 get AREA
                    try:
                        modification.append(
                            ' AREA=\''+edits["edited_rows"][item]['AREA']+'\'')
                    except Exception:
                        pass
                    # 9 get CARD_HOLDER
                    try:
                        modification.append(
                            ' CITY=\''+edits["edited_rows"][item]['CITY']+'\'')
                    except Exception:
                        pass
                    # 10 get STATE
                    try:
                        modification.append(
                            ' STATE=\''+edits["edited_rows"][item]['STATE']+'\'')
                    except Exception:
                        pass
                    # 10 get PINCODE
                    try:
                        modification.append(
                            ' PINCODE=\''+edits["edited_rows"][item]['PINCODE']+'\'')
                    except Exception:
                        pass
                    # delete rows
                    try:
                        delete = edits["edited_rows"][item]['MODIFIER']
                        if delete:
                            del_row = df.loc[item]['ROW_ID']
                            query = 'delete from bizcard.bizcards WHERE ID=' + \
                                str(del_row)+';'
                            
                            df_out, status, output = query_db(query)

                    except Exception:
                        pass
                    # Update rows
                    try:
                        query = 'UPDATE bizcard.bizcards SET ' + \
                            ','.join(modification) + \
                            ' WHERE ID='+str(mod_row)+';'
                        df_out, status, output = query_db(query)
                    except Exception:
                        pass
    
        with col2:
            refresh = st.button('Refresh', key='ref2')
            if refresh:
                pass
        with col3:
            if st.button('Remove duplicates'):
                query = ''' WITH DATASET AS (SELECT ROW_NUMBER() OVER(PARTITION BY COMPANY_NAME,CARD_HOLDER,DESIGNATION,MOBILE_NUMBER,EMAIL,WEBSITE,AREA,CITY,STATE,PINCODE)ROW_NUM,
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
                        WHERE ID IN (SELECT ID FROM DATASET A WHERE ROW_NUM>1);
                        '''
                query_db(query)
                streamlit_js_eval(
                    js_expressions="parent.window.location.reload()")
except Exception:
    pass
