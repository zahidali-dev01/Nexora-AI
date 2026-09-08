import streamlit as st
import requests
import json
import os
from datetime import datetime


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Nexora AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8080/v1/chat/completions"

CHAT_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "chats"
)

os.makedirs(CHAT_FOLDER, exist_ok=True)


SYSTEM_PROMPT = """
You are Nexora, a helpful private AI assistant.

Your goals:
- Give accurate answers.
- Explain things clearly.
- Keep answers easy to understand.
- Be friendly and natural.
- Use examples when useful.
- If you do not know something, say so honestly.
"""


# =========================================================
# CHAT FUNCTIONS
# =========================================================

def create_chat():
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


def generate_chat_title(message):

    title = " ".join(message.split())

    title = title.replace("?", "")
    title = title.replace("!", "")

    if len(title) > 45:

        title = title[:45]

        if " " in title:
            title = title.rsplit(" ", 1)[0]

        title += "..."

    return title


def save_chat(messages, filename, title):

    filepath = os.path.join(
        CHAT_FOLDER,
        filename
    )

    data = {
        "title": title,
        "messages": messages
    }

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_chat(filename):

    filepath = os.path.join(
        CHAT_FOLDER,
        filename
    )

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    # New format
    if isinstance(data, dict):

        return (
            data.get(
                "messages",
                create_chat()
            ),
            data.get(
                "title",
                "Untitled Chat"
            )
        )

    # Old format
    if isinstance(data, list):

        title = "Previous Chat"

        for message in data:

            if message.get("role") == "user":

                title = generate_chat_title(
                    message.get(
                        "content",
                        ""
                    )
                )

                break

        return data, title

    return create_chat(), "Untitled Chat"


def get_chat_files():

    files = []

    for file in os.listdir(CHAT_FOLDER):

        if file.endswith(".json"):
            files.append(file)

    return sorted(
        files,
        reverse=True
    )


def get_chat_title(filename):

    filepath = os.path.join(
        CHAT_FOLDER,
        filename
    )

    try:

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, dict):

            return data.get(
                "title",
                "Untitled Chat"
            )

        if isinstance(data, list):

            for message in data:

                if message.get("role") == "user":

                    return generate_chat_title(
                        message.get(
                            "content",
                            ""
                        )
                    )

    except Exception:
        pass

    return "Untitled Chat"


def delete_chat(filename):

    filepath = os.path.join(
        CHAT_FOLDER,
        filename
    )

    if os.path.exists(filepath):

        os.remove(filepath)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = create_chat()


if "chat_file" not in st.session_state:
    st.session_state.chat_file = None


if "chat_title" not in st.session_state:
    st.session_state.chat_title = None


if "rename_chat" not in st.session_state:
    st.session_state.rename_chat = None


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0f1117;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #151821;
        border-right: 1px solid #252936;
    }

    .main-title {
        text-align: center;
        margin-top: 25px;
        margin-bottom: 4px;
        color: white;
        font-size: 38px;
        font-weight: 700;
    }

    .subtitle {
        text-align: center;
        color: #9ca3af;
        margin-bottom: 25px;
        font-size: 15px;
    }

    .status {
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
        padding: 6px 14px;
        border-radius: 20px;
        background-color: #18251d;
        border: 1px solid #294b35;
        color: #7ee2a8;
        font-size: 13px;
        margin-bottom: 30px;
    }

    [data-testid="stChatMessage"] {
        background-color: transparent;
        padding-top: 8px;
        padding-bottom: 8px;
    }

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        background-color: #1b1f2a;
        color: white;
        border: 1px solid #2b3040;
    }

    .stButton > button:hover {
        background-color: #242938;
        border-color: #6b7280;
    }

    .bottom-text {
        text-align: center;
        color: #6b7280;
        font-size: 12px;
        margin-top: 25px;
    }

    .welcome-title {
        text-align: center;
        color: #d1d5db;
        margin-top: 80px;
        font-size: 27px;
        font-weight: 600;
    }

    .welcome-subtitle {
        text-align: center;
        color: #6b7280;
        margin-top: 8px;
        margin-bottom: 30px;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🤖 Nexora")

    st.caption(
        "Private • Local • Offline"
    )

    st.divider()


    # =====================================================
    # NEW CHAT
    # =====================================================

    if st.button(
        "＋ New Chat",
        use_container_width=True
    ):

        if len(
            st.session_state.messages
        ) > 1:

            if st.session_state.chat_file is None:

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                st.session_state.chat_file = (
                    f"chat_{timestamp}.json"
                )


            if st.session_state.chat_title is None:

                for message in (
                    st.session_state.messages
                ):

                    if message["role"] == "user":

                        st.session_state.chat_title = (
                            generate_chat_title(
                                message["content"]
                            )
                        )

                        break


            save_chat(
                st.session_state.messages,
                st.session_state.chat_file,
                st.session_state.chat_title
            )


        st.session_state.messages = create_chat()

        st.session_state.chat_file = None

        st.session_state.chat_title = None

        st.session_state.rename_chat = None

        st.rerun()


    st.divider()


    # =====================================================
    # SAVED CHATS
    # =====================================================

    st.markdown("### 💬 Saved Chats")

    chat_files = get_chat_files()


    if chat_files:

        for chat_file in chat_files:

            title = get_chat_title(
                chat_file
            )


            # -------------------------------------------------
            # CHAT TITLE
            # -------------------------------------------------

            col1, col2 = st.columns(
                [5, 1]
            )


            with col1:

                if st.button(
                    f"💬 {title}",
                    key=f"open_{chat_file}",
                    use_container_width=True
                ):

                    (
                        messages,
                        loaded_title
                    ) = load_chat(
                        chat_file
                    )

                    st.session_state.messages = (
                        messages
                    )

                    st.session_state.chat_file = (
                        chat_file
                    )

                    st.session_state.chat_title = (
                        loaded_title
                    )

                    st.session_state.rename_chat = None

                    st.rerun()


            # -------------------------------------------------
            # MENU BUTTON
            # -------------------------------------------------

            with col2:

                if st.button(
                    "⋮",
                    key=f"menu_{chat_file}"
                ):

                    if (
                        st.session_state.rename_chat
                        == chat_file
                    ):

                        st.session_state.rename_chat = None

                    else:

                        st.session_state.rename_chat = (
                            chat_file
                        )

                    st.rerun()


            # -------------------------------------------------
            # RENAME / DELETE MENU
            # -------------------------------------------------

            if (
                st.session_state.rename_chat
                == chat_file
            ):

                st.caption(
                    "Chat options"
                )


                # Rename input
                new_title = st.text_input(
                    "Rename",
                    value=title,
                    key=f"title_{chat_file}"
                )


                if st.button(
                    "✏️ Save Name",
                    key=f"rename_{chat_file}"
                ):

                    try:

                        messages, _ = load_chat(
                            chat_file
                        )

                        save_chat(
                            messages,
                            chat_file,
                            new_title.strip()
                            if new_title.strip()
                            else "Untitled Chat"
                        )

                        # Update current chat
                        if (
                            st.session_state.chat_file
                            == chat_file
                        ):

                            st.session_state.chat_title = (
                                new_title.strip()
                                if new_title.strip()
                                else "Untitled Chat"
                            )

                        st.session_state.rename_chat = None

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Rename failed: {e}"
                        )


                # Delete
                if st.button(
                    "🗑️ Delete Chat",
                    key=f"delete_{chat_file}"
                ):

                    delete_chat(
                        chat_file
                    )

                    # If deleting current chat
                    if (
                        st.session_state.chat_file
                        == chat_file
                    ):

                        st.session_state.messages = (
                            create_chat()
                        )

                        st.session_state.chat_file = None

                        st.session_state.chat_title = None

                    st.session_state.rename_chat = None

                    st.rerun()


    else:

        st.caption(
            "No saved conversations yet."
        )


    st.divider()


    # =====================================================
    # MODEL
    # =====================================================

    st.markdown("### ⚙️ Model")

    st.write("**Qwen 1.5B**")

    st.caption(
        "GGUF • Q4_K_M"
    )


    st.divider()


    # =====================================================
    # STATUS
    # =====================================================

    st.markdown("### 🖥️ Status")

    st.success(
        "Local AI Server"
    )

    st.caption(
        "Running on your computer"
    )


    st.divider()

    st.caption(
        "No API • No Cloud"
    )

    st.caption(
        "Your conversations stay local."
    )


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    '<div class="main-title">'
    '🤖 Nexora'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="subtitle">'
    'Your private AI assistant running locally'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="status">'
    '● Local AI is ready'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# WELCOME
# =========================================================

if len(
    st.session_state.messages
) == 1:

    st.markdown(
        '<div class="welcome-title">'
        'How can I help you?'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="welcome-subtitle">'
        'Ask anything. Your request is processed locally.'
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# DISPLAY CHAT
# =========================================================

for message in (
    st.session_state.messages
):

    if message["role"] == "system":
        continue

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# USER INPUT
# =========================================================

user_input = st.chat_input(
    "Message Nexora..."
)


if user_input:

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    if (
        st.session_state.chat_title
        is None
    ):

        st.session_state.chat_title = (
            generate_chat_title(
                user_input
            )
        )


    # -----------------------------------------------------
    # CHAT FILE
    # -----------------------------------------------------

    if (
        st.session_state.chat_file
        is None
    ):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        st.session_state.chat_file = (
            f"chat_{timestamp}.json"
        )


    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )


    with st.chat_message(
        "user"
    ):

        st.markdown(
            user_input
        )


    # -----------------------------------------------------
    # REQUEST
    # -----------------------------------------------------

    data = {

        "messages":
            st.session_state.messages,

        "temperature":
            0.7,

        "max_tokens":
            1024,

        "stream":
            True
    }


    try:

        with st.chat_message(
            "assistant"
        ):

            response = requests.post(

                API_URL,

                json=data,

                stream=True,

                timeout=120
            )


            response.raise_for_status()


            placeholder = st.empty()

            full_response = ""


            # -------------------------------------------------
            # STREAM RESPONSE
            # -------------------------------------------------

            for line in (
                response.iter_lines()
            ):

                if not line:
                    continue


                line = line.decode(
                    "utf-8"
                )


                if line.startswith(
                    "data: "
                ):

                    line = line[6:]


                if line == "[DONE]":

                    break


                try:

                    chunk = json.loads(
                        line
                    )


                    token = (
                        chunk
                        ["choices"][0]
                        .get(
                            "delta",
                            {}
                        )
                        .get(
                            "content",
                            ""
                        )
                    )


                    if token:

                        full_response += token


                        placeholder.markdown(
                            full_response
                            + "▌"
                        )


                except json.JSONDecodeError:

                    continue


            placeholder.markdown(
                full_response
            )


        # -----------------------------------------------------
        # SAVE RESPONSE
        # -----------------------------------------------------

        st.session_state.messages.append(
            {
                "role":
                    "assistant",

                "content":
                    full_response
            }
        )


        # -----------------------------------------------------
        # SAVE CHAT
        # -----------------------------------------------------

        save_chat(

            st.session_state.messages,

            st.session_state.chat_file,

            st.session_state.chat_title
        )


    except Exception as e:

        st.error(
            "⚠️ Unable to connect to Nexora."
        )

        st.caption(
            "Make sure llama-server is running "
            "on port 8080."
        )

        st.code(
            str(e)
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="bottom-text">'
    'Nexora AI • Qwen 1.5B • llama.cpp • 100% Local'
    '</div>',
    unsafe_allow_html=True
)