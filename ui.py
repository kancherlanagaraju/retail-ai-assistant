"""
Streamlit UI for Retail AI Assistant.
Provides a web interface for both internal employees and external customers.
"""

import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Retail AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        border-radius: 0.5rem;
        font-size: 1rem;
    }
    .escalation-box {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_type" not in st.session_state:
    st.session_state.user_type = "external"
if "escalated" not in st.session_state:
    st.session_state.escalated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

# API Base URL
API_BASE_URL = "http://localhost:8000"

def make_api_call(query: str, user_info: dict = None) -> dict:
    """Make API call to the agent."""
    try:
        payload = {
            "query": query,
            "user_info": user_info
        }

        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"API Error: {response.status_code}",
                "response": "I apologize, but I encountered an error processing your request."
            }
    except requests.ConnectionError:
        return {
            "error": "Connection Error",
            "response": "I'm unable to connect to the service. Please ensure the API is running on localhost:8000"
        }
    except Exception as e:
        return {
            "error": str(e),
            "response": "I apologize, but I encountered an error processing your request."
        }


def submit_escalation(user_info: dict) -> dict:
    """Submit escalation ticket."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/escalation",
            json=user_info,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


# Main UI Layout
col1, col2 = st.columns([3, 1])

with col1:
    st.title("🤖 Retail AI Assistant")
    st.markdown("*Your intelligent support companion*")

with col2:
    st.markdown("### User Type")
    user_type = st.radio(
        "Select your type:",
        ["👤 External (Customer)", "👨‍💼 Internal (Employee)"],
        format_func=lambda x: x,
        key="user_type_radio"
    )
    st.session_state.user_type = "external" if "External" in user_type else "internal"

st.markdown("---")

# User Information Section
with st.expander("👤 Your Information", expanded=False):
    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input(
            "Full Name",
            value=st.session_state.user_info.get('name', ''),
            key="name_input"
        )

    with col2:
        email = st.text_input(
            "Email Address",
            value=st.session_state.user_info.get('email', ''),
            key="email_input"
        )

    with col3:
        phone = st.text_input(
            "Phone Number",
            value=st.session_state.user_info.get('phone', ''),
            key="phone_input"
        )

    # Update session state
    st.session_state.user_info = {
        'name': name,
        'email': email,
        'phone': phone,
        'user_type': st.session_state.user_type
    }

st.markdown("---")

# Chat Interface
st.markdown("### Chat with Assistant")

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
                if "metadata" in message:
                    with st.expander("View Details"):
                        st.json(message["metadata"])

# Input area
col1, col2 = st.columns([5, 1])

with col1:
    user_query = st.text_input(
        "Your question:",
        placeholder="Ask me anything about our services...",
        key="query_input"
    )

with col2:
    send_button = st.button("Send", use_container_width=True)

# Handle message
if send_button and user_query:
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })

    # Show thinking message
    with st.spinner("Processing your request..."):
        # Make API call
        response = make_api_call(user_query, st.session_state.user_info)

    if "error" not in response or response.get("response"):
        # Add assistant response to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response.get("response", "I apologize, but I encountered an error."),
            "metadata": {
                "sentiment": response.get("sentiment"),
                "department": response.get("department"),
                "escalated": response.get("escalated"),
                "session_id": response.get("session_id")
            }
        })

        # Store escalation status
        if response.get("escalated"):
            st.session_state.escalated = True

        st.rerun()
    else:
        st.error("Failed to process request. Please try again.")

st.markdown("---")

# Escalation Form (shown when escalation triggered)
if st.session_state.escalated or st.button("Request Human Support"):
    st.markdown("### 📞 Escalation Form")
    st.markdown("""
    <div class="escalation-box">
    <strong>Human Support Request</strong><br>
    Your query requires specialized attention. A support specialist will contact you within 24 hours.
    </div>
    """, unsafe_allow_html=True)

    with st.form("escalation_form", clear_on_submit=True):
        st.markdown("#### Please confirm your information:")

        escalation_name = st.text_input(
            "Full Name *",
            value=st.session_state.user_info.get('name', ''),
        )

        escalation_email = st.text_input(
            "Email Address *",
            value=st.session_state.user_info.get('email', ''),
        )

        escalation_phone = st.text_input(
            "Phone Number *",
            value=st.session_state.user_info.get('phone', ''),
        )

        escalation_details = st.text_area(
            "Additional Details (Optional)",
            placeholder="Please provide any additional information about your issue..."
        )

        # Get last query from messages
        last_query = ""
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "user":
                last_query = msg["content"]
                break

        submitted = st.form_submit_button("Submit Escalation Request", use_container_width=True)

        if submitted:
            if not escalation_name or not escalation_email or not escalation_phone:
                st.error("Please fill in all required fields (marked with *)")
            else:
                # Prepare escalation data
                escalation_data = {
                    'name': escalation_name,
                    'email': escalation_email,
                    'phone': escalation_phone,
                    'department': 'Support',
                    'original_query': last_query,
                    'additional_details': escalation_details,
                    'user_type': st.session_state.user_type,
                    'timestamp': datetime.now().isoformat()
                }

                # Submit escalation
                with st.spinner("Creating support ticket..."):
                    result = submit_escalation(escalation_data)

                if "error" not in result:
                    st.markdown("""
                    <div class="success-box">
                    <strong>✓ Support Ticket Created!</strong><br>
                    <strong>Ticket ID:</strong> """ + result.get('ticket_id', 'N/A') + """<br>
                    <strong>Status:</strong> """ + result.get('status', 'CREATED').upper() + """<br>
                    A support specialist will contact you within <strong>24 hours</strong>.<br><br>
                    <em>Confirmation email sent to """ + escalation_email + """</em>
                    </div>
                    """, unsafe_allow_html=True)

                    st.session_state.escalated = False
                    st.session_state.messages.append({
                        "role": "system",
                        "content": f"✓ Escalation ticket {result.get('ticket_id')} has been created."
                    })
                else:
                    st.error(f"Error submitting escalation: {result.get('error')}")

st.markdown("---")

# Footer
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**About**")
    st.caption("Retail AI Assistant v1.0")

with col2:
    st.markdown("**Support**")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

with col3:
    st.markdown("**Status**")
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health_response.status_code == 200:
            st.caption("🟢 API Online")
        else:
            st.caption("🔴 API Offline")
    except:
        st.caption("🔴 API Offline")
