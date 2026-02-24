from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal

from ..data_loader import load_docx_text, load_pptx_text
from ..llm import get_llm


TemplateType = Literal[
    "BRD",
    "TDD",
    "MoM",
    "WeeklyStatus",
    "CompletionCertificate",
    "ProjectPlanSummary",
    "RCA",
]


@dataclass
class TemplateRequest:
    template_type: TemplateType
    context: Dict[str, str]  # answers from the UI form


def _build_system_prompt(template_type: TemplateType, reference_text: str) -> str:
    return (
        "You are a senior PMO documentation assistant.\n"
        "You write concise, well-structured project artefacts following the reference template and style.\n"
        "Use the user's answers to fill in the sections. Do not invent fake data; if something is unknown, "
        "leave a clear placeholder.\n\n"
        f"REFERENCE TEMPLATE FOR {template_type}:\n"
        "---------------------------------------\n"
        f"{reference_text}\n"
        "---------------------------------------\n"
    )


def generate_document(req: TemplateRequest) -> str:
    """
    Main entrypoint for Template / Document Agent.
    Returns a draft document as plain text (which the UI can present or download).
    """
    llm = get_llm()

    if req.template_type == "BRD":
        reference = load_docx_text("brd_reference")
    elif req.template_type == "TDD":
        reference = load_docx_text("tdd_reference")
    elif req.template_type == "MoM":
        reference = load_docx_text("mom_template")
    elif req.template_type == "WeeklyStatus":
        reference = load_pptx_text("weekly_status")
    elif req.template_type == "CompletionCertificate":
        reference = load_docx_text("completion_certificate")
    elif req.template_type == "ProjectPlanSummary":
        # For now reuse BRD style as high-level plan summary; could be extended to use the Excel plan structure
        reference = load_docx_text("brd_reference")
    elif req.template_type == "RCA":
        # Use MoM style (action log) as it is closest to RCA narratives
        reference = load_docx_text("mom_template")
    else:
        raise ValueError(f"Unsupported template type: {req.template_type}")

    system_prompt = _build_system_prompt(req.template_type, reference)

    # Turn context dict into a readable Q&A section
    qa_lines = []
    for key, value in req.context.items():
        qa_lines.append(f"{key}: {value}")
    qa_block = "\n".join(qa_lines)

    user_content = (
        f"Using the reference above, draft a complete {req.template_type}.\n\n"
        "USER INPUT / ANSWERS:\n"
        f"{qa_block}\n\n"
        "OUTPUT:\n"
        f"- A single, coherent {req.template_type} in plain text.\n"
    )

    return llm.complete(system_prompt=system_prompt, user_content=user_content, temperature=0.2)

