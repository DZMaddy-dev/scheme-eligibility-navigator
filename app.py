"""
YojanaSaarthi -- Government Scheme Eligibility Navigator
Track 4: Public Services & Civic Tech | Problem 18
Clean, Interactive, and Grounded Decision Support
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
import base64
import urllib.parse
import pandas as pd
import io
import subprocess
import re

from engine.rule_engine import SchemeRegistry, RuleEngine

# Page Setup
st.set_page_config(
    page_title="YojanaSaarthi",
    page_icon="🪔",
    layout="wide",
    initial_sidebar_state="expanded"
)


def _load_hero_image_b64():
    """Base64-encode the rural illustration (theme.jpeg) if present, for the hero banner."""
    for fname in ("theme.jpeg", "theme.jpg", os.path.join("assets", "theme.jpeg")):
        path = os.path.join(os.path.dirname(__file__), fname)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return None


HERO_IMAGE_B64 = _load_hero_image_b64()

# Reusable inline SVG brand mark (two-tone, matches the YojanaSaarthi logo)
BRAND_LOGO_SVG = '<svg width="34" height="34" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"><circle cx="14" cy="18" r="11" fill="#C98E37" /><polygon points="27,5 5,13 13,17" fill="#274472" /><polygon points="27,5 13,17 19,27" fill="#132238" /><polygon points="13,17 13,24 16.5,20.5" fill="#FDFCF8" /></svg>'

# Modern, Clean Civic Tech Design System CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@700;900&family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-page: #FDFCF8;
        --text-main: #1A2942;
        --text-muted: #4A5568;
        --primary-green: #3B7254;
        --primary-green-hover: #2F5C43;
        --accent-saffron: #E88D67;
        --logo-blue: #274472;
        --logo-blue-dark: #1A2942;
        --logo-mustard: #C98E37;
        --border-rust: #B93C31;
        --input-border: #D8D4CA;
        --card-border: #EAE5D9;
        --card-shadow: 0 10px 30px rgba(26, 41, 66, 0.05);
        --card-shadow-hover: 0 16px 36px rgba(26, 41, 66, 0.09);
        --font-heading: 'Merriweather', 'Noto Sans Devanagari', Georgia, serif;
        --font-sans: 'Inter', 'Noto Sans Devanagari', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        box-sizing: border-box;
    }

    .stApp {
        background-color: var(--bg-page) !important;
        font-family: var(--font-sans) !important;
        color: var(--text-main) !important;
    }

    /* Screen Fitting & Padding without Header Collisions */
    html, body, [data-testid="stAppViewContainer"], .main {
        overflow-x: hidden !important;
        max-width: 100vw !important;
        box-sizing: border-box !important;
    }

    .block-container {
        padding-top: 2.8rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2.2rem !important;
        padding-right: 2.2rem !important;
        max-width: 100% !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    @media (max-width: 1024px) {
        .block-container {
            padding-left: 1.4rem !important;
            padding-right: 1.4rem !important;
            padding-top: 2.4rem !important;
        }
        .main-title {
            font-size: 1.85rem !important;
        }
    }
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.9rem !important;
            padding-right: 0.9rem !important;
            padding-top: 2rem !important;
        }
        .main-title {
            font-size: 1.55rem !important;
        }
    }

    /* Traditional Maithili-motif decorative accent strip */
    .maithili-strip {
        height: 8px;
        width: 100%;
        border-radius: 4px;
        margin: 6px 0 20px 0;
        background-image: repeating-linear-gradient(
            135deg,
            var(--logo-blue) 0px, var(--logo-blue) 12px,
            var(--border-rust) 12px, var(--border-rust) 24px,
            var(--logo-mustard) 24px, var(--logo-mustard) 36px
        );
        opacity: 0.9;
    }

    /* Clean Frosted Header */
    header[data-testid="stHeader"] {
        background-color: rgba(253, 252, 248, 0.92) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid rgba(26, 41, 66, 0.06) !important;
        z-index: 99 !important;
    }

    /* Clean Elevated Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid var(--card-border) !important;
        box-shadow: 2px 0 16px rgba(26, 41, 66, 0.03) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 0.85rem;
    }

    /* Main Title & Subtitle */
    .main-title {
        font-family: var(--font-heading);
        font-size: 2.25rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: var(--text-main);
        margin-bottom: 3px;
        line-height: 1.25;
    }
    .main-sub {
        font-size: 1.02rem;
        color: var(--text-muted);
        margin-bottom: 14px;
        font-weight: 500;
        line-height: 1.55;
    }

    /* Top Metadata Pill Badges */
    .top-badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 22px;
    }
    .top-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #ffffff;
        color: var(--text-muted);
        border: 1px solid var(--input-border);
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(26, 41, 66, 0.03);
        transition: all 0.2s ease;
    }
    .top-badge:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(26, 41, 66, 0.06);
        border-color: var(--logo-mustard);
    }
    .top-badge-green {
        background-color: #EAF2ED;
        color: #1C4532;
        border-color: #B7D4C4;
    }
    .top-badge-blue {
        background-color: #EBF2FA;
        color: var(--logo-blue);
        border-color: #B9C9DE;
    }

    /* Segmented Control Navigation Bar */
    div[data-testid="stSegmentedControl"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid var(--input-border) !important;
        border-radius: 50px !important;
        padding: 5px !important;
        box-shadow: 0 3px 12px rgba(26, 41, 66, 0.04) !important;
        margin-bottom: 24px !important;
        width: 100% !important;
        display: flex !important;
        gap: 6px !important;
    }
    div[data-testid="stSegmentedControl"] button {
        border-radius: 50px !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 10px 24px !important;
        min-height: 44px !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        color: var(--text-muted) !important;
        background: transparent !important;
    }
    div[data-testid="stSegmentedControl"] button:hover {
        color: var(--logo-blue) !important;
        background: rgba(39, 68, 114, 0.05) !important;
    }
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background: var(--logo-blue) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(39, 68, 114, 0.28) !important;
    }

    /* Streamlit Buttons: Clean Pill Buttons */
    button[kind="primary"], .stButton > button[type="primary"], div[data-testid="stFormSubmitButton"] > button {
        background: var(--primary-green) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0 !important;
        padding: 0.65rem 1.4rem !important;
        min-height: 44px !important;
        line-height: 1.25 !important;
        box-shadow: 0 4px 14px rgba(59, 114, 84, 0.24) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        white-space: normal !important;
        word-break: keep-all !important;
        text-align: center !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    button[kind="primary"]:hover, .stButton > button[type="primary"]:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background: var(--primary-green-hover) !important;
        box-shadow: 0 6px 18px rgba(59, 114, 84, 0.35) !important;
        transform: translateY(-2px) !important;
    }
    button[kind="secondary"], .stButton > button:not([type="primary"]) {
        background: #ffffff !important;
        color: var(--text-main) !important;
        border: 1.5px solid var(--input-border) !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.65rem 1.3rem !important;
        min-height: 44px !important;
        line-height: 1.25 !important;
        box-shadow: 0 1px 3px rgba(26, 41, 66, 0.03) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        white-space: normal !important;
        word-break: keep-all !important;
        text-align: center !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    button[kind="secondary"]:hover, .stButton > button:not([type="primary"]):hover {
        background: #FCFAED !important;
        border-color: var(--logo-mustard) !important;
        color: var(--text-main) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(201, 142, 55, 0.15) !important;
    }

    /* Native Link Buttons */
    a[data-testid="baseLinkButton-primary"], a[data-testid="baseLinkButton-secondary"] {
        border-radius: 50px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.6rem 1.2rem !important;
        min-height: 42px !important;
        line-height: 1.25 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    a[data-testid="baseLinkButton-secondary"] {
        border: 1.5px solid var(--input-border) !important;
        color: var(--text-main) !important;
        background: #ffffff !important;
        box-shadow: 0 1px 3px rgba(26, 41, 66, 0.03) !important;
    }
    a[data-testid="baseLinkButton-secondary"]:hover {
        border-color: var(--logo-blue) !important;
        color: var(--logo-blue) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(39, 68, 114, 0.12) !important;
    }

    /* Modern Text Inputs, Selectboxes, Number Inputs */
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] > div {
        border-radius: 12px !important;
        border: 1.5px solid var(--input-border) !important;
        padding: 10px 14px !important;
        font-size: 0.95rem !important;
        background-color: #ffffff !important;
        box-shadow: 0 1px 3px rgba(26, 41, 66, 0.03) !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    div[data-testid="stTextInput"] input:focus, div[data-testid="stNumberInput"] input:focus {
        border-color: var(--logo-blue) !important;
        box-shadow: 0 0 0 3px rgba(39, 68, 114, 0.12) !important;
    }

    /* Container Card Framing (st.container(border=True)) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        border: 1.5px solid var(--card-border) !important;
        background-color: #ffffff !important;
        box-shadow: var(--card-shadow) !important;
        transition: border-color 0.22s ease, box-shadow 0.22s ease, transform 0.22s ease !important;
        box-sizing: border-box !important;
        width: 100% !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: var(--logo-mustard) !important;
        box-shadow: var(--card-shadow-hover) !important;
    }

    /* Form Card Container */
    div[data-testid="stForm"] {
        background: #ffffff !important;
        border: 1.5px solid var(--card-border) !important;
        border-top: 5px solid var(--logo-blue) !important;
        border-radius: 22px !important;
        padding: 28px !important;
        box-shadow: var(--card-shadow) !important;
    }

    /* Modern Hero Card (warm ivory canvas with illustration) */
    .modern-hero-card {
        position: relative;
        width: 100%;
        min-height: 380px;
        border-radius: 24px;
        box-shadow: 0 16px 40px rgba(26, 41, 66, 0.06);
        border: 1.5px solid var(--card-border);
        overflow: hidden;
        display: flex;
        align-items: center;
        background-color: #FDFCF8;
        background-size: cover;
        background-position: center right;
        background-repeat: no-repeat;
        margin-bottom: 24px;
    }
    .modern-hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, rgba(253,252,248,0.98) 0%, rgba(253,252,248,0.92) 50%, rgba(253,252,248,0.35) 80%, rgba(253,252,248,0.05) 100%);
        z-index: 1;
    }
    .modern-hero-content {
        position: relative;
        z-index: 2;
        width: 62%;
        padding: 3.2rem 3rem;
    }
    .hero-brand-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #EAF2ED;
        color: var(--primary-green);
        border: 1px solid #B7D4C4;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .hero-tagline {
        font-family: var(--font-heading);
        font-size: 2.25rem;
        line-height: 1.2;
        color: var(--text-main);
        margin-bottom: 8px;
        letter-spacing: -0.01em;
    }
    .hero-subtitle {
        font-size: 1.12rem;
        font-weight: 500;
        color: var(--text-muted);
        margin-bottom: 12px;
        line-height: 1.4;
    }
    .hero-description {
        font-size: 0.95rem;
        line-height: 1.65;
        color: var(--text-main);
        margin-bottom: 8px;
        max-width: 95%;
    }
    @media (max-width: 900px) {
        .modern-hero-content {
            width: 100%;
            padding: 2.2rem 1.8rem;
        }
        .modern-hero-overlay {
            background: linear-gradient(180deg, rgba(253,252,248,0.98) 0%, rgba(253,252,248,0.92) 60%, rgba(253,252,248,0.3) 100%);
        }
        .hero-tagline {
            font-size: 1.85rem;
        }
    }

    /* Scheme Card Header in Search Engine */
    .scheme-card-header {
        background: linear-gradient(135deg, #1A2942 0%, #274472 65%, #2C5282 100%);
        color: #ffffff;
        padding: 24px 28px;
        border-radius: 20px;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px -5px rgba(26, 41, 66, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.12);
        position: relative;
        overflow: hidden;
        font-family: var(--font-sans);
    }
    .scheme-card-header::after {
        content: '';
        position: absolute;
        top: -50px;
        right: -50px;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(201, 142, 55, 0.25) 0%, rgba(201, 142, 55, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    /* Badges in Hero Cards */
    .hero-benefit-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: linear-gradient(135deg, #3B7254 0%, #2F5C43 100%);
        color: #ffffff;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
        box-shadow: 0 2px 6px rgba(59, 114, 84, 0.25);
    }
    .hero-target-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: #F0F4F8;
        color: var(--logo-blue);
        border: 1px solid #B9C9DE;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-left: 6px;
    }

    /* Verdict Boxes */
    .verdict-box {
        padding: 24px 28px;
        border-radius: 20px;
        margin: 18px 0 22px 0;
        box-shadow: 0 8px 24px rgba(26, 41, 66, 0.05);
    }
    .verdict-eligible {
        background: linear-gradient(135deg, #F0F7F3 0%, #E6F3EB 100%);
        border: 1.5px solid #A3D1B5;
        border-left: 8px solid var(--primary-green);
        color: #1C4532;
    }
    .verdict-ineligible {
        background: linear-gradient(135deg, #FFF7F6 0%, #FDF0EE 100%);
        border: 1.5px solid #F5C6CB;
        border-left: 8px solid var(--border-rust);
        color: #7F1D1D;
    }
    .verdict-uncertain {
        background: linear-gradient(135deg, #FCFAED 0%, #FBF6E3 100%);
        border: 1.5px solid #E8D39B;
        border-left: 8px solid var(--logo-mustard);
        color: #6B4A1C;
    }

    /* Benefit Entitlement Banner */
    .benefit-banner {
        background: linear-gradient(135deg, #3B7254 0%, #2F5C43 100%);
        color: #ffffff;
        padding: 16px 24px;
        border-radius: 16px;
        font-size: 1.18rem;
        font-weight: 700;
        margin: 14px 0 18px 0;
        box-shadow: 0 6px 18px rgba(59, 114, 84, 0.24);
        font-family: var(--font-heading);
        letter-spacing: -0.01em;
    }

    /* Reason Card (Ineligible feedback) */
    .reason-card {
        background-color: #ffffff;
        border: 1.5px solid #F5D3D6;
        border-left: 6px solid var(--border-rust);
        padding: 16px 20px;
        border-radius: 14px;
        margin-bottom: 12px;
        font-size: 0.94rem;
        color: #7F1D1D;
        box-shadow: 0 2px 8px rgba(185, 60, 49, 0.04);
    }

    /* Match Chip */
    .match-chip {
        display: inline-flex;
        align-items: center;
        background-color: #EAF2ED;
        border: 1px solid #B7D4C4;
        color: #1C4532;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.86rem;
        font-weight: 600;
        margin: 4px 6px 4px 0;
    }

    /* Action Cards (Village Help Desks) */
    .action-card {
        background-color: #ffffff;
        border: 1.5px solid var(--card-border);
        border-radius: 18px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 3px 10px rgba(26, 41, 66, 0.03);
        transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .action-card:hover {
        border-color: var(--logo-mustard);
        box-shadow: 0 10px 24px -4px rgba(26, 41, 66, 0.1);
        transform: translateY(-3px);
    }

    /* Official Citizen Slip */
    .citizen-slip {
        background-color: #ffffff;
        border: 1.5px dashed #CBD5E1;
        border-top: 6px solid var(--logo-blue);
        border-radius: 20px;
        padding: 28px 32px;
        margin: 20px 0;
        font-family: var(--font-sans);
        color: var(--text-main);
        box-shadow: 0 8px 24px rgba(26, 41, 66, 0.05);
    }
    .slip-stamp {
        display: inline-block;
        border: 2px solid var(--primary-green);
        background: #EAF2ED;
        color: #1C4532;
        padding: 5px 12px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 0.88rem;
        letter-spacing: 0.5px;
    }
    .slip-stamp-fail {
        display: inline-block;
        border: 2px solid var(--border-rust);
        background: #FFF5F5;
        color: #7F1D1D;
        padding: 5px 12px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 0.88rem;
        letter-spacing: 0.5px;
    }

    /* Radio Items & Custom Controls */
    div[role="radiogroup"] > label {
        background-color: #ffffff !important;
        border: 1.5px solid var(--input-border) !important;
        border-radius: 14px !important;
        padding: 12px 18px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 2px 6px rgba(26, 41, 66, 0.02) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: pointer !important;
    }
    div[role="radiogroup"] > label:hover {
        border-color: var(--logo-mustard) !important;
        background-color: #FCFAED !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(26, 41, 66, 0.06) !important;
    }

    /* Sliders */
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: var(--primary-green) !important;
        border-color: var(--primary-green) !important;
    }

    /* Section heading style */
    h1, h2, h3, h4 {
        font-family: var(--font-heading);
        color: var(--text-main);
    }
</style>
""", unsafe_allow_html=True)


def build_hindi_speech_text(selected_scheme, item, status):
    """Constructs natural, fluent spoken Hindi text for rural voice guidance."""
    scheme_name = selected_scheme.get("hindi_name") or selected_scheme.get("name")

    if status in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE"]:
        benefit = selected_scheme.get("benefit_value", "")
        benefit_hi = (
            benefit.replace("₹", "")
            .replace("per year", "सालाना")
            .replace("annual", "वार्षिक")
            .replace("Lakh", "लाख")
            .replace("k", " हजार")
        )
        return (
            f"बधाई हो! आपकी जानकारी के अनुसार, आप {scheme_name} के लिए पात्र हैं। "
            f"इस योजना के अंतर्गत आपको {benefit_hi} रुपये का लाभ मिलेगा। "
            f"कृपया अपने जरूरी दस्तावेज जैसे आधार कार्ड और बैंक पासबुक लेकर नजदीकी ग्राम पंचायत भवन या जन सेवा केंद्र सीएससी पर जाएं।"
        )

    elif status == "INELIGIBLE":
        criterion_map = {
            "Income Requirement": "आपकी पारिवारिक आय इस योजना की तय सीमा से अधिक है",
            "Housing Asset Exclusion": "आपके पास पहले से पक्का मकान है, जबकि यह योजना बेघर या कच्चे मकान वालों के लिए है",
            "Occupation Requirement": "आपका व्यवसाय इस योजना के नियमों के अनुसार नहीं है",
            "Age Requirement": "आपकी उम्र इस योजना की निर्धारित आयु सीमा में नहीं है",
            "Cultivable Land Ownership": "इस योजना के लिए आपके नाम पर कृषि योग्य जमीन होना अनिवार्य है",
            "Girl Child (Age ≤10) Guardian Status": "सुकन्या समृद्धि के लिए दस वर्ष तक की बालिका का अभिभावक होना जरूरी है",
            "Income Taxpayer Exclusion": "परिवार में कोई आयकर दाता होने के कारण यह लाभ नहीं मिल सकता",
            "Government Employee": "परिवार में सरकारी नौकरी होने के कारण आप पात्र नहीं हैं",
            "Government Employee Exclusion": "परिवार में सरकारी नौकरी होने के कारण आप पात्र नहीं हैं",
            "BPL / Deprivation Status": "इस योजना के लिए बीपीएल या राशन कार्ड सूची में नाम होना अनिवार्य है",
            "Area Requirement": "यह योजना केवल ग्रामीण क्षेत्र के निवासियों के लिए है",
            "State / Territorial Requirement": "यह योजना आपके राज्य में लागू नहीं है"
        }

        hindi_reasons = []
        for f in item.get("why_you_dont_match", []):
            crit = f.get("criterion", "")
            if crit in criterion_map:
                hindi_reasons.append(criterion_map[crit])
            else:
                hindi_reasons.append(f.get("details", ""))

        if not hindi_reasons:
            reasons_str = "आप इस योजना की कुछ जरूरी शर्तों को पूरा नहीं करते हैं।"
        elif len(hindi_reasons) == 1:
            reasons_str = hindi_reasons[0]
        else:
            reasons_str = "। पहला, " + "। दूसरा, ".join(hindi_reasons)

        return (
            f"नमस्कार। आपके द्वारा दी गई जानकारी के अनुसार, आप {scheme_name} के लिए पात्र नहीं हैं। "
            f"अपात्रता का मुख्य कारण है: {reasons_str}। "
            f"यदि आप किसी अन्य योजना की जांच करना चाहते हैं, तो ऊपर दी गई सूची से दूसरी योजना चुन सकते हैं।"
        )

    else:
        return (
            f"नमस्कार। {scheme_name} के लिए आपकी कुछ जानकारी अभी अधूरी है। "
            f"कृपया फॉर्म में बाकी विवरण भी भरें ताकि आपकी पात्रता की सही जांच हो सके।"
        )


def render_voice_guidance(hindi_text_content: str):
    """Client-side browser speech synthesis using Web Speech API in authentic Hindi."""
    clean_text = (
        hindi_text_content.replace('"', ' ')
        .replace("'", " ")
        .replace("\n", " ")
        .replace("₹", "रुपये ")
        .replace("—", "-")
    )
    btn_label = "🔊 हिंदी में बोलकर सुनें (Listen in Hindi)"

    html_code = f"""
    <div style="display:inline-flex; align-items:center; flex-wrap:wrap; gap:10px; background:#FFFFFF; border:1.5px solid #E2DDD2; padding:6px 14px; border-radius:50px; box-shadow:0 2px 8px rgba(26,41,66,0.04); margin:6px 0 16px 0;">
        <button onclick="playSpeech()" style="
            background: linear-gradient(135deg, #3B7254, #2F5C43);
            color: #ffffff;
            border: none;
            padding: 8px 18px;
            font-size: 0.88rem;
            font-weight: 700;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(59,114,84,0.3);
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        ">
            {btn_label}
        </button>
        <button onclick="stopSpeech()" style="
            background: #F4EFE6;
            color: #4A5568;
            border: 1px solid #D6CEBE;
            padding: 8px 14px;
            font-size: 0.84rem;
            font-weight: 600;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.2s;
        ">
            ⏹️ बंद करें (Stop)
        </button>
        <span style="font-size:0.82rem; color:#3B7254; font-weight:600; display:inline-flex; align-items:center; gap:4px; padding-right:6px;">
            <span>🎙️</span> शुद्ध हिंदी आवाज (Native Audio)
        </span>
    </div>
    <script>
    var hindiVoice = null;
    function loadHindiVoice() {{
        if ('speechSynthesis' in window) {{
            var voices = window.speechSynthesis.getVoices();
            for (var i = 0; i < voices.length; i++) {{
                if (voices[i].lang === 'hi-IN' || voices[i].lang.startsWith('hi') || voices[i].name.toLowerCase().includes('hindi')) {{
                    hindiVoice = voices[i];
                    break;
                }}
            }}
        }}
    }}
    if ('speechSynthesis' in window) {{
        loadHindiVoice();
        window.speechSynthesis.onvoiceschanged = loadHindiVoice;
    }}
    function playSpeech() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            loadHindiVoice();
            var ut = new SpeechSynthesisUtterance("{clean_text}");
            ut.lang = "hi-IN";
            if (hindiVoice) {{
                ut.voice = hindiVoice;
            }}
            ut.rate = 0.88; // Comfortable pace for rural listeners
            ut.pitch = 1.0;
            window.speechSynthesis.speak(ut);
        }}
    }}
    function stopSpeech() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
        }}
    }}
    </script>
    """
    components.html(html_code, height=52)


def transcribe_audio_file(audio_bytes: bytes, is_hi: bool = True) -> str:
    """Transcribes recorded audio stream using Google Speech Recognition in Hindi or English."""
    import speech_recognition as sr
    try:
        # Convert any audio format (webm/ogg/wav) to 16kHz mono WAV via ffmpeg pipe
        cmd = ["ffmpeg", "-y", "-i", "pipe:0", "-ar", "16000", "-ac", "1", "-f", "wav", "pipe:1"]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wav_bytes, err = proc.communicate(input=audio_bytes)

        recognizer = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
            audio_data = recognizer.record(source)
            lang_code = "hi-IN" if is_hi else "en-IN"
            text = recognizer.recognize_google(audio_data, language=lang_code)
            return text.strip()
    except Exception as e:
        return ""


def detect_scheme_from_text(text: str):
    """Detects target scheme from spoken keywords in Hindi or English."""
    if not text:
        return None
    t = text.lower()
    if any(k in t for k in ["किसान", "खेती", "फसल", "सम्मान निधि", "कृषि", "भूमि", "farmer", "kisan", "agriculture", "6000"]):
        return "PM-KISAN"
    if any(k in t for k in ["आयुष्मान", "अस्पताल", "इलाज", "बीमारी", "स्वास्थ्य", "डॉक्टर", "दवा", "ayushman", "hospital", "health", "treatment", "500000", "5 लाख"]):
        return "PM-JAY"
    if any(k in t for k in ["आवास", "मकान", "घर", "पक्का मकान", "कच्चा मकान", "छत", "awaas", "housing", "pucca house", "kutcha house", "120000", "1.2"]):
        return "PMAY-G"
    if any(k in t for k in ["स्वनिधि", "रेहड़ी", "पटरी", "ठेला", "फेरी", "दुकान", "सड़क", "vendor", "street vendor", "hawker", "loan", "कर्ज", "ऋण", "10000", "50000"]):
        return "PM-SVANIDHI"
    if any(k in t for k in ["सुकन्या", "बालिका", "बेटी", "बच्ची", "लड़की", "कन्या", "डाकघर", "sukanya", "girl child", "daughter", "saving", "8.2"]):
        return "SSY"
    return None


def render_live_web_speech_search(is_hi: bool):
    """Client-side Web Speech Recognition with live transcript and instant search trigger."""
    btn_start = "🎙️ लाइव बोलें (Speak)" if is_hi else "🎙️ Click to Speak"
    btn_stop = "⏹️ रोकें (Stop)" if is_hi else "⏹️ Stop"
    lang_code = "hi-IN" if is_hi else "en-IN"
    info_label = "🔴 आवाज़ पहचान (Live Voice):" if is_hi else "🔴 Live Voice Transcript:"
    help_note = "📌 बोले गए शब्द स्वतः खोज बार में प्रविष्ट होंगे।" if is_hi else "📌 Spoken words will automatically populate scheme search."

    html_code = f"""
    <style>
    * {{ box-sizing: border-box; }}
    body {{
        margin: 0;
        padding: 0;
        background: transparent;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        overflow: hidden;
    }}
    .mic-card {{
        background: #FDFCF8;
        border: 1px solid #C9C2B3;
        border-radius: 12px;
        padding: 10px 14px;
        margin: 0;
        width: 100%;
        box-sizing: border-box;
    }}
    </style>
    <div class="mic-card">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:6px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <button id="startMicBtn" onclick="toggleRecognition()" style="
                    background: linear-gradient(135deg, #B93C31, #7F1D1D);
                    color: #ffffff;
                    border: none;
                    padding: 6px 14px;
                    font-size: 0.88rem;
                    font-weight: 700;
                    border-radius: 20px;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    box-shadow: 0 2px 5px rgba(185,60,49,0.22);
                    white-space: nowrap;
                ">
                    <span id="micIcon">🎙️</span> <span id="micLabel">{btn_start}</span>
                </button>
                <span id="micStatus" style="font-size:0.8rem; font-weight:600; color:#4A5568;">
                    ⚪ {"माइक तैयार (Ready)" if is_hi else "Mic Ready"}
                </span>
            </div>
            <span style="font-size:0.78rem; color:#4A5568;">
                🌐 {"भाषा:" if is_hi else "Language:"} <strong>{"हिंदी (hi-IN)" if is_hi else "English (en-IN)"}</strong>
            </span>
        </div>
        <div style="margin-top:8px;">
            <div style="font-size:0.8rem; color:#4A5568; margin-bottom:3px;">{info_label}</div>
            <div id="transcriptBox" style="
                background:#ffffff;
                border:1px solid #94897A;
                border-radius:6px;
                padding:6px 10px;
                font-size:0.9rem;
                font-weight:600;
                color:#1A2942;
                min-height:34px;
                display:flex;
                align-items:center;
                overflow:hidden;
                text-overflow:ellipsis;
                white-space:nowrap;
            ">
                <span style="color:#94897A; font-weight:400; font-style:italic; font-size:0.83rem;">
                    {"माइक दबाकर बोलें, जैसे: 'किसान योजना', 'आयुष्मान'..." if is_hi else "Click mic and speak, e.g., 'farmer scheme', 'ayushman'..."}
                </span>
            </div>
        </div>
        <div style="margin-top:5px; font-size:0.75rem; color:#4A5568;">
            {help_note}
        </div>
    </div>
    <script>
    var recognition = null;
    var isListening = false;
    var startBtn = document.getElementById('startMicBtn');
    var micLabel = document.getElementById('micLabel');
    var micIcon = document.getElementById('micIcon');
    var micStatus = document.getElementById('micStatus');
    var transcriptBox = document.getElementById('transcriptBox');

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
        var SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRec();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = "{lang_code}";

        recognition.onstart = function() {{
            isListening = true;
            micLabel.innerText = "{btn_stop}";
            micIcon.innerText = "⏹️";
            startBtn.style.background = "linear-gradient(135deg, #2F5C43, #234433)";
            micStatus.innerHTML = "<span style='color:#B93C31;'>🔴 {"सुन रहे हैं... बोलिए (Listening...)" if is_hi else "Listening..."}</span>";
        }};

        recognition.onresult = function(event) {{
            var interim = '';
            var final = '';
            for (var i = event.resultIndex; i < event.results.length; ++i) {{
                if (event.results[i].isFinal) {{
                    final += event.results[i][0].transcript;
                }} else {{
                    interim += event.results[i][0].transcript;
                }}
            }}
            var display = final || interim;
            if (display) {{
                transcriptBox.innerHTML = "<span style='color:#1A2942;'>" + display + "</span>";
                try {{
                    navigator.clipboard.writeText(display);
                }} catch(e) {{}}
            }}
        }};

        recognition.onerror = function(event) {{
            isListening = false;
            micLabel.innerText = "{btn_start}";
            micIcon.innerText = "🎙️";
            startBtn.style.background = "linear-gradient(135deg, #B93C31, #7F1D1D)";
            micStatus.innerHTML = "<span style='color:#A97426;'>⚠️ {"त्रुटि: माइक अनुमति जांचें" if is_hi else "Notice: Check mic permissions"}</span>";
        }};

        recognition.onend = function() {{
            isListening = false;
            micLabel.innerText = "{btn_start}";
            micIcon.innerText = "🎙️";
            startBtn.style.background = "linear-gradient(135deg, #B93C31, #7F1D1D)";
            micStatus.innerHTML = "✅ {"बोला गया दर्ज हुआ (Captured! Copied to clipboard)" if is_hi else "Captured! Copied to clipboard"}";
        }};
    }} else {{
        micStatus.innerHTML = "<span style='color:#4A5568;'>ℹ️ Browser speech supported in Chrome / Edge / Android</span>";
    }}

    function toggleRecognition() {{
        if (!recognition) {{
            alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Android browser.");
            return;
        }}
        if (isListening) {{
            recognition.stop();
        }} else {{
            transcriptBox.innerHTML = "<span style='color:#C98E37; font-weight:600;'>🎙️ {"बोलिए... (Listening...)" if is_hi else "Listening..."}</span>";
            recognition.start();
        }}
    }}
    </script>
    """
    components.html(html_code, height=148)


@st.cache_resource
def load_data():
    reg = SchemeRegistry()
    eng = RuleEngine(reg)
    with open(os.path.join(os.path.dirname(__file__), "data", "synthetic_profiles.json"), "r", encoding="utf-8") as f:
        profiles = json.load(f)
    return reg, eng, profiles

registry, rule_engine, synthetic_profiles = load_data()


# Sidebar: Modern Brand Card, Language & Interactive Profiles
with st.sidebar:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1A2942 0%, #274472 100%); padding: 18px 20px; border-radius: 16px; color: #ffffff; margin-bottom: 16px; box-shadow: 0 4px 14px rgba(39,68,114,0.22); display:flex; align-items:center; gap:12px;'>
        <div style='background:#FDFCF8; border-radius:10px; padding:6px; display:flex; align-items:center; justify-content:center;'>{BRAND_LOGO_SVG}</div>
        <div>
            <div style='font-size: 1.28rem; font-weight: 800; display: flex; align-items: center; gap: 2px; letter-spacing: -0.02em; font-family: var(--font-heading);'>
                <span style='color:#B9C9DE;'>Yojana</span><span style='color:#E8D39B;'>Saarthi</span>
            </div>
            <div style='font-size: 0.78rem; opacity: 0.9; margin-top: 2px; font-weight: 500;'>
                Public Services & Civic Tech Navigator
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**🌐 भाषा / Language**")
    lang = st.radio("भाषा / Language:", ["हिंदी", "English"], index=0, horizontal=True, label_visibility="collapsed")
    is_hi = (lang == "हिंदी")

    st.markdown("---")
    st.markdown("⚡ **त्वरित परीक्षण प्रोफाइल (Demo Profiles):**" if is_hi else "⚡ **Interactive Demo Profiles:**")
    st.caption("विभिन्न नागरिकों के विवरण तुरंत लोड करके टेस्ट करें:" if is_hi else "Load sample citizen profiles for instant verification:")

    profile_labels = [
        "-- नया फॉर्म भरें (Manual Form) --" if is_hi else "-- Manual Form Entry --"
    ] + [f"{p['name']} — {p['label']}" for p in synthetic_profiles]

    selected_p_idx = st.selectbox(
        "प्रोफाइल चुनें:" if is_hi else "Select Profile:",
        range(len(profile_labels)),
        format_func=lambda x: profile_labels[x],
        label_visibility="collapsed"
    )

# App Header (Native Streamlit Title - No raw div class leak)
app_title_text = "योजनासारथी" if is_hi else "YojanaSaarthi"
st.title(f"🪔 {app_title_text}")
st.caption("सही योजना, साफ़ जानकारी — 5 प्रमुख सरकारी योजनाओं की त्वरित पात्रता जांच" if is_hi else "Fast, Deterministic Eligibility Checker for 5 Major Government Schemes")


# =========================================================
# 5 SCHEMES HERO DATA & COMPREHENSIVE OVERVIEW (BILINGUAL)
# =========================================================
SCHEMES_HERO_DATA = [
    {
        "id": "PM-KISAN",
        "category_tag": "kisan",
        "keywords": ["kisan", "farmer", "agriculture", "कृषि", "किसान", "खेती", "फसल", "सम्मान निधि", "6000", "dbt", "land", "जमीन"],
        "icon": "🌾",
        "title_hi": "प्रधानमंत्री किसान सम्मान निधि (PM-KISAN)",
        "title_en": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "tagline_hi": "भूमिधारक किसान परिवारों को सुनिश्चित आय सहायता",
        "tagline_en": "Income support for landholder farmer families",
        "benefit_hi": "₹6,000 / वर्ष (प्रत्यक्ष बैंक अंतरण DBT)",
        "benefit_en": "₹6,000 / year (Direct Bank Transfer - DBT)",
        "beneficiary_hi": "कृषि भूमिधारक किसान (Farmer)",
        "beneficiary_en": "Landholding Farmer",
        "dept_hi": "कृषि एवं किसान कल्याण मंत्रालय",
        "dept_en": "Ministry of Agriculture & Farmers Welfare",
        "brief_hi": "पात्र भूमिधारक किसानों को ₹6,000 प्रति वर्ष की सीधी सहायता (₹2,000 की 3 समान किश्तों में बैंक खाते में DBT)।",
        "brief_en": "Direct financial support of ₹6,000/year (3 installments of ₹2,000 via DBT) for eligible landholding farmers.",
        "criteria_hi": "• नाम पर कृषि योग्य भूमि दर्ज हो\n• परिवार में कोई आयकर दाता या सरकारी कर्मचारी न हो",
        "criteria_en": "• Own registered cultivable agricultural land\n• No income taxpayer or govt employee in family",
        "portal": "https://pmkisan.gov.in"
    },
    {
        "id": "PM-JAY",
        "category_tag": "health",
        "keywords": ["health", "hospital", "cashless", "ayushman", "स्वास्थ्य", "अस्पताल", "इलाज", "बीमारी", "डॉक्टर", "500000", "5 लाख", "दवा", "उपचार"],
        "icon": "🏥",
        "title_hi": "आयुष्मान भारत - प्रधानमंत्री जन आरोग्य योजना (PM-JAY)",
        "title_en": "Ayushman Bharat - PM Jan Arogya Yojana (PM-JAY)",
        "tagline_hi": "गरीब परिवारों को ₹5 लाख तक का मुफ्त व कैशलेस इलाज",
        "tagline_en": "Free & cashless hospital treatment up to ₹5 Lakh for eligible families",
        "benefit_hi": "₹5,00,000 / वर्ष प्रति परिवार मुफ्त इलाज",
        "benefit_en": "₹5,00,000 / year cashless hospital treatment per family",
        "beneficiary_hi": "बीपीएल (BPL) व सामाजिक-आर्थिक रूप से वंचित परिवार",
        "beneficiary_en": "BPL & socio-economically deprived families",
        "dept_hi": "स्वास्थ्य एवं परिवार कल्याण मंत्रालय / NHA",
        "dept_en": "Ministry of Health & Family Welfare / NHA",
        "brief_hi": "पात्र गरीब परिवारों को प्रति वर्ष ₹5 लाख तक का पूर्णतः मुफ्त एवं कैशलेस अस्पताल उपचार।",
        "brief_en": "Free cashless hospital treatment up to ₹5 Lakh/year per family across empaneled hospitals.",
        "criteria_hi": "• SECC 2011 या पात्र बीपीएल राशन कार्ड सूची में नाम\n• परिवार के आकार या आयु की कोई सीमा नहीं",
        "criteria_en": "• Identified under SECC 2011 or valid BPL card\n• No restriction on family size or age",
        "portal": "https://beneficiary.nha.gov.in"
    },
    {
        "id": "PMAY-G",
        "category_tag": "house",
        "keywords": ["housing", "house", "shelter", "pucca", "kutcha", "आवास", "मकान", "घर", "पक्का मकान", "कच्चा मकान", "छत", "120000", "1.2", "ग्रामीण"],
        "icon": "🏠",
        "title_hi": "प्रधानमंत्री आवास योजना - ग्रामीण (PMAY-G)",
        "title_en": "Pradhan Mantri Awaas Yojana - Gramin (PMAY-G)",
        "tagline_hi": "ग्रामीण बेघर परिवारों को पक्का मकान हेतु अनुदान",
        "tagline_en": "Direct construction grant for rural houseless families to build a pucca house",
        "benefit_hi": "₹1,20,000 पक्का मकान अनुदान + 90 दिन मनरेगा मजदूरी",
        "benefit_en": "₹1,20,000 pucca house grant + 90 days MGNREGA wages",
        "beneficiary_hi": "ग्रामीण बेघर या कच्चा मकान निवासी",
        "beneficiary_en": "Rural houseless or kutcha house resident",
        "dept_hi": "ग्रामीण विकास मंत्रालय",
        "dept_en": "Ministry of Rural Development",
        "brief_hi": "ग्रामीण बेघर या कच्चे मकान वाले परिवारों को पक्का मकान निर्माण हेतु ₹1.20 लाख की सीधी सहायता।",
        "brief_en": "Financial grant of ₹1.20 Lakh to construct a durable pucca house for rural houseless families.",
        "criteria_hi": "• ग्रामीण निवासी हों और पहले से पक्का मकान न हो\n• परिवार में 4-पहिया वाहन या सरकारी कर्मचारी न हो",
        "criteria_en": "• Rural resident with no existing pucca house\n• No 4-wheeler or government employee in family",
        "portal": "https://www.myscheme.gov.in/schemes/pmayg"
    },
    {
        "id": "PM-SVANIDHI",
        "category_tag": "vendor",
        "keywords": ["vendor", "street vendor", "hawker", "loan", "working capital", "credit", "रेहड़ी", "पटरी", "ठेला", "फेरी", "दुकान", "स्वनिधि", "कर्ज", "ऋण", "10000", "50000"],
        "icon": "🛒",
        "title_hi": "पीएम स्वनिधि योजना (PM-SVANIDHI)",
        "title_en": "PM Street Vendor's AtmaNirbhar Nidhi (PM-SVANIDHI)",
        "tagline_hi": "रेहड़ी-पटरी विक्रेताओं को बिना गारंटी कार्यशील पूंजी ऋण",
        "tagline_en": "Collateral-free working capital loan for street vendors",
        "benefit_hi": "₹10k - ₹50k सस्ता ऋण + 7% ब्याज सब्सिडी + ₹1,200 कैशबैक",
        "benefit_en": "₹10k - ₹50k credit + 7% interest subsidy + ₹1,200 cashback",
        "beneficiary_hi": "शहरी रेहड़ी-पटरी विक्रेता (Street Vendors / फेरीवाले)",
        "beneficiary_en": "Urban Street Vendors / Hawkers",
        "dept_hi": "आवास एवं शहरी कार्य मंत्रालय",
        "dept_en": "Ministry of Housing and Urban Affairs",
        "brief_hi": "शहरी रेहड़ी-पटरी विक्रेताओं को ₹10,000 से ₹50,000 तक बिना गारंटी सस्ता कार्यशील पूंजी ऋण व 7% ब्याज छूट।",
        "brief_en": "Collateral-free working capital micro-loan of ₹10,000 to ₹50,000 with 7% interest rebate for street vendors.",
        "criteria_hi": "• शहरी क्षेत्र में वेंडिंग प्रमाण पत्र / पहचान पत्र उपलब्ध हो\n• किसी बैंक से डिफ़ॉल्ट न किया हो",
        "criteria_en": "• Active urban street vendor with vending certificate / ID\n• Clear repayment track record",
        "portal": "https://pmsvanidhi.mohua.gov.in"
    },
    {
        "id": "SSY",
        "category_tag": "girl",
        "keywords": ["girl", "girl child", "daughter", "child", "sukanya", "savings", "post office", "सुकन्या", "बालिका", "बेटी", "बच्ची", "लड़की", "कन्या", "डाकघर", "8.2", "8.2%"],
        "icon": "👧",
        "title_hi": "सुकन्या समृद्धि योजना (Sukanya Samriddhi Yojana)",
        "title_en": "Sukanya Samriddhi Yojana (SSY - Girl Child Savings)",
        "tagline_hi": "10 वर्ष तक की बालिकाओं हेतु 8.2% सुरक्षित ब्याज व कर छूट",
        "tagline_en": "8.2% compound interest & tax-free savings for girl children ≤10 years",
        "benefit_hi": "8.2% चक्रवृद्धि ब्याज + धारा 80C कर छूट (EEE)",
        "benefit_en": "8.2% compound interest + Section 80C tax exemption (EEE)",
        "beneficiary_hi": "10 वर्ष तक की बालिका के माता-पिता / अभिभावक",
        "beneficiary_en": "Parent / Guardian of a Girl Child (≤10 Yrs)",
        "dept_hi": "वित्त मंत्रालय / डाक विभाग (India Post)",
        "dept_en": "Ministry of Finance / Department of Posts",
        "brief_hi": "10 वर्ष तक की बालिकाओं के नाम पर 8.2% उच्चतम सुरक्षित ब्याज दर व पूर्णतः कर-मुक्त बचत खाता।",
        "brief_en": "High 8.2% compound annual interest tax-free savings account for girl children aged 10 years or below.",
        "criteria_hi": "• 10 वर्ष या उससे कम आयु की बालिका के नाम पर खाता\n• परिवार में अधिकतम 2 बालिकाओं हेतु मान्य",
        "criteria_en": "• Opened for girl child aged 10 years or younger\n• Maximum 2 accounts per family",
        "portal": "https://www.indiapost.gov.in"
    }
]

DOC_NAME_MAP_HI = {
    "DOC-AADH": "आधार कार्ड (Aadhaar Card)",
    "DOC-LAND": "भूमि स्वामित्व अभिलेख / खतौनी (Land Records)",
    "DOC-BANK": "बैंक खाता पासबुक (Bank Passbook)",
    "DOC-RATN": "राशन कार्ड / बीपीएल प्रमाण पत्र (Ration / BPL Card)",
    "DOC-INCM": "आय प्रमाण पत्र (Income Certificate)",
    "DOC-MNREGA": "मनरेगा जॉब कार्ड (MGNREGA Job Card)",
    "DOC-VEND": "वेंडिंग पहचान पत्र / टीवीसी सिफ़ारिश (Street Vendor CoV/LoR)",
    "DOC-BRTH": "बालिका जन्म प्रमाण पत्र (Birth Certificate)",
    "DOC-PHOT": "पासपोर्ट साइज फोटो (Passport Size Photos)"
}

HINDI_STEPS_MAP = {
    "PM-KISAN": [
        "आधार कार्ड और ज़मीन की खतौनी/भूलेख दस्तावेज़ लेकर नजदीकी जन सेवा केंद्र (CSC) या pmkisan.gov.in पर जाएं।",
        "ओटीपी (OTP) या बायोमेट्रिक फिंगरप्रिंट द्वारा e-KYC प्रमाणीकरण पूरा करें।",
        "आवेदन जमा करें और फार्मर कॉर्नर (Farmer Corner) से अपने आवेदन की स्थिति ट्रैक करें।"
    ],
    "PM-JAY": [
        "अपने राशन कार्ड और आधार कार्ड के साथ नजदीकी सरकारी अस्पताल या सीएससी केंद्र के 'आयुष्मान मित्र' डेस्क पर जाएं।",
        "SECC / राशन कार्ड डेटाबेस में परिवार का नाम सत्यापित करवाकर e-KYC बायोमेट्रिक सत्यापन करें।",
        "आयुष्मान गोल्डन कार्ड (Ayushman Card) प्राप्त करें और सूचीबद्ध किसी भी अस्पताल में ₹5 लाख तक का कैशलेस इलाज कराएं।"
    ],
    "PMAY-G": [
        "ग्राम पंचायत में ग्राम रोजगार सहायक या पंचायत सचिव से मिलकर आवास+ (Awaas+) सर्वेक्षण सूची में नाम सत्यापित कराएं।",
        "कच्चे मकान (Kutcha House) की जियो-टैग्ड फोटो और बैंक पासबुक ग्राम पंचायत में जमा कराएं।",
        "स्वीकृति के बाद ₹1.20 लाख की सहायता राशि सीधे 3 किश्तों में आपके बैंक खाते में अंतरित की जाएगी।"
    ],
    "PM-SVANIDHI": [
        "नगर निगम / नगर पालिका कार्यालय या नजदीकी सीएससी से वेंडिंग पहचान पत्र (Letter of Recommendation / CoV) प्राप्त करें।",
        "pmsvanidhi.mohua.gov.in पोर्टल अथवा बैंक शाखा में आधार से जुड़े मोबाइल नंबर से ₹10,000 के शुरुआती ऋण हेतु आवेदन करें।",
        "डिजिटल लेनदेन (QR Code) का उपयोग करें और समय पर मासिक किश्त चुकाकर 7% ब्याज सब्सिडी व ₹20,000 का अगला बड़ा ऋण प्राप्त करें।"
    ],
    "SSY": [
        "नजदीकी डाकघर (Post Office) या किसी राष्ट्रीयकृत बैंक की शाखा में जाएं।",
        "बालिका का जन्म प्रमाण पत्र, माता-पिता का आधार कार्ड व पासपोर्ट साइज फोटो संलग्न कर खाता खोलने का फॉर्म भरें।",
        "न्यूनतम ₹250 से खाता खोलें और प्रति वर्ष 8.2% की उच्चतम कर-मुक्त ब्याज दर का लाभ प्राप्त करें।"
    ]
}

# Navigation State Initialization
if "nav_view" not in st.session_state:
    st.session_state.nav_view = "hero"
if "selected_scheme_id" not in st.session_state:
    st.session_state.selected_scheme_id = "PM-KISAN"
if "hero_search_query" not in st.session_state:
    st.session_state.hero_search_query = ""

# Navigation Helper
def set_nav(target: str, scheme_id: str = None):
    st.session_state.nav_view = target
    st.session_state.main_nav_segmented = target
    if scheme_id:
        st.session_state.selected_scheme_id = scheme_id

# Navigation State Initialization
if "nav_view" not in st.session_state:
    st.session_state.nav_view = "hero"
if "main_nav_segmented" not in st.session_state:
    st.session_state.main_nav_segmented = st.session_state.nav_view
if "selected_scheme_id" not in st.session_state:
    st.session_state.selected_scheme_id = "PM-KISAN"

# Modern Segmented Navigation Bar
nav_options = ["hero", "search", "compare"]
nav_labels = {
    "hero": "🏠 मुख्य पृष्ठ (Home)" if is_hi else "🏠 Home (Overview)",
    "search": "🧭 पात्रता सर्च इंजन" if is_hi else "🧭 Eligibility Engine",
    "compare": "⚖️ योजनाओं की तुलना" if is_hi else "⚖️ Scheme Comparison"
}

def on_segmented_change():
    chosen = st.session_state.get("main_nav_segmented")
    if chosen:
        st.session_state.nav_view = chosen

selected_nav = st.segmented_control(
    "Navigation",
    options=nav_options,
    format_func=lambda opt: nav_labels.get(opt, opt),
    label_visibility="collapsed",
    key="main_nav_segmented",
    on_change=on_segmented_change,
    width="stretch"
)
if selected_nav and selected_nav != st.session_state.nav_view:
    st.session_state.nav_view = selected_nav

st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)


# =========================================================
# VIEW 1: HERO PAGE & SCHEMES OVERVIEW (STARTING PAGE)
# =========================================================
if st.session_state.nav_view == "hero":
    col_cta1, col_cta2 = st.columns(2)
    with col_cta1:
        st.button(
            "🚀 पात्रता सर्च इंजन खोलें (Check Eligibility)" if is_hi else "🚀 Open Eligibility Search Engine",
            type="primary",
            use_container_width=True,
            key="hero_open_engine_btn",
            on_click=set_nav,
            args=("search",)
        )
    with col_cta2:
        st.button(
            "⚖️ योजनाओं की तुलना देखें (Compare Schemes)" if is_hi else "⚖️ Compare Schemes Side-by-Side",
            type="secondary",
            use_container_width=True,
            key="hero_open_comp_btn",
            on_click=set_nav,
            args=("compare",)
        )

    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

    # Ensure filter state initialization
    if "hero_selected_category" not in st.session_state:
        st.session_state.hero_selected_category = "all"
    if "hero_search_text_input" not in st.session_state:
        st.session_state.hero_search_text_input = ""

    def apply_filter_category(cat_name: str, query_text: str = ""):
        st.session_state.hero_selected_category = cat_name
        st.session_state.hero_search_text_input = query_text

    def apply_clear_filter():
        st.session_state.hero_selected_category = "all"
        st.session_state.hero_search_text_input = ""

    with st.container(border=True):
        st.markdown("#### 🔍 योजना खोजें एवं फ़िल्टर (Search & Filter Tags):" if is_hi else "#### 🔍 Search Schemes & Quick Filter Tags:")
        col_s_input, col_s_clr = st.columns([5, 1])
        with col_s_input:
            hero_search = st.text_input(
                "योजना या लाभ खोजें:" if is_hi else "Search Scheme or Benefit:",
                placeholder="जैसे: किसान (Farmer), स्वास्थ्य (Health), ₹6000, आवास (Housing), वेंडर (Vendor), सुकन्या, 8.2%..." if is_hi else "e.g. Farmer, Health, ₹6000, Housing, Street Vendor, Sukanya, 8.2%...",
                label_visibility="collapsed",
                key="hero_search_text_input"
            )

        with col_s_clr:
            st.button("🔄 साफ़ करें" if is_hi else "🔄 Clear", use_container_width=True, key="btn_clear_hero_search", on_click=apply_clear_filter)

        tag_cols = st.columns(6)
        with tag_cols[0]:
            t_type = "primary" if st.session_state.hero_selected_category == "kisan" else "secondary"
            st.button("🌾 किसान (Farmer)", use_container_width=True, key="tag_kisan", type=t_type,
                      on_click=apply_filter_category, args=("kisan", "किसान"))
        with tag_cols[1]:
            t_type = "primary" if st.session_state.hero_selected_category == "health" else "secondary"
            st.button("🏥 स्वास्थ्य (Health)", use_container_width=True, key="tag_health", type=t_type,
                      on_click=apply_filter_category, args=("health", "स्वास्थ्य"))
        with tag_cols[2]:
            t_type = "primary" if st.session_state.hero_selected_category == "house" else "secondary"
            st.button("🏠 आवास (Housing)", use_container_width=True, key="tag_house", type=t_type,
                      on_click=apply_filter_category, args=("house", "आवास"))
        with tag_cols[3]:
            t_type = "primary" if st.session_state.hero_selected_category == "vendor" else "secondary"
            st.button("🛒 वेंडर (Vendor)", use_container_width=True, key="tag_vendor", type=t_type,
                      on_click=apply_filter_category, args=("vendor", "वेंडर"))
        with tag_cols[4]:
            t_type = "primary" if st.session_state.hero_selected_category == "girl" else "secondary"
            st.button("👧 सुकन्या (Girl)", use_container_width=True, key="tag_girl", type=t_type,
                      on_click=apply_filter_category, args=("girl", "सुकन्या"))
        with tag_cols[5]:
            t_type = "primary" if st.session_state.hero_selected_category == "all" else "secondary"
            st.button("🔄 सभी 5 (Show All)", use_container_width=True, key="tag_all", type=t_type,
                      on_click=apply_clear_filter)

    filtered_schemes = []
    current_search = st.session_state.get("hero_search_text_input", "").strip().lower()
    selected_cat = st.session_state.get("hero_selected_category", "all")

    # Split search query into clean tokens
    tokens = [t for t in re.split(r"[\s,\(\)\/\-\+]+", current_search) if t]

    for s in SCHEMES_HERO_DATA:
        cat_match = (selected_cat == "all") or (s.get("category_tag") == selected_cat)
        if not tokens:
            text_match = True
        else:
            corpus = (
                s["id"] + " " + s["title_hi"] + " " + s["title_en"] + " " +
                s["tagline_hi"] + " " + s["tagline_en"] + " " +
                s["benefit_hi"] + " " + s["benefit_en"] + " " +
                s["beneficiary_hi"] + " " + s["beneficiary_en"] + " " +
                s["dept_hi"] + " " + s["dept_en"] + " " +
                s["brief_hi"] + " " + s["brief_en"] + " " +
                s["criteria_hi"] + " " + s["criteria_en"] + " " +
                " ".join(s.get("keywords", []))
            ).lower()
            text_match = any(tok in corpus for tok in tokens)

        if cat_match and text_match:
            filtered_schemes.append(s)

    st.caption(
        f"प्रदर्शित योजनाएं: **{len(filtered_schemes)}** / 5" if is_hi else
        f"Displaying **{len(filtered_schemes)}** of 5 Government Schemes"
    )

    if not filtered_schemes:
        st.warning("कोई मेल खाती योजना नहीं मिली। कृपया कोई दूसरा शब्द खोजें।" if is_hi else "No matching scheme found. Please try another search keyword.")
    else:
        def render_scheme_card_content(s):
            title = s["title_hi"] if is_hi else s["title_en"]
            tagline = s["tagline_hi"] if is_hi else s["tagline_en"]
            benefit = s["benefit_hi"] if is_hi else s["benefit_en"]
            beneficiary = s["beneficiary_hi"] if is_hi else s["beneficiary_en"]
            dept = s["dept_hi"] if is_hi else s["dept_en"]
            brief = s["brief_hi"] if is_hi else s["brief_en"]
            criteria = s["criteria_hi"] if is_hi else s["criteria_en"]

            st.markdown(f"""
            <div style='display:flex; align-items:center; gap:12px; margin-bottom:12px;'>
                <div style='background:#F0F4F8; border:1px solid #D6E0EC; border-radius:14px; font-size:1.75rem; min-width:48px; height:48px; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 6px rgba(26,41,66,0.04);'>
                    {s['icon']}
                </div>
                <div style='flex:1;'>
                    <div style='font-family:var(--font-heading); font-size:1.22rem; font-weight:800; color:#1A2942; line-height:1.3;'>{title}</div>
                    <div style='font-size:0.8rem; color:#64748B; font-weight:600; margin-top:3px; display:flex; align-items:center; gap:4px;'>🏛️ {dept}</div>
                </div>
            </div>
            <div style='margin:12px 0 10px 0; display:flex; flex-wrap:wrap; gap:6px;'>
                <span class='hero-benefit-badge'>🎁 {benefit}</span>
                <span class='hero-target-badge'>👤 {beneficiary}</span>
            </div>
            <div style='font-size:0.9rem; color:#1A2942; line-height:1.6; margin-bottom:14px;'>
                {brief}
            </div>
            <div style='background-color:#FAF8F3; border:1px solid #EFECE3; border-radius:12px; padding:12px 14px; font-size:0.84rem; color:#4A5568; margin-bottom:16px; line-height:1.55;'>
                <strong style='color:#1A2942; font-weight:700;'>{"📌 मुख्य पात्रता शर्तें:" if is_hi else "📌 Key Eligibility Conditions:"}</strong><br>
                <div style='margin-top:4px;'>{criteria.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)

            btn_c1, btn_c2 = st.columns(2)
            with btn_c1:
                st.button(
                    f"👉 {s['id']} पात्रता जांचें" if is_hi else f"👉 Check {s['id']} Eligibility",
                    key=f"btn_check_hero_{s['id']}",
                    type="primary",
                    use_container_width=True,
                    on_click=set_nav,
                    args=("search", s["id"])
                )
            with btn_c2:
                st.link_button(
                    "🌐 " + ("आधिकारिक पोर्टल" if is_hi else "Official Portal"),
                    url=s["portal"],
                    use_container_width=True
                )

        idx = 0
        while idx < len(filtered_schemes):
            if idx + 1 < len(filtered_schemes):
                c_left, c_right = st.columns(2)
                with c_left:
                    with st.container(border=True):
                        render_scheme_card_content(filtered_schemes[idx])
                with c_right:
                    with st.container(border=True):
                        render_scheme_card_content(filtered_schemes[idx + 1])
                idx += 2
            else:
                with st.container(border=True):
                    render_scheme_card_content(filtered_schemes[idx])
                idx += 1
            st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)


# =========================================================
# VIEW 2: ELIGIBILITY SEARCH ENGINE (SELECTIONS ONLY)
# =========================================================
elif st.session_state.nav_view == "search":
    # Default Profile Data (Synced with Selected Preset)
    defaults = {
        "age": 35, "gender": "Female", "state": "Uttar Pradesh", "annual_income": 120000,
        "residence_area": "Rural", "occupation": "Farmer", "social_category": "OBC",
        "landholding_hectares": 1.0, "is_bpl": True, "owns_pucca_house": False,
        "pays_income_tax": False, "is_govt_employee": False,
        "has_girl_child_under_10": False, "is_student": False
    }
    if selected_p_idx > 0:
        defaults = synthetic_profiles[selected_p_idx - 1]["attributes"]
        st.info(f"💡 {'सक्रिय प्रोफाइल:' if is_hi else 'Active Profile:'} **{synthetic_profiles[selected_p_idx - 1]['name']}** ({synthetic_profiles[selected_p_idx - 1]['label']})")
    schemes_data = registry.get_all_schemes()
    scheme_ids = [s["scheme_id"] for s in schemes_data]
    scheme_map = {s["scheme_id"]: s for s in schemes_data}

    scheme_icons = {
        "PM-KISAN": "🌾",
        "PM-JAY": "🏥",
        "PMAY-G": "🏠",
        "PM-SVANIDHI": "🛒",
        "SSY": "👧"
    }

    scheme_display_names = {
        "PM-KISAN": "🌾 PM-KISAN (पीएम किसान सम्मान निधि) — ₹6,000 / वर्ष" if is_hi else "🌾 PM-KISAN (Kisan Samman Nidhi) — ₹6,000 / year",
        "PM-JAY": "🏥 PM-JAY (आयुष्मान भारत) — ₹5 लाख मुफ्त इलाज" if is_hi else "🏥 PM-JAY (Ayushman Bharat) — ₹5 Lakh Cashless Cover",
        "PMAY-G": "🏠 PMAY-G (पीएम आवास ग्रामीण) — ₹1.20 लाख पक्का घर" if is_hi else "🏠 PMAY-G (Gramin Awaas) — ₹1.20 Lakh Pucca House",
        "PM-SVANIDHI": "🛒 PM-SVANIDHI (पीएम स्वनिधि) — ₹10k - ₹50k ऋण" if is_hi else "🛒 PM-SVANIDHI (Street Vendor Loan) — ₹10k - ₹50k Credit",
        "SSY": "👧 SSY (सुकन्या समृद्धि) — 8.2% ब्याज, बालिकाओं हेतु" if is_hi else "👧 SSY (Sukanya Samriddhi) — 8.2% Interest for Girls"
    }

    with st.container(border=True):
        st.markdown("### 1. जिस योजना की जांच करनी है, उसे चुनें (Select Scheme)" if is_hi else "### 1. Select Scheme for Eligibility Assessment")
        st.caption("नीचे दी गई 5 योजनाओं में से किसी एक पर क्लिक करें:" if is_hi else "Choose exactly one scheme below to evaluate your specific eligibility:")

        st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)

        curr_s_idx = scheme_ids.index(st.session_state.selected_scheme_id) if st.session_state.selected_scheme_id in scheme_ids else 0

        selected_scheme_id = st.radio(
            "योजना चुनें:" if is_hi else "Select Scheme:",
            options=scheme_ids,
            format_func=lambda sid: scheme_display_names.get(sid, sid),
            index=curr_s_idx,
            horizontal=False,
            label_visibility="collapsed"
        )
        st.session_state.selected_scheme_id = selected_scheme_id

        selected_scheme = scheme_map[selected_scheme_id]
        hero_info = {s["id"]: s for s in SCHEMES_HERO_DATA}.get(selected_scheme_id, {})
        disp_title = hero_info.get("title_hi", selected_scheme.get("hindi_name", selected_scheme["name"])) if is_hi else hero_info.get("title_en", selected_scheme["name"])
        disp_dept = hero_info.get("dept_hi", selected_scheme.get("department")) if is_hi else hero_info.get("dept_en", selected_scheme.get("department"))
        disp_benefit = hero_info.get("benefit_hi", selected_scheme.get("benefit_value")) if is_hi else hero_info.get("benefit_en", selected_scheme.get("benefit_value"))
        disp_brief = hero_info.get("brief_hi", selected_scheme.get("summary")) if is_hi else hero_info.get("brief_en", selected_scheme.get("summary"))

        st.markdown(f"""
        <div class='scheme-card-header'>
            <div style='font-size:1.25rem; font-weight:800;'>{scheme_icons.get(selected_scheme_id, '🏛️')} {disp_title} ({selected_scheme['scheme_id']})</div>
            <div style='font-size:0.95rem; margin-top:6px; opacity:0.95;'>🎁 <strong>{"लाभ (Benefit):" if is_hi else "Benefit:"}</strong> {disp_benefit} &nbsp;|&nbsp; 🏛️ <strong>{"विभाग:" if is_hi else "Department:"}</strong> {disp_dept}</div>
            <div style='font-size:0.88rem; margin-top:8px; opacity:0.9; line-height:1.5;'>{disp_brief}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 2. नागरिक विवरण (Citizen Profile - Selections Only)" if is_hi else "### 2. Enter Citizen Profile Attributes")

    indian_states = [
        "All States", "Uttar Pradesh", "Bihar", "Madhya Pradesh", "Rajasthan",
        "Maharashtra", "West Bengal", "Gujarat", "Karnataka", "Tamil Nadu",
        "Delhi", "Other State/UT"
    ]

    with st.form("visual_profile_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**🎂 आयु एवं लिंग (Age & Gender)**" if is_hi else "**🎂 Age & Gender**")
            age_in = st.slider(
                "आयु (Years)" if is_hi else "Age (Years)",
                min_value=18,
                max_value=85,
                value=int(defaults.get("age", 35)) if (defaults.get("age") and 18 <= defaults.get("age") <= 85) else 35,
                help="नागरिक की वर्तमान आयु (वर्षों में)"
            )

            genders = ["Female", "Male", "Transgender"]
            gender_labels = {"Female": "👩 महिला (Female)", "Male": "👨 पुरुष (Male)", "Transgender": "⚧ अन्य (Other)"}
            g_idx = genders.index(defaults.get("gender", "Female")) if defaults.get("gender") in genders else 0
            gender_in = st.radio(
                "लिंग (Gender)" if is_hi else "Gender",
                genders,
                format_func=lambda g: gender_labels.get(g, g),
                index=g_idx,
                horizontal=True
            )

        with c2:
            st.markdown("**📍 निवास स्थान (Location)**" if is_hi else "**📍 Location**")
            s_idx = indian_states.index(defaults.get("state", "Uttar Pradesh")) if defaults.get("state") in indian_states else 1
            state_in = st.selectbox("राज्य (State / UT)" if is_hi else "State / UT", indian_states, index=s_idx)

            areas = ["Rural", "Urban"]
            area_labels = {"Rural": "🌾 ग्रामीण (Rural)", "Urban": "🏙️ शहरी (Urban)"}
            a_idx = areas.index(defaults.get("residence_area", "Rural")) if defaults.get("residence_area") in areas else 0
            area_in = st.radio(
                "निवास क्षेत्र (Area)" if is_hi else "Area",
                areas,
                format_func=lambda a: area_labels.get(a, a),
                index=a_idx,
                horizontal=True
            )

        with c3:
            st.markdown("**💼 आजीविका एवं श्रेणी (Occupation)**" if is_hi else "**💼 Livelihood & Category**")
            occs = [
                "Farmer", "Street Vendor", "Artisan", "Student",
                "Senior Citizen", "Small Business", "Agricultural Laborer", "Other"
            ]
            occ_labels = {
                "Farmer": "🌾 किसान (Farmer)",
                "Street Vendor": "🛒 रेहड़ी-पटरी / वेंडर (Street Vendor)",
                "Artisan": "🧵 कारीगर / दस्तकार (Artisan)",
                "Agricultural Laborer": "🚜 कृषि मजदूर (Agri Laborer)",
                "Student": "🎓 विद्यार्थी (Student)",
                "Senior Citizen": "👴 वृद्धजन (Senior Citizen)",
                "Small Business": "🏪 छोटा व्यवसायी (Small Business)",
                "Other": "💼 अन्य (Other)"
            }
            o_idx = occs.index(defaults.get("occupation", "Farmer")) if defaults.get("occupation") in occs else 0
            occ_in = st.selectbox(
                "मुख्य व्यवसाय (Occupation)" if is_hi else "Occupation",
                occs,
                format_func=lambda o: occ_labels.get(o, o),
                index=o_idx
            )

            cats = ["General", "OBC", "SC", "ST", "EWS"]
            c_idx = cats.index(defaults.get("social_category", "OBC")) if defaults.get("social_category") in cats else 1
            cat_in = st.radio(
                "सामाजिक श्रेणी (Category)" if is_hi else "Social Category",
                cats,
                index=c_idx,
                horizontal=True
            )

        st.markdown("---")

        fc1, fc2 = st.columns(2)
        with fc1:
            st.markdown("**💰 पारिवारिक कमाई / आय (Income)**" if is_hi else "**💰 Household Income**")
            col_inc_freq, col_inc_val = st.columns([1.2, 1.8])
            with col_inc_freq:
                inc_freq = st.radio(
                    "आय अवधि" if is_hi else "Income Period",
                    ["वार्षिक (Yearly)", "मासिक (Monthly)"],
                    index=0,
                    horizontal=False
                )
            with col_inc_val:
                curr_income = int(defaults.get("annual_income", 80000))
                if "Monthly" in inc_freq or "मासिक" in inc_freq:
                    curr_income = int(curr_income / 12)
                    inc_step = 2000
                    inc_max = 200000
                    inc_label = "मासिक आय (₹ / Month)" if is_hi else "Monthly Income (₹)"
                else:
                    inc_step = 10000
                    inc_max = 3000000
                    inc_label = "वार्षिक आय (₹ / Year)" if is_hi else "Annual Income (₹)"

                entered_inc = st.number_input(
                    inc_label,
                    min_value=0,
                    max_value=inc_max,
                    value=curr_income,
                    step=inc_step
                )

            computed_annual_income = (entered_inc * 12) if ("Monthly" in inc_freq or "मासिक" in inc_freq) else entered_inc

        with fc2:
            st.markdown("**📐 कृषि भूमि का आकार (Cultivable Land)**" if is_hi else "**📐 Agricultural Landholding**")
            col_unit, col_val = st.columns([1.2, 1.8])
            with col_unit:
                land_unit = st.radio(
                    "माप इकाई" if is_hi else "Unit",
                    ["एकड़ (Acres)", "बीघा (Bigha)", "हेक्टेयर (Hectare)"],
                    index=0,
                    horizontal=False
                )
            with col_val:
                default_ha = float(defaults.get("landholding_hectares", 1.0)) if defaults.get("landholding_hectares") is not None else 1.0
                if "एकड़" in land_unit or "Acres" in land_unit:
                    initial_val = round(default_ha / 0.4047, 1)
                elif "बीघा" in land_unit or "Bigha" in land_unit:
                    initial_val = round(default_ha / 0.2529, 1)
                else:
                    initial_val = round(default_ha, 2)

                raw_land_val = st.number_input(
                    "भूमि का माप (Land Size)" if is_hi else "Land Size",
                    min_value=0.0,
                    max_value=100.0,
                    value=initial_val,
                    step=0.5
                )

            if "एकड़" in land_unit or "Acres" in land_unit:
                computed_ha = round(raw_land_val * 0.4047, 3)
            elif "बीघा" in land_unit or "Bigha" in land_unit:
                computed_ha = round(raw_land_val * 0.2529, 3)
            else:
                computed_ha = round(raw_land_val, 3)

        st.markdown("---")

        st.markdown("**🏡 पारिवारिक स्थिति एवं शर्तें (Living Conditions & Rules):**" if is_hi else "**🏡 Living Conditions & Statutory Exclusions:**")
        chk1, chk2 = st.columns(2)
        with chk1:
            pucca_in = st.checkbox(
                "🏠 पक्का सीमेंट का मकान है (Owns Pucca House)" if is_hi else "🏠 Owns Pucca Concrete House",
                value=bool(defaults.get("owns_pucca_house", False)),
                help="कच्चा, झोपड़ी या खपरैल मकान होने पर इसे अनचेक रखें"
            )
            bpl_in = st.checkbox(
                "🟡 बीपीएल / अंत्योदय राशन कार्ड है (BPL / Antyodaya Card)" if is_hi else "🟡 BPL / Antyodaya Ration Card Holder",
                value=bool(defaults.get("is_bpl", True)),
                help="राष्ट्रीय खाद्य सुरक्षा या अंत्योदय राशन कार्ड"
            )
            tax_in = st.checkbox(
                "📄 परिवार में कोई आयकर (Income Tax) भरता है" if is_hi else "📄 Pays Income Tax / Filed ITR",
                value=bool(defaults.get("pays_income_tax", False)),
                help="आयकर दाता होने पर टिक करें"
            )
        with chk2:
            govt_in = st.checkbox(
                "🏛️ परिवार में कोई सरकारी नौकरी में है (Govt Employee)" if is_hi else "🏛️ Family Member in Government Job",
                value=bool(defaults.get("is_govt_employee", False)),
                help="सेवारत या सेवानिवृत्त सरकारी कर्मचारी"
            )
            girl_in = st.checkbox(
                "👧 10 वर्ष तक की बालिका के अभिभावक हैं (Girl child ≤ 10)" if is_hi else "👧 Parent of Girl Child ≤ 10 Yrs",
                value=bool(defaults.get("has_girl_child_under_10", False)),
                help="सुकन्या समृद्धि योजना हेतु आवश्यक"
            )

        st.markdown("")
        check_btn = st.form_submit_button(
            f"🔍 {selected_scheme_id} के लिए पात्रता जांचें (Check Eligibility)" if is_hi else f"🔍 Check Eligibility for {selected_scheme_id}",
            width="stretch",
            type="primary"
        )

    profile = {
        "age": age_in, "gender": gender_in, "state": state_in, "annual_income": computed_annual_income,
        "residence_area": area_in, "occupation": occ_in, "social_category": cat_in,
        "landholding_hectares": computed_ha, "is_bpl": bpl_in, "owns_pucca_house": pucca_in,
        "pays_income_tax": tax_in, "is_govt_employee": govt_in,
        "has_girl_child_under_10": girl_in, "is_student": (occ_in == "Student")
    }

    item = rule_engine.evaluate_single_scheme(selected_scheme, profile)
    status = item["status"]

    st.markdown("---")
    st.markdown(
        f"### 3. पात्रता निर्णय (Eligibility Result): {selected_scheme.get('hindi_name', selected_scheme['name'])}"
        if is_hi else
        f"### 3. Eligibility Decision: {selected_scheme['name']} ({selected_scheme['scheme_id']})"
    )

    hindi_speech_text = build_hindi_speech_text(selected_scheme, item, status)
    render_voice_guidance(hindi_speech_text)

    # =========================================================
    # CASE 1: INELIGIBLE (❌ अपात्र) - Clean Visual Reasons Only
    # =========================================================
    if status == "INELIGIBLE":
        inelig_title = "❌ अपात्र (NOT ELIGIBLE)" if is_hi else "❌ NOT ELIGIBLE (अपात्र)"
        inelig_sub = (
            f"दी गई जानकारी के अनुसार आप <strong>{selected_scheme.get('hindi_name', selected_scheme['name'])}</strong> की शर्तों को पूरा नहीं करते हैं।"
            if is_hi else
            f"Based on the provided information, you do not fulfill the eligibility requirements for <strong>{selected_scheme['name']}</strong>."
        )
        st.markdown(f"""
        <div class='verdict-box verdict-ineligible'>
            <div style='font-size:1.3rem; font-weight:800; margin-bottom:4px;'>{inelig_title}</div>
            <div style='font-size:0.96rem;'>{inelig_sub}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "#### 🚫 अपात्रता के विशिष्ट कारण (Specific Reasons Why You Do Not Match):"
            if is_hi else
            "#### 🚫 Specific Reasons Why You Do Not Match (अपात्रता के विशिष्ट कारण):"
        )

        reasons = item.get("why_you_dont_match", [])
        for f in reasons:
            crit = f.get("criterion", "")
            user_val = f.get("user_val", "")
            req_val = f.get("required_val", "")
            details = f.get("details", "")

            if is_hi:
                if "Housing" in crit or "Pucca" in crit:
                    clean_msg = "🏠 **पक्का मकान (Pucca House):** आपके पास पहले से पक्का मकान है, जबकि यह योजना केवल बेघर या कच्चे मकान (Kutcha House) में रहने वालों के लिए है।"
                elif "Tax" in crit:
                    clean_msg = "📄 **आयकर दाता (Income Tax):** परिवार में कोई आयकर दाता होने के कारण आप इस योजना के पात्र नहीं हैं।"
                elif "Public" in crit or "Govt" in crit:
                    clean_msg = "🏛️ **सरकारी नौकरी (Govt Employee):** परिवार में सरकारी कर्मचारी होने के कारण आप इस योजना के पात्र नहीं हैं।"
                elif "Land" in crit:
                    clean_msg = "🌾 **कृषि भूमि (Agricultural Land):** इस योजना के लिए अपने नाम पर कृषि योग्य भूमि दर्ज होना अनिवार्य है।"
                elif "Girl" in crit:
                    clean_msg = "👧 **बालिका अभिभावक (Girl Child):** सुकन्या समृद्धि योजना हेतु 10 वर्ष तक की बालिका का अभिभावक होना जरूरी है।"
                elif "Income" in crit:
                    clean_msg = f"💰 **आय सीमा (Income Ceiling):** आपकी वार्षिक आय ₹{computed_annual_income:,} इस योजना की निर्धारित सीमा से अधिक है।"
                elif "Occupation" in crit:
                    clean_msg = f"💼 **व्यवसाय (Occupation):** आपका व्यवसाय ({occ_in}) इस योजना के निर्धारित लाभार्थी वर्ग से मेल नहीं खाता है।"
                elif "Age" in crit:
                    clean_msg = f"🎂 **आयु सीमा (Age Limit):** आपकी आयु ({age_in} वर्ष) इस योजना की निर्धारित आयु सीमा में नहीं है।"
                elif "BPL" in crit:
                    clean_msg = "🟡 **बीपीएल कार्ड (BPL Card):** इस योजना के लिए बीपीएल या प्राथमिकता राशन कार्ड होना अनिवार्य है।"
                else:
                    clean_msg = f"⚠️ **{crit}:** {details}"
                entry_note = f"दर्ज विवरण: {user_val} | नियम: {req_val}"
            else:
                if "Housing" in crit or "Pucca" in crit:
                    clean_msg = "🏠 **Pucca House (पक्का मकान):** You already own a permanent pucca house. This scheme is exclusively for houseless families or kutcha house (कच्चा मकान) dwellers."
                elif "Tax" in crit:
                    clean_msg = "📄 **Income Taxpayer (आयकर दाता):** Family members who pay income tax are excluded by statutory mandate."
                elif "Public" in crit or "Govt" in crit:
                    clean_msg = "🏛️ **Government Employee (सरकारी नौकरी):** Households with regular government employees are ineligible for this welfare support."
                elif "Land" in crit:
                    clean_msg = "🌾 **Cultivable Land (कृषि भूमि):** Must own cultivable agricultural land registered in applicant's name."
                elif "Girl" in crit:
                    clean_msg = "👧 **Girl Child Guardian (बालिका अभिभावक):** Must be a parent or legal guardian of a girl child aged 10 years or below."
                elif "Income" in crit:
                    clean_msg = f"💰 **Income Ceiling (आय सीमा):** Your household annual income of ₹{computed_annual_income:,} exceeds the scheme threshold."
                elif "Occupation" in crit:
                    clean_msg = f"💼 **Occupation (व्यवसाय):** Your occupation ({occ_in}) does not match the target beneficiary category."
                elif "Age" in crit:
                    clean_msg = f"🎂 **Age Limit (आयु सीमा):** Your age ({age_in} years) is outside the prescribed eligible range."
                elif "BPL" in crit:
                    clean_msg = "🟡 **BPL Status (बीपीएल):** A verified BPL / priority ration card is required for this scheme."
                else:
                    clean_msg = f"⚠️ **{crit}:** {details}"
                entry_note = f"Your Entry: {user_val} | Scheme Rule: {req_val}"

            st.markdown(f"""
            <div class='reason-card'>
                {clean_msg}<br>
                <span style='font-size:0.83rem; color:#7F1D1D; opacity:0.85;'>{entry_note}</span>
            </div>
            """, unsafe_allow_html=True)

        st.info(
            "💡 **सुझाव (Tip):** आप ऊपर दी गई सूची में से किसी अन्य योजना (जैसे आयुष्मान भारत या पीएम किसान) का चयन करके अपनी पात्रता पुनः जांच सकते हैं।"
            if is_hi else
            "💡 **Tip:** You can select a different scheme above (e.g. PM-JAY or PM-KISAN) to check your eligibility for other public benefits."
        )

    # =========================================================
    # CASE 2: ELIGIBLE (✅ पात्र) - Visual Benefits & Simple Next Steps
    # =========================================================
    elif status in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE"]:
        elig_title = "✅ बधाई हो! आप पात्र हैं (ELIGIBLE)" if is_hi else "✅ Congratulations! You are ELIGIBLE (पात्र)"
        elig_sub = (
            f"आप <strong>{selected_scheme.get('hindi_name', selected_scheme['name'])}</strong> की सभी निर्धारित शर्तों को पूरा करते हैं!"
            if is_hi else
            f"You fulfill all statutory eligibility criteria for <strong>{selected_scheme['name']}</strong>!"
        )
        st.markdown(f"""
        <div class='verdict-box verdict-eligible'>
            <div style='font-size:1.35rem; font-weight:800; margin-bottom:4px;'>{elig_title}</div>
            <div style='font-size:0.98rem;'>{elig_sub}</div>
        </div>
        """, unsafe_allow_html=True)

        disp_ben = hero_info.get("benefit_hi", selected_scheme.get("benefit_value")) if is_hi else hero_info.get("benefit_en", selected_scheme.get("benefit_value"))
        st.markdown(f"""
        <div class='benefit-banner'>
            {"🎁 योजना लाभ (Entitlement):" if is_hi else "🎁 Scheme Benefit Entitlement:"} {disp_ben}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**संतुष्ट नियम (Satisfied Criteria):**" if is_hi else "**Satisfied Statutory Criteria (संतुष्ट नियम):**")
        matches = item.get("why_you_match", [])
        chips_html = ""
        for m in matches:
            chips_html += f"<span class='match-chip'>✔️ {m['criterion']}</span> "
        st.markdown(chips_html, unsafe_allow_html=True)

        st.markdown("")
        col_docs, col_steps = st.columns(2)

        with col_docs:
            with st.container(border=True):
                st.markdown("##### 📑 आवश्यक दस्तावेज़ चेकलिस्ट (Document Checklist):" if is_hi else "##### 📑 Required Documents Checklist:")
                docs_list = item.get("required_documents", [])
                checked_count = 0
                for d_i, d in enumerate(docs_list):
                    tag = ("(अनिवार्य)" if d.get("is_mandatory") else "(वैकल्पिक)") if is_hi else ("(Mandatory)" if d.get("is_mandatory") else "(Optional)")
                    doc_name = DOC_NAME_MAP_HI.get(d.get("doc_id"), d["name"]) if is_hi else d["name"]
                    chk_key = f"chk_vis_{selected_scheme_id}_{d_i}"
                    if st.checkbox(f"{doc_name} {tag}", key=chk_key, value=False):
                        checked_count += 1
                    issuing_label = "जारीकर्ता" if is_hi else "Issuing Authority"
                    st.caption(f"&nbsp;&nbsp;&nbsp;&nbsp;{issuing_label}: {d.get('issuing_authority')}")

                readiness_pct = int((checked_count / max(1, len(docs_list))) * 100)
                readiness_text = f"तैयारी: {checked_count}/{len(docs_list)} दस्तावेज़ उपलब्ध ({readiness_pct}%)" if is_hi else f"Readiness: {checked_count}/{len(docs_list)} documents prepared ({readiness_pct}%)"
                st.progress(readiness_pct / 100, text=readiness_text)
                if readiness_pct == 100:
                    st.success("🎉 सभी आवश्यक दस्तावेज़ तैयार हैं!" if is_hi else "🎉 All required documents are ready!")

        with col_steps:
            with st.container(border=True):
                st.markdown("##### 🚀 सरल आवेदन चरण (How to Apply):" if is_hi else "##### 🚀 Simple Application Steps (आवेदन प्रक्रिया):")
                if is_hi and selected_scheme_id in HINDI_STEPS_MAP:
                    steps = HINDI_STEPS_MAP[selected_scheme_id]
                else:
                    steps = item.get("application_process", {}).get("steps", [])
                for s_i, step in enumerate(steps, 1):
                    st.markdown(f"**{s_i}.** {step}")

                portal_url = item.get("application_process", {}).get("portal_url", "")
                if portal_url:
                    st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
                    st.link_button(
                        f"🌐 {'आधिकारिक पोर्टल पर जाएं' if is_hi else 'Visit Official Portal'} ({selected_scheme_id})",
                        url=portal_url,
                        use_container_width=True
                    )

    # =========================================================
    # CASE 3: UNCERTAIN / INCOMPLETE
    # =========================================================
    else:
        st.markdown(f"""
        <div class='verdict-box verdict-uncertain'>
            <div style='font-size:1.25rem; font-weight:800; margin-bottom:4px;'>{"🟡 अधूरी जानकारी (INCOMPLETE INFO)" if is_hi else "🟡 INCOMPLETE INFORMATION (अधूरी जानकारी)"}</div>
            <div>{"इस योजना की जांच हेतु कुछ आवश्यक विवरण अभी दर्ज नहीं किए गए हैं। कृपया फॉर्म पूरा भरें।" if is_hi else "Some essential details are missing. Please complete the form to verify your eligibility."}</div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================
    # RURAL ACTION SUITE: WHATSAPP SHARE, PRINT SLIP & VILLAGE DESK
    # =========================================================
    st.markdown("---")
    st.markdown("### 🌾 ग्रामीण नागरिक सेवा एवं सहायता (Rural Citizen Action Suite)" if is_hi else "### 🌾 Rural Citizen Action Suite (नागरिक सहायता)")

    if is_hi:
        wa_verdict_str = "✅ पात्र (ELIGIBLE)" if status in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE"] else ("❌ अपात्र (INELIGIBLE)" if status == "INELIGIBLE" else "🟡 अधूरी जानकारी")
        wa_msg = f"🏛️ *सरकारी योजना पात्रता पर्ची (YojanaSaarthi)*\n"
        wa_msg += f"📋 *योजना:* {selected_scheme.get('hindi_name', selected_scheme['name'])} ({selected_scheme['scheme_id']})\n"
        wa_msg += f"📌 *निर्णय:* {wa_verdict_str}\n"
        wa_msg += f"👤 *नागरिक विवरण:* {state_in} ({area_in}) | व्यवसाय: {occ_in} | वार्षिक आय: ₹{computed_annual_income:,}\n"
        wa_msg += f"🎁 *लाभ:* {selected_scheme.get('benefit_value', 'N/A')}\n"
        wa_msg += "--------------------------------\n"
        if status in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE"]:
            wa_msg += "*आवश्यक दस्तावेज़:*\n"
            for d in selected_scheme.get("required_documents", []):
                doc_name = DOC_NAME_MAP_HI.get(d.get("doc_id"), d["name"])
                wa_msg += f" • [{'अनिवार्य' if d.get('is_mandatory') else 'वैकल्पिक'}] {doc_name}\n"
        elif status == "INELIGIBLE":
            wa_msg += "*अपात्रता के विशिष्ट कारण:*\n"
            for f in item.get("why_you_dont_match", []):
                wa_msg += f" • {f.get('criterion')}: {f.get('details')}\n"
        wa_msg += "--------------------------------\n"
        wa_msg += f"📍 *नजदीकी सहायता केंद्र:* ग्राम पंचायत भवन / नजदीकी सीएससी (CSC) केंद्र\n"
        wa_msg += f"🌐 *आधिकारिक पोर्टल:* {selected_scheme.get('application_process', {}).get('portal_url', '')}\n"
    else:
        wa_verdict_str = "✅ ELIGIBLE (पात्र)" if status in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE"] else ("❌ NOT ELIGIBLE (अपात्र)" if status == "INELIGIBLE" else "🟡 INCOMPLETE INFORMATION")
        wa_msg = f"🏛️ *Government Scheme Eligibility Slip (YojanaSaarthi)*\n"
        wa_msg += f"📋 *Scheme:* {selected_scheme['name']} ({selected_scheme['scheme_id']})\n"
        wa_msg += f"📌 *Decision:* {wa_verdict_str}\n"
        wa_msg += f"👤 *Citizen Profile:* {state_in} ({area_in}) | Occupation: {occ_in} | Annual Income: ₹{computed_annual_income:,}\n"
        wa_msg += f"🎁 *Benefit:* {selected_scheme.get('benefit_value', 'N/A')}\n"
        wa_msg += "--------------------------------\n"
        if status in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE"]:
            wa_msg += "*Required Documents:*\n"
            for d in selected_scheme.get("required_documents", []):
                wa_msg += f" • [{'Mandatory' if d.get('is_mandatory') else 'Optional'}] {d['name']}\n"
        elif status == "INELIGIBLE":
            wa_msg += "*Specific Ineligibility Reasons:*\n"
            for f in item.get("why_you_dont_match", []):
                wa_msg += f" • {f.get('criterion')}: {f.get('details')}\n"
        wa_msg += "--------------------------------\n"
        wa_msg += f"📍 *Nearest Assistance:* Gram Panchayat Bhawan / Nearest CSC Kiosk\n"
        wa_msg += f"🌐 *Official Portal:* {selected_scheme.get('application_process', {}).get('portal_url', '')}\n"

    wa_encoded = urllib.parse.quote(wa_msg)
    wa_url = f"https://wa.me/?text={wa_encoded}"

    col_act1, col_act2 = st.columns(2)
    with col_act1:
        wa_btn_label = "📲 WhatsApp पर पर्ची शेयर करें (Share to WhatsApp)" if is_hi else "📲 Share Eligibility Slip to WhatsApp"
        st.link_button(
            wa_btn_label,
            url=wa_url,
            use_container_width=True,
            type="primary"
        )
    with col_act2:
        st.download_button(
            "📥 पर्ची डाउनलोड करें (.txt Slip)" if is_hi else "📥 Download Citizen Slip (.txt)",
            data=wa_msg,
            file_name=f"{selected_scheme['scheme_id']}_Citizen_Slip.txt",
            mime="text/plain",
            use_container_width=True
        )

    # Printable Slip for Gram Panchayat / CSC Operator
    with st.expander("📄 ग्राम पंचायत / सीएससी पावती पर्ची देखें (Print Official Slip)" if is_hi else "📄 View & Print Citizen Slip (ग्राम पंचायत पावती)"):
        stamp_html = (
            "<span class='slip-stamp'>✅ पात्र (ELIGIBLE)</span>"
            if status in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE"]
            else ("<span class='slip-stamp-fail'>❌ अपात्र (INELIGIBLE)</span>" if status == "INELIGIBLE" else "<span class='slip-stamp-fail'>🟡 अधूरी जानकारी</span>")
        )

        st.markdown(f"""
        <div class='citizen-slip'>
            <div style='text-align:center; border-bottom:2px solid #1A2942; padding-bottom:8px; margin-bottom:12px;'>
                <div style='font-size:1.15rem; font-weight:800; letter-spacing:-0.5px;'>🏛️ {"ग्राम पंचायत एवं सीएससी नागरिक पात्रता पावती" if is_hi else "GRAM PANCHAYAT & CSC CITIZEN ELIGIBILITY SLIP"}</div>
                <div style='font-size:0.82rem; color:#4A5568;'>{"सरकारी कल्याणकारी योजना मार्गदर्शक | सन्दर्भ:" if is_hi else "Government Scheme Grounded Decision Support | Ref:"} {selected_scheme['scheme_id']}-2026</div>
            </div>
            <div style='display:flex; justify-content:space-between; margin-bottom:10px;'>
                <div>
                    <strong>{"आवेदक राज्य (State):" if is_hi else "Applicant State:"}</strong> {state_in} ({area_in})<br>
                    <strong>{"व्यवसाय (Occupation):" if is_hi else "Livelihood:"}</strong> {occ_in} | <strong>{"सामाजिक श्रेणी (Category):" if is_hi else "Category:"}</strong> {cat_in}<br>
                    <strong>{"वार्षिक पारिवारिक आय (Income):" if is_hi else "Computed Annual Income:"}</strong> ₹{computed_annual_income:,}<br>
                    <strong>{"कृषि भूमि (Landholding):" if is_hi else "Agricultural Landholding:"}</strong> {computed_ha} Hectares
                </div>
                <div style='text-align:right;'>
                    {stamp_html}<br>
                    <small style='color:#4A5568;'>{"सत्यापन: 100% सटीक नियम" if is_hi else "Evaluation: 100% Deterministic"}</small>
                </div>
            </div>
            <div style='background-color:#FDFCF8; border:1px solid #D1D5DB; padding:10px; border-radius:6px; margin:10px 0;'>
                <strong>{"योजना (Target Scheme):" if is_hi else "Target Scheme:"}</strong> {selected_scheme.get('hindi_name', selected_scheme['name']) if is_hi else selected_scheme['name']} ({selected_scheme['scheme_id']})<br>
                <strong>{"देय लाभ (Entitlement):" if is_hi else "Entitlement:"}</strong> {selected_scheme.get('benefit_value', 'N/A')}<br>
                <strong>{"आधिकारिक पोर्टल (Official Portal):" if is_hi else "Official Portal:"}</strong> {selected_scheme.get('application_process', {}).get('portal_url', '')}
            </div>
            <div style='margin-top:10px;'>
                <strong>{"पात्रता निष्कर्ष (Summary Findings):" if is_hi else "Summary Findings:"}</strong><br>
                {("✓ सभी निर्धारित नियम एवं शर्तें संतुष्ट हैं।" if status in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE"] else "✗ अपात्रता की शर्तें: " + ", ".join([f.get("criterion", "") for f in item.get("why_you_dont_match", [])])) if is_hi else ("✓ All statutory rules satisfied." if status in ["ELIGIBLE", "POTENTIALLY_ELIGIBLE"] else "✗ Ineligibility conditions: " + ", ".join([f.get("criterion", "") for f in item.get("why_you_dont_match", [])]))}
            </div>
            <div style='margin-top:24px; border-top:1px dashed #94897A; padding-top:8px; display:flex; justify-content:space-between; font-size:0.8rem; color:#4A5568;'>
                <div>{"सत्यापन डेस्क: ग्राम पंचायत भवन / सीएससी केंद्र" if is_hi else "Verification Desk: Gram Panchayat Bhawan / CSC Kiosk"}</div>
                <div>{"अधिकृत हस्ताक्षर / मुहर: ___________________" if is_hi else "Authorized Signatory / Seal: ___________________"}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Village Offline Physical Assistance Guide
    st.markdown("##### 📍 गांव में सहायता कहां मिलेगी (Where to Get Physical Help in Your Village):" if is_hi else "##### 📍 Where to Get Physical Help in Your Village (सहायता केंद्र):")
    loc_c1, loc_c2, loc_c3 = st.columns(3)
    with loc_c1:
        if is_hi:
            st.markdown("""
            <div class='action-card'>
                <div style='font-size:1.1rem; font-weight:700;'>🏛️ ग्राम पंचायत भवन</div>
                <div style='font-size:0.85rem; color:#4A5568; margin-top:4px;'><strong>मिलें:</strong> पंचायत सचिव / ग्राम रोजगार सहायक</div>
                <div style='font-size:0.85rem; color:#4A5568; margin-top:2px;'><strong>सेवाएं:</strong> आवास+ प्रतीक्षा सूची, मनरेगा जॉब कार्ड, कच्चा मकान (Kutcha House) सत्यापन</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='action-card'>
                <div style='font-size:1.1rem; font-weight:700;'>🏛️ Gram Panchayat Bhawan (ग्राम पंचायत)</div>
                <div style='font-size:0.85rem; color:#4A5568; margin-top:4px;'><strong>Contact:</strong> Panchayat Secretary / Gram Rozgar Sahayak</div>
                <div style='font-size:0.85rem; color:#4A5568; margin-top:2px;'><strong>Services:</strong> Awaas+ waitlist, MGNREGA Job Card, Kutcha house (कच्चा मकान) physical inspection</div>
            </div>
            """, unsafe_allow_html=True)
    with loc_c2:
        if is_hi:
            st.markdown("""
            <div class='action-card'>
                <div style='font-size:1.1rem; font-weight:700;'>💻 जन सेवा केंद्र (CSC Kiosk)</div>
                <div style='font-size:0.85rem; color:#4A5568; margin-top:4px;'><strong>मिलें:</strong> वीएलई संचालक (VLE Operator)</div>
                <div style='font-size:0.85rem; color:#4A5568; margin-top:2px;'><strong>सेवाएं:</strong> आधार बायोमेट्रिक e-KYC, पीएम किसान (Farmer) रजिस्ट्रेशन, ऑनलाइन आवेदन</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='action-card'>
                <div style='font-size:1.1rem; font-weight:700;'>💻 Common Service Centre (जन सेवा केंद्र - CSC)</div>
                <div style='font-size:0.85rem; color:#4A5568; margin-top:4px;'><strong>Contact:</strong> Village Level Entrepreneur (VLE Operator)</div>
                <div style='font-size:0.85rem; color:#4A5568; margin-top:2px;'><strong>Services:</strong> Aadhaar biometric e-KYC, PM-Kisan farmer (किसान) registration, online filing</div>
            </div>
            """, unsafe_allow_html=True)
    with loc_c3:
        if is_hi:
            st.markdown("""
            <div class='action-card'>
                <div style='font-size:1.1rem; font-weight:700;'>📮 डाकघर (Post Office)</div>
                <div style='font-size:0.85rem; color:#4A5568; margin-top:4px;'><strong>मिलें:</strong> शाखा डाकपाल (Branch Post Master)</div>
                <div style='font-size:0.85rem; color:#4A5568; margin-top:2px;'><strong>सेवाएं:</strong> सुकन्या समृद्धि खाता, आईपीपीबी बैंक डीबीटी लिंकेज</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='action-card'>
                <div style='font-size:1.1rem; font-weight:700;'>📮 Post Office (डाकघर)</div>
                <div style='font-size:0.85rem; color:#4A5568; margin-top:4px;'><strong>Contact:</strong> Branch Post Master (BPM)</div>
                <div style='font-size:0.85rem; color:#4A5568; margin-top:2px;'><strong>Services:</strong> Sukanya Samriddhi account opening, IPPB direct bank DBT linkage</div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# VIEW 3: VISUAL SIDE-BY-SIDE SCHEME COMPARISON MATRIX
# =========================================================
elif st.session_state.nav_view == "compare":
    with st.container(border=True):
        st.markdown("### ⚖️ 5 प्रमुख सरकारी योजनाओं की तुलना तालिका (Scheme Comparison)" if is_hi else "### ⚖️ Side-by-Side Scheme Comparison Matrix (योजना तुलना)")
        st.caption("सभी 5 योजनाओं के लाभ, पात्रता आयु, आय सीमा और आवश्यक दस्तावेजों की एक नजर में तुलना करें:" if is_hi else "Compare benefits, age criteria, income rules, and documents across all 5 schemes at a glance:")

        comp_rows = []
        for s in registry.get_all_schemes():
            r = s.get("rules", {})
            if is_hi:
                age_str = f"{r.get('min_age', 0)} - {r.get('max_age', 'कोई सीमा नहीं')}" if r.get('max_age') else f"न्यूनतम {r.get('min_age', 0)} वर्ष"
                inc_str = f"≤ ₹{r.get('max_annual_income'):,}" if r.get("max_annual_income") else "कोई आय सीमा नहीं"
                docs_str = ", ".join([DOC_NAME_MAP_HI.get(d.get("doc_id"), d["name"]) for d in s.get("required_documents", []) if d.get("is_mandatory")])
                comp_rows.append({
                    "योजना का नाम (Scheme)": f"{s.get('hindi_name', s['name'])} ({s['scheme_id']})",
                    "देय लाभ (Benefit Value)": s.get("benefit_value"),
                    "पात्र आयु (Age)": age_str,
                    "अधिकतम आय (Income Ceiling)": inc_str,
                    "लक्षित वर्ग (Beneficiaries)": ", ".join(r.get("eligible_occupations", ["सभी नागरिक"])),
                    "अनिवार्य दस्तावेज़ (Key Documents)": docs_str,
                    "आधिकारिक पोर्टल (Portal)": s.get("application_process", {}).get("portal_url", "")
                })
            else:
                age_str = f"{r.get('min_age', 0)} - {r.get('max_age', 'No limit')}" if r.get('max_age') else f"Min {r.get('min_age', 0)} yrs"
                inc_str = f"≤ ₹{r.get('max_annual_income'):,}" if r.get("max_annual_income") else "No income ceiling"
                docs_str = ", ".join([d["name"] for d in s.get("required_documents", []) if d.get("is_mandatory")])
                comp_rows.append({
                    "Scheme Name": f"{s['name']} ({s['scheme_id']})",
                    "Benefit Value": s.get("benefit_value"),
                    "Eligible Age": age_str,
                    "Income Ceiling": inc_str,
                    "Beneficiaries": ", ".join(r.get("eligible_occupations", ["All citizens"])),
                    "Key Documents": docs_str,
                    "Official Portal": s.get("application_process", {}).get("portal_url", "")
                })

        idx_name = "योजना का नाम (Scheme)" if is_hi else "Scheme Name"
        df_comp = pd.DataFrame(comp_rows).set_index(idx_name)
        st.dataframe(df_comp, width="stretch")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        col_c_btn1, col_c_btn2 = st.columns([1, 1])
        with col_c_btn1:
            st.button(
                "🚀 अपनी पात्रता जांचें (Check My Eligibility)" if is_hi else "🚀 Check My Eligibility Now",
                type="primary",
                use_container_width=True,
                key="comp_goto_search",
                on_click=set_nav,
                args=("search",)
            )
        with col_c_btn2:
            st.button(
                "🏠 मुख्य पृष्ठ पर जाएं (Back to Home)" if is_hi else "🏠 Return to Home Dashboard",
                type="secondary",
                use_container_width=True,
                key="comp_goto_home",
                on_click=set_nav,
                args=("hero",)
            )





