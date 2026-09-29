import os
import re
from uuid import uuid4

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()

# Streamlit Page Configuration
st.set_page_config(
    page_title="PatchPilot — AI Release Intelligence",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom SaaS Developer Theme Styling
st.markdown(
    """
<style>
    /* Global Base */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Layout containment */
    .main .block-container {
        max-width: 1040px;
        padding-top: 1.5rem;
        padding-bottom: 3.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Header Section */
    .product-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1.25rem;
        margin-bottom: 1.25rem;
        border-bottom: 1px solid #1f293d;
    }
    .brand-group {
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }
    .brand-icon {
        font-size: 2rem;
        background: #151d2f;
        padding: 0.4rem 0.6rem;
        border-radius: 10px;
        border: 1px solid #28354f;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    .brand-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }
    .brand-subtitle {
        font-size: 0.875rem;
        color: #94a3b8;
        margin-top: 0.2rem;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.35rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #10b981;
    }

    /* Product Story / Flow Stepper */
    .pipeline-wrapper {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 0.65rem 1rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        overflow-x: auto;
    }
    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        white-space: nowrap;
    }
    .pipeline-step.active {
        color: #38bdf8;
    }
    .pipeline-step.completed {
        color: #34d399;
    }
    .step-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: #1e293b;
        color: #94a3b8;
        font-size: 0.65rem;
    }
    .pipeline-step.active .step-badge {
        background: #0284c7;
        color: #ffffff;
    }
    .pipeline-step.completed .step-badge {
        background: #059669;
        color: #ffffff;
    }
    .pipeline-arrow {
        color: #334155;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Cards & Containers */
    .saas-card {
        background: #111827;
        border: 1px solid #1f293d;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #1f293d;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f1f5f9;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .card-subtitle {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.15rem;
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .badge-service {
        background: #1e293b;
        color: #cbd5e1;
        border: 1px solid #334155;
    }
    .badge-baseline {
        background: rgba(148, 163, 184, 0.12);
        color: #94a3b8;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }
    .badge-memory {
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    .badge-risk-high {
        background: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.35);
    }
    .badge-risk-medium {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }
    .badge-risk-low {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }

    /* Mode Banners (Memory vs Baseline) */
    .mode-banner {
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.25rem;
    }
    .mode-banner-memory {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(14, 165, 233, 0.06) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    .mode-banner-baseline {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid #334155;
    }
    .mode-banner-title {
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .mode-banner-memory .mode-banner-title {
        color: #a5b4fc;
    }
    .mode-banner-baseline .mode-banner-title {
        color: #94a3b8;
    }
    .mode-banner-desc {
        font-size: 0.8rem;
        color: #94a3b8;
        line-height: 1.4;
    }

    /* Content Blocks */
    .content-box {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 1rem 1.15rem;
        margin-bottom: 0.75rem;
    }
    .content-box-title {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* Memory Quote Cards */
    .memory-item {
        background: #0b1120;
        border-left: 3px solid #6366f1;
        border-top: 1px solid #1e293b;
        border-right: 1px solid #1e293b;
        border-bottom: 1px solid #1e293b;
        border-radius: 0 6px 6px 0;
        padding: 0.65rem 0.85rem;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        color: #cbd5e1;
        line-height: 1.45;
    }

    /* Sidebar Clean Styling */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 0.5rem;
    }
    .sidebar-brand-name {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
    }
    .sidebar-desc {
        font-size: 0.8rem;
        color: #94a3b8;
        line-height: 1.4;
        margin-bottom: 1.25rem;
    }
    .sidebar-card {
        background: #111827;
        border: 1px solid #1f293d;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin-bottom: 1.25rem;
    }
    .sidebar-card-title {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 0.4rem;
    }
    .sidebar-metric-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.78rem;
        padding: 0.25rem 0;
        color: #94a3b8;
        border-bottom: 1px solid #1e293b;
    }
    .sidebar-metric-row:last-child {
        border-bottom: none;
    }
    .sidebar-metric-value {
        color: #e2e8f0;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-weight: 500;
    }

    /* Button and Form adjustments */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# API Keys and Environment Verification
api_key = os.getenv("HINDSIGHT_API_KEY")
base_url = os.getenv("HINDSIGHT_BASE_URL")
bank_id = os.getenv("HINDSIGHT_BANK_ID")
groq_key = os.getenv("GROQ_API_KEY")

system_ready = all([api_key, base_url, bank_id, groq_key])

if not system_ready:
    st.error("A setting is missing from your .env file. Check it in Terminal.")
    st.stop()


def make_hindsight_client():
    return Hindsight(base_url=base_url, api_key=api_key)


# Helper: Parse Groq advice into structured sections while preserving full content
def parse_advice_sections(advice_text):
    risk_match = re.search(r"(?:1\.\s*)?Risk:?\s*\*?\*?\s*(Low|Medium|High)", advice_text, re.I)
    risk = risk_match.group(1).capitalize() if risk_match else "Assessed"

    action_match = re.search(
        r"(?:(?:\*\*|\#\#)?\s*(?:2\.\s*)?Recommended [Aa]ction:?\*?\*?)(.*?)(?=(?:(?:\*\*|\#\#)?\s*(?:3\.\s*)?Why:?\*?\*?)|\Z)",
        advice_text,
        re.S | re.I,
    )
    action = action_match.group(1).strip() if action_match else None

    why_match = re.search(r"(?:(?:\*\*|\#\#)?\s*(?:3\.\s*)?Why:?\*?\*?)(.*)", advice_text, re.S | re.I)
    why_full = why_match.group(1).strip() if why_match else None

    past_evidence = None
    inference = None
    if why_full:
        pe_match = re.search(
            r"(?:[\*\#\-]*\s*Past [Ee]vidence:?[\*\#\-]*)(.*?)(?=(?:[\*\#\-]*\s*Inference:?[\*\#\-]*)|\Z)",
            why_full,
            re.S | re.I,
        )
        inf_match = re.search(r"(?:[\*\#\-]*\s*Inference:?[\*\#\-]*)(.*)", why_full, re.S | re.I)
        if pe_match and inf_match:
            pe_clean = pe_match.group(1).strip().strip("-*• \n")
            inf_clean = inf_match.group(1).strip().strip("-*• \n")
            if pe_clean:
                past_evidence = pe_clean
            if inf_clean:
                inference = inf_clean

    return {
        "risk": risk,
        "action": action,
        "why_full": why_full,
        "past_evidence": past_evidence,
        "inference": inference,
    }


# SIDEBAR: Clean, Professional Developer Setup
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <span style="font-size: 1.5rem;">🚦</span>
            <span class="sidebar-brand-name">PatchPilot</span>
        </div>
        <div class="sidebar-desc">
            AI Release Intelligence that learns from deployment history to prevent preventable production rollbacks.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Connected Architecture Details (derived solely from existing env state)
    st.markdown(
        f"""
        <div class="sidebar-card">
            <div class="sidebar-card-title">Connected Engine</div>
            <div class="sidebar-metric-row">
                <span>Memory Layer</span>
                <span class="sidebar-metric-value">Hindsight Cloud</span>
            </div>
            <div class="sidebar-metric-row">
                <span>Memory Bank</span>
                <span class="sidebar-metric-value">{bank_id}</span>
            </div>
            <div class="sidebar-metric-row">
                <span>LLM Provider</span>
                <span class="sidebar-metric-value">Groq (gpt-oss-120b)</span>
            </div>
            <div class="sidebar-metric-row">
                <span>Status</span>
                <span class="sidebar-metric-value" style="color: #34d399;">● Online</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-card">
            <div class="sidebar-card-title">Demo Setup</div>
            <p style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 0.5rem;">
                Seed your Hindsight memory bank with historical deployment precedents.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Add sample team history", use_container_width=True):
        examples = [
            "The payments-service database migration caused a rollback. The team found that the migration locked the orders table.",
            "A later payments-service migration succeeded after the team used a staged rollout and checked database locks first.",
            "A config-only change to the notifications-service deployed successfully without a staged rollout.",
        ]

        memory_client = make_hindsight_client()
        try:
            for example in examples:
                memory_client.retain(bank_id=bank_id, content=example)
            st.success("Added three sample deployment memories.")
        except Exception as error:
            st.error(f"Could not save the sample history: {error}")
        finally:
            memory_client.close()

    st.caption("These sample records are simulated, not live production incidents.")


# HEADER SECTION
status_html = ""
if system_ready:
    status_html = f"""
    <div class="status-badge">
        <span class="status-dot"></span>
        <span>Hindsight & Groq Ready</span>
    </div>
    """

st.markdown(
    f"""
    <div class="product-header">
        <div class="brand-group">
            <div class="brand-icon">🚦</div>
            <div>
                <h1 class="brand-title">PatchPilot</h1>
                <div class="brand-subtitle">AI Release Intelligence that learns from deployment history.</div>
            </div>
        </div>
        {status_html}
    </div>
    """,
    unsafe_allow_html=True,
)

# PRODUCT STORY / PIPELINE FLOW
has_result = "latest" in st.session_state
s1_class = "completed" if has_result else "active"
s2_class = "completed" if (has_result and not st.session_state["latest"]["baseline"]) else ("active" if has_result else "")
s3_class = "active" if has_result else ""
s4_class = ""
s5_class = ""

st.markdown(
    f"""
    <div class="pipeline-wrapper">
        <div class="pipeline-step {s1_class}">
            <span class="step-badge">1</span>
            <span>Release</span>
        </div>
        <span class="pipeline-arrow">→</span>
        <div class="pipeline-step {s2_class}">
            <span class="step-badge">2</span>
            <span>Recall History</span>
        </div>
        <span class="pipeline-arrow">→</span>
        <div class="pipeline-step {s3_class}">
            <span class="step-badge">3</span>
            <span>Recommendation</span>
        </div>
        <span class="pipeline-arrow">→</span>
        <div class="pipeline-step {s4_class}">
            <span class="step-badge">4</span>
            <span>Deployment Outcome</span>
        </div>
        <span class="pipeline-arrow">→</span>
        <div class="pipeline-step {s5_class}">
            <span class="step-badge">5</span>
            <span>Learn</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# SECTION 1: Plan a Release (Primary Card)
st.markdown(
    """
    <div class="saas-card">
        <div class="card-header">
            <div>
                <h3 class="card-title">📋 Plan a Release</h3>
                <div class="card-subtitle">Specify your planned service changes to assess release risk against team precedents.</div>
            </div>
        </div>
    """,
    unsafe_allow_html=True,
)

baseline = st.checkbox(
    "Show generic advice without using team memory",
    value=False,
    help="When enabled, Hindsight memory recall is bypassed to show generic LLM guidance.",
)

with st.form("release_form"):
    service = st.text_input("Service name", value="payments-service")
    release = st.text_area(
        "What are you planning to deploy?",
        value="Database migration that adds an index to the orders table.",
        height=90,
    )
    submitted = st.form_submit_button("Get release advice", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# Release Analysis Processing
if submitted:
    if not release.strip():
        st.warning("Describe the planned release first.")
    else:
        memories = []

        if not baseline:
            memory_client = make_hindsight_client()
            try:
                result = memory_client.recall(
                    bank_id=bank_id,
                    query=f"Past deployments, failures, and successful fixes for {service}: {release}",
                )
                memories = [item.text for item in result.results]
            except Exception as error:
                st.error(f"Hindsight could not recall team history: {error}")
            finally:
                memory_client.close()

        if baseline:
            history = "No team deployment history was provided."
        elif memories:
            history = "\n".join(f"- {item}" for item in memories)
        else:
            history = "No relevant team history was found."

        prompt = f"""
Assess this planned software release.

Service: {service}
Planned change: {release}

Relevant team history from Hindsight:
{history}

Give a concise answer with:
1. Risk: Low, Medium, or High
2. Recommended action
3. Why, separating past evidence from your inference
If history is missing, say the advice is generic. Do not invent incidents.
"""

        try:
            groq = Groq(api_key=groq_key)
            response = groq.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )
            advice = response.choices[0].message.content
            st.session_state["latest"] = {
                "service": service,
                "release": release,
                "advice": advice,
                "memories": memories,
                "baseline": baseline,
                "run_id": uuid4().hex,
            }
        except Exception as error:
            st.error(f"Could not generate advice: {error}")


# SECTION 2: RESULTS SECTION (Visual Recommendation & Evidence Cards)
if "latest" in st.session_state:
    latest = st.session_state["latest"]
    parsed = parse_advice_sections(latest["advice"])

    # Determine badges and styling
    risk_level = parsed["risk"]
    if risk_level.lower() == "high":
        risk_badge_class = "badge-risk-high"
        risk_icon = "🔴"
    elif risk_level.lower() == "low":
        risk_badge_class = "badge-risk-low"
        risk_icon = "🟢"
    else:
        risk_badge_class = "badge-risk-medium"
        risk_icon = "🟡"

    # Start Results Card
    st.markdown(
        """
        <div class="saas-card">
            <div class="card-header">
                <div>
                    <h3 class="card-title">⚡ Release Advice & Assessment</h3>
                    <div class="card-subtitle">AI analysis synthesized from operational context and historical precedents.</div>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # Memory Mode Difference Banner
    if latest["baseline"]:
        st.markdown(
            """
            <div class="mode-banner mode-banner-baseline">
                <div class="mode-banner-title">
                    <span>⚪ BASELINE RUN — HINDSIGHT MEMORY OFF</span>
                </div>
                <div class="mode-banner-desc">
                    Generic model guidance without team memory. No past deployment incidents, table lock issues, or past team fixes were referenced.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="mode-banner mode-banner-memory">
                <div class="mode-banner-title">
                    <span>✨ MEMORY-INFORMED RUN — HINDSIGHT RECALL ON</span>
                </div>
                <div class="mode-banner-desc">
                    Grounded in team deployment history. Hindsight recalled <strong>{len(latest['memories'])} past deployment records</strong> from bank <code>{bank_id}</code>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Badges Row
    mem_badge_html = (
        '<span class="badge badge-baseline">Baseline (No Memory)</span>'
        if latest["baseline"]
        else f'<span class="badge badge-memory">🧠 Hindsight Informed ({len(latest["memories"])} Recalled)</span>'
    )
    st.markdown(
        f"""
        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; margin-bottom: 1.25rem;">
            <span class="badge badge-service">Target: {latest['service']}</span>
            {mem_badge_html}
            <span class="badge {risk_badge_class}">{risk_icon} Risk: {risk_level}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Recommended Action Card
    if parsed["action"]:
        st.markdown(
            """
            <div class="content-box">
                <div class="content-box-title">🎯 Recommended Action</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(parsed["action"])
    else:
        # Fallback to direct markdown
        st.markdown(latest["advice"])

    # Why & Evidence Cards
    if parsed["past_evidence"] and parsed["inference"]:
        col_ev, col_inf = st.columns(2)
        with col_ev:
            st.markdown(
                """
                <div class="content-box">
                    <div class="content-box-title">📜 Past Evidence</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(parsed["past_evidence"])
        with col_inf:
            st.markdown(
                """
                <div class="content-box">
                    <div class="content-box-title">🧠 AI Inference</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(parsed["inference"])
    elif parsed["why_full"]:
        st.markdown(
            """
            <div class="content-box">
                <div class="content-box-title">💡 Why & Context</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(parsed["why_full"])

    # Recalled Hindsight Memories Display
    if latest["memories"]:
        st.markdown(
            f"""
            <div style="margin-top: 1rem; margin-bottom: 0.5rem;">
                <div style="font-size: 0.85rem; font-weight: 600; color: #a5b4fc; display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.5rem;">
                    <span>🔍 Hindsight Memories Recalled ({len(latest['memories'])})</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for memory in latest["memories"]:
            st.markdown(
                f'<div class="memory-item"><strong>Precedent:</strong> {memory}</div>',
                unsafe_allow_html=True,
            )
    elif not latest["baseline"]:
        st.info("Hindsight found no relevant team history for this release.")

    # Full Raw Response Accordion for transparency
    with st.expander("Inspect Complete Raw LLM Response"):
        st.markdown(latest["advice"])

    st.markdown("</div>", unsafe_allow_html=True)


    # SECTION 3: TEACH PATCHPILOT (Continuous Learning Stage)
    st.markdown(
        """
        <div class="saas-card">
            <div class="card-header">
                <div>
                    <h3 class="card-title">🔄 Teach PatchPilot What Happened</h3>
                    <div class="card-subtitle">
                        Record the deployment outcome back into Hindsight to complete the feedback loop for future releases.
                    </div>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("outcome_form"):
        col_dec, col_out = st.columns(2)
        with col_dec:
            decision = st.selectbox(
                "What did the engineer decide?",
                ["Followed the advice", "Overrode the advice"],
                key=f"decision_{latest['run_id']}",
            )
        with col_out:
            outcome = st.selectbox(
                "What happened after deployment?",
                ["Not deployed yet", "Succeeded", "Failed or rolled back"],
                key=f"outcome_{latest['run_id']}",
            )
        saved = st.form_submit_button("Save this experience to memory", use_container_width=True)

    if saved:
        if outcome == "Not deployed yet":
            st.info("No outcome saved. Choose an outcome after deployment to add this experience to memory.")
        else:
            experience = (
                f"Deployment experience for {latest['service']}: "
                f"{latest['release']} "
                f"Recommendation: {latest['advice']} "
                f"Engineer decision: {decision}. "
                f"Deployment outcome: {outcome}."
            )

            memory_client = make_hindsight_client()
            try:
                memory_client.retain(bank_id=bank_id, content=experience)
                st.success("Saved. PatchPilot can recall this experience next time.")
            except Exception as error:
                st.error(f"Could not save this experience: {error}")
            finally:
                memory_client.close()

    st.markdown("</div>", unsafe_allow_html=True)
