# -------------------------
# Imports
# -------------------------
import streamlit as st
import requests
import re
import html
from typing import Tuple
from datetime import datetime

# -------------------------
# Utility stubs for missing functions
# -------------------------
def truncated_label(text: str, ts: str, max_len: int = 20) -> str:
    """Return a truncated label for chat sidebar buttons."""
    label = text[:max_len] + ("..." if len(text) > max_len else "")
    if ts:
        label += f" ({ts})"
    return label

def now_time() -> str:
    """Return current time as HH:MM string."""
    return datetime.now().strftime("%H:%M")
# Config & light styling
# -------------------------
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #18191A !important;
    }
    .match-highlight {
        background-color: #33334d;
        border-radius: 6px;
        padding: 2px 6px;
        color: inherit;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Helpers
# -------------------------
def highlight_occurrences(text: str, query: str) -> Tuple[str, bool]:
    """
    Return (html_with_spans, found_any).
    - Safely escapes non-matching text.
    - Wraps each case-insensitive match of query with <span class='match-highlight'>...</span>.
    """
    if not query:
        return html.escape(text), False
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    found = False
    last_idx = 0
    result = ""
    for match in pattern.finditer(text):
        found = True
        start, end = match.span()
        result += html.escape(text[last_idx:start])
        result += f"<span class='match-highlight'>{html.escape(text[start:end])}</span>"
        last_idx = end
    result += html.escape(text[last_idx:])
    return result, found


# -------------------------
# Session state initialization
# -------------------------
if "chats" not in st.session_state:
    # Each chat is a list of messages: {"role": "user"/"assistant", "content": "...", "time": "HH:MM"}
    st.session_state.chats = []

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# store search term in session state so Clear button can modify it
if "search_term" not in st.session_state:
    st.session_state.search_term = ""

# flag for manual centering request (set True when user presses the button)
if "center_request" not in st.session_state:
    st.session_state.center_request = False

# -------------------------
# UI - Sidebar
# -------------------------

# Branding and sidebar title
st.sidebar.title("Azercell Chatbot")
st.title("")  # Remove main title, will show welcome message below

# Search input bound to session_state
st.sidebar.text_input("Search chats", key="search_term")

def clear_search() -> None:
    st.session_state.search_term = ""

st.sidebar.button("Clear search", on_click=clear_search)

# New chat button
if st.sidebar.button("➕ New Chat"):
    st.session_state.current_chat = None

search_term: str = (st.session_state.get("search_term") or "").strip().lower()


# Build filtered chat list
filtered = []
for i, chat in enumerate(st.session_state.chats):
    if not chat:
        continue
    if not search_term:
        filtered.append((i, chat))
    else:
        # check if any message contains search term
        found = any(search_term in (msg.get("content", "").lower()) for msg in chat)
        if found:
            filtered.append((i, chat))

# Render chat buttons

# Render chat buttons with delete button next to each
for i, chat in filtered:
    if chat:
        first_msg = chat[0].get("content", "")
        ts = chat[0].get("time", "")
        label = truncated_label(first_msg, ts)
    else:
        label = f"Chat {i+1}"

    cols = st.sidebar.columns([0.8, 0.2])
    if cols[0].button(label, key=f"chat_{i}"):
        st.session_state.current_chat = i
    # Delete button (trash icon)
    if cols[1].button("🗑️", key=f"delete_{i}"):
        del st.session_state.chats[i]
        # If deleted current chat, reset selection
        if st.session_state.current_chat == i:
            st.session_state.current_chat = None
        elif st.session_state.current_chat is not None and st.session_state.current_chat > i:
            st.session_state.current_chat -= 1
        st.rerun()

# -------------------------
# Main area - current chat display
# -------------------------

# Main area: welcome message if no chat selected, else show chat
if st.session_state.current_chat is not None and 0 <= st.session_state.current_chat < len(st.session_state.chats):
    current_history = st.session_state.chats[st.session_state.current_chat]
else:
    current_history = []
    st.markdown("""
        # Welcome to Azercell Chatbot
        You can ask questions about:
        - Code of Conduct and Business Ethics
        - Management responsibilities
        - Compliance with laws and regulations
        - Anti-bribery, corruption, and fair competition
        - Data protection and insider trading
        - Whistleblowing and non-retaliation
        - Conflict of interest guidelines
        - Reporting concerns and Ethics Ambassadors
        
        _Please ask only about Azercell's official policies and compliance topics._
    """)

# Render messages. If there's a search term, highlight matches in every message.
for msg in current_history:
    role = msg.get("role", "user")
    content = msg.get("content", "")
    if search_term:
        highlighted_html, _ = highlight_occurrences(content, search_term)
        # we escaped original text; only our span markup remains as HTML
        st.chat_message(role).markdown(highlighted_html, unsafe_allow_html=True)
    else:
        st.chat_message(role).write(content)


# -------------------------
# Chat input & backend streaming
# -------------------------
prompt = st.chat_input("Type your message...")
if prompt is not None and prompt != "":
    # ensure a chat exists
    if st.session_state.current_chat is None:
        st.session_state.chats.append([])
        st.session_state.current_chat = len(st.session_state.chats) - 1
        current_history = st.session_state.chats[st.session_state.current_chat]

    # add user message
    user_time = now_time()
    current_history.append({"role": "user", "content": prompt, "time": user_time})
    st.chat_message("user").write(prompt)

    # stream assistant response into a single placeholder
    with st.chat_message("assistant"):
        placeholder = st.empty()
        received = ""
        with st.spinner('Thinking...'):
            try:
                resp = requests.post(
                    "http://backend:8000/generate/stream",
                    json={"prompt": prompt, "modelName": ""},
                    stream=True,
                    timeout=60
                )
                resp.raise_for_status()
                received = ""
                for chunk in resp.iter_content(chunk_size=32):
                    if not chunk:
                        continue
                    piece = chunk.decode(errors="ignore")
                    received += piece
                    placeholder.markdown(html.escape(received).replace("\n", "<br/>"), unsafe_allow_html=True)
            except requests.RequestException as exc:
                err = f"Error contacting backend: {exc}"
                placeholder.markdown(f"**{html.escape(err)}**")
                received = err
            finally:
                # store assistant message
                current_history.append({"role": "assistant", "content": received, "time": now_time()})
