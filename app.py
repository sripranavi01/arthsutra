import io
import os
import re
import uuid
from datetime import datetime

import streamlit as st
from PIL import Image, ImageEnhance, ImageOps

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except Exception:
    GTTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except Exception:
    SPEECH_RECOGNITION_AVAILABLE = False

st.set_page_config(page_title="ArthSutra", page_icon="🧵", layout="wide", initial_sidebar_state="collapsed")

LANGUAGES = {
    "English (English)": "en", "తెలుగు (Telugu)": "te", "हिन्दी (Hindi)": "hi",
    "தமிழ் (Tamil)": "ta", "ಕನ್ನಡ (Kannada)": "kn", "മലയാളം (Malayalam)": "ml",
    "मराठी (Marathi)": "mr", "বাংলা (Bengali)": "bn", "ગુજરાતી (Gujarati)": "gu",
    "ਪੰਜਾਬੀ (Punjabi)": "pa", "ଓଡ଼ିଆ (Odia)": "or", "অসমীয়া (Assamese)": "as",
    "اردو (Urdu)": "ur", "संस्कृतम् (Sanskrit)": "hi", "नेपाली (Nepali)": "ne",
    "कोंकणी (Konkani)": "mr", "मैथिली (Maithili)": "hi", "डोगरी (Dogri)": "hi",
    "কাশ্মীরি (Kashmiri)": "ur", "सिन्धी (Sindhi)": "hi", "बोडो (Bodo)": "hi",
    "संथाली (Santali)": "hi", "মণিপুরী (Manipuri)": "bn", "मिज़ो (Mizo)": "en",
    "खासी (Khasi)": "en", "गारो (Garo)": "en", "भोजपुरी (Bhojpuri)": "hi",
    "राजस्थानी (Rajasthani)": "hi",
}

TEXT = {
    "en": {
        "tagline": "A digital marketplace for India's artisans", "choose_language": "Choose your language",
        "welcome": "Welcome to ArthSutra",
        "welcome_text": "Turn your craft into a digital shop. Create product listings, get a suggested price, and reach more customers.",
        "choose_role": "How would you like to continue?", "artisan": "I'm an Artisan",
        "customer": "I'm a Customer", "speak": "🔊 Read instructions aloud",
        "login": "Sign in", "login_sub": "Prototype sign-in — use any non-empty mobile number and password.",
        "mobile": "Mobile number", "password": "Password", "continue": "Continue", "back": "← Back",
        "dashboard": "Dashboard", "logout": "Log out", "verify": "Artisan verification",
        "verify_text": "Upload an optional ID, artisan card, certificate, or other supporting document. You can also submit without a document for manual review.",
        "upload_doc": "Upload verification document", "submit_verify": "Submit for verification",
        "verify_pending": "Pending review", "verify_uploaded": "Submitted in this session. Verification is not automatic; this prototype marks it as pending review.",
        "add_product": "Add a product", "product_name": "Product name or craft type",
        "craft": "Craft category", "materials": "Materials used", "size": "Size / dimensions",
        "cost": "Your making cost (₹)", "hours": "Hours spent making it", "extra": "Other costs (₹)",
        "price": "Your preferred selling price (₹)", "voice_note": "Record a voice note (optional)",
        "voice_hint": "If voice transcription is available, the app will try to turn the recording into text. You can type details instead.",
        "product_photo": "Upload product photo", "make_listing": "Create listing",
        "listing_title": "Suggested listing title", "description": "Product description",
        "suggested_price": "Suggested price", "save_listing": "Save product to catalogue",
        "catalogue": "My catalogue", "no_products": "No products added yet.",
        "customer_browse": "Browse artisan products", "place_order": "Place demo order",
        "orders": "Orders and notifications", "no_orders": "No orders yet.", "delivery": "Delivery status",
        "update_status": "Update delivery status", "order_placed": "Order placed",
        "buyer_name": "Customer name", "buyer_phone": "Customer mobile number",
        "order_success": "Demo order placed. The artisan will see it in this app session.",
        "empty_catalogue": "There are no products available yet. Ask an artisan to add a product first.",
        "saved": "Product saved to your catalogue.",
        "price_note": "This is an estimate based on the cost and time you entered, not a guaranteed market price.",
        "enhanced": "Preview with simple photo enhancement", "voice_error": "Could not generate audio. Check your internet connection or read the text below.",
        "no_listing": "Enter a product name or craft type, then select Create listing.",
        "profile": "Profile", "role": "Account type", "verification_status": "Verification status",
        "not_submitted": "Not submitted",
    },
    "te": {
        "tagline": "భారతదేశ కళాకారుల కోసం డిజిటల్ మార్కెట్‌ప్లేస్", "choose_language": "మీ భాషను ఎంచుకోండి",
        "welcome": "అర్థసూత్రకు స్వాగతం", "welcome_text": "మీ చేతివృత్తిని డిజిటల్ దుకాణంగా మార్చండి. ఉత్పత్తి వివరాలు సృష్టించి, సూచించిన ధరను పొందండి.",
        "choose_role": "ఎలా కొనసాగాలనుకుంటున్నారు?", "artisan": "నేను కళాకారుడిని", "customer": "నేను వినియోగదారుడిని",
        "speak": "🔊 సూచనలను వినండి", "login": "లాగిన్", "login_sub": "ఇది నమూనా లాగిన్. ఏదైనా మొబైల్ నంబర్, పాస్‌వర్డ్ ఇవ్వండి.",
        "mobile": "మొబైల్ నంబర్", "password": "పాస్‌వర్డ్", "continue": "కొనసాగించండి", "back": "← వెనక్కి",
        "dashboard": "డాష్‌బోర్డ్", "logout": "లాగ్ అవుట్", "verify": "కళాకారుడి ధృవీకరణ",
        "verify_text": "ఐడీ, కళాకారుల కార్డు లేదా సర్టిఫికెట్‌ను ఐచ్చికంగా అప్‌లోడ్ చేయండి.",
        "upload_doc": "ధృవీకరణ పత్రాన్ని అప్‌లోడ్ చేయండి", "submit_verify": "ధృవీకరణకు పంపండి",
        "verify_uploaded": "సమీక్ష కోసం పంపబడింది. ఈ నమూనాలో ధృవీకరణ ఆటోమేటిక్ కాదు.",
        "add_product": "ఉత్పత్తిని జోడించండి", "product_name": "ఉత్పత్తి పేరు లేదా చేతివృత్తి",
        "craft": "చేతివృత్తి వర్గం", "materials": "ఉపయోగించిన పదార్థాలు", "size": "పరిమాణం",
        "cost": "తయారీ ఖర్చు (₹)", "hours": "తయారీకి పట్టిన గంటలు", "extra": "ఇతర ఖర్చులు (₹)",
        "price": "మీరు కోరుకునే ధర (₹)", "product_photo": "ఉత్పత్తి ఫోటో అప్‌లోడ్ చేయండి",
        "make_listing": "లిస్టింగ్ సృష్టించండి", "listing_title": "సూచించిన లిస్టింగ్ పేరు",
        "description": "ఉత్పత్తి వివరణ", "suggested_price": "సూచించిన ధర", "save_listing": "కేటలాగ్‌లో సేవ్ చేయండి",
        "catalogue": "నా కేటలాగ్", "no_products": "ఇంకా ఉత్పత్తులు జోడించలేదు.",
        "customer_browse": "కళాకారుల ఉత్పత్తులను చూడండి", "place_order": "డెమో ఆర్డర్ చేయండి",
        "orders": "ఆర్డర్లు మరియు నోటిఫికేషన్లు", "no_orders": "ఇంకా ఆర్డర్లు లేవు.",
        "delivery": "డెలివరీ స్థితి", "update_status": "డెలివరీ స్థితిని మార్చండి",
        "buyer_name": "వినియోగదారుడి పేరు", "buyer_phone": "వినియోగదారుడి మొబైల్ నంబర్",
        "order_success": "డెమో ఆర్డర్ చేయబడింది.", "empty_catalogue": "ఇంకా ఉత్పత్తులు లేవు. ముందుగా కళాకారుడిని ఉత్పత్తి జోడించమని అడగండి.",
        "saved": "ఉత్పత్తి కేటలాగ్‌లో సేవ్ చేయబడింది.", "price_note": "ఇది మీరు ఇచ్చిన ఖర్చు, సమయం ఆధారంగా లెక్కించిన అంచనా మాత్రమే.",
        "profile": "ప్రొఫైల్", "verification_status": "ధృవీకరణ స్థితి",
    },
    "hi": {
        "tagline": "भारत के कारीगरों के लिए डिजिटल बाज़ार", "choose_language": "अपनी भाषा चुनें",
        "welcome": "अर्थसूत्र में आपका स्वागत है", "welcome_text": "अपने हस्तशिल्प को डिजिटल दुकान में बदलें। उत्पाद की जानकारी जोड़ें और सुझाई गई कीमत पाएँ।",
        "choose_role": "आप कैसे आगे बढ़ना चाहते हैं?", "artisan": "मैं कारीगर हूँ", "customer": "मैं ग्राहक हूँ",
        "speak": "🔊 निर्देश सुनें", "login": "लॉग इन", "login_sub": "यह डेमो लॉग इन है। कोई भी मोबाइल नंबर और पासवर्ड डालें।",
        "mobile": "मोबाइल नंबर", "password": "पासवर्ड", "continue": "आगे बढ़ें", "back": "← वापस",
        "dashboard": "डैशबोर्ड", "logout": "लॉग आउट", "verify": "कारीगर सत्यापन",
        "verify_text": "पहचान पत्र, कारीगर कार्ड या प्रमाणपत्र वैकल्पिक रूप से अपलोड करें।",
        "upload_doc": "सत्यापन दस्तावेज़ अपलोड करें", "submit_verify": "सत्यापन के लिए भेजें",
        "verify_uploaded": "समीक्षा के लिए भेज दिया गया है। यह डेमो अपने आप सत्यापन नहीं करता।",
        "add_product": "उत्पाद जोड़ें", "product_name": "उत्पाद का नाम या शिल्प", "craft": "शिल्प श्रेणी",
        "materials": "इस्तेमाल की गई सामग्री", "size": "आकार", "cost": "बनाने की लागत (₹)",
        "hours": "बनाने में लगे घंटे", "extra": "अन्य खर्च (₹)", "price": "आपकी पसंदीदा बिक्री कीमत (₹)",
        "product_photo": "उत्पाद की फोटो अपलोड करें", "make_listing": "लिस्टिंग बनाएँ",
        "listing_title": "सुझाया गया शीर्षक", "description": "उत्पाद विवरण", "suggested_price": "सुझाई गई कीमत",
        "save_listing": "कैटलॉग में सेव करें", "catalogue": "मेरा कैटलॉग", "no_products": "अभी कोई उत्पाद नहीं जोड़ा गया है।",
        "customer_browse": "कारीगरों के उत्पाद देखें", "place_order": "डेमो ऑर्डर करें",
        "orders": "ऑर्डर और सूचनाएँ", "no_orders": "अभी कोई ऑर्डर नहीं है।", "delivery": "डिलीवरी स्थिति",
        "update_status": "डिलीवरी स्थिति बदलें", "buyer_name": "ग्राहक का नाम", "buyer_phone": "ग्राहक का मोबाइल नंबर",
        "order_success": "डेमो ऑर्डर कर दिया गया है।", "empty_catalogue": "अभी उत्पाद उपलब्ध नहीं हैं। पहले कोई उत्पाद जोड़ें।",
        "saved": "उत्पाद कैटलॉग में सेव हो गया।", "price_note": "यह आपके दिए गए खर्च और समय पर आधारित अनुमान है, पक्की बाज़ार कीमत नहीं।",
        "profile": "प्रोफ़ाइल", "verification_status": "सत्यापन स्थिति",
    },
}

def tr(key):
    lang = st.session_state.get("language_code", "en")
    return TEXT.get(lang, TEXT["en"]).get(key, TEXT["en"].get(key, key.replace("_", " ").title()))

defaults = {
    "screen": "welcome", "role": None, "logged_in": False, "mobile": "",
    "language": "English (English)", "language_code": "en", "products": [],
    "orders": [], "notifications": [], "verification_status": "Not submitted",
    "verification_filename": None, "draft_listing": None, "last_voice_text": "",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown("""
<style>
.stApp {background:#F8F3EA;color:#34352B}
[data-testid="stHeader"] {background:rgba(248,243,234,.95)}
h1,h2,h3,p,label,.stMarkdown {color:#34352B}
.arth-card {background:#FFFDF9;border:1px solid #E8D3B7;border-radius:18px;padding:22px;margin:10px 0 16px}
.arth-subtitle {color:#6D6559;font-size:1rem}
div.stButton>button,div.stFormSubmitButton>button {background:#A85D3B;color:white;border:0;border-radius:10px;min-height:44px;font-weight:600;width:100%}
div.stButton>button:hover,div.stFormSubmitButton>button:hover {background:#87472D;color:white;border:0}
div[data-baseweb="select"]>div {background:white;color:#34352B}
input,textarea {background:white!important;color:#34352B!important}
</style>
""", unsafe_allow_html=True)

def go(screen):
    st.session_state.screen = screen
    st.rerun()

def make_speech(text_to_speak, lang_code):
    if not GTTS_AVAILABLE:
        return None
    try:
        supported = {"en","te","hi","ta","kn","ml","mr","bn","gu","pa","or","ur","ne"}
        language = lang_code if lang_code in supported else "en"
        buffer = io.BytesIO()
        gTTS(text=text_to_speak, lang=language).write_to_fp(buffer)
        return buffer.getvalue()
    except Exception:
        return None

def enhance_image(image):
    image = ImageOps.exif_transpose(image).convert("RGB")
    image = ImageEnhance.Brightness(image).enhance(1.04)
    image = ImageEnhance.Contrast(image).enhance(1.10)
    image = ImageEnhance.Sharpness(image).enhance(1.18)
    return image

def image_to_bytes(image):
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=92)
    return output.getvalue()

def suggest_price(cost, hours, other_costs):
    base = max(0, cost) + max(0, other_costs) + max(0, hours) * 50
    return int(round((base * 1.20) / 10) * 10)

def create_listing_title(name, category):
    name, category = (name or "").strip(), (category or "").strip()
    if not name:
        name = category or "Handcrafted product"
    return f"Handcrafted {name} – {category}" if category and category.lower() not in name.lower() else name.title()

def create_description(name, category, materials, size):
    parts = [f"Handcrafted {(name or category or 'item').strip().lower()} made with care by an artisan."]
    if category.strip(): parts.append(f"Craft: {category.strip()}.")
    if materials.strip(): parts.append(f"Materials: {materials.strip()}.")
    if size.strip(): parts.append(f"Size: {size.strip()}.")
    parts.append("Small variations may occur because each piece is handmade.")
    return " ".join(parts)

def attempt_transcription(audio_file, lang_code):
    if not SPEECH_RECOGNITION_AVAILABLE or audio_file is None:
        return None
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_file.getvalue())) as source:
            audio = recognizer.record(source)
        language_map = {"en":"en-IN","te":"te-IN","hi":"hi-IN","ta":"ta-IN","kn":"kn-IN",
                        "ml":"ml-IN","mr":"mr-IN","bn":"bn-IN","gu":"gu-IN","pa":"pa-IN","or":"or-IN"}
        return recognizer.recognize_google(audio, language=language_map.get(lang_code, "en-IN"))
    except Exception:
        return None

def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.mobile = ""
    st.session_state.screen = "welcome"
    st.session_state.draft_listing = None
    st.rerun()

st.title("🧵 ArthSutra")
st.caption(tr("tagline"))

# Language selector is intentionally only on the welcome screen.
if st.session_state.screen == "welcome":
    selected = st.selectbox("🌐 " + tr("choose_language"), list(LANGUAGES.keys()),
                            index=list(LANGUAGES.keys()).index(st.session_state.language),
                            key="language_picker")
    st.session_state.language = selected
    st.session_state.language_code = LANGUAGES[selected]
    st.divider()

if st.session_state.screen == "welcome":
    st.markdown('<div class="arth-card">', unsafe_allow_html=True)
    st.header(tr("welcome"))
    st.markdown(f'<p class="arth-subtitle">{tr("welcome_text")}</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(tr("speak"), key="speak_welcome"):
        spoken = f"{tr('welcome')}. {tr('welcome_text')} {tr('choose_role')}"
        audio = make_speech(spoken, st.session_state.language_code)
        if audio:
            st.audio(audio, format="audio/mp3")
        else:
            st.warning(tr("voice_error"))
    st.caption("Audio is generated when possible; use the audio player's controls to pause or stop.")

    st.subheader(tr("choose_role"))
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="arth-card">', unsafe_allow_html=True)
        st.subheader("🧶 Artisan")
        st.write("Create product listings, manage your catalogue, and track demo orders.")
        if st.button(tr("artisan"), key="choose_artisan"):
            st.session_state.role = "Artisan"
            go("login")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="arth-card">', unsafe_allow_html=True)
        st.subheader("🛍️ Customer")
        st.write("Explore handmade products and place a demo order.")
        if st.button(tr("customer"), key="choose_customer"):
            st.session_state.role = "Customer"
            go("login")
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.screen == "login":
    if st.button(tr("back"), key="back_from_login"):
        go("welcome")
    st.markdown('<div class="arth-card">', unsafe_allow_html=True)
    st.header(tr("login"))
    st.write(tr("login_sub"))
    with st.form("login_form"):
        mobile = st.text_input(tr("mobile"), value=st.session_state.mobile, max_chars=15)
        password = st.text_input(tr("password"), type="password")
        submitted = st.form_submit_button(tr("continue"))
    if submitted:
        clean_mobile = re.sub(r"\s+", "", mobile)
        if clean_mobile and password.strip():
            st.session_state.mobile = clean_mobile
            st.session_state.logged_in = True
            go("dashboard")
        else:
            st.error("Enter both a mobile number and password to continue.")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.screen == "dashboard":
    if not st.session_state.logged_in or not st.session_state.role:
        go("welcome")

    col1, col2 = st.columns([4, 1])
    with col1:
        st.header(f"{tr('dashboard')} — {st.session_state.role}")
        st.caption(f"{tr('profile')}: {st.session_state.mobile}")
    with col2:
        if st.button(tr("logout"), key="logout_button"):
            logout()

    if st.session_state.notifications:
        with st.expander(f"🔔 {tr('orders')} ({len(st.session_state.notifications)})"):
            for note in reversed(st.session_state.notifications[-10:]):
                st.write("• " + note)

    if st.session_state.role == "Artisan":
        tabs = st.tabs([tr("add_product"), tr("catalogue"), tr("verify"), tr("orders")])

        with tabs[0]:
            st.subheader(tr("add_product"))
            with st.form("product_form"):
                product_name = st.text_input(tr("product_name"))
                category = st.selectbox(tr("craft"), [
                    "Textiles and weaving", "Pottery and ceramics", "Jewellery", "Woodwork",
                    "Metal craft", "Paintings and art", "Bamboo and cane", "Leather craft",
                    "Home decor", "Other handmade craft"])
                materials = st.text_input(tr("materials"))
                size = st.text_input(tr("size"))
                c1, c2, c3 = st.columns(3)
                with c1: cost = st.number_input(tr("cost"), min_value=0.0, step=50.0)
                with c2: hours = st.number_input(tr("hours"), min_value=0.0, step=1.0)
                with c3: other_costs = st.number_input(tr("extra"), min_value=0.0, step=10.0)
                preferred_price = st.number_input(tr("price"), min_value=0.0, step=50.0)
                photo_file = st.file_uploader(tr("product_photo"), type=["png","jpg","jpeg"])
                audio_file = st.audio_input(tr("voice_note")) if hasattr(st, "audio_input") else None
                st.caption(tr("voice_hint") if tr("voice_hint") in TEXT.get(st.session_state.language_code, {}) else
                           "Voice transcription requires optional SpeechRecognition support and an internet connection.")
                create = st.form_submit_button(tr("make_listing"))

            if create:
                transcript = attempt_transcription(audio_file, st.session_state.language_code) if audio_file else None
                if transcript:
                    st.session_state.last_voice_text = transcript
                    st.info(f"Voice transcript: {transcript}")
                    if not product_name.strip():
                        product_name = transcript[:100]
                if not product_name.strip():
                    st.error(tr("no_listing"))
                else:
                    recommended = suggest_price(cost, hours, other_costs)
                    final_price = float(preferred_price) if preferred_price > 0 else float(recommended)
                    photo_bytes = None
                    if photo_file:
                        try:
                            photo_bytes = image_to_bytes(enhance_image(Image.open(photo_file)))
                        except Exception:
                            st.warning("The photo could not be processed; the listing will be saved without a photo.")
                    st.session_state.draft_listing = {
                        "title": create_listing_title(product_name, category),
                        "description": create_description(product_name, category, materials, size),
                        "category": category, "materials": materials, "size": size,
                        "price": final_price, "suggested_price": recommended,
                        "created_by": st.session_state.mobile, "artisan_name": st.session_state.mobile,
                        "photo": photo_bytes, "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
                    }
                    st.success("Listing draft created. Review it below before saving.")

            draft = st.session_state.draft_listing
            if draft:
                st.divider()
                st.subheader(tr("listing_title"))
                st.write(draft["title"])
                st.subheader(tr("description"))
                st.write(draft["description"])
                a, b = st.columns(2)
                with a: st.metric(tr("suggested_price"), f"₹{draft['suggested_price']:,}")
                with b: st.metric("Listing price", f"₹{draft['price']:,.0f}")
                st.caption(tr("price_note"))
                if draft["photo"]:
                    st.image(draft["photo"], caption=tr("enhanced"), use_container_width=True)
                if st.button(tr("save_listing"), key="save_listing_button"):
                    product = dict(draft)
                    product["id"] = str(uuid.uuid4())[:8]
                    st.session_state.products.append(product)
                    st.session_state.notifications.append(f"New product listing saved: {product['title']}")
                    st.session_state.draft_listing = None
                    st.success(tr("saved"))
                    st.rerun()

        with tabs[1]:
            st.subheader(tr("catalogue"))
            my_products = [p for p in st.session_state.products if p.get("created_by") == st.session_state.mobile]
            if not my_products: st.info(tr("no_products"))
            for product in my_products:
                with st.container(border=True):
                    if product.get("photo"): st.image(product["photo"], width=220)
                    st.markdown(f"### {product['title']}")
                    st.write(product["description"])
                    st.write(f"**Price:** ₹{product['price']:,.0f}")
                    st.caption(f"Added: {product['created_at']}")

        with tabs[2]:
            st.subheader(tr("verify"))
            st.write(tr("verify_text"))
            verification_file = st.file_uploader(tr("upload_doc"), type=["png","jpg","jpeg","pdf"], key="verification_upload")
            if st.button(tr("submit_verify"), key="submit_verification"):
                st.session_state.verification_status = "Pending review"
                st.session_state.verification_filename = verification_file.name if verification_file else "No document supplied"
                st.session_state.notifications.append("Artisan verification submitted and is pending review.")
                st.success(tr("verify_uploaded"))
            st.write(f"**{tr('verification_status')}:** {st.session_state.verification_status}")
            if st.session_state.verification_filename:
                st.caption(f"Document for this session: {st.session_state.verification_filename}")
            st.caption("This prototype does not verify documents or store them securely on a server.")

        with tabs[3]:
            st.subheader(tr("orders"))
            artisan_orders = [o for o in st.session_state.orders if o.get("artisan_mobile") == st.session_state.mobile]
            if not artisan_orders: st.info(tr("no_orders"))
            for order in artisan_orders:
                with st.container(border=True):
                    st.markdown(f"**{order['product_title']}** — ₹{order['price']:,.0f}")
                    st.write(f"Customer: {order['buyer_name']} ({order['buyer_phone']})")
                    st.write(f"{tr('delivery')}: {order['status']}")
                    statuses = ["Order placed", "Accepted by artisan", "Preparing", "Shipped", "Delivered", "Cancelled"]
                    idx = statuses.index(order["status"]) if order["status"] in statuses else 0
                    status = st.selectbox(tr("update_status"), statuses, index=idx, key=f"status_{order['id']}")
                    if st.button("Save status", key=f"save_status_{order['id']}"):
                        order["status"] = status
                        st.session_state.notifications.append(f"Order update: {order['product_title']} is now '{status}'.")
                        st.success("Delivery status updated in this session.")
                        st.rerun()

    else:
        st.subheader(tr("customer_browse"))
        if not st.session_state.products:
            st.info(tr("empty_catalogue"))
        for product in st.session_state.products:
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                with c1:
                    if product.get("photo"): st.image(product["photo"], use_container_width=True)
                    else: st.markdown("🧵")
                with c2:
                    st.markdown(f"### {product['title']}")
                    st.write(product["description"])
                    st.markdown(f"**₹{product['price']:,.0f}**")
                    st.caption(f"Artisan contact: {product.get('artisan_name', 'Not provided')}")
                    with st.form(f"order_form_{product['id']}"):
                        buyer_name = st.text_input(tr("buyer_name"), key=f"buyer_name_{product['id']}")
                        buyer_phone = st.text_input(tr("buyer_phone"), key=f"buyer_phone_{product['id']}")
                        submit_order = st.form_submit_button(tr("place_order"))
                    if submit_order:
                        if not buyer_name.strip() or not buyer_phone.strip():
                            st.error("Enter your name and mobile number.")
                        else:
                            order = {
                                "id": str(uuid.uuid4())[:8], "product_id": product["id"],
                                "product_title": product["title"], "price": product["price"],
                                "buyer_name": buyer_name.strip(), "buyer_phone": buyer_phone.strip(),
                                "artisan_mobile": product.get("created_by"), "status": "Order placed",
                                "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
                            }
                            st.session_state.orders.append(order)
                            st.session_state.notifications.append(f"Demo order placed for {product['title']} by {buyer_name.strip()}.")
                            st.success(tr("order_success"))
                            st.rerun()

        st.divider()
        st.subheader(tr("orders"))
        my_orders = [o for o in st.session_state.orders if o.get("buyer_phone") == st.session_state.mobile]
        if not my_orders: st.info(tr("no_orders"))
        for order in my_orders:
            st.markdown(f"**{order['product_title']}** — ₹{order['price']:,.0f}  \n{tr('delivery')}: **{order['status']}**")

st.divider()
st.caption("ArthSutra prototype • Data stays in the current Streamlit session. Login, verification, orders, notifications, listing generation and pricing are demos. No real payments, secure document storage, SMS/calls, or delivery integrations are connected.")
