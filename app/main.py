from __future__ import annotations

from datetime import date

import streamlit as st

import sys
import os

# FIX: Add root directory to Python path (pmo_assistant lives here)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pmo_assistant.agents import governance_agent, orchestrator, portfolio_agent, staffing_agent, template_agent
from pmo_assistant.agents.staffing_agent import StaffingRequest
from pmo_assistant.agents.template_agent import TemplateRequest, TemplateType
from pmo_assistant.data_loader import build_employee_summaries, load_talent_pool


st.set_page_config(page_title="PMO Assistant", layout="wide")


def staffing_page() -> None:
    st.header("Staffing Assistant")
    st.write("Find best-fit resources from the talent pool for a project.")

    # Build a dropdown of distinct roles from the talent pool for convenience.
    # Fallback: if the Role column is missing or empty, we keep a free-text input.
    roles = []
    try:
        df_roles = load_talent_pool()
        if "Role" in df_roles.columns:
            roles = sorted({str(r).strip() for r in df_roles["Role"].dropna() if str(r).strip()})
    except Exception:
        roles = []

    with st.form("staffing_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            if roles:
                role_options = ["Any"] + roles
                role = st.selectbox("Role", role_options)
                if role == "Any":
                    role = ""
            else:
                role = st.text_input("Role (e.g. Data Engineer, PM)")
            core_skill = st.text_input("Core Skill / Domain (e.g. Qlik, Databricks)")
        with col2:
            location = st.text_input("Preferred Location (city / region / remote)")
            primary_skills = st.text_input("Primary Skills (comma-separated)")
        with col3:
            min_exp = st.number_input("Minimum Experience (years)", min_value=0.0, max_value=40.0, value=0.0, step=0.5)
            min_bench = st.slider("Minimum Bench %", min_value=0.0, max_value=1.0, value=0.5, step=0.05)

        submitted = st.form_submit_button("Suggest Candidates")

    if submitted:
        req = StaffingRequest(
            role=role or None,
            core_skill=core_skill or None,
            location=location or None,
            primary_skills=primary_skills or None,
            min_experience_years=min_exp if min_exp > 0 else None,
            min_bench_pct=min_bench,
        )
        suggestions = staffing_agent.suggest_candidates(req=req, top_n=20)

        if not suggestions:
            st.warning("No candidates found with the given filters. Try relaxing some criteria.")
            return

        data = [
            {
                "Emp ID": s.emp_id,
                "Name": s.name,
                "Role": s.role,
                "Core Skill": s.core_skill,
                "Location": s.location,
                "Bench %": s.bench_pct,
                "Status": s.status,
                "Fit Score": round(s.score, 3),
                "Comments": s.comments,
            }
            for s in suggestions
        ]
        st.subheader("Suggested Candidates")
        # Older Streamlit versions do not support use_container_width argument
        st.dataframe(data)


def template_page() -> None:
    st.header("Document / Template Assistant")
    st.write("Generate BRD, TDD, MoM, Weekly Status, RCA, Completion Certificate and more.")

    template_map = {
        "Business Requirement Document (BRD)": "BRD",
        "Technical Design Document (TDD)": "TDD",
        "Minutes of Meeting (MoM)": "MoM",
        "Weekly Status Deck (text draft)": "WeeklyStatus",
        "Project Plan – high level summary": "ProjectPlanSummary",
        "Root Cause Analysis (RCA) narrative": "RCA",
        "Project Completion Certificate": "CompletionCertificate",
    }

    choice_label = st.selectbox("Template Type", list(template_map.keys()))
    template_type_str = template_map[choice_label]
    template_type: TemplateType = template_type_str  # type: ignore[assignment]

    st.markdown("#### Provide context for this artefact")
    with st.form("template_form"):
        project_name = st.text_input("Project Name")
        customer_name = st.text_input("Customer / Client Name")
        business_goal = st.text_area("Business Goal / Problem Statement")
        scope = st.text_area("Scope (and optionally out-of-scope)")
        risks = st.text_area("Key Risks / Dependencies (optional)")
        stakeholders = st.text_area("Key Stakeholders (optional)")
        tech_stack = st.text_area("High-level Technology / Platform (optional)")
        additional_notes = st.text_area("Any additional notes (optional)")

        submitted = st.form_submit_button("Generate Draft Document")

    if submitted:
        context = {
            "Project Name": project_name,
            "Customer Name": customer_name,
            "Business Goal": business_goal,
            "Scope": scope,
            "Risks and Dependencies": risks,
            "Stakeholders": stakeholders,
            "Tech Stack": tech_stack,
            "Additional Notes": additional_notes,
        }
        req = TemplateRequest(template_type=template_type, context=context)
        draft = template_agent.generate_document(req)

        st.subheader("Draft Document")
        st.write(draft)
        st.download_button(
            "Download as .txt",
            data=draft.encode("utf-8"),
            file_name=f"{template_type_str}_draft.txt",
            mime="text/plain",
        )


def portfolio_page() -> None:
    st.header("Portfolio & KPI Assistant")
    st.write("Ask questions about CSAT, utilization, allocations, and portfolio trends.")

    question = st.text_area(
        "Question",
        value="Summarize key portfolio highlights for the last year using CSAT, utilization and allocations.",
        height=120,
    )

    if st.button("Answer"):
        answer = portfolio_agent.answer_portfolio_question(question)
        st.subheader("Answer")
        st.write(answer)


def governance_page() -> None:
    st.header("Governance & Artefacts")
    st.write("See which artefacts are expected per phase, and use the Document Assistant to generate them.")

    phase = st.selectbox("Project Phase", ["Initiation", "Planning", "Execution", "Closure"])
    items = governance_agent.get_checklist_for_phase(phase=phase)  # type: ignore[arg-type]

    rows = [
        {
            "Artefact": item.artefact,
            "Mandatory": "Yes" if item.mandatory else "Optional",
            "Description": item.description,
        }
        for item in items
    ]
    st.subheader(f"Expected Artefacts for {phase}")
    # Older Streamlit versions do not support use_container_width argument
    st.dataframe(rows)

    st.info("Use the Document / Template Assistant tab to generate drafts for any missing artefacts.")


def chat_page() -> None:
    st.header("Chat – Agentic PMO Assistant")
    st.write("Ask anything; the orchestrator will route your query to the right agent.")

    user_query = st.text_area("Your question", height=150)
    if st.button("Ask"):
        if not user_query.strip():
            st.warning("Please type a question.")
            return
        result = orchestrator.handle_query(user_query)
        st.subheader(f"Routed to: {result.agent}")
        st.write(result.payload)


def main() -> None:
    st.sidebar.title("PMO Assistant")
    page = st.sidebar.radio(
        "Select mode",
        ["Staffing", "Documents", "Portfolio / KPIs", "Governance", "Chat (Agentic)"],
    )

    if page == "Staffing":
        staffing_page()
    elif page == "Documents":
        template_page()
    elif page == "Portfolio / KPIs":
        portfolio_page()
    elif page == "Governance":
        governance_page()
    else:
        chat_page()


if __name__ == "__main__":
    main()

