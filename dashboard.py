import streamlit as st  # Core Streamlit functionality
import pandas as pd      # Data handling
import requests          # HTTP requests for APIs
import datetime          # Date and time handling
import base64            # Encoding images to base64
from pathlib import Path # Filesystem paths
from streamlit_autorefresh import st_autorefresh  # Auto-refresh widgets
import altair as alt      # Advanced plotting (if needed)
import altair as alt
from pathlib import Path


# ─────────────────────────────────────────────────────────┐
# 0. Page Configuration: must be first Streamlit command  |
# ─────────────────────────────────────────────────────────┘
st.set_page_config(page_title="Mockup Site Digital Twin Dashboard", layout="wide")

# ─────────────────────────────────────────────────────────────────────────────┐
# 1. Load & Encode Logo                                                     |
#    - Read logo file, error out if missing                                       |
#    - Convert to base64 so we can embed in HTML                                |
# ─────────────────────────────────────────────────────────────────────────────┘
logo_path = Path("visuals/iitmlogo.png")
if not logo_path.exists():
    st.error(f"Logo not found at {logo_path}")
    st.stop()
logo_bytes = logo_path.read_bytes()
logo_b64 = base64.b64encode(logo_bytes).decode()

# ─────────────────────────────────────────────────────────────────────────────┐
# 2. Build Header HTML                                                        |
#    - Gold ribbon background, dark-brown border                                |
#    - Overlapping logo image                                                   |
#    - Main title and subtitle ribbon                                           |
# ─────────────────────────────────────────────────────────────────────────────┘
header_html = f"""
<div style="
    position: relative;
    background: #E9C46A;           /* Gold */
    border-bottom: 20px solid #7F1D1D; /* Dark brown */
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0;
">
  <img src="data:image/png;base64,{logo_b64}" style="
         position: absolute;
         left: 20px;
         top: 10px;
         width: 80px;
         height: 80px;
         z-index: 2;
       " />
  <h1 style="
      margin: 0;
      color: #264653;             /* Dark teal */
      font-size: 3rem;
      font-weight: 600;
    ">
    Mockup Site Digital Twin Dashboard
  </h1>
</div>
<div style="
    position: relative;
    height: 40px;
    margin-bottom: 1.5rem;
">
  <div style="
      position: absolute;
      left: 20px;
      top: -20px;
      background: linear-gradient(90deg,#7F1D1D,#E9C46A);
      color: white;
      padding: 4px 12px;
      border-radius: 4px;
      font-size: 1rem;
      font-weight: 600;
      z-index: 1;
    ">
    <strong>IIT Madras</strong> | BTCM Division
  </div>
</div>
"""
st.components.v1.html(header_html, height=140)

# ─────────────────────────────────────────────────────────┐
# 3. Navigation Buttons                                    |
#    - Define sections with icons                           |
#    - On click, set session_state.page                     |
# ─────────────────────────────────────────────────────────┘
sections = [
    ("Progress Monitoring", "🏗️"),
    ("Earned Value Analysis", "📊"),
    ("Milestone Tracker", "🎯"),
    ("Financial Overview(TBD)", "💰"),
    ("Precast Element Status(TBD)", "📦"),
    ("As Planned", "🧱"),
    ("Site Map", "🗺️"),
]
nav_cols = st.columns(len(sections), gap="small")
for (name, icon), col in zip(sections, nav_cols):
    with col:
        if st.button(f"{icon}  {name}", key=name):
            st.session_state.page = name
st.markdown("---")

# ─────────────────────────────────────────────────────────┐
# 4. Shared Data & Assets                                   |
#    - Progress data paths and GIFs                          |
#    - Speckle model URLs                                    |
#    - Default EVA data                                       |
#    - Milestone, financial, and precast DataFrames           |
# ─────────────────────────────────────────────────────────┘
prog_excels = {
    "06 Feb": "data/progress_06feb.xlsx",
    "08 Mar": "data/progress_08mar.xlsx",
    "17 Mar": "data/progress_17mar.xlsx"
}
prog_gifs = {
    "06 Feb": "visuals/progress_06feb.gif",
    "08 Mar": "visuals/progress_08mar.gif",
    "17 Mar": "visuals/progress_17mar.gif"
}

def find_site_image(key):
    # Look for site photos matching date key
    pattern = key.lower().replace(' ', '')
    for f in Path("visuals").glob(f"{pattern}*"):
        if f.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            return str(f)
    return None
site_images = {k: find_site_image(k) for k in prog_excels}

as_planned_url = "https://app.speckle.systems/projects/a95c025094/models/7f6e8a8520?embed=true"
as_built_urls = {
    "06 Feb": "https://app.speckle.systems/projects/3db7806786/models/8c40f67a94?embed=true",
    "08 Mar": "https://app.speckle.systems/projects/3db7806786/models/4b57f57c40?embed=true",
    "17 Mar": "https://app.speckle.systems/projects/3db7806786/models/78d9e95751?embed=true"
}

# Load default EVA if available
try:
    eva_raw_default = pd.read_excel("data/EVA_Analysis.xlsx", engine="openpyxl")
except Exception:
    eva_raw_default = None

# Milestone tracker
ms_df = pd.DataFrame([
    ["Foundation Complete", "2025-02-15", "✅ Done"],
    ["First Lifting Frame",   "2025-03-01", "⏳ In Progress"],
    ["Roof Installation",      "2025-04-01", "❌ Not Started"],
], columns=["Milestone", "Target Date", "Status"])

# Financial overview
fin_df = pd.DataFrame([
    ["Manufacturing", 120, 95],
    ["Transport",      30, 20],
    ["Installation",  100, 60],
], columns=["Category", "Planned (₹L)", "Spent (₹L)"]).set_index("Category")

# Precast element status
elem_df = pd.DataFrame([
    ["PC-101", "Wall",   "Manufactured",       "2025-04-20"],
    ["PC-102", "Beam",   "QA Passed",          "2025-04-22"],
    ["PC-103", "Slab",   "Installed on Site",  "2025-04-23"],
    ["PC-104", "Column", "QA Pending",         "2025-04-24"],
], columns=["Element ID", "Type", "Status", "Last Updated"])

# Map coordinates for embedding
lat, lon = 12.989750, 80.230093

# Determine current page (default: Home)
page = st.session_state.get("page", "Home")

# ─────────────────────────────────────────────────────────┐
# Home Page                                              |
# ─────────────────────────────────────────────────────────┘
if page == "Home":
    # Auto-refresh every minute
    st_autorefresh(interval=60000, limit=None, key="minute-refresh")

    # Weather & local time card
    try:
        api_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"  
            "&current_weather=true"
            "&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum"
            "&timezone=Asia/Kolkata"
        )
        w = requests.get(api_url, timeout=5).json()
        cw = w.get("current_weather", {})
        daily = w.get("daily", {})
        dates = daily.get("time", [])
    except Exception:
        cw, daily, dates = {}, {}, []

    col_w, col_cam = st.columns([2,1], gap="large")
    with col_w:
        st.markdown("### Weather & Local Time")
        if cw:
            st.markdown(f"**Temperature:** {cw['temperature']} °C")
        now_str = datetime.datetime.now().strftime("%H:%M")
        st.markdown(f"**Local Time:** {now_str}")
        st.markdown("---")
        if dates:
            selected = st.selectbox("Select date", dates, key="fc-select")
            idx = dates.index(selected)
            st.markdown(f"- **High:** {daily['temperature_2m_max'][idx]}°  **Low:** {daily['temperature_2m_min'][idx]}°")
            st.markdown(f"- **Sunrise:** {daily['sunrise'][idx].split('T')[1]}  **Sunset:** {daily['sunset'][idx].split('T')[1]}")
            precip = daily['precipitation_sum'][idx]
            st.markdown(f"- **Precipitation:** {precip} mm {'🌧️' if precip>0 else '☀️'}")
    with col_cam:
        # CCTV camera feed card
        st.markdown(
            """
            <div style="padding:1rem;border:1px solid #ddd;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,0.1);text-align:center;">
              <h3 style="margin-bottom:0.5rem;">CCTV Camera</h3>
              <a href="http://10.21.56.110/" target="_blank" style="display:inline-block;padding:0.5rem 1rem;border-radius:4px;background:#264653;color:white;text-decoration:none;font-weight:500;">
                Live Site ▶️
              </a>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")
    # 3D model and site photo
    col_3d, col_img = st.columns(2, gap="large")
    with col_3d:
        st.markdown("### 3D Model Viewer (As-Planned)")
        st.components.v1.iframe(as_planned_url, height=650, scrolling=True)
    with col_img:
        st.markdown("### Site Photo")
        img_path = Path("visuals/Siteimage.png")
        if img_path.exists():
            st.image(str(img_path), use_container_width=True)
        else:
            st.warning("Site photo not found.")
    st.markdown("---")
    # 2D drawing embed
    st.markdown("### 2D Drawing")
    html_iframe = """
      <iframe
      src="https://app.speckle.systems/projects/970c0e268f/models/65931bb453?embed=true"
      width="650" height="650" frameborder="0" scrolling="true">
      </iframe>
      """
    st.components.v1.html(html_iframe, width=650, height=650)
 
    # Google Maps for project location
    st.markdown("### Project Location (3D Map)")
    st.components.v1.html(
        f"<iframe width='100%' height='400' frameborder='0' style='border:0;' src='https://maps.google.com/maps?q={lat},{lon}&z=18&output=embed'></iframe>",
        height=420
    )

# ─────────────────────────────────────────────────────────┐
# Progress Monitoring Page                                |
# ─────────────────────────────────────────────────────────┘
elif page == "Progress Monitoring":
    # Home button
    if st.button("🏠 Home"):
        st.session_state.page = "Home"
    st.markdown('<div style="padding:1.5rem;background:white; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    st.subheader("Progress Monitoring")
    date_key = st.selectbox("Choose date", list(prog_excels.keys()))
    col_gif, col_photo = st.columns(2)
    col_gif.image(prog_gifs[date_key], caption=f"GIF: {date_key}", use_container_width=True)
    photo = site_images.get(date_key)
    if photo:
        col_photo.image(photo, caption=f"Photo: {date_key}", use_container_width=True)
    st.markdown("**3D Models**")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**As-Planned**")
        st.components.v1.iframe(as_planned_url, height=650, scrolling=True)
    with c2:
        st.markdown(f"**As-Built ({date_key})**")
        st.components.v1.iframe(as_built_urls[date_key], height=650, scrolling=True)
    st.markdown("**Progress Data**")
    try:
        df_prog = pd.read_excel(prog_excels[date_key], engine="openpyxl")
        st.dataframe(df_prog, use_container_width=True)
    except Exception:
        st.error("Could not load progress data.")
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────┐
# Earned Value Analysis Page                              |
# ─────────────────────────────────────────────────────────┘
elif page == "Earned Value Analysis":
    if st.button("🏠 Home"):
        st.session_state.page = "Home"
    st.markdown('<div style="padding:1.5rem;background:white; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    st.subheader("Earned Value Analysis")
    # File uploader or default
    upload = st.file_uploader("Upload EVA Excel (or skip)", type=["xlsx"])
    if upload:
        eva_df = pd.read_excel(upload, engine="openpyxl")
    else:
        default_path = Path("data/EVA_Analysis.xlsx")
        if not default_path.exists():
            st.error("No default EVA file found. Please upload.")
            st.stop()
        eva_df = pd.read_excel(default_path, engine="openpyxl")
    # Prepare data
    eva_df["Planned Date"] = pd.to_datetime(eva_df["Planned Date"], errors="coerce")
    eva_df["Actual Date"]  = pd.to_datetime(eva_df["Actual Date"], errors="coerce")
    eva_df = eva_df.set_index("Planned Date").sort_index()
    st.markdown("**EVA Input Table**")
    st.dataframe(eva_df, use_container_width=True)

    # Metrics
    total_planned = eva_df["Planned Cost"].sum()
    total_actual  = eva_df["Actual Cost"].sum()
    pct_complete  = eva_df["Actual Percentage"].max() * 100
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Planned Cost", f"₹{total_planned:,.0f}")
    m2.metric("Total Actual Cost",  f"₹{total_actual:,.0f}")
    m3.metric("Project % Complete", f"{pct_complete:.1f}%")

    st.markdown("---")
    # S-Curve chart
    scurve = eva_df[["Cummulative Planned Cost","Cummulative Actual Cost"]]
    scurve = scurve.rename(columns={"Cummulative Planned Cost":"Planned (Cum.)","Cummulative Actual Cost":"Actual (Cum.)"})
    st.markdown("**S-Curve: Cumulative Planned vs Actual Cost**")
    st.line_chart(scurve)


    st.markdown("---")
    # Delays bar chart
    delays = eva_df.copy()
    delays["Delay Days"] = (delays["Actual Date"] - delays.index).dt.days
    delays = delays.set_index("Activities")
    st.markdown("**Activity Delays (Actual – Planned) in Days**")
    st.bar_chart(delays["Delay Days"])

    st.markdown("---")
    # SPI & CPI table
    spi_cpi = eva_df[["SPI = BCWP / BCWS","CPI = BCWP / ACWP"]]
    spi_cpi = spi_cpi.rename(columns={"SPI = BCWP / BCWS":"SPI","CPI = BCWP / ACWP":"CPI"})
    st.markdown("**Activity Performance Indices (SPI & CPI)**")
    def highlight(v): return 'background-color:#c6efce' if v>=1 else 'background-color:#ffc7ce'
    st.dataframe(spi_cpi.style.applymap(highlight), use_container_width=True)

    st.markdown("---")
    # Variance bar chart
    var = eva_df[["SV = BCWP - BCWS","CV = BCWP - ACWP"]]
    var = var.rename(columns={"SV = BCWP - BCWS":"SV","CV = BCWP - ACWP":"CV"})
    st.markdown("**Schedule & Cost Variance**")
    st.bar_chart(var)

    st.markdown("---")
    # SPI vs CPI scatter
    st.markdown("**SPI vs CPI Scatter**")
    st.scatter_chart(spi_cpi)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────┐
# Milestone Tracker Page                                   |
# ─────────────────────────────────────────────────────────┘
# ─────────────────────────────────────────────────────────┐
# Milestone Tracker Page                                   |
# ─────────────────────────────────────────────────────────┘
elif page == "Milestone Tracker":
    if st.button("🏠 Home"):
        st.session_state.page = "Home"

    st.subheader("Milestone Tracker")

    # 1. Load your Excel
    milestone_path = Path("data/Milestone.xlsx")
    if not milestone_path.exists():
        st.error(f"Milestone file not found at {milestone_path}")
        st.stop()
    ms_df = pd.read_excel(milestone_path, 
                          parse_dates=["Planned Date", "Actual Date"],
                          engine="openpyxl")

    # 2. Show the raw table
    st.markdown("**Milestone Table**")
    st.dataframe(ms_df, use_container_width=True)

    # 3. Prepare for the Gantt chart
    #    Fill missing Actual Date with today (so incomplete tasks span to now)
    today = pd.Timestamp.today().normalize()
    ms_df["End"] = ms_df["Actual Date"].fillna(today)

    # 4. Build the Altair Gantt-style chart
    gantt = (
        alt.Chart(ms_df)
           .mark_bar(cornerRadiusTopLeft=3, cornerRadiusBottomLeft=3)
           .encode(
               y=alt.Y("Activities:N", sort=ms_df["Activities"].tolist(),
                       title=None, axis=alt.Axis(labelFontSize=12)),
               x=alt.X("Planned Date:T", title="Date"),
               x2="End:T",
               color=alt.condition(
                   "datum['Actual Date'] != null",
                   alt.value("#264653"),   # completed (dark teal)
                   alt.value("#E76F51")    # pending (reddy orange)
               ),
               tooltip=[
                   "Activities",
                   alt.Tooltip("Planned Date", title="Planned"),
                   alt.Tooltip("Actual Date",  title="Actual")
               ]
           )
           .properties(height=350)
           .configure_axis(grid=False)
    )

    st.markdown("**Milestone Timeline**")
    st.altair_chart(gantt, use_container_width=True)
    st.markdown("---")


# ─────────────────────────────────────────────────────────┐
# Financial Overview Page                                  |
# ─────────────────────────────────────────────────────────┘
elif page == "Financial Overview":
    if st.button("🏠 Home"):
        st.session_state.page = "Home"
    st.markdown('<div style="padding:1.5rem;background:white; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    st.subheader("Financial Overview")
    st.bar_chart(fin_df)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────┐
# Precast Element Status Page                              |
# ─────────────────────────────────────────────────────────┘
elif page == "Precast Element Status":
    if st.button("🏠 Home"):
        st.session_state.page = "Home"
    st.markdown('<div style="padding:1.5rem;background:white; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    st.subheader("Precast Element Status")
    filter_type = st.selectbox("Filter by type", ["All"] + elem_df["Type"].unique().tolist())
    df_filtered = elem_df if filter_type=="All" else elem_df[elem_df["Type"]==filter_type]
    st.dataframe(df_filtered, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────┐
# As Planned Model Viewer Page                              |
# ─────────────────────────────────────────────────────────┘
elif page == "As Planned":
    if st.button("🏠 Home"):
        st.session_state.page = "Home"
    st.markdown('<div style="padding:1.5rem;background:white; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    st.subheader("3D Model Viewer (As-Planned)")
    st.components.v1.iframe(as_planned_url, height=650, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────┐
# Site Map Page                                           |
# ─────────────────────────────────────────────────────────┘
elif page == "Site Map":
    if st.button("🏠 Home"):
        st.session_state.page = "Home"
    st.markdown('<div style="padding:1.5rem;background:white; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    st.subheader("Project Location (3D Map)")
    map_html = f"<iframe width='100%' height='700' frameborder='0' style='border:0;' src='https://maps.google.com/maps?q={lat},{lon}&z=18&output=embed'></iframe>"
    st.components.v1.html(map_html, height=720)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────┐
# Fallback for unknown page                                |
# ─────────────────────────────────────────────────────────┘
else:
    st.error(f"Unknown page: {page}")
