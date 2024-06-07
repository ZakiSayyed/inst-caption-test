import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import base64
import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from email.mime.image import MIMEImage

smtp_server = 'smtp.mail.yahoo.com'
smtp_port = 587  # or 465 for SSL
yahoo_email = st.secrets["yahoo_email"]
yahoo_password = st.secrets["yahoo_pass"]

st.markdown("<h1 style='text-align: center;'>Instagram Caption Generator</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; font-size: 20px;'>Use AI to generate captions for any images.</h1>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)


def send_email(subject, message, to_email, image_filename, image_data):
    # Create message container
    msg = MIMEMultipart()
    msg['From'] = yahoo_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach message
    msg.attach(MIMEText(message, 'plain'))

    try:
        img = MIMEImage(image_data)
        img.add_header('Content-Disposition', 'attachment', filename=image_filename)
        msg.attach(img)
    except Exception as e:
        print(f"Error attaching image: {e}")

    try:
        # Establish a secure session with the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        # Login using your Yahoo email and password
        server.login(yahoo_email, yahoo_password)

        # Send the email
        server.sendmail(yahoo_email, to_email, msg.as_string())
        print("Email sent successfully!")

    except smtplib.SMTPException as e:
        print(f"Error: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Quit the server
        try:
            if server:
                server.quit()
        except Exception as e:
            print(f"Error while quitting server: {e}")

def is_file_size_acceptable(file, max_size):
    return file.size <= max_size  

def upload_image():
    uploaded_file = st.file_uploader('1.UPLOAD AN IMAGE OR PHOTO (MAX 4MB)', type=["jpg", "jpeg", "png"], accept_multiple_files=False)
    
    if uploaded_file is not None:
        if is_file_size_acceptable(uploaded_file, 4*1024*1024):
            st.image(uploaded_file, width=300)
            st.success("Image uploaded successfully")
            filename = os.path.basename(uploaded_file.name)
            image_data = uploaded_file.getvalue()  # Already bytes
            base64_image = encode_image(image_data)
            
            return filename, image_data, base64_image
        else:
            st.error("File size exceeds the maximum limit of 4 MB")
    return None, None, None  # Indicate no image uploaded

def select_vibe():
    vibes = [
        "😆 Fun",
        "😜 Joke",
        "🤣 Funny",
        "🥳 Happy",
        "😑 Serious",
        "😭 Sad",
        "😡 Angry",
        "🙌🏻 Ecstatic",
        "🧐 Curious",
        "📔 Informative",
        "😻 Cute",
        "🧊 Cool",
        "😲 Controversial",
    ]
    selected_vibe = st.selectbox("2.SELECT VIBE", options=vibes)
    return selected_vibe

def additional_prompt():    
    add_prompt = st.text_input("3.ADDITIONAL PROMPT (OPTIONAL)", placeholder="eg. the photo is in Byron Bay")
    return add_prompt

def generate_caption(image_filename, image_data, vibe, prompt, username, password):
    print(username,password)
    placeholder = st.empty()
            
    st.write("""
    <style>
    .stButton > button {
        width: 250px;
        height: 60px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("Generate Captions"):
        state = check_user(username, password)
        
        if state == 'limit':
            st.error("Sorry, Limit Exceeded. Please Subscribe to use the tool")
            st.error("Contact Support to Subscribe")
            with st.spinner('Logging out...'):
                time.sleep(5)
            st.session_state.logged_in = False
            st.rerun()  # Rerun to reflect logout            
        
        else:

            captions_generated_count(username, password)

            if image_filename is not None and image_data is not None:

                with placeholder.container():
                    st.write("Generating captions...")   
                caption = call_api(image_data, vibe, prompt)
                
                # Enable for Caption 2
                # caption_2 = call_api(image_data, vibe, prompt)

                source_background_color = st.get_option("theme.backgroundColor")

                placeholder.empty()

                box_style = """
                <style>
                .shadow-box {
                    background-color: #333333;
                    border-radius: 15px; /* Increase the curvature of the edges */
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                    padding: 20px;
                    margin: 20px 0;
                    max-width: auto;
                    color: #ffffff; /* Set text color to white */
                }
                </style>
                """

                # Add the CSS to the Streamlit app
                st.markdown(box_style, unsafe_allow_html=True)

                # st.markdown("<h1 style='text-align: center; font-size: 20px;'>Generated Captions:</h1>", unsafe_allow_html=True)
                
                box_content = f"""
                <div class="shadow-box">
                    {caption}
                </div>
                """
                st.markdown(box_content, unsafe_allow_html=True)

                # Enable for Caption 2
                # time.sleep(2)
                # box_content = f"""
                # <div class="shadow-box">
                #     {caption_2}
                # </div>
                # """
                # st.markdown(box_content, unsafe_allow_html=True)

            else:
                st.error("Please upload an image first.")

    col1, col2, col3, col4= st.columns([1, 2, 3, 4])

    with col4:
        if st.button("Logout"):
                st.session_state.logged_in = False
                st.rerun()  # Rerun to reflect logout
        

def encode_image(image_data):
    return base64.b64encode(image_data).decode('utf-8')
  
def call_api(image_data, vibe, prompt):

    code_k=st.secrets["openai_apikey"]

    placeholder = st.empty()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {code_k}"
    }

    base64_image = base64.b64encode(image_data).decode('utf-8')
    structure = "[Opening phrase] [action] [description of subject] [location]! [Relevant Emotion/feeling if needed] [additional thoughts]. #[hashtag1] #[hashtag2] #[hashtag3]"

    prompt_use = f"Generate only 1 Instagram caption between 130-150 characters only for any type of picture uploaded, make sure to add only 1 emoji and incorporate the vibe:{vibe} and additional prompt:{prompt} if any. Make sure to generate caption using the structure :{structure}, highlighting the practical benefits. Consider the fact that it is a personal instagram post caption. Use a possessive to introduce the subject and specific activities and organization and its impact."
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_use,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        content = data['choices'][0]['message']['content']
        print(content)

        return content
    else:
        placeholder.empty()

        source_background_color = st.get_option("theme.backgroundColor")

        print("Error:", response.text)
        st.markdown(f"""
        <div style="background-color:{source_background_color};border-radius:10px;">
            <h3>Error generating caption, please try later...</h3>
        </div>
        """, unsafe_allow_html=True)
        return None
    

def main(username,password):

    image_filename, image_data, base64_image = upload_image()
    
    selected_vibe = select_vibe()

    additional_prompt_text = additional_prompt()
    
    generate_caption(image_filename, image_data, selected_vibe, additional_prompt_text,username,password)

def load_google_sheets_credentials():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": "service_account",
        "project_id": st.secrets["google_sheets"]["project_id"],
        "private_key_id": st.secrets["google_sheets"]["private_key_id"],
        "private_key": st.secrets["google_sheets"]["private_key"],
        "client_email": st.secrets["google_sheets"]["client_email"],
        "client_id": st.secrets["google_sheets"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["google_sheets"]["client_x509_cert_url"]
    }, scope)
    client = gspread.authorize(creds)
    sheet_id = '1Bsv2n_12_wmWhNI5I5HgCmBWsVyAHFw3rfTGoIrT5ho'
    sheet = client.open_by_key(sheet_id).sheet1
    all_records = sheet.get_all_records()  # Use get_all_values instead
    return all_records
    
sheet = load_google_sheets_credentials()

# Define the expected headers explicitly
expected_headers = ['Username', 'Password', 'Count', 'Sender', 'Status']

def check_user(username, password):
    users = sheet

    for user in users:
        if user['Username'] == username and user['Password'] == password and user['Count'] >= 1 and user['Status'] == 'trial':
            return 'limit'
        if user['Username'] == username and user['Password'] == password and user['Count'] <= 2 and user['Status'] == 'trial':
            return True        
        elif user['Username'] == username and user['Password'] == password and user['Status'] == 'verified':
            return True
        elif user['Username'] == username and user['Password'] == password and user['Status'] == 'pending':
            return 'pending'
    return False

def signup_add_user(username, password, sender_email, status):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": "service_account",
        "project_id": st.secrets["google_sheets"]["project_id"],
        "private_key_id": st.secrets["google_sheets"]["private_key_id"],
        "private_key": st.secrets["google_sheets"]["private_key"],
        "client_email": st.secrets["google_sheets"]["client_email"],
        "client_id": st.secrets["google_sheets"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["google_sheets"]["client_x509_cert_url"]
    }, scope)
    client = gspread.authorize(creds)
    sheet_id = '1Bsv2n_12_wmWhNI5I5HgCmBWsVyAHFw3rfTGoIrT5ho'
    sheet = client.open_by_key(sheet_id).sheet1
    sheet.append_row([username, password, 0, sender_email, status, 0]) 
    return True


def signup_user(username, password, sender_email, status):
    users = sheet
    for user in users:
        if user['Username'] == username:
            return False  # Username already exists
    signup_add_user(username, password, sender_email, status)
    # sheet.append_row([username, password, 0, sender_email])
    return True

def update_caption_count(i, user):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": "service_account",
        "project_id": st.secrets["google_sheets"]["project_id"],
        "private_key_id": st.secrets["google_sheets"]["private_key_id"],
        "private_key": st.secrets["google_sheets"]["private_key"],
        "client_email": st.secrets["google_sheets"]["client_email"],
        "client_id": st.secrets["google_sheets"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["google_sheets"]["client_x509_cert_url"]
    }, scope)
    client = gspread.authorize(creds)
    sheet_id = '1Bsv2n_12_wmWhNI5I5HgCmBWsVyAHFw3rfTGoIrT5ho'
    sheet = client.open_by_key(sheet_id).sheet1
    new_count = user['Count'] + 1
    sheet.update_cell(i + 2, 3, new_count)  # Update the count in the sheet (i + 2 to account for header)
    return True

def update_login_count(i, user):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": "service_account",
        "project_id": st.secrets["google_sheets"]["project_id"],
        "private_key_id": st.secrets["google_sheets"]["private_key_id"],
        "private_key": st.secrets["google_sheets"]["private_key"],
        "client_email": st.secrets["google_sheets"]["client_email"],
        "client_id": st.secrets["google_sheets"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["google_sheets"]["client_x509_cert_url"]
    }, scope)
    client = gspread.authorize(creds)
    sheet_id = '1Bsv2n_12_wmWhNI5I5HgCmBWsVyAHFw3rfTGoIrT5ho'
    sheet = client.open_by_key(sheet_id).sheet1
    new_count = user['Logins'] + 1
    sheet.update_cell(i + 2, 6, new_count)  # Update the count in the sheet (i + 2 to account for header)
    last_login = str(datetime.now())
    sheet.update_cell(i + 2, 7, last_login)  # Update the count in the sheet (i + 2 to account for header)

    return True

def login_count(username, password):
    users = sheet
    for i, user in enumerate(users):
        if user['Username'] == username and user['Password'] == password:
            # Increment the login count
            update_login_count(i, user)
            
    return False  # Username or password incorrect

def captions_generated_count(username, password):
    users = sheet
    for i, user in enumerate(users):
        if user['Username'] == username and user['Password'] == password:
            # Increment the login count
            update_caption_count(i, user)
            
    return False  # Username or password incorrect


# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'password' not in st.session_state:
    st.session_state.password = None

menu = ["Signup", "Login", "Support"]

# Use the index of the default choice in the options list
default_index = 1  # Index of "Login" in menu (starts from 0)
choice = st.sidebar.selectbox("Menu", menu, index=default_index)

if not st.session_state.logged_in:
    if choice == "Signup":
        st.subheader("Create a new account")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        subscription_type = st.radio("Select Subscription Type", ["Free Trial (1 Caption only)", "Paid Subscription"])

        sender_email_1 = None  # Define sender_email_1 here
        status = 'pending'
        if subscription_type == "Paid Subscription":
            # payment_type = st.radio("Select Payment Type", ["Crypto - USDT", "Paypal"])
            payment_type = st.radio("Select Payment Type", ["Crypto - USDT"])
            if payment_type == "Crypto - USDT":
                st.subheader("Crypto - USDT (5$ for 10 Captions)")
                st.markdown("<h1 style='text-align: left; font-size: 20px;'>Make sure to use only -BNB Smart Chain- Network.</h1>", unsafe_allow_html=True)
                st.markdown("<h1 style='text-align: left; font-size: 25px;'>Wallet Address</h1>", unsafe_allow_html=True)
                st.markdown("<h1 style='text-align: left; font-size: 20px;'>0x12c9A85Ae794A84aCdD0B781DD7F6A3a2C96eBf1</h1>", unsafe_allow_html=True)

                if st.button("Signup"):
                    sender_email = sender_email_1
                    if new_username and new_password:
                        if signup_user(new_username, new_password,sender_email, status):
                            st.success('Congratulations! You have signed up for the account.')
                            recipient_email = 'szaki1871993@gmail.com'
                            email_subject = 'New user signup'
                            current_time = datetime.now()
                            print(current_time)
                            email_message = f'A new user has signed up\nUsername : {new_username}\nSubscription : {status}\nTime : {current_time}'
                            send_email(email_subject, email_message, recipient_email, 'empty', 'empty')
                            
                            with st.spinner('Please wait while your payment is being processed...'):
                                time.sleep(5)
                            st.success('You can log in to continue once your payment is verified.')
                            time.sleep(5)
                            st.rerun()
                        else:
                            st.error("Username already exists. Please choose a different username.")
                    else:
                        st.error("Please enter a username and password")

                # st.im("",caption="0x12c9A85Ae794A84aCdD0B781DD7F6A3a2C96eBf1")
            else:
                st.subheader("Pay to : xyz@gmail.com")
                # st.markdown("<h1 style='text-align: left; font-size: 20px;'>Email : xyz@gmail.com.</h1>", unsafe_allow_html=True)
                sender_email_1 = st.text_input("Sender Email (For confirmation)")
        else:
            status = 'trial'

            if st.button("Signup"):
                sender_email = sender_email_1
                if new_username and new_password:
                    if signup_user(new_username, new_password,sender_email, status):
                        with st.spinner('Creating Trial Account...'):
                            time.sleep(5)
                        st.success('Congratulations! You have signed up for the Trial account.')
                        recipient_email = 'szaki1871993@gmail.com'
                        email_subject = 'New user signup'
                        current_time = datetime.now()
                        print(current_time)
                        email_message = f'A new user has signed up\nUsername : {new_username}\nSubscription : {status}\nTime : {current_time}'
                        send_email(email_subject, email_message, recipient_email, 'empty', 'empty')
                        st.success('You can log in to generate 1 caption')
                        time.sleep(5)
                        st.rerun()
                    else:
                        st.error("Username already exists. Please choose a different username.")
                else:
                    st.error("Please enter a username and password")

    elif choice == "Login":
        st.subheader("Login to your account")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            state = check_user(username, password)
            if state == True:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.password = password
                with st.spinner("Logging in..."):
                    time.sleep(5)                
                st.success(f"Welcome back {username}!")
                login_count(username, password)
                time.sleep(3)
                st.rerun()
            elif state == 'limit':
                st.error("Sorry, Limit Exceeded. Please subscribe to use the tool")
                st.error("Contact Support to Subscribe")
            elif state == 'pending':
                st.error("Sorry, Your payment is still pending. Please wait..")
                st.error("Contact Support if payment is not verified within 5 minutes. Please share your username and payment confirmation screenshot")
            else:
                st.error("Invalid username or password")

    elif choice == "Support":
        st.subheader("Welcome to Support")
        ticket_type = st.radio("Select Ticket Type", ["Subscription Request", "Issue"])
        if ticket_type == "Issue":
            support_email_sender = st.text_input("Please enter your email address")
            email_text = st.text_input("Please enter your query")
            if st.button("Send"):
                recipient_email = 'automatexpos@gmail.com'
                email_subject = 'New Ticket'
                current_time = datetime.now()
                print(current_time)
                email_message = f'A new ticket has been opened\n\nTime : {current_time}\nEmail address : {support_email_sender}\nQuestion : {email_text}'
                send_email(email_subject, email_message, recipient_email, 'empty', 'empty')
                with st.spinner("Creating ticket..."):
                    time.sleep(3)
                st.success("Your ticket has been received, a support agent will get back to you soon")
                st.rerun()
        elif ticket_type == "Subscription Request":
            support_email_sender = st.text_input("Please enter your email address")
            support_username_sender = st.text_input("Please enter your Username")
            image_filename, image_data, base64_image = upload_image()
            if st.button("Send"):    
                recipient_email = 'automatexpos@gmail.com'
                email_subject = 'New Subscription Request'
                current_time = datetime.now()
                print(current_time)
                email_message = f'A new ticket has been opened\n\nTime : {current_time}\nEmail address : {support_email_sender}\nUsername : {support_username_sender}'
                send_email(email_subject, email_message, recipient_email, image_filename, image_data)
                with st.spinner("Creating ticket..."):
                    time.sleep(3)
                st.success("Your request has been received, a support agent will get back to you soon")
                st.rerun()            
            
else:
    main(st.session_state.username, st.session_state.password)

st.write("<br>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size: 15px;'>Support Email: automatexpos@gmail.com</h1>", unsafe_allow_html=True)
