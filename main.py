import streamlit as st

def calculate_copper_r20(measured_r, measured_temp, nominal_r):
    """Calculates R20 and deviation for standard copper (constant = 234.5)."""
    copper_constant = 234.5
    r_20 = measured_r * ((copper_constant + 20.0) / (copper_constant + measured_temp))
    
    if nominal_r > 0:
        deviation = ((r_20 - nominal_r) / nominal_r) * 100.0
    else:
        deviation = 0.0
        
    return r_20, deviation

# --- Coil Database ---
# Defines the number of pancakes and the nominal resistance for each pancake
COILS = {
    "Q2": {"pancakes": 1, "nominals": [0.1]},
    "MP25": {"pancakes": 1, "nominals": [0.2]},
    "MP50": {"pancakes": 1, "nominals": [0.3]},
    "BBQ": {"pancakes": 3, "nominals": [0.1, 0.2, 0.1]},
    "BBS": {"pancakes": 1, "nominals": [0.5]}
}

# --- UI Configuration ---
st.set_page_config(page_title="Coil QA Calculator", layout="centered")

st.title("Copper Coil R20 Calculator")
st.markdown("Calculate temperature-corrected resistance and tolerances for specific coil assemblies.")

# --- Coil Selection ---
selected_coil = st.selectbox("Select Coil Model", list(COILS.keys()))
coil_info = COILS[selected_coil]

st.divider()

# --- Global Test Parameters ---
st.subheader("Global Test Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    measured_temp = st.number_input("Coil Temp (°C)", min_value=0.0, max_value=100.0, value=20.0, step=0.1)
with col2:
    lower_tolerance = st.number_input("Lower Limit (%)", value=-2.3, step=0.1)
with col3:
    upper_tolerance = st.number_input("Upper Limit (%)", value=5.4, step=0.1)

st.divider()

# --- Dynamic Pancake Inputs ---
st.subheader(f"Measurements for {selected_coil} ({coil_info['pancakes']} Pancake{'s' if coil_info['pancakes'] > 1 else ''})")

measurements = []

# Dynamically generate input fields based on the number of pancakes
for i in range(coil_info["pancakes"]):
    nominal_val = coil_info["nominals"][i]
    
    c1, c2 = st.columns(2)
    with c1:
        # Default the measured value to the nominal value to start
        meas_r = st.number_input(
            f"Pancake {i+1} Measured R (Ω)", 
            min_value=0.0000000, 
            value=float(nominal_val), 
            step=0.0000100, 
            format="%.7f", 
            key=f"meas_{i}" # Unique key required by Streamlit for dynamic loops
        )
    with c2:
        st.text_input(f"Pancake {i+1} Nominal R20", value=f"{nominal_val:.7f} Ω", disabled=True, key=f"nom_{i}")
        
    measurements.append((meas_r, nominal_val))

# --- Calculation & Output Section ---
if st.button("Calculate R20 Results", type="primary"):
    st.divider()
    st.subheader("QA Test Results")
    
    total_measured_r = 0.0
    total_nominal_r = 0.0
    
    for i, (meas_r, nom_r) in enumerate(measurements):
        r20, deviation = calculate_copper_r20(meas_r, measured_temp, nom_r)
        
        # Add to totals for overall assembly check
        total_measured_r += meas_r
        total_nominal_r += nom_r
        
        st.markdown(f"**Pancake {i+1} Analysis**")
        res_col, dev_col = st.columns(2)
        
        res_col.metric(label="Calculated R20", value=f"{r20:.7f} Ω")
        
        if lower_tolerance <= deviation <= upper_tolerance:
            dev_col.metric(label="Deviation", value=f"{deviation:.5f} %", delta="Pass", delta_color="normal")
            st.success(f"✅ **PASS**: Pancake {i+1} deviation ({deviation:.5f}%) is within limits.")
        else:
            dev_col.metric(label="Deviation", value=f"{deviation:.5f} %", delta="Fail", delta_color="inverse")
            st.error(f"❌ **FAIL**: Pancake {i+1} deviation ({deviation:.5f}%) is outside limits.")
        
        # Add spacing between pancake results
        if i < len(measurements) - 1:
            st.write("---")
            
    # --- Total Assembly Calculation for Multi-Pancake Coils ---
    if coil_info["pancakes"] > 1:
        st.divider()
        st.subheader(f"Total Assembly Results ({selected_coil})")
        
        total_r20, total_deviation = calculate_copper_r20(total_measured_r, measured_temp, total_nominal_r)
        
        tot_res_col, tot_dev_col = st.columns(2)
        
        tot_res_col.metric(label="Total Calculated R20", value=f"{total_r20:.7f} Ω")
        
        if lower_tolerance <= total_deviation <= upper_tolerance:
            tot_dev_col.metric(label="Total Deviation", value=f"{total_deviation:.5f} %", delta="Pass", delta_color="normal")
            st.success(f"✅ **ASSEMBLY PASS**: The total coil deviation ({total_deviation:.5f}%) is within limits.")
        else:
            tot_dev_col.metric(label="Total Deviation", value=f"{total_deviation:.5f} %", delta="Fail", delta_color="inverse")
            st.error(f"❌ **ASSEMBLY FAIL**: The total coil deviation ({total_deviation:.5f}%) is outside limits.")

# --- Signature Section ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: right; color: gray; font-size: 0.9em; line-height: 1.4;'>
        <i>App developed & maintained by:</i><br>
        <b>Bimo Adhi Prastya</b><br>
        Coil Shop Technician
    </div>
    """, 
    unsafe_allow_html=True
)
