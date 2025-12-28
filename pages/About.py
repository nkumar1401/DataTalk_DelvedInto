import streamlit as st
import os

st.set_page_config(page_title="About the Creator", page_icon="👩‍💻")

def show_about_page():
    st.title("👩‍💻 About the Developer & Vision")
    st.markdown("---")
    
    # Creator Profile Section
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Check if the image exists locally, otherwise use a placeholder
        if os.path.exists("profile.png"):
            st.image("profile.png", use_container_width=True)
        else:
            st.image("https://img.icons8.com/fluency/150/000000/artificial-intelligence.png", caption="Image not found")

    with col2:
        st.subheader("Nirmal Kumar Bhagatkar")
        st.markdown("**AI/ML Specialist | Systems Architect | Founder**")
        st.write("""
        Dedicated to engineering intelligent systems that bridge the gap between complex 
        data architectures and actionable business intelligence. My objective is to solve 
        global-scale challenges by automating high-friction human tasks, thereby increasing 
        the dignity and efficiency of human labor.
        """)

    st.markdown("---")

    # Project Philosophy
    st.header("🚀 The DataTalk Mission")
    st.info("""
    **DataTalk** was conceived as a solution to the 'Data Literacy Gap.' This system 
    utilizes Generative AI (Google Gemini) to democratize analytics—allowing users 
    to 'talk' to their data through natural language.
    """)

    # Technical Leadership Section
    st.header("🛠️ Technical Implementation")
    tab1, tab2, tab3 = st.tabs(["Automation", "Intelligence", "Security"])
    
    with tab1:
        st.write("**Data Preparation:** Implemented automated missing value imputation and IQR-based outlier detection.")
    with tab2:
        st.write("**Conversational Engine:** Leveraged Gemini-1.5-Flash for zero-shot natural language to Pandas translation.")
    with tab3:
        st.write("**Data Privacy:** Built with a security-first approach using secret management and secure namespaces.")

    # Future Outlook - FIXED TYPO HERE
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d; font-size: 1.1em; font-weight: 500;">
        <i>"Building the future of AI-driven automation to solve world problems and minimize human workload."</i>
    </div>
    """, unsafe_allow_html=True) # Corrected argument name

if __name__ == "__main__":
    show_about_page()