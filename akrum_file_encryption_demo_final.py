
import streamlit as st
import numpy as np
import hashlib
import base64
import json
from cryptography.fernet import Fernet

# Cellular Automata-based entropy
def rule30(prev_row):
    row_len = len(prev_row)
    new_row = np.zeros_like(prev_row)
    for i in range(1, row_len - 1):
        left, center, right = prev_row[i - 1], prev_row[i], prev_row[i + 1]
        new_row[i] = left ^ (center or right)
    return new_row

def generate_ca_entropy(seed_index=30, steps=30, width=61):
    grid = np.zeros((steps, width), dtype=int)
    grid[0, seed_index] = 1
    for i in range(1, steps):
        grid[i] = rule30(grid[i - 1])
    return ''.join(str(bit) for bit in grid[-1])

def derive_fernet_key(binary_string):
    hashed = hashlib.sha256(binary_string.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

st.set_page_config(page_title="AKRUM File Encryption Demo", layout="wide")
st.markdown("<h2 style='text-align: center;'>AKRUM File Encryption Demo (Final Fix)</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Encrypt and decrypt uploaded files using AKRUM's entropy engine, now preserving original file names on download.</p>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["🔐 Encrypt File", "📬 Decrypt File"])

with tab1:
    st.subheader("Upload and Encrypt File")
    uploaded_file = st.file_uploader("Drop your file here (any type)", type=None)
    if uploaded_file:
        file_bytes = uploaded_file.read()
        original_name = uploaded_file.name

        entropy = generate_ca_entropy()
        key = derive_fernet_key(entropy)
        f = Fernet(key)
        encrypted_bytes = f.encrypt(file_bytes)

        package = {
            "filename": original_name,
            "filedata": base64.b64encode(encrypted_bytes).decode()
        }
        package_bytes = json.dumps(package).encode()

        st.success("File encrypted successfully!")
        st.code(base64.b64encode(package_bytes).decode()[:300] + '...', language="text")
        st.text_input("Encryption Key (share securely):", key.decode(), key="encryption_key", disabled=True)

        st.download_button("Download Encrypted File",
                           data=package_bytes,
                           file_name=f"encrypted_package.akrum",
                           mime="application/octet-stream")

with tab2:
    st.subheader("Upload Encrypted File & Decrypt")
    enc_file = st.file_uploader("Upload encrypted package file:", type=None, key="enc_file")
    recv_key = st.text_input("Paste the encryption key:")
    if st.button("Decrypt File"):
        try:
            enc_package = enc_file.read()
            package = json.loads(enc_package.decode())
            filename = package["filename"]
            encrypted_data = base64.b64decode(package["filedata"])
            f = Fernet(recv_key.encode())
            decrypted_bytes = f.decrypt(encrypted_data)

            st.success("File decrypted successfully!")
            st.download_button("Download Decrypted File",
                               data=decrypted_bytes,
                               file_name=filename,
                               mime="application/octet-stream")
        except Exception:
            st.error("Decryption failed. Ensure file and key match.")

st.markdown("---")
st.caption("AKRUM is protected under US Patent No. 10,078,492 B2. This prototype demonstrates full file encryption and recovery.")
