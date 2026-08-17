import hashlib
import html

import pandas as pd
import streamlit as st

from app.ai_assistant import (
    candidate_analysis,
    interview_questions,
    ollama_available,
    ranking_explanation,
    skill_gap_analysis,
)
from app.analyzer import rank_candidates
from app.database import (
    create_screening,
    get_screening_candidates,
    get_screening_history,
    initialize_database,
    save_candidate,
)
from app.exporter import export_xlsx
from app.parser import extract_resume
from app.simple_rag import SimpleRAG

# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="SmartScreen AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# DATABASE
# ============================================================

try:
    initialize_database()
except Exception as error:
    st.error(f"PostgreSQL connection failed: {error}")
    st.stop()

# ============================================================
# DESIGN SYSTEM
# Inspired by the supplied Read.cv reference:
# editorial typography, generous whitespace, thin rules,
# monochrome surfaces and restrained orange accent.
# ============================================================

st.html(
    r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --ink: #101713;
    --black: #0c1720;
    --paper: #f7fbf8;
    --surface: #eef8f3;
    --white: #ffffff;
    --muted: #68736d;
    --muted-dark: #9aa69f;
    --line: #dce8e1;
    --line-dark: rgba(255,255,255,.15);
    --green: #20b486;
    --green-dark: #138c68;
    --green-soft: #e2f6ed;
    --orange: #ffb52e;
    --orange-soft: #fff1d3;
}

html {
    scroll-behavior: smooth;
}

body,
[class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    background: var(--paper);
    color: var(--ink);
}

#MainMenu,
footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}

.block-container {
    max-width: 100% !important;
    padding: 0 !important;
}

section[data-testid="stSidebar"] {
    background: var(--black);
    color: white;
}

section[data-testid="stSidebar"] * {
    color: white;
}

/* ============================================================
   HERO
   ============================================================ */

.hero {
    position: relative;
    min-height: 92vh;
    overflow: hidden;
    background:
        radial-gradient(circle at 78% 28%, rgba(32,180,134,.16), transparent 26%),
        radial-gradient(circle at 20% 90%, rgba(255,181,46,.08), transparent 22%),
        var(--black);
    color: white;
    isolation: isolate;
}

.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(rgba(255,255,255,.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.045) 1px, transparent 1px);
    background-size: 68px 68px;
    mask-image: linear-gradient(to bottom, #000 0%, transparent 88%);
    pointer-events: none;
}

.hero::after {
    content: "";
    position: absolute;
    width: 560px;
    height: 560px;
    right: -160px;
    bottom: -250px;
    border: 1px solid rgba(255,171,24,.20);
    border-radius: 50%;
    box-shadow:
        0 0 0 90px rgba(255,171,24,.025),
        0 0 0 180px rgba(255,171,24,.015);
    pointer-events: none;
}

.hero-nav {
    position: absolute;
    inset: 0 0 auto;
    z-index: 30;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 23px 5vw;
    border-bottom: 1px solid var(--line-dark);
}

.hero-logo {
    color: white;
    font-family: "Instrument Serif", serif;
    font-size: 30px;
    letter-spacing: -1px;
}

.hero-logo sup {
    margin-left: 3px;
    color: #77766f;
    font: 9px "Inter", sans-serif;
}

.hero-nav-links {
    display: flex;
    align-items: center;
    gap: 27px;
}

.hero-nav-links a {
    color: #9d9c96;
    text-decoration: none;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    transition: color .2s ease;
}

.hero-nav-links a:hover,
.hero-nav-links a:first-child {
    color: white;
}

.hero-nav-cta {
    padding: 11px 15px;
    color: var(--black) !important;
    background: white;
}

.hero-nav-cta:hover {
    color: white !important;
    background: var(--green) !important;
}

.hero-grid {
    position: relative;
    z-index: 10;
    display: grid;
    grid-template-columns: minmax(0, 1.15fr) minmax(340px, .85fr);
    align-items: center;
    gap: 6vw;
    min-height: 92vh;
    padding: 150px 7vw 100px;
}

.hero-copy {
    max-width: 900px;
}

.hero-eyebrow,
.section-eyebrow {
    color: #8c8b85;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
}

.hero-eyebrow {
    margin-bottom: 25px;
}

.hero-title {
    max-width: 900px;
    margin: 0;
    color: white;
    font-family: "Instrument Serif", serif;
    font-size: clamp(70px, 8.2vw, 140px);
    font-weight: 400;
    line-height: .83;
    letter-spacing: -5px;
}

.hero-title em {
    color: #878680;
    font-style: italic;
}

.hero-description {
    max-width: 610px;
    margin: 34px 0 0;
    color: #aaa9a3;
    font-size: 14px;
    line-height: 1.8;
}

.hero-actions {
    display: flex;
    align-items: center;
    gap: 18px;
    margin-top: 31px;
}

.hero-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 14px 19px;
    color: var(--black) !important;
    background: white;
    text-decoration: none;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.3px;
    text-transform: uppercase;
    transition: transform .2s ease, background .2s ease;
}

.hero-button:hover {
    color: var(--black) !important;
    background: var(--green);
    color: white !important;
    transform: translateY(-2px);
}

.hero-note {
    color: #73726d;
    font-size: 10px;
    letter-spacing: .5px;
}

/* Editorial candidate card */

.hero-visual {
    position: relative;
    width: min(390px, 100%);
    height: 490px;
    justify-self: end;
}

.hero-visual::before {
    content: "LIVE CANDIDATE ANALYSIS";
    position: absolute;
    top: -27px;
    right: 0;
    color: #65645f;
    font-size: 8px;
    letter-spacing: 2px;
}

.resume-card {
    position: absolute;
    inset: 0;
    padding: 25px;
    background:
        linear-gradient(145deg, rgba(255,255,255,.045), transparent 55%),
        #101a19;
    border: 1px solid rgba(32,180,134,.28);
    box-shadow: 28px 30px 0 rgba(255,255,255,.045);
    transform: rotate(-3deg);
    animation: float-card 5s ease-in-out infinite;
}

.resume-card-back {
    position: absolute;
    inset: 30px -34px -30px 35px;
    border: 1px solid rgba(255,255,255,.10);
    transform: rotate(7deg);
}

.resume-top {
    display: flex;
    justify-content: space-between;
    color: #77766f;
    font-size: 8px;
    letter-spacing: 1.7px;
}

.resume-name {
    margin-top: 58px;
    color: white;
    font: 54px/.86 "Instrument Serif", serif;
    letter-spacing: -1.5px;
}

.resume-role {
    margin-top: 10px;
    color: #85847e;
    font-size: 10px;
}

.resume-rule {
    height: 1px;
    margin-top: 52px;
    background: rgba(255,255,255,.12);
}

.resume-rule:nth-child(2) {
    width: 74%;
    margin-top: 11px;
}

.resume-rule:nth-child(3) {
    width: 88%;
    margin-top: 11px;
}

.resume-score {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-top: 39px;
}

.resume-score strong {
    color: white;
    font: 78px/.75 "Instrument Serif", serif;
    letter-spacing: -3px;
}

.resume-score span {
    color: #85847e;
    font-size: 8px;
    letter-spacing: 1.8px;
    text-transform: uppercase;
}

.resume-tag {
    display: inline-block;
    margin: 25px 5px 0 0;
    padding: 6px 8px;
    border: 1px solid rgba(255,255,255,.14);
    color: #aaa9a3;
    font-size: 8px;
}

.resume-tag.accent {
    border-color: rgba(32,180,134,.45);
    color: #5de0b4;
}

.hero-stamp {
    position: absolute;
    right: -42px;
    bottom: 28px;
    width: 108px;
    height: 108px;
    display: grid;
    place-items: center;
    border: 1px solid rgba(255,171,24,.35);
    border-radius: 50%;
    color: var(--orange);
    font-size: 8px;
    letter-spacing: 1.2px;
    text-align: center;
    transform: rotate(9deg);
}

/* ============================================================
   GENERAL SECTIONS
   ============================================================ */

.section {
    padding: 120px 7vw;
    border-bottom: 1px solid var(--line);
}

.section-head {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 7vw;
    align-items: end;
    margin-bottom: 55px;
}

.section-title {
    max-width: 900px;
    margin: 10px 0 0;
    font-family: "Instrument Serif", serif;
    font-size: clamp(56px, 6.5vw, 96px);
    font-weight: 400;
    line-height: .88;
    letter-spacing: -3px;
}

.section-description {
    max-width: 570px;
    margin: 0;
    color: var(--muted);
    font-size: 13px;
    line-height: 1.8;
}

/* ============================================================
   HOW IT WORKS
   ============================================================ */

.process-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    border-top: 1px solid var(--line);
}

.process-card {
    min-height: 235px;
    padding: 28px 26px 25px 0;
    border-right: 1px solid var(--line);
}

.process-card:not(:first-child) {
    padding-left: 26px;
}

.process-card:last-child {
    border-right: 0;
}

.process-number {
    color: #9a9992;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
}

.process-title {
    margin-top: 52px;
    font: 32px/.95 "Instrument Serif", serif;
}

.process-text {
    max-width: 330px;
    margin-top: 13px;
    color: var(--muted);
    font-size: 11px;
    line-height: 1.7;
}

/* ============================================================
   PROOF STRIP
   ============================================================ */

.proof-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    border-bottom: 1px solid var(--line);
    background: #eef8f3;
}

.proof-item {
    min-height: 112px;
    padding: 25px 28px;
    border-right: 1px solid var(--line);
}

.proof-item:last-child {
    border-right: 0;
}

.proof-item strong {
    display: block;
    color: var(--green-dark);
    font-size: 9px;
    letter-spacing: 1.8px;
}

.proof-item span {
    display: block;
    margin-top: 12px;
    color: #68736d;
    font-size: 10px;
}

/* ============================================================
   PRODUCT FEATURE CARDS
   ============================================================ */

.feature-grid {
    display: grid;
    grid-template-columns: 1.15fr .85fr .85fr;
    gap: 12px;
    margin-top: 55px;
}

.feature-card {
    min-height: 270px;
    padding: 28px;
    border: 1px solid var(--line);
    background: white;
}

.feature-card.feature-primary {
    background: #e4f7ee;
}

.feature-index {
    color: var(--green-dark);
    font-size: 8px;
    font-weight: 700;
    letter-spacing: 2px;
}

.feature-card h3 {
    max-width: 300px;
    margin: 60px 0 12px;
    font: 35px/.92 "Instrument Serif", serif;
}

.feature-card p {
    max-width: 320px;
    color: var(--muted);
    font-size: 10px;
    line-height: 1.75;
}

.feature-line {
    width: 52px;
    height: 3px;
    margin-top: 22px;
    background: var(--green);
}

/* ============================================================
   CTA BAND
   ============================================================ */

.cta-band {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 35px;
    margin: 0 7vw;
    padding: 55px 0;
    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
}

.cta-band-title {
    max-width: 800px;
    font: clamp(45px, 5vw, 72px)/.9 "Instrument Serif", serif;
}

.cta-band-copy {
    max-width: 530px;
    margin-top: 14px;
    color: var(--muted);
    font-size: 11px;
    line-height: 1.75;
}

.cta-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 155px;
    padding: 14px 18px;
    color: white;
    background: var(--green-dark);
    text-decoration: none;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.4px;
    text-transform: uppercase;
}

.cta-pill:hover {
    color: white;
    background: #0f7458;
}

/* ============================================================
   FOOTER UPGRADE
   ============================================================ */

.site-footer {
    margin-top: 70px;
    padding-top: 55px !important;
    padding-bottom: 55px !important;
    background: var(--black);
    color: #9ca9a3 !important;
}

.site-footer strong {
    color: white !important;
}

/* ============================================================
   SCREENING WORKSPACE
   ============================================================ */

.workspace {
    padding-top: 95px;
}

.form-label {
    margin: 37px 0 9px;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2.2px;
    text-transform: uppercase;
}

.form-help {
    margin-bottom: 12px;
    color: #898881;
    font-size: 11px;
    line-height: 1.65;
}

div[data-testid="stTextArea"] label,
div[data-testid="stFileUploader"] label {
    display: none;
}

div[data-testid="stTextArea"] textarea {
    min-height: 185px !important;
    padding: 17px !important;
    border: 1px solid #c9c8c0 !important;
    border-radius: 2px !important;
    background: #eef7f2 !important;
    color: #111 !important;
    font: 13px/1.7 "Inter", sans-serif !important;
    box-shadow: none !important;
}

div[data-testid="stTextArea"] textarea:focus {
    border-color: #111 !important;
    background: white !important;
    box-shadow: none !important;
}

div[data-testid="stFileUploader"] section {
    min-height: 180px !important;
    border: 1px dashed #aaa9a2 !important;
    border-radius: 2px !important;
    background: #eef7f2 !important;
    transition: border .2s ease, background .2s ease;
}

div[data-testid="stFileUploader"] section:hover {
    border-color: #111 !important;
    background: white !important;
}

.screen-action {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 30px;
    margin-top: 38px;
    padding: 25px 0;
    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
}

.screen-action-title {
    font: 32px/1 "Instrument Serif", serif;
}

.screen-action-subtext {
    max-width: 580px;
    margin-top: 8px;
    color: var(--muted);
    font-size: 11px;
    line-height: 1.7;
}

.stButton > button {
    min-height: 44px;
    padding: 11px 19px !important;
    border: 1px solid #111 !important;
    border-radius: 2px !important;
    background: #111 !important;
    color: white !important;
    font: 700 10px "Inter", sans-serif !important;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    box-shadow: none !important;
    transition: transform .2s ease, background .2s ease !important;
}

.stButton > button:hover {
    background: #2a2a28 !important;
    transform: translateY(-2px);
}

.stButton > button:disabled {
    opacity: .45;
}

/* ============================================================
   RESULTS
   ============================================================ */

.results-section {
    padding-top: 105px;
}

.analysis-bar {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 20px;
    padding-bottom: 17px;
    border-bottom: 1px solid #c9c8c0;
}

.analysis-bar span {
    color: #888782;
    font-size: 8px;
    letter-spacing: 2px;
}

.metric-grid {
    margin: 35px 0 55px;
}

[data-testid="stMetric"] {
    min-height: 115px;
    padding: 20px !important;
    border: 1px solid #d1d0c8 !important;
    border-radius: 2px !important;
    background: #eef7f2 !important;
}

[data-testid="stMetricLabel"] {
    color: #888782 !important;
    font-size: 8px !important;
    letter-spacing: 1.7px;
    text-transform: uppercase;
}

[data-testid="stMetricValue"] {
    color: #111 !important;
    font: 42px/.9 "Instrument Serif", serif !important;
}

.candidate-card {
    position: relative;
    padding: 27px 0;
    border-top: 1px solid #c9c8c0;
    transition: padding .2s ease, background .2s ease;
}

.candidate-card:hover {
    padding-left: 15px;
    background: rgba(255,255,255,.40);
}

.candidate-number {
    color: #8b8a84;
    font-size: 8px;
    font-weight: 700;
    letter-spacing: 2px;
}

.candidate-name {
    margin-top: 7px;
    font: 40px/1 "Instrument Serif", serif;
}

.candidate-role {
    margin-top: 6px;
    color: #818079;
    font-size: 10px;
}

.candidate-score {
    position: absolute;
    top: 24px;
    right: 0;
    text-align: right;
}

.candidate-score-number {
    font: 58px/.8 "Instrument Serif", serif;
}

.candidate-score-label {
    margin-top: 8px;
    color: #888782;
    font-size: 8px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.candidate-skills {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 21px;
}

.skill-pill {
    padding: 5px 8px;
    border: 1px solid #d0cfc7;
    border-radius: 1px;
    color: #66655f;
    background: transparent;
    font-size: 8px;
}

.candidate-summary {
    max-width: 700px;
    margin: 8px 0 25px;
    color: #77766f;
    font-size: 11px;
    line-height: 1.7;
}

[data-testid="stExpander"] {
    border: 1px solid #d0cfc7 !important;
    border-radius: 2px !important;
    background: transparent !important;
}

.ai-heading {
    margin-top: 28px;
    font: 33px/1 "Instrument Serif", serif;
}

.ai-subheading {
    margin: 8px 0 15px;
    color: #898881;
    font-size: 8px;
    letter-spacing: 1.8px;
    text-transform: uppercase;
}

.ai-evidence {
    padding: 20px;
    border: 1px solid #d3d2ca;
    border-radius: 2px;
    background: #eef7f2;
    color: #55544f;
    font: 11px/1.75 "Inter", sans-serif;
    white-space: pre-wrap;
}

[data-testid="stDataFrame"] {
    border: 1px solid #d3d2ca;
    border-radius: 2px;
    overflow: hidden;
}

.download-row {
    margin: 18px 0 0;
}

/* ============================================================
   INTELLIGENCE SECTION
   ============================================================ */

.intelligence-grid {
    display: grid;
    grid-template-columns: 1.3fr .7fr;
    gap: 1px;
    margin-top: 55px;
    border: 1px solid var(--line);
    background: var(--line);
}

.intelligence-card {
    min-height: 270px;
    padding: 30px;
    background: var(--paper);
}

.intelligence-card.dark {
    background: var(--black);
    color: white;
}

.intelligence-card h3 {
    margin: 55px 0 12px;
    font: 38px/.95 "Instrument Serif", serif;
}

.intelligence-card p {
    max-width: 520px;
    margin: 0;
    color: var(--muted);
    font-size: 11px;
    line-height: 1.75;
}

.intelligence-card.dark p {
    color: #9d9c96;
}

.intelligence-chip {
    display: inline-block;
    padding: 6px 9px;
    border: 1px solid var(--line);
    font-size: 8px;
    letter-spacing: 1.3px;
}

.intelligence-card.dark .intelligence-chip {
    border-color: var(--line-dark);
    color: var(--orange);
}

/* ============================================================
   HISTORY
   ============================================================ */

.history-section {
    padding-top: 105px;
}

.history-description {
    max-width: 620px;
    margin-top: 15px;
    color: var(--muted);
    font-size: 13px;
    line-height: 1.8;
}

/* ============================================================
   FOOTER
   ============================================================ */

.site-footer {
    display: flex;
    justify-content: space-between;
    gap: 30px;
    padding: 35px 7vw;
    color: #8a8983;
    font-size: 9px;
    line-height: 1.6;
}

.site-footer strong {
    color: #44433f;
}

/* ============================================================
   MOTION
   ============================================================ */

@keyframes float-card {
    0%, 100% {
        transform: rotate(-3deg) translateY(0);
    }
    50% {
        transform: rotate(-2deg) translateY(-9px);
    }
}

@media (prefers-reduced-motion: reduce) {
    html {
        scroll-behavior: auto;
    }

    .resume-card {
        animation: none;
    }
}

/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 900px) {
    .proof-strip {
        grid-template-columns: repeat(2, 1fr);
    }

    .proof-item:nth-child(2) {
        border-right: 0;
    }

    .proof-item:nth-child(-n+2) {
        border-bottom: 1px solid var(--line);
    }

    .feature-grid {
        grid-template-columns: 1fr;
    }

    .cta-band {
        grid-template-columns: 1fr;
        margin: 0 20px;
    }


    .hero-grid,
    .section-head,
    .intelligence-grid {
        grid-template-columns: 1fr;
    }

    .hero-grid {
        padding-top: 145px;
    }

    .hero-visual {
        justify-self: start;
        width: min(370px, 85vw);
        height: 440px;
    }

    .process-grid {
        grid-template-columns: 1fr;
    }

    .process-card,
    .process-card:not(:first-child) {
        padding: 25px 0;
        border-right: 0;
        border-bottom: 1px solid var(--line);
    }

    .process-card:last-child {
        border-bottom: 0;
    }

    .screen-action {
        align-items: flex-start;
        flex-direction: column;
    }
}

@media (max-width: 650px) {
    .hero-nav {
        padding: 19px 20px;
    }

    .hero-nav-links a:not(.hero-nav-cta) {
        display: none;
    }

    .hero-grid {
        display: block;
        padding: 135px 20px 70px;
    }

    .hero {
        min-height: auto;
    }

    .hero-title {
        font-size: clamp(58px, 16vw, 90px);
        letter-spacing: -3px;
    }

    .hero-description {
        font-size: 12px;
    }

    .hero-visual {
        width: 285px;
        height: 370px;
        margin: 75px auto 20px;
    }

    .resume-name {
        margin-top: 45px;
        font-size: 42px;
    }

    .resume-score strong {
        font-size: 62px;
    }

    .section {
        padding: 80px 20px;
    }

    .section-title {
        font-size: 57px;
    }

    .candidate-score {
        position: static;
        margin-top: 18px;
        text-align: left;
    }

    .candidate-score-number {
        font-size: 47px;
    }

    .site-footer {
        display: block;
        padding: 30px 20px;
    }
}
</style>
"""
)

# ============================================================
# HERO
# ============================================================

st.html(
    r"""
<div class="hero">
    <nav class="hero-nav">
        <div class="hero-logo">SmartScreen<sup>®</sup></div>

        <div class="hero-nav-links">
            <a href="#home">Home</a>
            <a href="#workflow">Workflow</a>
            <a href="#screening">Screening</a>
            <a href="#intelligence">Intelligence</a>
            <a href="#history">History</a>
            <a class="hero-nav-cta" href="#screening">Start Screening</a>
        </div>
    </nav>

    <div id="home"></div>

    <section class="hero-grid">
        <div class="hero-copy">
            <div class="hero-eyebrow">AI · RAG · Candidate Intelligence</div>

            <h1 class="hero-title">
                Find the people<br>
                <em>behind the paperwork.</em>
            </h1>

            <p class="hero-description">
                Screen resumes faster, surface evidence that matters,
                rank candidates with transparent signals, and use
                Generative AI to turn raw applications into decisions
                you can actually explain.
            </p>

            <div class="hero-actions">
                <a class="hero-button" href="#screening">Start screening →</a>
                <span class="hero-note">NLP / Semantic Search / Ollama</span>
            </div>
        </div>

        <div class="hero-visual">
            <div class="resume-card-back"></div>

            <div class="resume-card">
                <div class="resume-top">
                    <span>SMARTSCREEN / 01</span>
                    <span>LIVE ANALYSIS</span>
                </div>

                <div class="resume-name">
                    Candidate<br>Profile
                </div>

                <div class="resume-role">
                    Python / AI Engineer
                </div>

                <div class="resume-rule"></div>
                <div class="resume-rule"></div>
                <div class="resume-rule"></div>

                <div class="resume-score">
                    <strong>94%</strong>
                    <span>Match score</span>
                </div>

                <span class="resume-tag accent">PYTHON</span>
                <span class="resume-tag">FASTAPI</span>
                <span class="resume-tag">RAG</span>
            </div>

            <div class="hero-stamp">
                HUMAN<br>REVIEW<br>REQUIRED
            </div>
        </div>
    </section>
</div>
"""
)

# ============================================================
# WORKFLOW
# ============================================================

st.html(
    r"""
<div id="workflow"></div>

<section class="section">
    <div class="section-head">
        <div>
            <div class="section-eyebrow">01 / Workflow</div>
            <div class="section-title">
                From resumes<br>
                to evidence.
            </div>
        </div>

        <p class="section-description">
            SmartScreen keeps the workflow simple: describe the role,
            upload the candidate resumes, then inspect ranked results
            and the evidence behind every decision.
        </p>
    </div>

    <div class="process-grid">
        <article class="process-card">
            <div class="process-number">01</div>
            <div class="process-title">Define the role.</div>
            <div class="process-text">
                Add the skills, qualifications, experience and
                requirements that matter for the position.
            </div>
        </article>

        <article class="process-card">
            <div class="process-number">02</div>
            <div class="process-title">Read the resumes.</div>
            <div class="process-text">
                Upload multiple PDF or DOCX resumes and let the
                ranking pipeline compare candidates against the role.
            </div>
        </article>

        <article class="process-card">
            <div class="process-number">03</div>
            <div class="process-title">Explain the match.</div>
            <div class="process-text">
                Use semantic retrieval and Generative AI to inspect
                supporting evidence, gaps and interview questions.
            </div>
        </article>
    </div>
</section>
"""
)

st.html(
    r"""
<div class="proof-strip">
    <div class="proof-item">
        <strong>PDF + DOCX</strong>
        <span>Resume ingestion</span>
    </div>
    <div class="proof-item">
        <strong>RAG</strong>
        <span>Evidence retrieval</span>
    </div>
    <div class="proof-item">
        <strong>AI</strong>
        <span>Candidate explanations</span>
    </div>
    <div class="proof-item">
        <strong>POSTGRESQL</strong>
        <span>Persistent history</span>
    </div>
</div>
"""
)

# ============================================================
# PRODUCT FEATURES
# ============================================================

st.html(
    r"""
<section class="section">
    <div class="section-head">
        <div>
            <div class="section-eyebrow">02 / Why SmartScreen</div>
            <div class="section-title">
                Less searching.<br>
                More signal.
            </div>
        </div>

        <p class="section-description">
            A focused screening workspace designed around the parts of
            recruiting that deserve clarity: relevance, evidence,
            explainability and follow-up.
        </p>
    </div>

    <div class="feature-grid">
        <article class="feature-card feature-primary">
            <div class="feature-index">01 / RANKING</div>
            <h3>See your strongest candidates first.</h3>
            <p>
                Compare candidates using the application's relevance,
                skills, experience and semantic signals instead of
                scanning every resume manually.
            </p>
            <div class="feature-line"></div>
        </article>

        <article class="feature-card">
            <div class="feature-index">02 / EVIDENCE</div>
            <h3>Know why the score exists.</h3>
            <p>
                RAG retrieves relevant resume passages so candidate
                analysis starts from evidence rather than a blank prompt.
            </p>
            <div class="feature-line"></div>
        </article>

        <article class="feature-card">
            <div class="feature-index">03 / AI</div>
            <h3>Turn results into action.</h3>
            <p>
                Generate ranking explanations, candidate analysis,
                interview questions and skill-gap insights with Ollama.
            </p>
            <div class="feature-line"></div>
        </article>
    </div>
</section>
"""
)

# ============================================================
# SCREENING INPUT
# ============================================================

st.html(
    r"""
<div id="screening"></div>

<section class="section workspace">
    <div class="section-eyebrow">03 / Smart Resume Screening</div>

    <div class="section-title">
        Screen candidates<br>
        with better evidence.
    </div>

    <p class="section-description">
        Add a job description and upload resumes. The system calculates
        relevance, retrieves useful resume evidence using RAG, and uses
        Generative AI to explain the results.
    </p>
</section>
"""
)

with st.sidebar:
    st.markdown("### SmartScreen Settings")
    model = st.text_input("Ollama model", "llama3.2")
    st.caption("Candidate ranking is calculated by the application.")
    st.caption("Generative AI is used for explanations and generated content.")

st.html(
    """
<div class="form-label">JOB DESCRIPTION</div>
<div class="form-help">
    Tell the system what skills, experience and qualifications you're looking for.
</div>
"""
)

job = st.text_area(
    "Job Description",
    height=170,
    label_visibility="collapsed",
    placeholder=(
        "Example:\n\n"
        "Looking for a Python developer with experience in "
        "FastAPI, REST APIs, SQL and machine learning."
    ),
)

st.html(
    """
<div class="form-label">RESUME FILES</div>
<div class="form-help">
    Upload candidate resumes in PDF or DOCX format. Multiple resumes are supported.
</div>
"""
)

uploaded_files = st.file_uploader(
    "Upload Resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if "screening_started" not in st.session_state:
    st.session_state.screening_started = False

if "screening_id" not in st.session_state:
    st.session_state.screening_id = None

if "database_saved" not in st.session_state:
    st.session_state.database_saved = False

if "database_signature" not in st.session_state:
    st.session_state.database_signature = None

if job.strip() and uploaded_files:
    st.html(
        """
<div class="screen-action">
    <div>
        <div class="screen-action-title">Ready to analyze the candidates?</div>
        <div class="screen-action-subtext">
            The system will rank the uploaded resumes, retrieve relevant evidence,
            save the screening session, and prepare candidates for AI analysis.
        </div>
    </div>
</div>
"""
    )

    start_screening = st.button(
        "Screen Candidates",
        type="primary",
        key="start_screening",
    )

    if start_screening:
        st.session_state.screening_started = True

    if not st.session_state.screening_started:
        st.stop()

    resumes = []

    for file in uploaded_files:
        try:
            text = extract_resume(file.name, file.getvalue())
            resumes.append((file.name, text))
        except Exception as error:
            st.error(f"Could not read {file.name}: {error}")

    if resumes:
        signature_hasher = hashlib.sha256()
        signature_hasher.update(job.strip().encode("utf-8"))

        for uploaded_file in uploaded_files:
            signature_hasher.update(uploaded_file.name.encode("utf-8"))
            signature_hasher.update(uploaded_file.getvalue())

        current_database_signature = signature_hasher.hexdigest()

        if st.session_state.database_signature != current_database_signature:
            st.session_state.database_saved = False
            st.session_state.screening_id = None
            st.session_state.database_signature = current_database_signature

        with st.spinner("Analyzing candidates..."):
            results = rank_candidates(job, resumes)

        if not results:
            st.warning(
                "No candidates could be ranked. Please check the uploaded resumes."
            )
            st.stop()

        # --------------------------------------------------------
        # SAVE SCREENING + REAL CANDIDATE RESULTS
        # --------------------------------------------------------

        if not st.session_state.database_saved:
            try:
                st.session_state.screening_id = create_screening(job)

                for result in results:
                    matched_skills = result.get("matched_skills", []) or []
                    missing_skills = result.get("missing_skills", []) or []

                    save_candidate(
                        screening_id=st.session_state.screening_id,
                        candidate_name=str(result.get("candidate", "Unknown")),
                        resume_filename=str(result.get("candidate", "resume")),
                        match_score=float(result.get("score", 0)),
                        skill_score=float(result.get("skill_score", 0)),
                        experience_score=float(result.get("experience_score", 0)),
                        semantic_score=float(
                            result.get("semantic_score", result.get("score", 0))
                        ),
                        matched_skills=", ".join(map(str, matched_skills)),
                        missing_skills=", ".join(map(str, missing_skills)),
                    )

                st.session_state.database_saved = True
                st.success(
                    f"Screening #{st.session_state.screening_id} saved to PostgreSQL."
                )

            except Exception as error:
                st.error(f"Could not save screening results to PostgreSQL: {error}")

        # --------------------------------------------------------
        # RAG
        # --------------------------------------------------------

        rag = None

        try:
            rag_data = [
                {
                    "candidate": result["candidate"],
                    "resume_text": result["resume_text"],
                }
                for result in results
            ]

            with st.spinner("Preparing semantic resume search..."):
                rag = SimpleRAG().add_resumes(rag_data)

        except Exception as error:
            st.warning(f"RAG could not be loaded: {error}")

        # --------------------------------------------------------
        # RESULTS
        # --------------------------------------------------------

        st.html(
            """
<div class="results-section">
    <div class="analysis-bar">
        <span>ANALYSIS / 02</span>
        <span>SEMANTIC + EVIDENCE-BASED</span>
    </div>

    <div style="margin-top: 55px;">
        <div class="section-eyebrow">SCREENING RESULTS</div>
        <div class="section-title">Candidate ranking.</div>
        <p class="section-description">
            Candidates are ranked according to their relevance to the
            requirements provided in the job description.
        </p>
    </div>
</div>
"""
        )

        c1, c2, c3 = st.columns(3)

        c1.metric("Candidates", len(results))
        c2.metric("Top Match", f"{results[0]['score']:.1f}%")

        average_score = sum(r["score"] for r in results) / len(results)
        c3.metric("Average Score", f"{average_score:.1f}%")

        for i, result in enumerate(results):
            candidate_name = html.escape(str(result["candidate"]))
            score = float(result["score"])
            matched_skills = result.get("matched_skills", []) or []

            skills_html = "".join(
                f'<span class="skill-pill">{html.escape(str(skill))}</span>'
                for skill in matched_skills[:8]
            )

            st.html(
                f"""
<div class="candidate-card">
    <div class="candidate-number">CANDIDATE {i + 1:02d}</div>
    <div class="candidate-name">{candidate_name}</div>
    <div class="candidate-role">Resume relevance score</div>

    <div class="candidate-score">
        <div class="candidate-score-number">{score:.0f}%</div>
        <div class="candidate-score-label">Match</div>
    </div>

    <div class="candidate-skills">{skills_html}</div>
</div>
"""
            )

            st.html(
                f"""
<div class="candidate-summary">
    Candidate ranked at <strong>{score:.0f}%</strong>
    based on relevance to the supplied job description.
</div>
"""
            )

        table = pd.DataFrame(
            [
                {
                    "Rank": i + 1,
                    "Candidate": result["candidate"],
                    "Match": f"{result['score']:.1f}%",
                    "Skills": f"{result['skill_score']:.0f}%",
                    "Experience": f"{result['experience_score']:.0f}%",
                    "Missing Skills": (
                        ", ".join(result["missing_skills"][:4]) or "None"
                    ),
                }
                for i, result in enumerate(results)
            ]
        )

        with st.expander("View detailed ranking table"):
            st.dataframe(
                table,
                use_container_width=True,
                hide_index=True,
            )

        st.download_button(
            "Download Excel Ranking",
            data=export_xlsx(results),
            file_name="candidate_rankings.xlsx",
            mime=("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        )

        # --------------------------------------------------------
        # CANDIDATE DETAILS
        # --------------------------------------------------------

        st.html(
            """
<div style="margin-top: 90px;">
    <div class="section-eyebrow">CANDIDATE ANALYSIS</div>
    <div class="section-title">Candidate details.</div>
</div>
"""
        )

        for number, result in enumerate(results):
            with st.expander(
                f"#{number + 1} {result['candidate']} — {result['score']:.1f}%"
            ):
                a, b, c = st.columns(3)

                a.metric("Overall", f"{result['score']:.1f}%")
                b.metric("Skill Match", f"{result['skill_score']:.0f}%")
                c.metric("Experience", f"{result['experience_score']:.0f}%")

                st.markdown("**Matched Skills**")
                st.write(", ".join(result["matched_skills"]) or "None")

                st.markdown("**Missing Skills**")
                st.write(", ".join(result["missing_skills"]) or "None")

                evidence = result["resume_text"][:6000]

                if rag:
                    try:
                        retrieved = rag.retrieve(
                            job,
                            candidate=result["candidate"],
                            top_k=5,
                        )

                        if retrieved:
                            evidence = "\n\n".join(item["text"] for item in retrieved)
                    except Exception:
                        pass

                st.html(
                    """
<div class="ai-heading">Relevant resume evidence</div>
<div class="ai-subheading">
    Retrieved using semantic similarity
</div>
"""
                )

                evidence_html = html.escape(evidence[:5000])

                st.html(
                    f"""
<div class="ai-evidence">{evidence_html}</div>
"""
                )

                st.html(
                    """
<div class="ai-heading">Generative AI</div>
<div class="ai-subheading">
    Ollama · Llama · RAG-assisted analysis
</div>
"""
                )

                ai_ready = ollama_available(model)

                if not ai_ready:
                    st.warning(
                        f"Ollama model '{model}' is not available. "
                        "Make sure Ollama is running and the model is installed."
                    )

                # Keep both columns inside the same scope.
                ai_col1, ai_col2 = st.columns(2)

                with ai_col1:
                    if st.button(
                        "AI Candidate Analysis",
                        key=f"analysis_{number}",
                        disabled=not ai_ready,
                    ):
                        with st.spinner("Generating candidate analysis..."):
                            try:
                                answer = candidate_analysis(
                                    job,
                                    evidence,
                                    model,
                                )
                                st.write(answer)
                            except Exception as error:
                                st.error(error)

                    if st.button(
                        "Why This Ranking?",
                        key=f"ranking_{number}",
                        disabled=not ai_ready,
                    ):
                        with st.spinner("Generating ranking explanation..."):
                            try:
                                answer = ranking_explanation(
                                    job,
                                    result["score"],
                                    result["matched_skills"],
                                    result["missing_skills"],
                                    evidence,
                                    model,
                                )
                                st.write(answer)
                            except Exception as error:
                                st.error(error)

                with ai_col2:
                    if st.button(
                        "Generate Interview Questions",
                        key=f"questions_{number}",
                        disabled=not ai_ready,
                    ):
                        with st.spinner("Generating interview questions..."):
                            try:
                                answer = interview_questions(
                                    job,
                                    evidence,
                                    model,
                                )
                                st.write(answer)
                            except Exception as error:
                                st.error(error)

                    if st.button(
                        "AI Skill Gap Analysis",
                        key=f"gap_{number}",
                        disabled=not ai_ready,
                    ):
                        with st.spinner("Analyzing candidate skill gaps..."):
                            try:
                                answer = skill_gap_analysis(
                                    job,
                                    result["matched_skills"],
                                    result["missing_skills"],
                                    model,
                                )
                                st.write(answer)
                            except Exception as error:
                                st.error(error)

else:
    st.session_state.screening_started = False
    st.session_state.screening_id = None
    st.session_state.database_saved = False

    st.html(
        """
<div style="
    max-width: 720px;
    margin: 45px auto;
    padding: 55px 20px;
    text-align: center;
">
    <div style="
        color: #111;
        font: 54px/1 'Instrument Serif', serif;
        letter-spacing: -1px;
    ">
        Ready to screen?
    </div>

    <div style="
        max-width: 500px;
        margin: 18px auto 0;
        color: #77766f;
        font: 13px/1.8 'Inter', sans-serif;
    ">
        Add a job description and upload one or more resumes
        to begin candidate analysis.
    </div>
</div>
"""
    )

# ============================================================
# INTELLIGENCE
# ============================================================

st.html(
    r"""
<div id="intelligence"></div>

<section class="section">
    <div class="section-head">
        <div>
            <div class="section-eyebrow">04 / Intelligence</div>
            <div class="section-title">
                Explain the<br>
                score, not just the score.
            </div>
        </div>

        <p class="section-description">
            The ranking pipeline stays separate from Generative AI.
            RAG retrieves supporting resume evidence, while Ollama-powered
            features turn that evidence into useful analysis.
        </p>
    </div>

    <div class="intelligence-grid">
        <div class="intelligence-card">
            <span class="intelligence-chip">SEMANTIC RETRIEVAL</span>
            <h3>Evidence before explanation.</h3>
            <p>
                Relevant resume passages are retrieved for the candidate
                and job description before the AI analysis is generated.
                This makes the output easier to inspect and challenge.
            </p>
        </div>

        <div class="intelligence-card dark">
            <span class="intelligence-chip">OLLAMA / LLAMA</span>
            <h3>Local AI layer.</h3>
            <p>
                Generate candidate analysis, ranking explanations,
                interview questions and skill-gap analysis through the
                configured local Ollama model.
            </p>
        </div>
    </div>
</section>
"""
)

# ============================================================
# FINAL CTA
# ============================================================

st.html(
    r"""
<div class="cta-band">
    <div>
        <div class="cta-band-title">Ready to find the right candidate?</div>
        <div class="cta-band-copy">
            Start with the role. Upload the resumes. Let SmartScreen
            organize the evidence so you can spend your time making
            the decision — not finding the information.
        </div>
    </div>

    <a class="cta-pill" href="#screening">Start screening →</a>
</div>
"""
)

# ============================================================
# SCREENING HISTORY
# ============================================================

st.html(
    r"""
<div id="history"></div>

<section class="section history-section">
    <div class="section-eyebrow">05 / Database</div>

    <div class="section-title">
        Screening history.
    </div>

    <div class="history-description">
        Review previous screening sessions and their saved candidate
        rankings directly from PostgreSQL.
    </div>
</section>
"""
)

try:
    history = get_screening_history()
except Exception as error:
    history = []
    st.warning(f"Could not load screening history: {error}")

if not history:
    st.info("No previous screening sessions found.")
else:
    screening_options = {}

    for row in history:
        screening_id = row[0]
        created_at = row[2]
        candidate_count = row[3]

        if created_at:
            label = (
                f"Screening #{screening_id} — "
                f"{candidate_count} candidates — "
                f"{created_at.strftime('%d %b %Y, %I:%M %p')}"
            )
        else:
            label = f"Screening #{screening_id} — {candidate_count} candidates"

        screening_options[label] = screening_id

    selected_screening = st.selectbox(
        "Select a previous screening",
        list(screening_options.keys()),
        key="history_screening_selector",
    )

    selected_screening_id = screening_options[selected_screening]

    try:
        history_candidates = get_screening_candidates(selected_screening_id)
    except Exception as error:
        history_candidates = []
        st.error(f"Could not load saved candidates: {error}")

    if history_candidates:
        history_data = []

        for candidate in history_candidates:
            history_data.append(
                {
                    "Candidate": candidate[0] or "Unknown",
                    "Resume": candidate[1] or "Unknown",
                    "Match": (
                        f"{float(candidate[2]):.1f}%"
                        if candidate[2] is not None
                        else "0.0%"
                    ),
                    "Skills": (
                        f"{float(candidate[3]):.1f}%"
                        if candidate[3] is not None
                        else "0.0%"
                    ),
                    "Experience": (
                        f"{float(candidate[4]):.1f}%"
                        if candidate[4] is not None
                        else "0.0%"
                    ),
                    "Semantic": (
                        f"{float(candidate[5]):.1f}%"
                        if candidate[5] is not None
                        else "0.0%"
                    ),
                    "Matched Skills": candidate[6] or "None",
                    "Missing Skills": candidate[7] or "None",
                }
            )

        st.dataframe(
            history_data,
            use_container_width=True,
            hide_index=True,
        )

        scores = [
            float(candidate[2])
            for candidate in history_candidates
            if candidate[2] is not None
        ]

        if scores:
            h1, h2, h3 = st.columns(3)
            h1.metric("Saved Candidates", len(history_candidates))
            h2.metric("Top Match", f"{max(scores):.1f}%")
            h3.metric(
                "Average Score",
                f"{sum(scores) / len(scores):.1f}%",
            )
    else:
        st.info("No candidates were saved for this screening.")

# ============================================================
# FOOTER
# ============================================================

st.html(
    """
<div class="site-footer">
    <div>
        <strong>SmartScreen®</strong> · Academic BTech Project
    </div>

    <div>
        NLP · RAG · Generative AI<br>
        Final hiring decisions should always involve human review.
    </div>
</div>
"""
)
