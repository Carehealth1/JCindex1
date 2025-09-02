import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import sqlite3
import numpy as np

# Set page config
st.set_page_config(
    page_title="JC Index Drug Monitoring",
    page_icon="💊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1rem;
        font-weight: 600;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    .risk-high {
        background-color: #fef2f2;
        color: #dc2626;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: 1px solid #fecaca;
    }
    .risk-medium {
        background-color: #fffbeb;
        color: #d97706;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: 1px solid #fed7aa;
    }
    .risk-low {
        background-color: #f0fdf4;
        color: #16a34a;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: 1px solid #bbf7d0;
    }
    .completed-badge {
        background-color: #dcfce7;
        color: #16a34a;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Database initialization
def init_db():
    conn = sqlite3.connect('jc_drug_monitoring.db')
    c = conn.cursor()
    
    # Infusions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS infusions
        (id INTEGER PRIMARY KEY, patient_id TEXT, date DATE, 
         weight INTEGER, dose TEXT, volume TEXT, status TEXT, notes TEXT)
    ''')
    
    # JC Index table
    c.execute('''
        CREATE TABLE IF NOT EXISTS jc_measurements
        (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, date DATE, 
         jc_index REAL, type TEXT, notes TEXT)
    ''')
    
    conn.commit()
    conn.close()

# Calculate risk level
def calculate_risk(jc_index):
    if jc_index >= 4.0:
        return "High"
    elif jc_index >= 3.5:
        return "Medium"
    return "Low"

# Save infusion data
def save_infusion(patient_id, infusion_data):
    conn = sqlite3.connect('jc_drug_monitoring.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO infusions (id, patient_id, date, weight, dose, volume, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        infusion_data['id'],
        patient_id,
        infusion_data['date'],
        infusion_data['weight'],
        infusion_data['dose'],
        infusion_data['volume'],
        'completed',
        infusion_data['notes']
    ))
    conn.commit()
    conn.close()

# Save JC Index data
def save_jc_measurement(patient_id, jc_data):
    conn = sqlite3.connect('jc_drug_monitoring.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO jc_measurements (patient_id, date, jc_index, type, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        patient_id,
        jc_data['date'],
        jc_data['jc_index'],
        jc_data['type'],
        jc_data['notes']
    ))
    conn.commit()
    conn.close()

# Load infusions
def load_infusions(patient_id):
    conn = sqlite3.connect('jc_drug_monitoring.db')
    query = f"SELECT * FROM infusions WHERE patient_id = '{patient_id}' ORDER BY date DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Load JC measurements
def load_jc_measurements(patient_id):
    conn = sqlite3.connect('jc_drug_monitoring.db')
    query = f"SELECT * FROM jc_measurements WHERE patient_id = '{patient_id}' ORDER BY date DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Initialize sample data if database is empty
def init_sample_data(patient_id):
    infusions_df = load_infusions(patient_id)
    jc_df = load_jc_measurements(patient_id)
    
    if infusions_df.empty:
        sample_infusions = [
            {'id': 21, 'date': '2025-08-27', 'weight': 91, 'dose': '910 mg', 'volume': '9.1 mL', 'notes': 'infusion'},
            {'id': 20, 'date': '2025-08-13', 'weight': 91, 'dose': '910 mg', 'volume': '9.1 mL', 'notes': 'No notes'},
            {'id': 19, 'date': '2025-07-28', 'weight': 91, 'dose': '910 mg', 'volume': '9.1 mL', 'notes': 'No notes'},
            {'id': 18, 'date': '2025-05-12', 'weight': 91, 'dose': '910 mg', 'volume': '9.1 mL', 'notes': 'No notes'}
        ]
        for infusion in sample_infusions:
            save_infusion(patient_id, infusion)
    
    if jc_df.empty:
        sample_jc = [
            {'date': '2025-08-27', 'jc_index': 4.5, 'type': 'Baseline', 'notes': 'mri'},
            {'date': '2025-08-13', 'jc_index': 4.1, 'type': 'Baseline', 'notes': 'N/A'},
            {'date': '2025-07-30', 'jc_index': 3.8, 'type': 'Baseline', 'notes': 'weew'},
            {'date': '2025-07-15', 'jc_index': 3.6, 'type': 'Baseline', 'notes': '1'},
            {'date': '2025-06-05', 'jc_index': 3.2, 'type': 'Baseline', 'notes': '44'},
            {'date': '2025-05-12', 'jc_index': 3.4, 'type': 'Follow-up', 'notes': '4r'}
        ]
        for jc in sample_jc:
            save_jc_measurement(patient_id, jc)

# Initialize database and sample data
init_db()

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

# Initialize sample data for the patient
init_sample_data(patient_id)

# Load data
infusions_df = load_infusions(patient_id)
jc_df = load_jc_measurements(patient_id)

# Main title
st.title("Drug Treatment Flowsheet")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Summary", "Infusions", "JC Index Tracking"])

with tab1:
    st.header("Summary")
    
    # Overview metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_infusions = len(infusions_df) if not infusions_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h4>Treatment Progress</h4>
            <h2>Infusion {total_infusions} of 14</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if not jc_df.empty:
            latest_jc = jc_df.iloc[0]
            st.markdown(f"""
            <div class="metric-card">
                <h4>Latest JC Index Status</h4>
                <p><strong>Date:</strong> {latest_jc['date']}</p>
                <p>🧠 <strong>JC Index:</strong> {latest_jc['type']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>CMS Registry</h4>
            <h2>123445</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # JC Index Status
    if not jc_df.empty:
        latest_jc = jc_df.iloc[0]
        risk_level = calculate_risk(latest_jc['jc_index'])
        
        st.subheader("JC Index Status")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.selectbox("Select Status", ["Select Status"], key="status_select")
        
        risk_class = f"risk-{risk_level.lower()}"
        st.markdown(f"""
        <div class="{risk_class}">
            <strong>{risk_level} Risk</strong><br>
            Current JC Index: {latest_jc['jc_index']}
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.header("Infusion History")
    
    # Add new infusion button
    if st.button("➕ Add New Infusion", type="primary"):
        st.session_state.show_infusion_form = True
    
    # New infusion form
    if st.session_state.get('show_infusion_form', False):
        with st.expander("New Infusion Entry", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                new_infusion_id = st.number_input("Infusion Number", min_value=1, value=22)
                weight = st.number_input("Patient Weight (kg)", min_value=1, value=91)
                
            with col2:
                infusion_date = st.date_input("Infusion Date", value=datetime.now().date())
                notes = st.text_area("Notes", placeholder="Enter notes")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("Calculate Dose"):
                    dose = weight * 10
                    volume = dose / 100
                    st.success(f"Dose: {dose} mg, Volume: {volume:.1f} mL")
            
            with col2:
                if st.button("Save Infusion"):
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
                    
                    save_infusion(patient_id, new_infusion)
                    st.success("Infusion saved successfully!")
                    st.session_state.show_infusion_form = False
                    st.rerun()
            
            with col3:
                if st.button("Cancel"):
                    st.session_state.show_infusion_form = False
                    st.rerun()
    
    # Display infusions
    if not infusions_df.empty:
        for _, infusion in infusions_df.iterrows():
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4>Infusion #{infusion['id']} - {infusion['date']}</h4>
                        <p>Weight: {infusion['weight']} kg | Dose: {infusion['dose']} | Volume: {infusion['volume']}</p>
                        <p style="color: #666;">Notes: {infusion['notes']}</p>
                    </div>
                    <span class="completed-badge">✓ Completed</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.header("JC Index Tracking")
    
    # Add new JC Index button
    if st.button("➕ Add JC Index Tracking", type="primary"):
        st.session_state.show_jc_form = True
    
    # New JC Index form
    if st.session_state.get('show_jc_form', False):
        with st.expander("New JC Index Entry", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                jc_date = st.date_input("Date", value=datetime.now().date(), key="jc_date")
                jc_index = st.number_input("JC Index", min_value=0.0, max_value=10.0, step=0.1, format="%.1f")
                
            with col2:
                jc_type = st.selectbox("JC Index Type", ["Baseline", "Follow-up"])
                jc_notes = st.text_area("Radiologist Notes", placeholder="Enter notes", key="jc_notes")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save JC Entry"):
                    new_jc = {
                        'date': str(jc_date),
                        'jc_index': jc_index,
                        'type': jc_type,
                        'notes': jc_notes if jc_notes else 'N/A'
                    }
                    
                    save_jc_measurement(patient_id, new_jc)
                    st.success("JC Index entry saved successfully!")
                    st.session_state.show_jc_form = False
                    st.rerun()
            
            with col2:
                if st.button("Cancel", key="cancel_jc"):
                    st.session_state.show_jc_form = False
                    st.rerun()
    
    # JC Index Trend Chart
    if not jc_df.empty:
        st.subheader("JC Index Trend")
        
        # Prepare data for plotting
        jc_df_sorted = jc_df.sort_values('date')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=jc_df_sorted['date'],
            y=jc_df_sorted['jc_index'],
            mode='lines+markers',
            name='JC Index',
            line=dict(color='#2563eb', width=2),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="JC Index",
            yaxis=dict(range=[0, 6]),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # JC Index History
        st.subheader("JC Index History")
        for _, entry in jc_df.iterrows():
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4>Date: {entry['date']}</h4>
                        <p>🧠 JC Index Type: {entry['type']}</p>
                        <p style="color: #666;">Radiologist Notes: {entry['notes']}</p>
                    </div>
                    <div style="color: #2563eb; font-size: 1.5rem; font-weight: bold;">
                        {entry['jc_index']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)