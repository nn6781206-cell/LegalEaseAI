import html
import os
from datetime import date

import requests
import streamlit as st

from dotenv import load_dotenv

from utils.document_export import (
    format_docx,
    format_pdf,
    format_txt,
)


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


st.set_page_config(

    page_title="LegalEase",

    page_icon="⚖️",

    layout="wide",
)


# -----------------------------
# CSS
# -----------------------------

st.markdown(
    """
    <style>

    .hero {

        padding: 1.5rem;

        border-radius: 16px;

        background:
        linear-gradient(
            135deg,
            #111827,
            #1f2937
        );

        color: white;

        margin-bottom: 1rem;
    }

    .preview {

        background: #111827;

        color: #f9fafb;

        border-radius: 12px;

        padding: 1.25rem;

        min-height: 420px;

        max-height: 620px;

        overflow-y: auto;

        white-space: pre-wrap;

        font-family: Georgia, serif;

        line-height: 1.65;
    }

    .notice {

        padding: .75rem 1rem;

        border-left: 4px solid #64748b;

        background: #f8fafc;

        border-radius: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Session state
# -----------------------------

if "document_text" not in st.session_state:

    st.session_state.document_text = ""


if "generated_type" not in st.session_state:

    st.session_state.generated_type = (
        "Legal Document"
    )


# -----------------------------
# Header
# -----------------------------

st.markdown(
    """
    <div class="hero">

        <h1>⚖️ LegalEase</h1>

        <p>
        AI-powered legal document
        drafting, editing and export.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="notice">

    <b>Important:</b>

    LegalEase creates drafts for
    informational purposes.

    Review the document with a qualified
    legal professional for your jurisdiction
    before signing or relying on it.

    </div>
    """,
    unsafe_allow_html=True,
)


st.write("")


# -----------------------------
# Layout
# -----------------------------

left, right = st.columns(
    [1, 1.35],
    gap="large"
)


# =====================================================
# LEFT SIDE
# =====================================================

with left:

    st.subheader(
        "Document details"
    )

    document_type = st.selectbox(

        "Document type",

        [

            "Employment Contract",

            "Non-Disclosure Agreement (NDA)",

            "Lease Agreement",

            "Freelance Work Contract",

            "Service Agreement",

            "Employment Offer Letter",

            "General Agreement",

            "Other",
        ],
    )


    if document_type == "Other":

        document_type = st.text_input(

            "Enter document type",

            placeholder=(
                "e.g. Partnership Agreement"
            ),
        )


    parties = st.text_area(

        "Parties involved",

        height=110,

        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
    )


    terms = st.text_area(

        "Terms & conditions",

        height=170,

        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),

        help=(
            "Separate individual terms "
            "with semicolons."
        ),
    )


    effective_date = st.date_input(

        "Effective date",

        value=date.today(),
    )


    additional_instructions = st.text_area(

        "Additional instructions (optional)",

        height=100,

        placeholder=(
            "Use simple professional English; "
            "include a signature section."
        ),
    )


    generate = st.button(

        "✨ Generate Document",

        type="primary",

        use_container_width=True,
    )


    # -----------------------------
    # Generate
    # -----------------------------

    if generate:

        if (
            not document_type.strip()
            or not parties.strip()
            or not terms.strip()
        ):

            st.error(
                "Please fill in document type, "
                "parties, and terms."
            )

        else:

            payload = {

                "document_type":
                    document_type.strip(),

                "parties":
                    parties.strip(),

                "terms":
                    terms.strip(),

                "effective_date":
                    effective_date.isoformat(),

                "additional_instructions":
                    additional_instructions.strip(),
            }


            with st.spinner(
                "Generating your document draft..."
            ):

                try:

                    response = requests.post(

                        f"{BACKEND_URL}/generate",

                        json=payload,

                        timeout=120,
                    )


                    response.raise_for_status()


                    data = response.json()


                    st.session_state.document_text = (
                        data["generated_text"]
                    )


                    st.session_state.generated_type = (
                        data["document_type"]
                    )


                    st.success(
                        "Document generated successfully."
                    )


                except requests.RequestException as exc:

                    detail = ""

                    if getattr(
                        exc,
                        "response",
                        None
                    ) is not None:

                        try:

                            detail = (
                                exc.response
                                .json()
                                .get(
                                    "detail",
                                    ""
                                )
                            )

                        except Exception:

                            detail = (
                                exc.response
                                .text[:500]
                            )


                    st.error(

                        "Could not connect to "
                        "the LegalEase backend. "

                        f"{detail or exc}"
                    )


# =====================================================
# RIGHT SIDE
# =====================================================

with right:

    st.subheader(
        "Preview & Edit"
    )


    if st.session_state.document_text:

        # HTML preview
        escaped_text = html.escape(
            st.session_state.document_text
        )


        st.markdown(

            f"""
            <div class="preview">
            {escaped_text}
            </div>
            """,

            unsafe_allow_html=True,
        )


        # Editable version
        edited_text = st.text_area(

            "Editable document text",

            value=st.session_state.document_text,

            height=420,

            key="document_editor",
        )


        st.session_state.document_text = (
            edited_text
        )


        # -----------------------------
        # Download buttons
        # -----------------------------

        st.markdown(
            "### Download"
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.download_button(

                "⬇️ TXT",

                data=format_txt(
                    edited_text
                ),

                file_name=(
                    "legalease_document.txt"
                ),

                mime="text/plain",

                use_container_width=True,
            )


        with col2:

            st.download_button(

                "⬇️ DOCX",

                data=format_docx(

                    edited_text,

                    st.session_state
                    .generated_type,
                ),

                file_name=(
                    "legalease_document.docx"
                ),

                mime=(
                    "application/vnd."
                    "openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),

                use_container_width=True,
            )


        with col3:

            st.download_button(

                "⬇️ PDF",

                data=format_pdf(

                    edited_text,

                    st.session_state
                    .generated_type,
                ),

                file_name=(
                    "legalease_document.pdf"
                ),

                mime="application/pdf",

                use_container_width=True,
            )


    else:

        st.info(

            "Your generated document will "
            "appear here. Enter the details "
            "on the left and click "
            "Generate Document."
        )


# -----------------------------
# Footer
# -----------------------------

st.divider()


st.caption(

    "LegalEase • FastAPI + Streamlit + "
    "Google Gemini • AI-generated drafts "
    "should be reviewed before use."
)