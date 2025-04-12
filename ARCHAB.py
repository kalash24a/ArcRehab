import streamlit as st

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="INTRODUCTION", page_icon="🏥", layout="wide")

st.title("🏥 Welcome to the Smart Rehab & Health Monitoring Dashboard")

# Create two columns: content (left), image (right)
left_col, right_col = st.columns([2, 1])  # adjust ratios as needed

with left_col:
    st.markdown("This dashboard is designed to make your recovery **transparent**, **interactive**, and **safe**.")

    st.info("👀 Here's what you can expect:")

    st.markdown("""
      🎮 **Track Rehab Progress**  
      View your game performance scores after each Unity-based therapy session.

      💓 **Live Health Monitoring**  
      Watch real-time graphs of your vitals:  
      &nbsp;&nbsp;&nbsp;&nbsp;⭐ Body Temperature 🌡️  
      &nbsp;&nbsp;&nbsp;&nbsp;⭐ Heart Rate (BPM) ❤️  
      &nbsp;&nbsp;&nbsp;&nbsp;⭐ Oxygen Saturation (SpO₂) 🫁  

      ⏱️ **Time-Stamped Logs**  
      Every reading is logged with a timestamp to track trends over time.

      🚨 **Instant Alerts**  
      If your vitals exceed safe thresholds:  
      &nbsp;&nbsp;&nbsp;&nbsp;📌  A warning will appear here  
      &nbsp;&nbsp;&nbsp;&nbsp;📌   An email alert will be sent automatically to your caregivers
    """)

    with st.expander("📖 Learn More About How It Works"):
        st.markdown("""
        The Unity game captures your physical therapy movements and calculates scores based on performance.  
        Simultaneously, our connected monitoring device streams your vitals into this dashboard using cloud integration.  
        All data is securely stored, and only authorized personnel can access your progress.

        You and your caregivers can revisit your journey anytime, spot trends, and make informed decisions for faster recovery.
        """)

    if st.checkbox("✅ I understand how to use this dashboard"):
        st.success("Awesome! You're all set to explore the other tabs 🚀")

with right_col:
    st.image("model.jpg", caption="Rehab Monitoring Model", use_container_width=True)


# Hide Streamlit menu and footer
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


