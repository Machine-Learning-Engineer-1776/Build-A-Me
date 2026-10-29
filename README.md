# Build-A-ME 🎨

**True Virtual Makeover Experience**

Stop trying on one thing at a time. A Streamlit hackathon app: upload a selfie, design **two full custom makeovers** (hair, beard and makeup) with the YouCam AI API, and get a third **Surprise** look.

<img width="364" height="270" alt="{BBCFCE44-648B-4615-B621-45103D569181}" src="https://github.com/user-attachments/assets/e53d3e17-b560-4aa7-8b5d-b2435739fe8a" />


---

### ✨ Live Demo
**http://44.254.44.122:8501/** (may be offline when the server isn't running)

---

### 🎯 The Problem It Solves

Most virtual try-on tools force users to test one hairstyle, beard, or makeup look at a time. This creates a fragmented and frustrating experience.

**Build-A-ME** changes that. It lets users design **two complete virtual makeovers** in one session — combining hair, beard, and makeup — and adds a **Surprise** look as a third option.

---

### 🚀 Key Features
- Upload selfie with automatic orientation correction
- Live template galleries for Hair, Beard, and Makeup
- Build **two custom full makeovers**
- **Surprise** third look: a random combination of the available hair, beard and makeup templates
- Real-time progress tracking with calm UX
- Beautiful downloadable collage with style breakdown
- Powered by YouCam AI API

---

### 📝 How It Works
1. Upload a clear selfie
2. Design Look 1 and Look 2 (mix & match styles)
3. Receive 3 complete makeovers — your two choices + 1 Surprise look
4. Download a collage of all looks

---

### 📸 Screenshots
***Visual Guide***
<img width="611" height="222" alt="{24C46411-F850-4687-BB18-4D1456142854}" src="https://github.com/user-attachments/assets/6523b7b9-84fc-440e-90e8-919dd58dee34" />

---

### 🛠 Tech Stack
- **Frontend**: Streamlit
- **AI Engine**: YouCam Makeup API (V2) – templates, file upload, async task polling
- **Image Processing**: PIL (Pillow)
- **Deployment**: AWS Lightsail + Systemd (persistent service)

---

### ▶️ Run Locally
```bash
pip install streamlit requests pillow
cp .env.example .env        # then set YOUCAM_API_KEY (YouCam / Perfect Corp API key)
export YOUCAM_API_KEY=...   # app.py reads the key from the environment
streamlit run app.py
```
Note: `requirements.txt` currently lists FastAPI packages; the app itself runs on Streamlit.

---

**Collage Output**

<img width="399" height="178" alt="{3250F0AC-9F28-4739-B15C-183E5A536124}" src="https://github.com/user-attachments/assets/2a011f24-d69c-406b-9ffb-7f090d81461e" />

---

### Lessons Learned
- Chaining multiple AI calls requires good error handling and user feedback
- Calm, clear progress messaging dramatically improves user experience
- Delivering a polished final output (collage) is just as important as the AI itself

---

### Built By
**Ron Lance**  
Product Manager | 15+ years | Now building with AI  

[LinkedIn](https://www.linkedin.com/in/ron-lance-49aa2a8/)

---

**Built in 2026 for Hackathon**
