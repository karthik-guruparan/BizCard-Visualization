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

3. Click on the browse file option and select the business card image files.

![image](https://github.com/karthik-guruparan/BizCard-Visualization/assets/77478705/1239316f-258b-457c-8d92-274240e03521)

4.




   
