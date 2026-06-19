# Flip Finder - Marketplace Edition (Deployable)
# Carvana/Amazon-inspired UI with location detection, junk car toggle, and suggestion box

import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import re
import time

# ============================================================
# CONFIG
# ============================================================
REGIONS = {
    "California": ["orangecounty", "losangeles", "inlandempire", "sandiego", "sfbay", "sacramento", "fresno"],
    "New York": ["newyork", "longisland", "hudsonvalley", "buffalo", "rochester"],
    "Texas": ["dallas", "austin", "houston", "sanantonio", "elpaso"],
    "Florida": ["miami", "orlando", "tampa", "jacksonville", "fortlauderdale"],
    "Illinois": ["chicago", "peoria", "rockford", "springfield"],
    "Arizona": ["phoenix", "tucson", "flagstaff"],
    "Nevada": ["lasvegas", "reno"],
    "Washington": ["seattle", "spokane", "tacoma"],
    "Colorado": ["denver", "boulder", "cosprings"],
    "Georgia": ["atlanta", "augusta", "savannah"],
    "Other": []
}

MAKES = ["BMW", "Mercedes", "Audi", "Lexus", "Porsche", "Honda", "Toyota"]
BODY_TYPES = ["Any", "Sedan", "Coupe", "SUV", "Truck", "Convertible", "Wagon", "Hatchback"]
COLORS = ["Any", "Black", "White", "Silver", "Gray", "Blue", "Red", "Green", "Beige", "Brown"]

BMW_MODELS = ["328", "330", "335", "340", "528", "530", "535", "540", "550", "740", "745", "750", "x3", "x5", "x6", "x7", "z3", "z4", "m3", "m4", "m5", "m6", "3 series", "5 series", "7 series"]
MERC_MODELS = ["c300", "c350", "e350", "e550", "s550", "glk", "gle", "ml", "cla", "clk"]
AUDI_MODELS = ["a3", "a4", "a5", "a6", "q3", "q5", "q7", "s4", "s5", "tt"]
LEXUS_MODELS = ["is250", "is350", "es350", "gs350", "rx350", "nx", "ls"]
PORSCHE_MODELS = ["boxster", "cayman", "cayenne", "macan", "911", "panamera"]
HONDA_MODELS = ["civic", "accord", "crv", "pilot", "fit", "s2000"]
TOYOTA_MODELS = ["camry", "corolla", "rav4", "4runner", "tacoma", "tundra", "supra"]
ALL_MODELS = BMW_MODELS + MERC_MODELS + AUDI_MODELS + LEXUS_MODELS + PORSCHE_MODELS + HONDA_MODELS + TOYOTA_MODELS

SCAM_KEYWORDS = ["dwpymnt", "down payment", "downpayment", "financing", "finance", "lease", "leasing", "monthly", "per month", "/mo", "0 down", "bad credit", "no credit", "repo", "repossession"]

MAKE_MARKET_VALUES = {
    "BMW": {"328": 7000, "330": 8000, "335": 9000, "340": 18000, "528": 8000, "530": 9000, "535": 11000, "540": 10000, "550": 15000, "740": 9000, "745": 10000, "750": 12000, "x3": 10000, "x5": 12000, "x6": 18000, "x7": 35000, "z3": 10000, "z4": 11000, "m3": 15000, "m4": 30000, "m5": 18000, "m6": 25000},
    "Mercedes": {"c300": 10000, "c350": 12000, "e350": 12000, "e550": 18000, "s550": 20000, "glk": 12000, "gle": 20000, "ml": 10000, "cla": 14000, "clk": 8000},
    "Audi": {"a3": 12000, "a4": 11000, "a5": 14000, "a6": 12000, "q3": 14000, "q5": 13000, "q7": 16000, "s4": 18000, "s5": 20000, "tt": 10000},
    "Lexus": {"is250": 10000, "is350": 14000, "es350": 12000, "gs350": 14000, "rx350": 13000, "nx": 18000, "ls": 18000},
    "Porsche": {"boxster": 18000, "cayman": 25000, "cayenne": 15000, "macan": 25000, "911": 35000, "panamera": 25000},
    "Honda": {"civic": 7000, "accord": 8000, "crv": 9000, "pilot": 10000, "fit": 6000, "s2000": 18000},
    "Toyota": {"camry": 7000, "corolla": 6000, "rav4": 10000, "4runner": 12000, "tacoma": 15000, "tundra": 14000, "supra": 30000},
}

# ============================================================
# STYLING - Marketplace Inspired
# ============================================================
st.set_page_config(page_title="Flip Finder - Find Your Next Flip", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Force dark mode always */
    [data-testid="stAppViewContainer"] {
        background-color: #0d1117;
    }
    [data-testid="stHeader"] {
        background-color: #0d1117;
    }
    .stApp {
        background-color: #0d1117;
    }
    body { background-color: #0d1117; }
    .main { background-color: #0d1117; padding: 0; }
    
    .header-bar {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 24px 40px;
        border-bottom: 1px solid #2a2a4a;
        margin-bottom: 0;
    }
    .header-title {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
    }
    .header-subtitle {
        font-size: 14px;
        color: #8888aa;
        margin: 4px 0 0 0;
    }
    
    .location-bar {
        background: #161b22;
        padding: 12px 40px;
        border-bottom: 1px solid #2a2a4a;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .location-chip {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        background: #21262d;
        color: #c9d1d9;
        font-size: 13px;
        cursor: pointer;
        border: 1px solid #30363d;
        transition: all 0.2s;
    }
    .location-chip:hover {
        background: #30363d;
        border-color: #58a6ff;
    }
    .location-chip.active {
        background: #1f6feb;
        border-color: #58a6ff;
        color: white;
    }
    
    .stats-bar {
        display: flex;
        gap: 16px;
        padding: 16px 40px;
        background: #0d1117;
    }
    .stat-item {
        background: #161b22;
        border-radius: 8px;
        padding: 12px 20px;
        border: 1px solid #21262d;
    }
    .stat-number {
        font-size: 24px;
        font-weight: 700;
        color: #58a6ff;
    }
    .stat-label {
        font-size: 11px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 20px;
        padding: 20px 40px;
    }
    
    .deal-card {
        background: #161b22;
        border-radius: 12px;
        border: 1px solid #21262d;
        overflow: hidden;
        transition: all 0.2s;
        cursor: pointer;
    }
    .deal-card:hover {
        border-color: #58a6ff;
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }
    .card-image {
        width: 100%;
        height: 180px;
        background: linear-gradient(135deg, #1a1a2e 0%, #0d1117 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
    }
    .card-body {
        padding: 16px;
    }
    .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #e6edf3;
        margin: 0 0 4px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-meta {
        font-size: 12px;
        color: #8b949e;
        margin-bottom: 8px;
    }
    .card-price-row {
        display: flex;
        align-items: baseline;
        gap: 8px;
        margin-bottom: 4px;
    }
    .card-price {
        font-size: 24px;
        font-weight: 700;
        color: #4ecdc4;
    }
    .card-market {
        font-size: 13px;
        color: #8b949e;
        text-decoration: line-through;
    }
    .card-score {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
        margin-top: 6px;
    }
    .score-fire { background: #da3633; color: white; }
    .score-hot { background: #f0883e; color: white; }
    .score-warm { background: #d29922; color: #0d1117; }
    .score-mild { background: #3fb950; color: #0d1117; }
    .score-cold { background: #21262d; color: #8b949e; }
    
    .profit-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        margin-top: 4px;
    }
    .profit-green { background: #1b3a1b; color: #3fb950; }
    .profit-yellow { background: #3a2e1b; color: #d29922; }
    .profit-red { background: #3a1b1b; color: #f85149; }
    
    section[data-testid="stSidebar"] {
        background: #161b22;
        border-right: 1px solid #21262d;
    }
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] .stCaption {
        color: #c9d1d9;
    }
    
    .stButton > button {
        background: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 8px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #30363d;
        border-color: #58a6ff;
        color: white;
    }
    
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #c9d1d9;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCTIONS
# ============================================================

def is_scam(title):
    title_lower = title.lower()
    for keyword in SCAM_KEYWORDS:
        if keyword in title_lower:
            return True
    return False

def extract_year(text):
    match = re.search(r'\b(19[8-9]\d|20[0-2]\d)\b', text)
    if match:
        return int(match.group(1)), True
    return 0, False

def extract_model_from_title(title, makes):
    title_lower = title.lower()
    for model in ALL_MODELS:
        if model in title_lower:
            for make in makes:
                if model in MAKE_MARKET_VALUES.get(make, {}):
                    return model, make
    return "other", "Unknown"

def extract_mileage_from_text(text):
    exact_patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*miles', r'(\d{2,6})\s*miles',
        r'(\d{1,3}(?:,\d{3})*)\s*mi\b', r'(\d{2,6})\s*mi\b',
    ]
    for pattern in exact_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            mileage = int(match.group(1).replace(",", ""))
            if 1000 < mileage < 400000:
                return mileage, True
    k_patterns = [
        r'(\d{2,3})\s*k\s*miles', r'(\d{2,3})\s*k\s*mi',
        r'(\d{2,3})k\s*miles', r'(\d{2,3})k\s*mi',
        r'(\d{2,3})k\b', r'(\d{2,3})\s*k\b',
    ]
    for pattern in k_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            mileage = int(match.group(1)) * 1000
            if 10000 < mileage < 400000:
                return mileage, False
    return 0, False

def extract_color(title, description):
    text = (title + " " + description).lower()
    color_map = {"black": "Black", "white": "White", "silver": "Silver", "gray": "Gray", "grey": "Gray", "blue": "Blue", "red": "Red", "green": "Green", "beige": "Beige", "brown": "Brown", "tan": "Beige", "gold": "Beige", "burgundy": "Red", "navy": "Blue"}
    for word, color in color_map.items():
        if re.search(r'\b' + word + r'\b', text):
            return color
    return "Unknown"

def extract_body_type(title, description):
    text = (title + " " + description).lower()
    body_map = {"sedan": "Sedan", "coupe": "Coupe", "suv": "SUV", "truck": "Truck", "convertible": "Convertible", "cabriolet": "Convertible", "wagon": "Wagon", "hatchback": "Hatchback", "roadster": "Convertible"}
    for word, body in body_map.items():
        if re.search(r'\b' + word + r'\b', text):
            return body
    return "Unknown"

def calculate_deal_score(price, market_value, year, year_confident, mileage, mileage_confident):
    score = 0
    if market_value > 0:
        discount = ((market_value - price) / market_value) * 100
        score += min(discount * 1.5, 50)
    if year > 0:
        age = 2026 - year
        if age <= 5: score += 20
        elif age <= 10: score += 15
        elif age <= 15: score += 10
        elif age <= 20: score += 5
        if not year_confident: score -= 3
    else: score -= 5
    if mileage > 0:
        if mileage < 75000: score += 20
        elif mileage < 100000: score += 15
        elif mileage < 150000: score += 10
        elif mileage < 200000: score += 5
        if not mileage_confident: score -= 3
    else: score -= 5
    return max(round(score, 1), 0)

def get_market_value(title, make, year):
    model, _ = extract_model_from_title(title, [make])
    make_values = MAKE_MARKET_VALUES.get(make, {})
    base_value = make_values.get(model, 8000)
    if year > 0:
        age = 2026 - year
        if age > 0:
            base_value = base_value * (1 - age * 0.06)
    return max(round(base_value), 1000)

def get_score_emoji_and_class(score):
    if score >= 70: return "🔥", "score-fire"
    elif score >= 55: return "⭐", "score-hot"
    elif score >= 40: return "👍", "score-warm"
    elif score >= 25: return "👀", "score-mild"
    else: return "❄️", "score-cold"

def get_profit_class(profit):
    if profit > 2000: return "profit-green"
    elif profit > 500: return "profit-yellow"
    else: return "profit-red"

def format_mileage_display(mileage, confident):
    if mileage == 0: return "?"
    formatted = f"{mileage:,}"
    if not confident: formatted += "?"
    return formatted

def detect_user_state():
    try:
        ip_data = requests.get("https://ipapi.co/json/", timeout=5).json()
        return ip_data.get("region", "California")
    except:
        return "California"

def build_craigslist_url(region_name, make, min_price=500, max_price=50000):
    region_key = region_name.lower().replace(" ", "")
    if not region_key:
        return None
    base = f"https://{region_key}.craigslist.org/search/cta"
    query = make.lower().replace(" ", "")
    return f"{base}?query={query}&min_price={min_price}&max_price={max_price}"

def scrape_craigslist(region_name, make, price_min, price_max):
    url = build_craigslist_url(region_name, make, price_min, price_max)
    if not url:
        return [], 0
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "lxml")
        listings = []
        scams = 0
        results = soup.find_all("li", class_="cl-static-search-result")
        for item in results:
            try:
                title_elem = item.find("div", class_="title")
                title = title_elem.text.strip() if title_elem else "N/A"
                if is_scam(title): scams += 1; continue
                price_elem = item.find("div", class_="price")
                price_text = price_elem.text.strip() if price_elem else "$0"
                price_text = price_text.replace("$", "").replace(",", "")
                try: price = int(price_text)
                except: price = 0
                location_elem = item.find("div", class_="location")
                location = location_elem.text.strip() if location_elem else "Unknown"
                link_elem = item.find("a", href=True)
                link = link_elem["href"] if link_elem else "#"
                details_elem = item.find("div", class_="details")
                details_text = details_elem.text if details_elem else ""
                full_text = title + " " + details_text
                if price > 0 and make.lower() in title.lower():
                    year, year_confident = extract_year(title)
                    model, detected_make = extract_model_from_title(title, [make])
                    mileage, mileage_confident = extract_mileage_from_text(full_text)
                    if mileage == 0: mileage, mileage_confident = extract_mileage_from_text(title)
                    market_value = get_market_value(title, make, year)
                    discount = round(((market_value - price) / market_value) * 100, 1)
                    deal_score = calculate_deal_score(price, market_value, year, year_confident, mileage, mileage_confident)
                    color = extract_color(title, "")
                    body = extract_body_type(title, "")
                    listings.append({
                        "Title": title, "Year": year, "YearConfident": year_confident,
                        "Make": make, "Model": model.upper(), "Price": price,
                        "Mileage": mileage, "MileageConfident": mileage_confident,
                        "Market Value": market_value, "Discount %": discount,
                        "Deal Score": deal_score, "Color": color, "Body": body,
                        "Location": location, "Link": link,
                        "CalcRepair": 0, "CalcReg": 0, "CalcDetail": 0, "CalcOther": 0, "ShowCalc": False
                    })
            except: continue
        return listings, scams
    except: return [], 0

# ============================================================
# SESSION STATE
# ============================================================
if "listings_cache" not in st.session_state:
    st.session_state.listings_cache = []
if "scams_filtered" not in st.session_state:
    st.session_state.scams_filtered = 0
if "last_scan_params" not in st.session_state:
    st.session_state.last_scan_params = None
if "user_state" not in st.session_state:
    st.session_state.user_state = detect_user_state()
if "selected_region" not in st.session_state:
    st.session_state.selected_region = None
if "scan_triggered" not in st.session_state:
    st.session_state.scan_triggered = False

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="header-bar">
    <div class="header-title">🚗 Flip Finder</div>
    <div class="header-subtitle">Find undervalued cars. Flip for profit.</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 🔍 Search Filters")
    
    st.markdown("**Make**")
    selected_makes = st.multiselect("Select makes", MAKES, default=["BMW"], label_visibility="collapsed")
    make_custom = st.text_input("Or type any make", placeholder="e.g. subaru, ford, vw")
    if make_custom:
        custom_makes = [m.strip().capitalize() for m in make_custom.split(",") if m.strip()]
        selected_makes = custom_makes
    
    st.divider()
    st.markdown("**Price Range**")
    price_min, price_max = st.slider("Price", 0, 100000, (500, 30000), step=500, label_visibility="collapsed")
    st.markdown("**Deal Score**")
    score_min, score_max = st.slider("Score", 0, 100, (25, 100), step=5, label_visibility="collapsed")
    st.markdown("**Max Mileage**")
    max_mileage = st.slider("Mileage", 0, 300000, 0, step=10000, label_visibility="collapsed")
    
    st.divider()
    selected_body = st.selectbox("Body Type", BODY_TYPES)
    selected_color = st.selectbox("Color", COLORS)
    
    st.divider()
    search_term = st.text_input("Keyword Search", placeholder="e.g. manual, leather...")
    
    st.divider()
    hide_scams = st.checkbox("Hide financing ads", value=True)
    hide_no_year = st.checkbox("Require year", value=False)
    hide_no_mileage = st.checkbox("Require mileage", value=False)
    show_junk = st.checkbox("Show junk/parts cars", value=False)
    
    st.divider()
    if st.button("🔍 SEARCH", use_container_width=True):
        st.session_state.scan_triggered = True
        st.session_state.listings_cache = []
        st.rerun()

# ============================================================
# LOCATION BAR
# ============================================================
user_state = st.session_state.user_state
regions_in_state = REGIONS.get(user_state, [])
if not regions_in_state:
    regions_in_state = REGIONS.get("California", [])

st.markdown(f'<div class="location-bar"><span style="color:#8b949e;font-size:13px;">📍 Near {user_state}:</span>', unsafe_allow_html=True)

for region_key in regions_in_state[:6]:
    region_display = region_key.replace("orangecounty", "Orange County").replace("losangeles", "Los Angeles").replace("inlandempire", "Inland Empire").replace("sandiego", "San Diego").replace("sfbay", "SF Bay").replace("sacramento", "Sacramento").replace("fresno", "Fresno").capitalize()
    active_class = "active" if st.session_state.selected_region == region_key else ""
    if st.button(region_display, key=f"loc_{region_key}"):
        st.session_state.selected_region = region_key
        st.session_state.scan_triggered = True
        st.session_state.listings_cache = []
        st.rerun()

st.markdown('<span style="color:#8b949e;font-size:13px;margin-left:8px;">or</span>', unsafe_allow_html=True)
custom_region = st.text_input("Type city", placeholder="e.g. phoenix", key="custom_region_input", label_visibility="collapsed")
if custom_region:
    st.session_state.selected_region = custom_region.lower().replace(" ", "")
    st.session_state.scan_triggered = True
    st.session_state.listings_cache = []

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# VALIDATION
# ============================================================
if not st.session_state.selected_region:
    st.info("👆 Select a region above to start browsing deals.")
    st.stop()
if not selected_makes:
    st.info("👆 Select at least one make in the sidebar.")
    st.stop()

# ============================================================
# RUN SCAN
# ============================================================
current_params = (st.session_state.selected_region, tuple(sorted(selected_makes)), price_min, price_max, st.session_state.scan_triggered)

if not st.session_state.listings_cache or st.session_state.scan_triggered:
    all_listings = []
    total_scams = 0
    
    with st.spinner(f"Searching {st.session_state.selected_region} for deals..."):
        for make in selected_makes:
            listings, scams = scrape_craigslist(st.session_state.selected_region, make, price_min, price_max)
            all_listings.extend(listings)
            total_scams += scams
            if len(selected_makes) > 1:
                time.sleep(0.3)
    
    st.session_state.listings_cache = all_listings
    st.session_state.scams_filtered = total_scams
    st.session_state.scan_triggered = False

listings = st.session_state.listings_cache
scams_filtered = st.session_state.scams_filtered

# ============================================================
# FILTER & DISPLAY
# ============================================================
df = pd.DataFrame(listings) if listings else pd.DataFrame()

if not df.empty:
    # Junk car filter
    junk_keywords = ["junk", "parts only", "salvage", "rebuildable", "not running", "mechanic special"]
    if not show_junk:
        df = df[~df["Title"].str.lower().str.contains('|'.join(junk_keywords), na=False)]
    
    df = df[(df["Price"] >= price_min) & (df["Price"] <= price_max)]
    df = df[(df["Deal Score"] >= score_min) & (df["Deal Score"] <= score_max)]
    if max_mileage > 0:
        df = df[(df["Mileage"] == 0) | (df["Mileage"] <= max_mileage)]
    if selected_body != "Any":
        df = df[df["Body"].str.lower() == selected_body.lower()]
    if selected_color != "Any":
        df = df[df["Color"].str.lower() == selected_color.lower()]
    if search_term:
        df = df[df["Title"].str.lower().str.contains(search_term.lower(), na=False)]
    if hide_no_year:
        df = df[df["Year"] > 0]
    if hide_no_mileage:
        df = df[df["Mileage"] > 0]
    df = df.sort_values("Deal Score", ascending=False)

if hide_scams and scams_filtered > 0:
    st.caption(f"🚫 {scams_filtered} financing ads removed")

if df.empty:
    st.warning("😕 No listings found. Try expanding your search or changing region.")
else:
    hot_deals = len(df[df["Deal Score"] >= 70])
    avg_score = round(df["Deal Score"].mean(), 1)
    
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item"><div class="stat-number">{len(df)}</div><div class="stat-label">Deals Found</div></div>
        <div class="stat-item"><div class="stat-number">🔥 {hot_deals}</div><div class="stat-label">Hot Deals</div></div>
        <div class="stat-item"><div class="stat-number">{avg_score}</div><div class="stat-label">Avg Score</div></div>
        <div class="stat-item"><div class="stat-number">${price_min:,} - ${price_max:,}</div><div class="stat-label">Price Range</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    
    cols = st.columns(3)
    col_idx = 0
    
    for i, (_, deal) in enumerate(df.iterrows()):
        with cols[col_idx % 3]:
            emoji, score_class = get_score_emoji_and_class(deal["Deal Score"])
            year_display = str(deal["Year"]) if deal["Year"] > 0 else "?"
            if deal["Year"] > 0 and not deal["YearConfident"]:
                year_display += "?"
            mileage_display = format_mileage_display(deal["Mileage"], deal["MileageConfident"])
            profit = deal["Market Value"] - deal["Price"]
            profit_class = get_profit_class(profit)
            make_emoji = {"BMW": "🔵", "Mercedes": "⭐", "Audi": "🔴", "Lexus": "🟤", "Porsche": "🟡", "Honda": "🟢", "Toyota": "⚪"}.get(deal["Make"], "🚗")
            
            st.markdown(f"""
            <div class="deal-card" onclick="window.open('{deal['Link']}', '_blank')">
                <div class="card-image">{make_emoji}</div>
                <div class="card-body">
                    <div class="card-title">{deal['Title'][:50]}</div>
                    <div class="card-meta">{year_display} • {deal['Model']} • {mileage_display} mi • {deal['Location']}</div>
                    <div class="card-price-row">
                        <span class="card-price">${deal['Price']:,}</span>
                        <span class="card-market">${deal['Market Value']:,}</span>
                    </div>
                    <span class="card-score {score_class}">{emoji} {deal['Deal Score']}/100</span>
                    <span class="profit-badge {profit_class}">${profit:,} est. profit</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"💰 Calculate Profit"):
                pc1, pc2 = st.columns(2)
                with pc1:
                    repair = st.number_input("Repairs", min_value=0, value=int(deal["CalcRepair"]), step=100, key=f"repair_{i}")
                    reg = st.number_input("Reg & Tax", min_value=0, value=int(deal["CalcReg"]), step=50, key=f"reg_{i}")
                with pc2:
                    detail = st.number_input("Detailing", min_value=0, value=int(deal["CalcDetail"]), step=50, key=f"detail_{i}")
                    other = st.number_input("Other", min_value=0, value=int(deal["CalcOther"]), step=50, key=f"other_{i}")
                
                total_cost = deal["Price"] + repair + reg + detail + other
                final_profit = deal["Market Value"] - total_cost
                roi = round((final_profit / total_cost) * 100, 1) if total_cost > 0 else 0
                
                st.metric("Total Cost", f"${total_cost:,}")
                st.metric("Net Profit", f"${final_profit:,}", delta=f"{roi}% ROI")
                
                if final_profit > 2000:
                    st.success("🚀 Strong Flip")
                elif final_profit > 500:
                    st.warning("🤔 Marginal")
                else:
                    st.error("💀 Skip")
            
            st.markdown(f'<div style="text-align:center;margin-top:4px;"><a href="{deal["Link"]}" target="_blank" style="color:#58a6ff;font-size:12px;">🔗 View Listing →</a></div>', unsafe_allow_html=True)
        
        col_idx += 1
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# USER SUGGESTION BOX (placed outside any loop / if block)
# ============================================================
st.divider()
st.subheader("💬 Suggestions?")
st.caption("Help us improve Flip Finder. Your message goes directly to the developer.")

suggestion_form = f"""
<form action="https://formspree.io/f/https://formspree.io/f/mqeovvqj" method="POST">
  <div style="display:flex; flex-direction:column; gap:0.5rem; max-width:500px;">
    <input type="email" name="email" placeholder="Your email (optional)" style="padding:0.5rem; border-radius:8px; border:1px solid #30363d; background:#0d1117; color:#c9d1d9;">
    <textarea name="message" rows="4" placeholder="Your suggestion..." style="padding:0.5rem; border-radius:8px; border:1px solid #30363d; background:#0d1117; color:#c9d1d9;"></textarea>
    <button type="submit" style="padding:0.6rem; border-radius:8px; background:#238636; color:white; border:none; cursor:pointer; font-weight:bold;">Send Suggestion</button>
  </div>
</form>
"""
st.markdown(suggestion_form, unsafe_allow_html=True)