import streamlit as st


def set_background(image_path: str):
    """
    Sets a full-page background in Streamlit.
    """

    st.markdown(
        """
        <style>
        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-color: rgba(0, 0, 0, 0.4); /* semi-transparent overlay */
            z-index: -1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
