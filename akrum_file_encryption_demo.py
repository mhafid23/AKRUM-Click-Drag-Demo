
import streamlit as st
import numpy as np
import hashlib
import base64
from cryptography.fernet import Fernet

# CA-based entropy generation
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
st.markdown("<h2 style='text-align: center;'>AKRUM File Upload Encryption Demo</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Encrypt and decrypt uploaded files using AKRUM's patented entropy engine.</p>", unsafe_allow_html=True)
st.markdown("---")

# Tabs for sender and receiver
tab1, tab2 = st.tabs(["🔐 Encrypt File", "📬 Decrypt File"])

with tab1:
    st.subheader("Upload and Encrypt File")
    uploaded_file = st.file_uploader("Drop your file here (any type)", type=None)
    if uploaded_file:
        file_bytes = uploaded_file.read()
        entropy = generate_ca_entropy()
        key = derive_fernet_key(entropy)
        f = Fernet(key)
        encrypted_bytes = f.encrypt(file_bytes)
        encoded_encrypted = base64.b64encode(encrypted_bytes).decode()

        st.success("File encrypted successfully!")
        st.code(encoded_encrypted[:300] + '...', language='text')
        st.text_input("Encryption Key (share securely with recipient):", key.decode(), key="encryption_key", disabled=True)

        st.download_button("Download Encrypted File",
                           data=encrypted_bytes,
                           file_name=f"encrypted_{uploaded_file.name}",
                           mime="application/octet-stream")

with tab2:
    st.subheader("Upload Encrypted File & Decrypt")
    enc_file = st.file_uploader("Upload encrypted file:", type=None, key="enc_file")
    recv_key = st.text_input("Paste the encryption key:")
    if st.button("Decrypt File"):
        try:
            enc_data = enc_file.read()
            f = Fernet(recv_key.encode())
            decrypted_bytes = f.decrypt(enc_data)
            st.success("File decrypted successfully!")
            st.download_button("Download Decrypted File",
                               data=decrypted_bytes,
                               file_name="decrypted_output",
                               mime="application/octet-stream")
        except Exception as e:
            st.error("Decryption failed. Check your file and key.")

st.markdown("---")
st.caption("AKRUM is protected under US Patent No. 10,078,492 B2. This product demo showcases file-level encryption with entropy from cellular automata.")
