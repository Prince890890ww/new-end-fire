
import streamlit as st
import time
import threading
import asyncio
import os
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import database as db

# Ensure Playwright browsers are installed on first run (Streamlit Cloud safe call)
os.system("playwright install chromium --with-deps > /dev/null 2>&1")

st.set_page_config(page_title="Streamlit_app", page_icon="💬", layout="wide")

# --- CSS (simple) ---
st.markdown(\"\"\"
<style>
body { background: linear-gradient(135deg,#0f2027,#203a43,#2c5364); color:white; }
.stTextInput, .stTextArea, .stNumberInput, .stFileUploader { color:white !important; }
</style>
\"\"\", unsafe_allow_html=True)

# ---- Session state defaults ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "automation_state" not in st.session_state:
    st.session_state.automation_state = {"running": False, "logs": [], "count": 0, "index": 0}

def log(msg):
    t = time.strftime("%H:%M:%S")
    entry = f"[{t}] {msg}"
    st.session_state.automation_state["logs"].append(entry)

# ---- Playwright async sender ----
async def send_messages_async(config, user_id):
    playwright = None
    browser = None
    context = None
    page = None
    try:
        log("Starting Playwright...")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage"])
        context = await browser.new_context()
        page = await context.new_page()

        log("Navigating to Facebook...")
        await page.goto("https://www.facebook.com/", wait_until="domcontentloaded", timeout=30000)

        # Add cookies to context if provided
        if config.get("cookies"):
            cookie_array = [c.strip() for c in config.get("cookies","").split(";") if c.strip()]
            cookies_payload = []
            for cookie in cookie_array:
                if "=" not in cookie:
                    continue
                name, value = cookie.split("=",1)
                cookies_payload.append({"name": name.strip(), "value": value.strip(), "domain": ".facebook.com", "path": "/"})
            if cookies_payload:
                try:
                    await context.add_cookies(cookies_payload)
                    log("Cookies added to browser context.")
                    await page.reload()
                    await asyncio.sleep(2)
                except Exception as e:
                    log(f"Failed to add cookies: {e}")

        # Check login via c_user cookie
        try:
            current_cookies = await context.cookies()
            has_c_user = any(c.get("name") == "c_user" for c in current_cookies)
        except Exception:
            has_c_user = False

        if not has_c_user:
            log("❌ Invalid or expired cookies! Login failed.")
            st.session_state.automation_state["running"] = False
            db.set_automation_running(user_id, False)
            return
        else:
            log("✅ Login successful!")

        # Navigate to chat
        if config.get("chat_id"):
            chat_id = config.get("chat_id").strip()
            chat_url = f"https://www.facebook.com/messages/t/{chat_id}"
        else:
            chat_url = "https://www.facebook.com/messages"
        log(f"Opening chat: {chat_url}")
        await page.goto(chat_url, wait_until="domcontentloaded")
        await asyncio.sleep(5)

        # Find message input
        selectors = [
            'div[contenteditable=\"true\"][role=\"textbox\"]',
            'div[contenteditable=\"true\"][data-lexical-editor=\"true\"]',
            'div[aria-label*=\"message\" i][contenteditable=\"true\"]',
            'textarea[placeholder*=\"message\" i]',
            'div[contenteditable=\"true\"]',
            'textarea',
            'input[type=\"text\"]'
        ]
        message_input = None
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    message_input = el
                    break
            except Exception:
                continue

        if not message_input:
            log("❌ Message input not found!")
            st.session_state.automation_state["running"] = False
            db.set_automation_running(user_id, False)
            return

        messages = [m.strip() for m in config.get("messages","").split("\\n") if m.strip()]
        if not messages:
            messages = ["Hello!"]

        delay = int(config.get("delay",5))
        log("🚀 Starting message loop...")

        while st.session_state.automation_state["running"]:
            idx = st.session_state.automation_state["index"] % len(messages)
            base_msg = messages[idx]
            st.session_state.automation_state["index"] += 1
            if config.get("name_prefix"):
                message_to_send = f\"{config.get('name_prefix')} {base_msg}\"
            else:
                message_to_send = base_msg

            try:
                # set value and send
                await message_input.fill(message_to_send)
                await message_input.press("Enter")
                st.session_state.automation_state["count"] += 1
                log(f\"✅ Message {st.session_state.automation_state['count']} sent: {message_to_send[:120]}\")
            except Exception as e:
                log(f\"Error sending message: {e}\")
                break

            await asyncio.sleep(delay)

        log(\"Automation loop ended.\")

    except Exception as e:
        log(f\"Fatal error: {e}\")
    finally:
        try:
            if page: await page.close()
        except: pass
        try:
            if context: await context.close()
        except: pass
        try:
            if browser: await browser.close()
        except: pass
        try:
            if playwright: await playwright.stop()
        except: pass
        st.session_state.automation_state['running'] = False
        db.set_automation_running(user_id, False)
        log(\"Browser closed.\")

# ---- Start/Stop wrappers ----
def start_automation(user_config, user_id):
    if st.session_state.automation_state['running']:
        return
    st.session_state.automation_state.update({'running': True, 'logs': [], 'count': 0, 'index': 0})
    db.set_automation_running(user_id, True)
    def target():
        asyncio.run(send_messages_async(user_config, user_id))
    thread = threading.Thread(target=target, daemon=True)
    thread.start()

def stop_automation(user_id):
    st.session_state.automation_state['running'] = False
    db.set_automation_running(user_id, False)

# ---- UI ----
st.title('Streamlit_app — Playwright Messenger Automation (Cloud-ready)')

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(['🔐 Login', '✨ Sign Up'])
    with tab1:
        username = st.text_input('Username', key='login_username')
        password = st.text_input('Password', type='password', key='login_password')
        if st.button('Login'):
            if username and password:
                user_id = db.verify_user(username, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    # auto-start if previously running
                    if db.get_automation_running(user_id) and db.get_user_config(user_id).get('chat_id'):
                        start_automation(db.get_user_config(user_id), user_id)
                    st.success(f'✅ Welcome back, {username}!')
                    st.experimental_rerun()
                else:
                    st.error('❌ Invalid username or password')
            else:
                st.warning('⚠️ Enter both username and password')
    with tab2:
        new_username = st.text_input('Choose Username', key='signup_username')
        new_password = st.text_input('Choose Password', type='password', key='signup_password')
        confirm_password = st.text_input('Confirm Password', type='password', key='confirm_password')
        if st.button('Create Account'):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    success, msg = db.create_user(new_username, new_password)
                    if success:
                        st.success('✅ Account created — please login.')
                    else:
                        st.error(f'❌ {msg}')
                else:
                    st.error('❌ Passwords do not match')
            else:
                st.warning('⚠️ Fill all fields')
else:
    st.sidebar.markdown(f'### 👤 {st.session_state.username}')
    st.sidebar.markdown(f'**User ID:** {st.session_state.user_id}')
    if st.sidebar.button('🚪 Logout'):
        if st.session_state.automation_state['running']:
            stop_automation(st.session_state.user_id)
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.experimental_rerun()

    config = db.get_user_config(st.session_state.user_id)
    tab1, tab2 = st.tabs(['⚙️ Configuration', '🚀 Automation'])

    with tab1:
        st.markdown('### Your Configuration')
        chat_id = st.text_input('Chat/Conversation ID', value=config.get('chat_id',''), placeholder='e.g., 1362400298935018')
        name_prefix = st.text_input('Name Prefix', value=config.get('name_prefix',''))
        delay = st.number_input('Delay (seconds)', min_value=1, max_value=300, value=config.get('delay',5))
        cookies = st.text_area('Facebook Cookies (optional - kept private)', value='', height=120)
        st.markdown('### Upload messages (.txt) — each line will be one message')
        uploaded = st.file_uploader('Choose a .txt file', type=['txt'])
        if uploaded is not None:
            try:
                raw = uploaded.read().decode('utf-8', errors='ignore')
            except:
                raw = uploaded.read().decode('latin-1', errors='ignore')
            messages_from_file = \"\\n\".join([line.strip() for line in raw.splitlines() if line.strip()])
            st.success(f'✅ File read — {len(messages_from_file.splitlines())} messages loaded.')
            st.text_area('Preview (first 500 chars)', value=messages_from_file[:500], height=150)
            if st.button('💾 Save messages to database'):
                final_cookies = cookies if cookies.strip() else config.get('cookies','')
                db.update_user_config(st.session_state.user_id, chat_id, name_prefix, delay, final_cookies, messages_from_file)
                st.success('✅ Messages saved to database!')
                st.experimental_rerun()
        else:
            st.info('No file uploaded — existing messages from your configuration will be used.')
            st.text_area('Messages preview', value=config.get('messages','')[:1000], height=150)

        if st.button('💾 Save Configuration'):
            final_cookies = cookies if cookies.strip() else config.get('cookies','')
            db.update_user_config(st.session_state.user_id, chat_id, name_prefix, delay, final_cookies, config.get('messages',''))
            st.success('✅ Configuration saved successfully!')
            st.experimental_rerun()

    with tab2:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric('Messages Sent', st.session_state.automation_state['count'])
        with c2:
            status = '🟢 Running' if st.session_state.automation_state['running'] else '🔴 Stopped'
            st.metric('Status', status)
        with c3:
            st.metric('Total Logs', len(st.session_state.automation_state['logs']))

        col1, col2 = st.columns(2)
        with col1:
            if st.button('▶️ Start E2ee', disabled=st.session_state.automation_state['running']):
                current_config = db.get_user_config(st.session_state.user_id)
                if current_config and current_config.get('chat_id'):
                    start_automation(current_config, st.session_state.user_id)
                    st.experimental_rerun()
                else:
                    st.error('❌ Please configure Chat ID first!')
        with col2:
            if st.button('⏹️ Stop E2ee', disabled=not st.session_state.automation_state['running']):
                stop_automation(st.session_state.user_id)
                st.experimental_rerun()

        st.markdown('### Live Console Monitor')
        logs = st.session_state.automation_state['logs']
        if logs:
            st.markdown(\"\"\"<div style='background:#000;color:#00ff88;padding:10px;height:300px;overflow:auto;font-family:monospace;font-size:13px;'>\"\"\" + \"<br>\".join(logs[-200:]) + \"</div>\" , unsafe_allow_html=True)
        else:
            st.info('🚀 Console ready... Start automation to see logs here.')

st.markdown('<div style=\"text-align:center;margin-top:20px;opacity:0.7;\">Streamlit_app — Deployable Playwright version</div>', unsafe_allow_html=True)
