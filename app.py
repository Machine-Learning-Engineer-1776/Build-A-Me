import streamlit as st
import requests
import time
import os
import random
from PIL import Image, ExifTags, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Build-A-ME", layout="wide")

# === GOOGLE FONT IMPORT + STYLES ===
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Great+Vibes&display=swap" rel="stylesheet">
<style>
    .big-title {
        font-size: 72px !important;
        font-weight: 700;
        font-family: 'Playfair Display', serif;
        color: #2c3e50;
        margin-bottom: 5px;
        letter-spacing: 1px;
    }
    .credit {
        font-size: 14px;
        color: #555;
        margin-top: 8px;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# === TOP BAR ===
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.markdown('<p class="big-title">🎨 Build-A-ME</p>', unsafe_allow_html=True)

with col_logo:
    logo = Image.open("static/SexyRon.jpg")
    try:
        exif = logo._getexif()
        if exif:
            orient = exif.get(ExifTags.Base.Orientation)
            if orient == 3: logo = logo.rotate(180, expand=True)
            elif orient == 6: logo = logo.rotate(270, expand=True)
            elif orient == 8: logo = logo.rotate(90, expand=True)
    except:
        pass
    st.image(logo, width=240)
    
    st.markdown(
        '<p class="credit">From <a href="https://www.linkedin.com/in/ron-lance-49aa2a8/" target="_blank">Ron Lance</a></p>',
        unsafe_allow_html=True
    )

# === OPTION 1 TAGLINE ===
st.markdown("""
### Complete Virtual Makeovers — Built Just for You

Tired of trying on one hairstyle or lipstick at a time?  

**Build-A-ME** lets you design **two full virtual makeovers** in minutes. Choose hair, beard, and makeup styles for each look, then receive your two custom creations plus one intelligent **AI Surprise** recommendation tailored for you.

**How it works**  
1. Upload a clear selfie  
2. Design Look 1 and Look 2 (mix and match any styles)  
3. Get 3 complete looks back — your two selections + one smart AI-generated surprise
""")

# ====================== CONFIG ======================
API_KEY = "sk-h8RZQvCWW03ZM81wBmnO42kC4PgjdOlPImGMwzvXbexlQNyiSE_nIBqd-x47pe80"
BASE_URL = "https://yce-api-01.makeupar.com"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ====================== HELPERS ======================
def fix_orientation(img):
    try:
        exif = img._getexif()
        if exif:
            orient = exif.get(ExifTags.Base.Orientation)
            if orient == 3: return img.rotate(180, expand=True)
            elif orient == 6: return img.rotate(270, expand=True)
            elif orient == 8: return img.rotate(90, expand=True)
    except: pass
    return img

def get_templates(feature):
    try:
        resp = requests.get(f"{BASE_URL}/s2s/v2.0/task/template/{feature}", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", {}).get("templates", [])
    except:
        return []

def run_edit(feature: str, template_id: str, input_path, is_makeup=False, progress_bar=None, status_text=None, step=0, total_steps=9):
    if progress_bar:
        progress_bar.progress(step / total_steps)
    
    if isinstance(input_path, str) and input_path.startswith("http"):
        payload = {"src_file_url": input_path, "template_id": template_id}
    else:
        fs = os.path.getsize(input_path)
        up = requests.post(f"{BASE_URL}/s2s/v2.0/file/{feature}",
                           json={"files": [{"content_type": "image/jpeg", "file_name": "img.jpg", "file_size": fs}]},
                           headers=HEADERS)
        up.raise_for_status()
        data = up.json().get("data", {})
        file_obj = data.get("files", [{}])[0]
        put_url = file_obj.get("requests", [{}])[0].get("url")
        file_id = file_obj.get("file_id")

        with open(input_path, "rb") as f:
            requests.put(put_url, data=f, headers={"Content-Type": "image/jpeg"}).raise_for_status()
        
        payload = {"src_file_id": file_id, "template_id": template_id}

    if is_makeup:
        payload["intensity"] = 0.85

    task = requests.post(f"{BASE_URL}/s2s/v2.0/task/{feature}", json=payload, headers=HEADERS)
    task.raise_for_status()
    task_id = task.json().get("data", {}).get("task_id")

    for _ in range(180):
        time.sleep(2.5)
        st_resp = requests.get(f"{BASE_URL}/s2s/v2.0/task/{feature}/{task_id}", headers=HEADERS)
        st_resp.raise_for_status()
        data = st_resp.json().get("data", {})
        status = data.get("task_status") or data.get("status")
        if status == "success":
            res = data.get("results")
            if isinstance(res, list) and res:
                return res[0].get("url") if isinstance(res[0], dict) else res[0]
            return res.get("url") or res if isinstance(res, dict) else res
    st.error(f"Timeout on {feature}")
    return None

# ====================== MAIN APP ======================
uploaded_file = st.file_uploader("Upload your selfie", type=["jpg", "jpeg", "png"])

if uploaded_file:
    file_path = f"{UPLOAD_DIR}/{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    img = Image.open(file_path)
    img = fix_orientation(img).convert("RGB")
    img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    img.save(file_path, quality=92)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(img, caption="Original Selfie (fixed)", width=240)

    hairs = get_templates("hair-style")
    beards = get_templates("beard-style")
    looks = get_templates("look-vto")

    NO_CHANGE = "No Change / Skip"

    st.subheader("Visual Guide")
    tab1, tab2, tab3 = st.tabs(["Hair", "Beard", "Makeup"])
    
    with tab1:
        cols = st.columns(6)
        for i, t in enumerate(hairs):
            with cols[i % 6]:
                st.image(t.get('thumb', ''), width=95)
                st.caption(t["title"])
    
    with tab2:
        cols = st.columns(6)
        for i, t in enumerate(beards):
            with cols[i % 6]:
                st.image(t.get('thumb', ''), width=95)
                st.caption(t["title"])
    
    with tab3:
        cols = st.columns(6)
        for i, t in enumerate(looks):
            with cols[i % 6]:
                st.image(t.get('thumb', ''), width=95)
                st.caption(t["title"])

    st.subheader("Design Your Looks")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Look 1")
        h1_title = st.selectbox("Hair Style", [NO_CHANGE] + [t["title"] for t in hairs], key="h1")
        b1_title = st.selectbox("Beard Style", [NO_CHANGE] + [t["title"] for t in beards], key="b1")
        l1_title = st.selectbox("Makeup Look", [NO_CHANGE] + [t["title"] for t in looks], key="l1")

    with col_right:
        st.subheader("Look 2")
        h2_title = st.selectbox("Hair Style", [NO_CHANGE] + [t["title"] for t in hairs], key="h2")
        b2_title = st.selectbox("Beard Style", [NO_CHANGE] + [t["title"] for t in beards], key="b2")
        l2_title = st.selectbox("Makeup Look", [NO_CHANGE] + [t["title"] for t in looks], key="l2")

    if st.button("🚀 Generate My 3 Looks", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.markdown("🔄 **We are putting together your Complete Virtual Makeover Photos, please stand by...**")

        finals = []
        infos = []
        total_steps = 9
        current_step = 0

        for look_num, (h_title, b_title, l_title) in enumerate([(h1_title, b1_title, l1_title), (h2_title, b2_title, l2_title)], 1):
            current = file_path
            info = {"Hair": h_title, "Beard": b_title, "Makeup": l_title}

            h = next((t for t in hairs if t["title"] == h_title), None)
            b = next((t for t in beards if t["title"] == b_title), None)
            l = next((t for t in looks if t["title"] == l_title), None)

            if h and h.get("id"):
                current_step += 1
                current = run_edit("hair-style", h["id"], current, progress_bar=progress_bar, status_text=status_text, step=current_step, total_steps=total_steps)
            if b and b.get("id"):
                current_step += 1
                current = run_edit("beard-style", b["id"], current, progress_bar=progress_bar, status_text=status_text, step=current_step, total_steps=total_steps)
            if l and l.get("id"):
                current_step += 1
                current = run_edit("look-vto", l["id"], current, is_makeup=True, progress_bar=progress_bar, status_text=status_text, step=current_step, total_steps=total_steps)

            finals.append(current)
            infos.append(info)

        # AI Surprise Look 3
        current = file_path
        h = random.choice(hairs) if hairs else None
        b = random.choice(beards) if beards else None
        l = random.choice(looks) if looks else None
        info = {"Hair": h["title"] if h else "None", "Beard": b["title"] if b else "None", "Makeup": l["title"] if l else "None"}

        if h and h.get("id"):
            current_step += 1
            current = run_edit("hair-style", h["id"], current, progress_bar=progress_bar, status_text=status_text, step=current_step, total_steps=total_steps)
        if b and b.get("id"):
            current_step += 1
            current = run_edit("beard-style", b["id"], current, progress_bar=progress_bar, status_text=status_text, step=current_step, total_steps=total_steps)
        if l and l.get("id"):
            current_step += 1
            current = run_edit("look-vto", l["id"], current, is_makeup=True, progress_bar=progress_bar, status_text=status_text, step=current_step, total_steps=total_steps)

        finals.append(current)
        infos.append(info)

        # Finish
        progress_bar.progress(1.0)
        status_text.markdown("✅ **All looks are ready!**")

        # === UPDATED SENTENCE ===
        st.markdown("### Here are your three complete makeovers. Which one feels the most like you?")

        if len(finals) == 3:
            collage = Image.new('RGB', (1250, 620), color=(245, 245, 245))
            draw = ImageDraw.Draw(collage)
            
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                font_title = ImageFont.load_default()
                font_small = ImageFont.load_default()

            orig = Image.open(file_path).resize((300, 400))
            collage.paste(orig, (0, 0))
            draw.text((30, 420), "Original", fill=(0,0,0), font=font_title)

            labels = ["Look 1", "Look 2", "AI Surprise (AI Generated)"]
            for i, (url, info) in enumerate(zip(finals, infos)):
                x = 300 + i * 300
                try:
                    look_img = Image.open(requests.get(url, stream=True).raw).resize((300, 400))
                    collage.paste(look_img, (x, 0))
                except:
                    pass
                
                draw.text((x + 30, 420), labels[i], fill=(0,0,0), font=font_title)
                draw.text((x + 30, 460), f"Hair:  {info['Hair']}", fill=(40,40,40), font=font_small)
                draw.text((x + 30, 490), f"Beard: {info['Beard']}", fill=(40,40,40), font=font_small)
                draw.text((x + 30, 520), f"Makeup: {info['Makeup']}", fill=(40,40,40), font=font_small)

            buf = io.BytesIO()
            collage.save(buf, format="PNG")
            buf.seek(0)

            st.download_button(
                label="📥 Download All Looks as Collage (with Selections)",
                data=buf,
                file_name="My_Build-A-ME_Makeover.png",
                mime="image/png",
                type="primary"
            )

        cols = st.columns(3)
        for idx, (url, info) in enumerate(zip(finals, infos)):
            with cols[idx]:
                st.image(url, use_container_width=True)
                if idx == 2:
                    st.write(f"**Look {idx+1} (AI Generated)**")
                else:
                    st.write(f"**Look {idx+1}**")
                st.write(f"Hair: {info['Hair']}")
                st.write(f"Beard: {info['Beard']}")
                st.write(f"Makeup: {info['Makeup']}")

st.caption("Build-A-ME • Powered by YouCam API")
