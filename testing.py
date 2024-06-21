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
import random


smtp_server = 'smtp.mail.yahoo.com'
smtp_port = 587  # or 465 for SSL
yahoo_email = st.secrets["yahoo_email"]
yahoo_password = st.secrets["yahoo_pass"]

st.markdown("<h1 style='text-align: center;'>Instagram Caption Generator</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; font-size: 20px;'>Use AI to generate captions for any images.</h1>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

def croc_game():
    # Initialize game state
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {
            'teeth': [True] * 5,  # All 5 teeth are initially up (True)
            'game_over': False,
            'winning_tooth': random.randint(0, 4),  # Random tooth that will close the mouth (0-4 for 5 teeth)
            'teeth_down': 0,  # Counter for teeth put down
            'tries_left': 3,  # User starts with 3 tries
            'user_won': False,  # Track if the user has won
            'promo_code': None,  # Store the promo code
            'game_started': False  # Track if the game has started
        }

    def generate_promo_code():
        return f"AX{random.randint(0, 9999):04}"

    def add_promo_code(promo, email_address_game):
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
        sheet = client.open_by_key(sheet_id).get_worksheet(1)
        sheet.append_row([promo, email_address_game])
        return True

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
        sheet = client.open_by_key(sheet_id).get_worksheet(1)
        all_records = sheet.get_all_records()  # Use get_all_values instead
        return all_records
        
    sheet = load_google_sheets_credentials()

    def check_email(email_address_game):
        users = sheet
        print(users)
        print(email_address_game)
        for user in users:
            if user['Email'] == email_address_game:
                print("Email used")
                return 'used'
        print("Email not used")
        return True
            
    def reset_game():
        """Function to reset the game."""
        if st.session_state.game_state['tries_left'] > 0 and not st.session_state.game_state['user_won']:
            st.session_state.game_state = {
                'teeth': [True] * 5,
                'game_over': False,
                'winning_tooth': random.randint(0, 4),
                'teeth_down': 0,
                'tries_left': st.session_state.game_state['tries_left'],
                'user_won': False,
                'promo_code': None,
                'game_started': True
            }

    def press_tooth(index):
        """Function to handle tooth press."""
        if st.session_state.game_state['game_over'] or st.session_state.game_state['user_won']:
            return

        if index == st.session_state.game_state['winning_tooth']:
            st.session_state.game_state['game_over'] = True
            st.session_state.game_state['tries_left'] -= 1
        else:
            st.session_state.game_state['teeth'][index] = False
            st.session_state.game_state['teeth_down'] += 1
            if st.session_state.game_state['teeth_down'] == 4:
                st.session_state.game_state['game_over'] = True
                st.session_state.game_state['user_won'] = True
                promo_code = generate_promo_code()
                st.session_state.game_state['promo_code'] = promo_code
                add_promo_code(promo_code, st.session_state.email_address_game)

    st.title("Crocodile Dentist Game 🐊")

    st.write("Click on the teeth to put them down one by one. Be careful, one of them will close the mouth!")

    email_address_game = st.text_input("Enter your Email address to play the game", key="email_address_game")

    if email_address_game:
        if validate_email(email_address_game):
            if st.button("Play Game"):
                status = check_email(email_address_game)
                if status == 'used':
                    st.error("Email address already used")
                    time.sleep(5)
                    st.rerun()
                else:
                    st.session_state.game_state['game_started'] = True
        else:
            st.error("Please enter a valid Email address")
        if st.session_state.game_state['game_started']:
            # Display remaining tries
            if st.session_state.game_state['tries_left'] > 0:
                st.info(f"Tries left: {st.session_state.game_state['tries_left']}")
            else:
                st.error("No more tries left. You cannot play again this session.")

            # Display crocodile's mouth status
            if st.session_state.game_state['game_over']:
                if st.session_state.game_state['teeth_down'] == 4:
                    st.success("🎉 Congratulations, you have been rewarded with 2 Free captions! 🏆")
                    st.session_state.game_state['user_won'] = True
                    st.balloons()
                    promo_code = st.session_state.game_state['promo_code']
                    st.write(f"Use the promo code **{promo_code}** while signing up to win free 5 captions.")
                else:
                    st.error("😬 Oops! The crocodile's mouth closed! 🐊")
                    if st.session_state.game_state['tries_left'] > 0:
                        if st.button("Play Again"):
                            reset_game()
                    else:
                        st.warning("No more tries left for this session.")
            else:
                st.info("Crocodile's mouth is open. Proceed with caution!")

            # Display teeth as buttons
            if not st.session_state.game_state['user_won'] and st.session_state.game_state['tries_left'] > 0:
                cols = st.columns(5)
                for i in range(5):
                    with cols[i % 5]:
                        tooth_status = st.session_state.game_state['teeth'][i]
                        if tooth_status:
                            if st.button(f"🦷 Tooth {i+1}", key=f"tooth_{i}", on_click=press_tooth, args=(i,)):
                                pass
                        else:
                            st.button(f"🦷 Tooth {i+1}", key=f"tooth_{i}", disabled=True, help="This tooth is already pressed down.")

            # Display teeth status
            teeth_display = []
            for i in range(5):
                if st.session_state.game_state['teeth'][i]:
                    teeth_display.append("🦷")
                else:
                    teeth_display.append("❌")

            st.write(" ".join(teeth_display))

            # Display a reminder or result message
            if not st.session_state.game_state['game_over']:
                st.write("Keep going, press another tooth! 🦷")
    else:
        st.warning("Please enter your email address to play the game.")


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

def upload_image_screenshot():

    uploaded_file = st.file_uploader('UPLOAD SCREENSHOT OF THE PAYMENT', type=["jpg", "jpeg", "png"], accept_multiple_files=False)

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

def upload_image():

    uploaded_file = st.file_uploader('UPLOAD AN IMAGE OR PHOTO (MAX 4MB)', type=["jpg", "jpeg", "png"], accept_multiple_files=False)

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
        
        if state == 'limit' or state == 'limit3':
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
    
def tries_left(username, password):
    users = sheet
    for user in users:
        if user['Username'] == username and user['Password'] == password and user['Count'] >= 1 and user['Status'] == 'trial':
            return 1 - user['Count']        
        if user['Username'] == username and user['Password'] == password and user['Count'] >= 1 and user['Status'] == 'trial' and user['Promo Code Status'] == 'unverified':
            return 1 - user['Count']
        if user['Username'] == username and user['Password'] == password and user['Count'] <= 3 and user['Status'] == 'trial' and user['Promo Code Status'] == 'verified':
            return 3 - user['Count']        
        if user['Username'] == username and user['Password'] == password and user['Count'] <= 1 and user['Status'] == 'trial':
            return 1 - user['Count']         
        elif user['Username'] == username and user['Password'] == password and user['Status'] == 'verified':
            return 3 - user['Count'] 
        elif user['Username'] == username and user['Password'] == password and user['Count'] <= 8 and user['Status'] == 'verified' and user['Promo Code Status'] == 'verified':
            return 8 - user['Count']
        elif user['Username'] == username and user['Password'] == password and user['Status'] == 'pending':
            return 0
    return False

def account_status(username,password):
    users = sheet
    for user in users:
        if user['Username'] == username and user['Password'] == password and user['Status'] == 'trial':
            return 'trial'
        elif user['Username'] == username and user['Password'] == password  and user['Status'] == 'verified':
            return 'verified'   
        
def main(username,password):

    remaining_captions = tries_left(username,password)
    st.markdown(f"Captions Remaining : {remaining_captions}")
    account_state = account_status(username, password)
    if account_state == 'trial':
        st.markdown("Account : Trial")
    elif account_state == 'verified':
        st.markdown("Account : Paid")

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
def check_user(username, password):
    users = sheet

    for user in users:
        if user['Username'] == username and user['Password'] == password and user['Count'] >= 1 and user['Status'] == 'trial':
            return 'limit'        
        if user['Username'] == username and user['Password'] == password and user['Count'] == 1 and user['Status'] == 'trial' and user['Promo Code Status'] == 'unverified':
            return 'limit'
        if user['Username'] == username and user['Password'] == password and user['Count'] == 3 and user['Status'] == 'trial' and user['Promo Code Status'] == 'verified':
            return 'limit3'        
        if user['Username'] == username and user['Password'] == password and user['Count'] <= 2 and user['Status'] == 'trial':
            return True        
        elif user['Username'] == username and user['Password'] == password and user['Status'] == 'verified':
            return True
        elif user['Username'] == username and user['Password'] == password and user['Count'] <= 8 and user['Status'] == 'verified' and user['Promo Code Status'] == 'verified':
            return True        
        elif user['Username'] == username and user['Password'] == password and user['Status'] == 'pending':
            return 'pending'
    return False


def feedback(email, text_feedback, ux, caption_quality):
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
    sheet = client.open_by_key(sheet_id).get_worksheet(3)
    sheet.append_row([email,text_feedback,ux,caption_quality])
    return True

def signup_add_user(username, password, sender_email, status, email, promo_code_status):
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
    sheet.append_row([username, password, 0, sender_email, status, 0, 0, email, promo_code_status]) 
    return True


def signup_user(username, password, sender_email, status, email, promo_code_status):
    users = sheet
    for user in users:
        if user['Username'] == username:
            return False  # Username already exists
    signup_add_user(username, password, sender_email, status, email, promo_code_status)
    # sheet.append_row([username, password, 0, sender_email])
    return True


def signup_user_check(email):
    users = sheet
    for user in users:
        if user['Email'] == email:
            return False  # Username already exists
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
    sheet = client.open_by_key(sheet_id).get_worksheet(1)
    all_records = sheet.get_all_records()  # Use get_all_values instead
    return all_records
    
promo_sheet = load_google_sheets_credentials()

def check_promo(promo_code, email_address_game):
    users = promo_sheet
    print(users)
    print(email_address_game)
    for user in users:
        if user['Promo'] == promo_code and user['Email'] == email_address_game:
            print("Promo Code Matched")
            return True
    print("Promo Code does not match")
    return False

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

def generate_otp():
    otp = str(random.randint(1000, 9999))  # Generate a 4-digit OTP
    return otp

def validate_email(email):
    if "@" not in email or "." not in email.split('@')[-1]:
        return False
    return True

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'password' not in st.session_state:
    st.session_state.password = None

menu = ["Signup", "Login", "Support", "Feedback", "Win Free Captions"]

# Use the index of the default choice in the options list
default_index = 1  # Index of "Login" in menu (starts from 0)
choice = st.sidebar.selectbox("Menu", menu, index=default_index)


if not st.session_state.logged_in:
    st.session_state.new_email = ''
    if choice == "Signup":
        st.subheader("Create a new account")
        st.session_state.new_email = st.text_input("Email Address")
        st.session_state.promo_code = st.text_input("Enter Promo Code (Optional)")
        promo_code_status = 'unverified'
        if st.session_state.promo_code and st.session_state.new_email:
            if check_promo(st.session_state.promo_code, st.session_state.new_email):
                st.success("Promo code verified")
                promo_code_status = 'verified'
            else:
                st.error("Promo code does not match")

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

                # Initialize session state variables if they don't exist
                if 'otp_generated' not in st.session_state:
                    st.session_state.otp_generated = None

                if st.button("Signup"):
                    email = st.session_state.new_email
                    
                    if not email:
                        print("No Email")
                        st.error("Please enter your email address to sign up")
                    else:
                        if not validate_email(email):
                            st.error("Please enter a valid email address")
                        else:
                            print("Email present in text: ",st.session_state.new_email)
                            if signup_user_check(email):
                                st.session_state.otp_generated = generate_otp()
                                send_email(
                                    'OTP Verification',
                                    f"Please use the following OTP to verify: {st.session_state.otp_generated}",
                                    email,
                                    'empty',  # Placeholder for subject, adjust as necessary
                                    'empty'   # Placeholder for body, adjust as necessary
                                )
                                st.success("Please check your email for the OTP")
                                time.sleep(2)
                                print(st.session_state.otp_generated)
                                st.session_state.signup_stage = 'otp_sent'
                            else:
                                st.error("Email address already registered")
                                st.rerun()

                if 'signup_stage' in st.session_state and st.session_state.signup_stage == 'otp_sent':
                    enter_otp = st.text_input("Please enter the OTP received on your Email")
                    print(enter_otp)
                    if st.button("Verify OTP"):
                        if enter_otp == st.session_state.otp_generated:
                            print("OTP Entered matched")
                            st.session_state.signup_stage = 'user_details'  # Move to the next stage
                        else:
                            st.error("OTP entered is incorrect")

                if 'signup_stage' in st.session_state and st.session_state.signup_stage == 'user_details':
                    new_username = st.text_input("Enter Username")  # Example input for username
                    new_password = st.text_input("Enter Password", type="password")  # Example input for password
                    sender_email_1 = ''  # Example sender email
                    sender_email = sender_email_1

                    if st.button("Proceed"):
                        if not st.session_state.new_email:
                            st.error("Please enter your email address to sign up")
                        elif new_username and new_password:
                            if signup_user(new_username, new_password, sender_email, status, st.session_state.new_email, promo_code_status):
                                st.success('Congratulations! You have signed up for the account.')
                                recipient_email = 'automatexpos@gmail.com'
                                email_subject = 'New user signup'
                                current_time = datetime.now()
                                print(current_time)
                                email_message = f'A new user has signed up\nUsername : {new_username}\nSubscription : {status}\nTime : {current_time}'
                                send_email(email_subject, email_message, recipient_email, 'empty', 'empty')

                                with st.spinner('Please wait while your payment is being processed...'):
                                    time.sleep(5)
                                st.success('You can log in to continue once your payment is verified.')
                                time.sleep(5)
                                st.session_state.signup_stage = None

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
            # Initialize session state variables if they don't exist
            if 'otp_generated' not in st.session_state:
                st.session_state.otp_generated = None
            if 'signup_stage' not in st.session_state:
                st.session_state.signup_stage = None

            if st.button("Signup"):
                email = st.session_state.new_email
                
                if not email:
                    print("No Email")
                    st.error("Please enter your email address to sign up")
                else:
                    if not validate_email(email):
                        st.error("Please enter a valid email address")
                    else:
                        print("Email present in text: ",st.session_state.new_email)
                        if signup_user_check(email):
                            st.session_state.otp_generated = generate_otp()
                            send_email(
                                'OTP Verification',
                                f"Please use the following OTP to verify: {st.session_state.otp_generated}",
                                email,
                                'empty',  # Placeholder for subject, adjust as necessary
                                'empty'   # Placeholder for body, adjust as necessary
                            )
                            st.success("Please check your email for the OTP")
                            time.sleep(2)
                            print(st.session_state.otp_generated)
                            st.session_state.signup_stage = 'otp_sent'
                        else:
                            st.error("Email address already registered")
                            st.rerun()

            if 'signup_stage' in st.session_state and st.session_state.signup_stage == 'otp_sent':
                enter_otp = st.text_input("Please enter the OTP received on your Email")
                print(enter_otp)
                if st.button("Verify OTP"):
                    if enter_otp == st.session_state.otp_generated:
                        print("OTP Entered matched")
                        st.session_state.signup_stage = 'user_details'  # Move to the next stage
                    else:
                        st.error("OTP entered is incorrect")

            if 'signup_stage' in st.session_state and st.session_state.signup_stage == 'user_details':
                new_username = st.text_input("Enter Username")  # Example input for username
                new_password = st.text_input("Enter Password", type="password")  # Example input for password
                sender_email_1 = ''  # Example sender email
                sender_email = sender_email_1

                if st.button("Proceed"):
                    if not st.session_state.new_email:
                        st.error("Please enter your email address to sign up")
                    elif new_username and new_password:
                        if signup_user(new_username, new_password, sender_email, status, st.session_state.new_email, promo_code_status):
                            st.success('Congratulations! You have signed up for the account.')
                            recipient_email = 'automatexpos@gmail.com'
                            email_subject = 'New user signup'
                            current_time = datetime.now()
                            print(current_time)
                            email_message = f'A new user has signed up\nUsername : {new_username}\nSubscription : {status}\nTime : {current_time}'
                            send_email(email_subject, email_message, recipient_email, 'empty', 'empty')

                            with st.spinner('Please wait while your payment is being processed...'):
                                time.sleep(5)
                            st.success('You can log in to continue once your payment is verified.')
                            time.sleep(5)
                            st.session_state.signup_stage = None

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
            elif state == 'limit3':
                st.error("Sorry, Limit Exceeded. Please subscribe to use the tool")
                st.error("Contact Support to Subscribe")                
            else:
                st.error("Invalid username or password")

    elif choice == "Win Free Captions":
        croc_game()
        print("Crocodile Game")

    elif choice == "Support":
        st.subheader("Welcome to Support")
        ticket_type = st.radio("Select Ticket Type", ["Subscription Request", "Issue"])

        if 'button_pressed' not in st.session_state:
            st.session_state.button_pressed = False

        if ticket_type == "Issue":
            support_email_sender = st.text_input("Please enter your email address")
            email_text = st.text_input("Please enter your query")

            if st.session_state.button_pressed:
                st.warning("You have already submitted your request.")
            else:
                if st.button("Send", disabled=not (support_email_sender and email_text)):
                    with st.spinner("Creating ticket..."):
                        recipient_email = 'automatexpos@gmail.com'
                        email_subject = 'New Ticket'
                        current_time = datetime.now()
                        email_message = f'A new ticket has been opened\n\nTime : {current_time}\nEmail address : {support_email_sender}\nQuestion : {email_text}'
                        send_email(email_subject, email_message, recipient_email, 'empty', 'empty')

                    st.session_state.button_pressed = True
                    st.success("Your ticket has been received, a support agent will get back to you soon")
                elif st.session_state.button_pressed:
                    st.warning("You have already submitted your request.")

        elif ticket_type == "Subscription Request":
            support_email_sender = st.text_input("Please enter your email address")
            support_username_sender = st.text_input("Please enter your Username")
            image_filename, image_data, base64_image = upload_image_screenshot()

            if st.session_state.button_pressed:
                st.warning("You have already submitted your request.")
            else:
                if st.button("Send", disabled=not (support_email_sender and support_username_sender and image_filename)):
                    with st.spinner("Creating ticket..."):
                        recipient_email = 'automatexpos@gmail.com'
                        email_subject = 'New Subscription Request'
                        current_time = datetime.now()
                        email_message = f'A new ticket has been opened\n\nTime : {current_time}\nEmail address : {support_email_sender}\nUsername : {support_username_sender}'
                        send_email(email_subject, email_message, recipient_email, image_filename, image_data)
                    
                    st.session_state.button_pressed = True
                    st.success("Your request has been received, a support agent will get back to you soon")
                elif st.session_state.button_pressed:
                    st.warning("You have already submitted your request.")

    elif choice == "Feedback":
        st.subheader("Welcome to Feedback")
        user_exp = st.slider('USER EXPERIENCE:', min_value=0, max_value=5, step=1)
        caption_quality = st.slider('CAPTION QUALITY:', min_value=0, max_value=5, step=1)
        feedback_email = st.text_input("Please enter your email")
        feedback_text = st.text_input("Please enter your feedback here")
        if st.button("Submit Feedback"):
            feedback(feedback_email, feedback_text, user_exp, caption_quality)
            st.balloons()
            st.success("Thank you for submitting your feedback, we will get back to you soon.")
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
