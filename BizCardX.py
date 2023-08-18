#------------------------------------------Importing Required Libraries---------------------------------------------

import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector

import sqlalchemy
from sqlalchemy import create_engine, text

import easyocr
import cv2
import re

import pandas as pd
import pymongo

#------------------------------------------Page Configuration Setup----------------------------------------------------

st.set_page_config(page_title="BizCardX",
                   layout="wide",
                   initial_sidebar_state='auto',
                   menu_items={'About':'Application developed by Praveen Sivakumar'}
                   )

#----------------------------------------------------MySql Connection-------------------------------------------------

connect = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "root"
        )

mycursor = connect.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS BizCard")
mycursor.execute("use BizCard")
mycursor.close()

engine = create_engine('mysql+mysqlconnector://root:root@localhost/bizcard', echo=False)
connection=engine.connect()

#-----------------------------------------------Mongo---------------------
client = pymongo.MongoClient('mongodb+srv://praveensivakumar:1111@cluster0.jxaowcs.mongodb.net/')
mydb = client['BizCard']
collection = mydb['Card_Details']


#-------------------------------------------Creating Navigation bar---------------------------------------------------

selected = option_menu(
        menu_title = None,
        options=["Home","Business card","About"],
        icons=["house-fill","database-fill","exclamation-lg"],
        default_index=0,
        orientation="horizontal",
        styles={
                "container": {"background-color": "#C7B79D"},
                "icon": {"color": "white", "font-size": "25px"},
                "nav-link": {"text-align": "centre","--hover-color": "#ABA082", "color" : "white"},
                "nav-link-selected": {"background-color": "#14E7D4"}
        }
    )

st.header(":blue[BizCardX: Extracting Business Card Data with OCR]")


#------------------------------------------------------Home---------------------------------------------------------
if selected == 'Home':
        st.subheader(':red[Home]')
        st.markdown('''A Streamlit application that allows users to upload an image of a business card and extract relevant information from it using easyOCR.''')

        st.markdown('''The extracted information would include the company name, card holder name, designation, mobile number, email address, website URL, area, city, state, and pincode.''')
     
        st.markdown('''In addition, the application should allow users to save the extracted information into a database along with the uploaded business card image''')

        st.markdown('''The database should be able to store multiple entries, each with its own business card extracted information.''')

        st.subheader('_How its done_')

        st.markdown('**:red[Step 1] :**  We create a web application using Streamlit library of Python ')

        st.markdown('**:red[Step 2] :**  We upload the Business card in file upload area.')

        st.markdown('**:red[Step 3] :**  The data from the card is extracted using easyOCR.')

        st.markdown('**:red[Step 4] :**  The data is displayed so we can make changes, if any.')

        st.markdown('**:red[Step 5] :**  Extracted data is stored in the database.')

        st.subheader('_Outcome_')

        st.markdown('**The final application would have a simple and intuitive user interface that guides users through the process of uploading the business card image and extracting its information.**')

#------------------------------------------------------Business card------------------------------------------------
if selected == 'Business card':
        st.subheader(':red[Business card]')
        business_card = st.file_uploader("Upload the image of Business Card", type=['png', 'jpg'], accept_multiple_files=False,
                                     help='Only .jpg & .png are allowed')
        
        if business_card != None:
                st.image(business_card)

                #converting img object to file
                up=' '
                with open(f'{up}.png', 'wb') as f:
                        f.write(business_card.getvalue())

                #reding converted file from cv2
                img = cv2.imread(f'{up}.png')

                reader = easyocr.Reader(['en'])

                result = reader.readtext(img,detail = 0, paragraph = True)

                result_statement = " ".join(result)

                url = re.findall(r"[www|WWW|wwW]+[\.|\s]+[a-zA-Z0-9]+[\.|\][a-zA-Z]+", result_statement)
                website = re.sub('[WWW|www|wwW]+ ','www.', url[0])

                email = re.findall(r"[a-zA-Z0-9\.\-+_]+@[a-zA-Z0-9\.\-+_]+\.[a-z]+", result_statement)

                mobile_numbers = re.findall(r"[6-9]\d{9}|[\+9]\d{12}|[\+91]+\-\d{3}\-\d{4}|[\+1-2]\d{3}\-\d{3}\-\d{4}|[1-2]\d{2}\-\d{3}\-\d{4}",result_statement)
                try:
                        if mobile_numbers[1] != None:
                                mobile_number = ', '.join(mobile_numbers)   
                except:
                        mobile_number = mobile_numbers[0]
                name_and_position = result[0]

                designation = re.findall(r"[A-Za-z]+[\s|\s\&\s]+[A-Za-z]+$",name_and_position)

                card_holder_name =  name_and_position.replace(designation[0],'').title()

                address = re.findall(r"([0-9]{1,4}\s[A-za-z]+\s[A-za-z]+)[\s|\.|\,]\,\s([A-za-z]+)[\|\,|\;]\s([A-za-z]+)[\,\s|\,\s|\;\s|\s]+([0-6]{5,7})",result_statement)
                area = address[0][0]
                city = address[0][1]
                state = address[0][2]
                pincode = address[0][3]

                #l_s=result
                for i in result:
                        if url[0] in i:
                                j=result.index(i)
                                del(result[j])
                        elif email[0] in i:
                                j=result.index(i)
                                del(result[j])

                st.subheader(':red[Verifiy the details before storing]')

                company_name = result[-1].title()

                
                #Display Details company name, card holder name, designation, mobile number, email address, website URL, area, city, state, and pin code.
                with st.form("Details"):
                        final_company_name = st.text_input('Company Name:', value=company_name.title())
                        final_card_holder_name = st.text_input('Card Holder Name:', value=card_holder_name.title())
                        final_designation = st.text_input('Designation:', value=designation[0].title())
                        final_mobile_number = st.text_input('Mobile Number:', value=mobile_number)
                        final_email = st.text_input('Email Address:', value=email[0].lower())
                        final_website = st.text_input('Website:', value=website.lower())
                        final_area = st.text_input('Area:', value=area)
                        final_city = st.text_input('City:', value=city)
                        final_state = st.text_input('State:', value=state)
                        final_pincode = st.text_input('Pincode:', value=pincode)
                        submit_button = st.form_submit_button(label="Save")
            #if save button is clicked the data will be uploaded to database
                if submit_button:
                        data = {
                                "company_name" : final_company_name,
                                "card_holder" : final_card_holder_name,
                                "designation" : final_designation,
                                "mobile_number" : final_mobile_number,
                                "email" : final_email,
                                "website" : final_website,
                                "area" : final_area,
                                "city" : final_city,
                                "state" : final_state,
                                "pin_code" : final_pincode
                        }
                        #collection.insert_one(data)
                        #result = collection.find_one({"company_name": final_company_name})
                        final_data = pd.DataFrame.from_dict(data, orient='index').T

                        st.subheader(':red[Data stored Successfully]')
                        st.dataframe(final_data)
               
                        final_data.to_sql('card_details', engine, if_exists='append', index=False,)
                        connect.commit()
                        connect.close()

        
                        st.subheader(':red[Data stored Successfully]')

                        
#------------------------------------------------------About--------------------------------------------------------
if selected == 'About':
        st.subheader(':red[About]')
        st.markdown('''A Streamlit application that allows users to upload an image of a business card and extract relevant information from it using easyOCR.''')

        st.markdown('''The extracted information would include the company name, card holder name, designation, mobile number, email address, website URL, area, city, state, and pincode.''')
     
        st.markdown('**:red[Technologies]** : OCR, Streamlit GUI, SQL, Data Extraction.')

        st.markdown('**:red[Domain]** : Business')


        st.markdown('**:red[Github Link]** : https://github.com/praveen-sivakumar/BizCardX')

        st.subheader('Project done by **:red[_Praveen Sivakumar_]**')