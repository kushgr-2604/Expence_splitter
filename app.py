import streamlit as st
import pytesseract
import cv2
import re
import numpy as np
from PIL import Image

st.set_page_config(page_title="Smart Expense Splitter", layout="wide")

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if "balances" not in st.session_state:
    st.session_state.balances = {}

# ---------- FUNCTIONS ----------
def categorize_expense(text):

    text = text.lower()

    if "restaurant" in text or "zomato" in text or "swiggy" in text:
        return "Food"

    if "uber" in text or "ola" in text:
        return "Travel"

    if "rent" in text:
        return "Rent"

    return "General"

def detect_amount(text):

    # detect ₹ symbol
    match = re.search(r'₹\s?([\d,]+)', text)

    if match:
        return int(match.group(1).replace(",", ""))

    # detect comma numbers like 2,000
    nums = re.findall(r'\d{1,3},\d{3}', text)

    if nums:
        values = [int(n.replace(",", "")) for n in nums]

        # ignore unrealistic values
        values = [v for v in values if v < 10000]

        if values:
            return values[0]

    # detect normal numbers like 2000
    nums = re.findall(r'\b\d{3,4}\b', text)

    if nums:
        return int(nums[0])

    return None
def split_expense(amount, members, payer):

    share = amount / len(members)

    result = []

    for m in members:

        if m != payer:

            result.append(f"{m} pays {payer} ₹{round(share,2)}")

            # update balances
            st.session_state.balances[m] = st.session_state.balances.get(m,0) - share
            st.session_state.balances[payer] = st.session_state.balances.get(payer,0) + share

    return result

# ---------- SESSION STATE ----------

if "members" not in st.session_state:
    st.session_state.members = []

if "expenses" not in st.session_state:
    st.session_state.expenses = []


# ---------- UI ----------

st.title("💰 AI Smart Expense Splitter")

st.sidebar.header("👥 Create Group")

name = st.sidebar.text_input("Add Member")

if st.sidebar.button("Add Member"):
    if name and name not in st.session_state.members:
        st.session_state.members.append(name)

st.sidebar.write("Members:")

for m in st.session_state.members:
    st.sidebar.write("•", m)


st.header("📸 Upload Payment Screenshot")

uploaded_file = st.file_uploader("Upload Screenshot", type=["png","jpg","jpeg"])


if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, width=300)

    img = np.array(image)

    # Ensure correct color conversion (PIL->numpy gives RGB)
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    except Exception:
        # fallback in case image is already BGR or conversion fails
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Wrap Tesseract call to show a helpful error instead of crashing
    try:
        text = pytesseract.image_to_string(gray, config="--psm 6")
    except Exception as e:
        st.error(f"Tesseract error: {e}")
        text = ""

    amount = detect_amount(text)

    st.subheader("🔍 Extracted Text")
    st.write(text)

    category = categorize_expense(text)
    st.info(f"Category: {category}")
    if amount:

        st.success(f"Detected Amount: ₹{amount}")
        st.subheader("💳 Split Expense")

        # Only allow selecting a payer when members exist
        if len(st.session_state.members) > 0:
            payer = st.selectbox("Who Paid?", st.session_state.members)

            if st.button("Split Expense"):

                result = split_expense(amount, st.session_state.members, payer)

                st.subheader("💸 Settlement")

                for r in result:
                    st.success(r)

                st.session_state.expenses.append({
                    "amount": amount,
                    "payer": payer,
                    "split": result
                })
        else:
            st.warning("No members in the group. Add members in the sidebar to split the expense.")


# ---------- HISTORY ----------

st.header("📊 Expense History")

for e in st.session_state.expenses:

    st.write(f"Amount ₹{e['amount']} paid by {e['payer']}")

    for s in e["split"]:
        st.write("   ", s)
st.header("💳 Group Balance")

if st.session_state.balances:

    for person, balance in st.session_state.balances.items():

        if balance > 0:
            st.success(f"{person} should receive ₹{round(balance,2)}")

        elif balance < 0:
            st.error(f"{person} owes ₹{round(abs(balance),2)}")

        else:
            st.info(f"{person} is settled up")