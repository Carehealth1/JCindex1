import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

# Set page config
st.set_page_config(
    page_title="JC Index Drug Monitoring",
    page_icon="💊",
    layout="wide"
)

# Initialize session state for data storage (instead of SQLite)
if 'infusions' not in st.session_state:
    st.session_state.infusions = [
        {'id': 21, 'date': '2025-08-27', 'weight': 91, 'dose': '910 mg', 'volume': '9.1 mL', 'notes': 'infusion'},
        {'id': 20, 'date': '2025-08-13', 'weight': 91, 'dose': '910 mg', 'volume': '9.1 mL', 'notes': 'No notes'},
        {'id': 19, 'date': '2025-07-28', 'weight': 91, 'dose': '910 mg', 'volume': '9.1 mL', 'notes': 'No notes'},
        {'id': 18, 'date': '2025-05-12', 'weight': 91, 'dose': '910 mg', 'volume': '9.1 mL', 'notes': 'No notes'}
    ]

if 'jc_measurements' not in st.session_state:
    st.session_state.jc_measurements = [
        {'date': '2025-08-27', 'jc_index': 4.5, 'type': 'Baseline', 'notes': 'mri'},
        {'date': '2025-08-13', 'jc_index': 4.1, 'type': 'Baseline', 'notes': 'N/A'},
        {'date': '2025-07-30', 'jc_index': 3.8, 'type': 'Baseline', 'notes': 'weew'},
        {'date': '2025-07-15', 'jc_index': 3.6, 'type': 'Baseline', 'notes': '1'},
        {'date': '2025-06-05', 'jc_index': 3.2, 'type': 'Baseline', 'notes': '44'},
        {'date': '2025-05-12', 'jc_index': 3.4, 'type': 'Follow-up', 'notes': '4r'}
    ]

# Calculate risk level
def calculate_risk(jc_index):
    if jc_index >= 4.0:
        return "High", "🔴"
    elif jc_index >= 3.5:
        return "Medium", "🟡"
    return "Low", "🟢"

# Sidebar
with st.sidebar:
    st.header("Patient Information")
    patient_id = st.text_input("Patient ID", "Patient 001")
    st.markdown("---")
    st.markdown("""
    ### Risk Levels
    - 🟢 Low: < 3.5
    - 🟡 Medium: 3.5 - 4.0
    - 🔴 High: > 4.0
    """)

# Main title
st.title("Drug Treatment Flowsheet")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📊 Summary", "💉 Infusions", "🧠 JC Index Tracking"])

with tab1:
    st.header("Summary")
    
    # Overview metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_infusions = len(st.session_state.infusions)
        st.metric(
            label="Treatment Progress", 
            value=f"Infusion {total_infusions} of 14"
        )
    
    with col2:
        if st.session_state.jc_measurements:
            latest_jc = st.session_state.jc_measurements[0]
            st.metric(
                label="Latest JC Index", 
                value=f"{latest_jc['jc_index']}"
            )
            st.caption(f"Date: {latest_jc['date']}")
            st.caption(f"Type: {latest_jc['type']}")
    
    with col3:
        st.metric(
            label="CMS Registry",
            value="123445"
        )
    
    # JC Index Status
    if st.session_state.jc_measurements:
        st.subheader("JC Index Status")
        latest_jc = st.session_state.jc_measurements[0]
        risk_level, risk_emoji = calculate_risk(latest_jc['jc_index'])
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.selectbox("Select Status", ["Select Status"])
        
        with col2:
            if risk_level == "High":
                st.error(f"{risk_emoji} {risk_level} Risk - Current JC Index: {latest_jc['jc_index']}")
            elif risk_level == "Medium":
                st.warning(f"{risk_emoji} {risk_level} Risk - Current JC Index: {latest_jc['jc_index']}")
            else:
                st.success(f"{risk_emoji} {risk_level} Risk - Current JC Index: {latest_jc['jc_index']}")

with tab2:
    st.header("Infusion History")
    
    # Add new infusion form
    with st.expander("➕ Add New Infusion"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_infusion_id = st.number_input("Infusion Number", min_value=1, value=22)
            weight = st.number_input("Patient Weight (kg)", min_value=1, value=91)
            
        with col2:
            infusion_date = st.date_input("Infusion Date", value=datetime.now().date())
            notes = st.text_area("Notes", placeholder="Enter notes")
        
        if st.button("Save Infusion", type="primary"):
            dose = f"{weight * 10} mg"
            volume = f"{weight * 10 / 100:.1f} mL"
            
            new_infusion = {
                'id': new_infusion_id,
                'date': str(infusion_date),
                'weight': weight,
                'dose': dose,
                'volume': volume,
                'notes': notes if notes else 'No notes'
            }
            
            st.session_state.infusions.insert(0, new_infusion)
            st.success("Infusion saved successfully!")
            st.rerun()
    
    # Display infusions
    for infusion in st.session_state.infusions:
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(f"Infusion #{infusion['id']} - {infusion['date']}")
                st.write(f"**Weight:** {infusion['weight']} kg | **Dose:** {infusion['dose']} | **Volume:** {infusion['volume']}")
                st.caption(f"Notes: {infusion['notes']}")
            with col2:
                st.success("✓ Completed")
            st.divider()

with tab3:
    st.header("JC Index Tracking")
    
    # Add new JC Index form
    with st.expander("➕ Add JC Index Entry"):
        col1, col2 = st.columns(2)
        
        with col1:
            jc_date = st.date_input("Date", value=datetime.now().date())
            jc_index = st.number_input("JC Index", min_value=0.0, max_value=10.0, step=0.1, format="%.1f")
            
        with col2:
            jc_type = st.selectbox("JC Index Type", ["Baseline", "Follow-up"])
            jc_notes = st.text_area("Radiologist Notes", placeholder="Enter notes")
        
        if st.button("Save JC Entry", type="primary"):
            new_jc = {
                'date': str(jc_date),
                'jc_index': jc_index,
                'type': jc_type,
                'notes': jc_notes if jc_notes else 'N/A'
            }
            
            st.session_state.jc_measurements.insert(0, new_jc)
            st.success("JC Index entry saved successfully!")
            st.rerun()
    
    # JC Index Trend Chart
    if st.session_state.jc_measurements:
        st.subheader("JC Index Trend")
        
        # Create DataFrame from session state
        jc_df = pd.DataFrame(st.session_state.jc_measurements)
        jc_df['date'] = pd.to_datetime(jc_df['date'])
        jc_df_sorted = jc_df.sort_values('date')
        
        fig = px.line(
            jc_df_sorted, 
            x='date', 
            y='jc_index',
            markers=True,
            title='JC Index Over Time'
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="JC Index",
            yaxis=dict(range=[0, 6])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # JC Index History
        st.subheader("JC Index History")
        for entry in st.session_state.jc_measurements:
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.subheader(f"Date: {entry['date']}")
                    st.write(f"🧠 **JC Index Type:** {entry['type']}")
                    st.caption(f"Radiologist Notes: {entry['notes']}")
                with col2:
                    st.metric("JC Index", entry['jc_index'])
                st.divider()

# Add download functionality
st.sidebar.markdown("---")
if st.sidebar.button("📥 Download Data"):
    # Create DataFrames
    infusions_df = pd.DataFrame(st.session_state.infusions)
    jc_df = pd.DataFrame(st.session_state.jc_measurements)
    
    # Display download info
    st.sidebar.success("Data prepared for download!")
    
    # You can add actual download functionality here
    st.sidebar.download_button(
        label="Download Infusions CSV",
        data=infusions_df.to_csv(index=False),
        file_name=f"infusions_{patient_id}.csv",
        mime="text/csv"
    )
    
    st.sidebar.download_button(
        label="Download JC Index CSV", 
        data=jc_df.to_csv(index=False),
        file_name=f"jc_index_{patient_id}.csv",
        mime="text/csv"
    )
