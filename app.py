import streamlit as st
import pandas as pd
from fractions import Fraction
from fpdf import FPDF
import io

# ------------------------- CONFIG -------------------------
st.set_page_config(page_title="LandSoft - Land Share Calculator", layout="centered")
st.title("📊 LandSoft - Punjab Land Share Calculator")

# ------------------------- LOGIN SYSTEM -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

VALID_USERS = {
    "admin": "1234",
    "user": "landsoft"
}

def login():
    with st.form("login_form", clear_on_submit=False):
        st.subheader("🔐 Please login to continue")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if username in VALID_USERS and VALID_USERS[username] == password:
                st.session_state.logged_in = True
                st.success("✅ Login successful! Please interact with the app or refresh to continue.")
                st.stop()  # Halt execution so on next interaction main app loads
            else:
                st.error("❌ Invalid username or password")

if not st.session_state.logged_in:
    login()
    st.stop()

def logout():
    st.session_state.logged_in = False
    st.success("✅ Logged out successfully.")
    # No st.experimental_rerun() used; user can manually refresh or interact

st.sidebar.success("✅ Logged in")
st.sidebar.button("🔓 Logout", on_click=logout)

# ------------------------- SHARE CALCULATION -------------------------
def calculate_shares(df):
    results = []
    for _, row in df.iterrows():
        try:
            khewat = str(row['Khewat'])
            total_kanals = int(row['Total_Kanal'])
            total_marlas = int(row['Total_Marla'])
            name = str(row['Owner'])
            share = str(row['Share'])
            remarks = str(row.get('Remarks', ''))

            total_marlas_full = total_kanals * 20 + total_marlas
            share_fraction = Fraction(share)
            owner_marlas = total_marlas_full * share_fraction

            killas = int(owner_marlas // 160)
            remaining = owner_marlas % 160

            kanals = int(remaining // 20)
            remaining = remaining % 20

            marlas = int(remaining)
            fractional_marla = remaining - marlas
            sarshai = round(fractional_marla * 9)

            area_string = f"{killas}K-{kanals}K-{marlas}M"
            if sarshai > 0:
                area_string += f"-{sarshai}S"

            results.append({
                "Khewat": khewat,
                "Owner": name,
                "Share": str(share_fraction),
                "Area": area_string,
                "Remarks": remarks
            })

        except Exception as e:
            results.append({
                "Khewat": row.get('Khewat', ''),
                "Owner": row.get('Owner', ''),
                "Share": row.get('Share', ''),
                "Area": f"Error: {e}",
                "Remarks": row.get('Remarks', '')
            })

    return pd.DataFrame(results)

# ------------------------- PDF GENERATOR -------------------------
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "LandSoft Share Calculation Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        line = f"Khewat: {row['Khewat']} | Owner: {row['Owner']} | Share: {row['Share']} | Area: {row['Area']} | Remarks: {row['Remarks']}"
        pdf.multi_cell(0, 10, txt=line)
    return pdf.output(dest='S').encode('latin1')

# ------------------------- INPUT MODE SWITCH -------------------------
st.subheader("✍️ Choose Input Mode")
input_mode = st.radio("Select how you want to enter data:", ["📄 Upload Excel", "📝 Manual Entry"])

df_result = None

if input_mode == "📄 Upload Excel":
    st.markdown("### Enter Land Details Manually (These fields are NOT imported)")
    khewat = st.text_input("Khewat No")
    col1, col2 = st.columns(2)
    total_kanal = col1.number_input("Total Kanals", min_value=0, step=1)
    total_marla = col2.number_input("Total Marlas", min_value=0, step=1)

    st.markdown("### Upload Excel File (Owner, Share, Remarks)")
    uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])

    if uploaded_file:
        df_input = pd.read_excel(uploaded_file)
        required_cols = ['Owner', 'Share']
        missing_cols = [col for col in required_cols if col not in df_input.columns]

        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
        else:
            if 'Remarks' not in df_input.columns:
                df_input['Remarks'] = ""

            st.write("Preview of uploaded owner/share data:")
            st.dataframe(df_input)

            if st.button("🧮 Calculate Shares"):
                # Combine manual inputs with uploaded data
                df_input['Khewat'] = khewat
                df_input['Total_Kanal'] = total_kanal
                df_input['Total_Marla'] = total_marla

                df_result = calculate_shares(df_input)
                st.success("✅ Share calculation completed!")
                st.dataframe(df_result)

elif input_mode == "📝 Manual Entry":
    st.markdown("### Enter Land Details Manually")

    khewat = st.text_input("Khewat No")
    col1, col2 = st.columns(2)
    total_kanal = col1.number_input("Total Kanals", min_value=0, step=1)
    total_marla = col2.number_input("Total Marlas", min_value=0, step=1)

    st.markdown("### 👥 Owners & Shares")
    num_owners = st.number_input("Number of Owners", min_value=1, step=1, value=1)

    owners = []
    for i in range(num_owners):
        st.markdown(f"**Owner #{i+1}**")
        name = st.text_input(f"Owner Name #{i+1}", key=f"name_{i}")
        share = st.text_input(f"Share (fraction) #{i+1}", key=f"share_{i}")
        remarks = st.text_input(f"Remarks #{i+1}", key=f"remarks_{i}")
        owners.append({
            "Khewat": khewat,
            "Total_Kanal": total_kanal,
            "Total_Marla": total_marla,
            "Owner": name,
            "Share": share,
            "Remarks": remarks
        })

    if st.button("🧮 Calculate Shares"):
        df_manual = pd.DataFrame(owners)
        df_result = calculate_shares(df_manual)
        st.success("✅ Share calculation completed!")
        st.dataframe(df_result)

# ------------------------- EXPORT SECTION -------------------------
if df_result is not None:
    st.subheader("⬇️ Export Result")
    col1, col2 = st.columns(2)

    with col1:
        excel_buffer = io.BytesIO()
        df_result.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)
        st.download_button(
            "📅 Download Excel",
            data=excel_buffer,
            file_name="land_shares.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col2:
        pdf_bytes = generate_pdf(df_result)
        st.download_button(
            "📄 Download PDF Report",
            data=pdf_bytes,
            file_name="land_shares.pdf",
            mime="application/pdf"
        )
