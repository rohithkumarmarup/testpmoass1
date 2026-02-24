from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

from ..llm import get_llm
from . import governance_agent, portfolio_agent, staffing_agent, template_agent
from .staffing_agent import StaffingRequest
from .template_agent import TemplateRequest, TemplateType


AgentName = Literal["STAFFING", "TEMPLATE", "PORTFOLIO", "GOVERNANCE"]


@dataclass
class OrchestratorResult:
    agent: AgentName
    payload: Any


def _route_with_llm(user_query: str) -> Dict[str, Any]:
    """
    Ask the LLM to decide which agent to call and with what high-level arguments.
    """
    llm = get_llm()
    system_prompt = (
        "You are a router for a PMO assistant system.\n"
        "Your job is to read the user's request and decide which specialist agent "
        "should handle it, and extract key arguments.\n"
        "Available agents:\n"
        "- STAFFING: For resource allocation, staffing, who is suitable for a project, availability, skills.\n"
        "- TEMPLATE: For generating or editing documents (BRD, TDD, MoM, Weekly Status, Project Plan, RCA, Completion Certificate).\n"
        "- PORTFOLIO: For questions about portfolio, CSAT, utilization, customers, projects.\n"
        "- GOVERNANCE: For questions about required artefacts, PMO checks, which documents are needed in which phase.\n\n"
        "Return ONLY a JSON object with these keys:\n"
        '{\n'
        '  "agent": "STAFFING | TEMPLATE | PORTFOLIO | GOVERNANCE",\n'
        '  "arguments": { ... free-form key/value pairs ... }\n'
        "}\n"
    )

    json_str = llm.complete(
        system_prompt=system_prompt,
        user_content=user_query,
        temperature=0.0,
        response_format="json",
    )

    try:
        return json.loads(json_str)
    except Exception:
        # Fallback: default to PORTFOLIO with raw question
        return {"agent": "PORTFOLIO", "arguments": {"question": user_query}}


def handle_query(user_query: str) -> OrchestratorResult:
    """
    Free-form entrypoint for the Chat tab.
    """
    routing = _route_with_llm(user_query)
    agent = routing.get("agent", "PORTFOLIO")
    args = routing.get("arguments", {}) or {}

    if agent == "STAFFING":
        req = StaffingRequest(
            role=args.get("role"),
            core_skill=args.get("core_skill"),
            location=args.get("location"),
            primary_skills=args.get("skills"),
        )
        suggestions = staffing_agent.suggest_candidates(req=req, top_n=10)
        payload = [s.__dict__ for s in suggestions]
        return OrchestratorResult(agent="STAFFING", payload=payload)

    if agent == "TEMPLATE":
        template_type_str: str = (args.get("template_type") or "BRD").upper()
        # Map a few common aliases
        alias_map = {
            "BRD": "BRD",
            "BUSINESS_REQUIREMENT_DOCUMENT": "BRD",
            "TDD": "TDD",
            "TECHNICAL_DESIGN_DOCUMENT": "TDD",
            "MOM": "MoM",
            "MINUTES_OF_MEETING": "MoM",
            "WEEKLY_STATUS": "WeeklyStatus",
            "STATUS_DECK": "WeeklyStatus",
            "COMPLETION_CERTIFICATE": "CompletionCertificate",
            "RCA": "RCA",
        }
        mapped = alias_map.get(template_type_str, "BRD")
        template_type: TemplateType = mapped  # type: ignore[assignment]
        context = args.get("context") or {"summary": user_query}
        req = TemplateRequest(template_type=template_type, context=context)
        text = template_agent.generate_document(req)
        return OrchestratorResult(agent="TEMPLATE", payload={"document": text})

    if agent == "GOVERNANCE":
        phase = args.get("phase") or "Initiation"
        items = governance_agent.get_checklist_for_phase(phase=phase)  # type: ignore[arg-type]
        payload = [item.__dict__ for item in items]
        return OrchestratorResult(agent="GOVERNANCE", payload=payload)

    # Default: portfolio
    question = args.get("question") or user_query
    answer = portfolio_agent.answer_portfolio_question(question)
    return OrchestratorResult(agent="PORTFOLIO", payload={"answer": answer})

