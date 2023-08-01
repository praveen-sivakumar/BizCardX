#------------------------------------------Importing Required Libraries---------------------------------------------

import streamlit as st
from streamlit_option_menu import option_menu

import easyocr
import cv2
import re



#------------------------------------------Page Configuration Setup-------------------------------------------------

st.set_page_config(page_title="BizCardX",
                   layout="wide",
                   initial_sidebar_state='auto',
                   menu_items={'About':'Application developed by Praveen Sivakumar'}
                   )

#-------------------------------------------Creating Navigation bar-------------------------------------------------

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


                st.write(result)

                company_name = result[-1].title()

                #Display Details company name, card holder name, designation, mobile number, email address, website URL, area, city, state, and pin code.
                with st.form("Details"):
                        final_company_name = st.text_input('Company Name:', value=company_name.title())
                        final_card_holder_name = st.text_input('Card Holder Name:', value=card_holder_name.title())
                        final_designation = st.text_input('Designation:', value=designation[0].title())
                        final_mobile_number = st.text_input('Mobile Number:', value=mobile_number)
                        final_email = st.text_input('Email Address:', value=email[0])
                        final_website = st.text_input('Website:', value=website)
                        final_area = st.text_input('Area:', value=area)
                        final_city = st.text_input('City:', value=city)
                        final_state = st.text_input('State:', value=state)
                        final_pincode = st.text_input('Pincode:', value=pincode)
                        submit_button = st.form_submit_button(label="Save")
            #if save button is clicked the data will be uploaded to database

                if submit_button:
                        st.write("Company Name : " + final_company_name)
                        st.write("Card Holder Name : " + final_card_holder_name)
                        st.write("Designation : " + final_designation)

                        #for i in final_mobile_number:
                        st.write("Mobile Number : "+ final_mobile_number)
                        st.write("Email Address : " + final_email)
                        st.write("Website URL : " + final_website)

                        st.write("Area : " + final_area)
                        st.write("City : " + final_city)
                        st.write("State : " + final_state)
                        st.write("Pincode : " + final_pincode)

#------------------------------------------------------About--------------------------------------------------------
if selected == 'About':
        st.subheader(':red[About]')