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



   
