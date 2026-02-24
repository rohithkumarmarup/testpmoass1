from __future__ import annotations

from typing import Dict, List

import pandas as pd

from ..data_loader import (
    load_csat_data,
    load_resource_allocation_master,
    load_resource_utilization_master,
)
from ..llm import get_llm


def _build_portfolio_snapshot() -> Dict[str, pd.DataFrame]:
    """
    Build a small snapshot dict of key portfolio tables that we can show
    and feed into the LLM for narrative summaries.
    """
    return {
        "allocations": load_resource_allocation_master().head(200),
        "utilization": load_resource_utilization_master().head(200),
        "csat": load_csat_data().head(200),
    }


def answer_portfolio_question(question: str) -> str:
    """
    Simple Portfolio & KPI Agent.
    - Extracts a small slice of relevant tables.
    - Asks the LLM to reason about them and produce a narrative answer.
    """
    llm = get_llm()
    snapshot = _build_portfolio_snapshot()

    # Convert small dataframes to CSV strings for compactness
    tables_text = []
    for name, df in snapshot.items():
        tables_text.append(f"=== TABLE: {name} (first 200 rows max) ===")
        tables_text.append(df.to_csv(index=False))
    tables_block = "\n".join(tables_text)

    system_prompt = (
        "You are a portfolio and KPI analyst for a PMO.\n"
        "You receive small slices of internal data tables (allocations, utilization, CSAT).\n"
        "You must:\n"
        "- Answer the user's question as well as possible from the data.\n"
        "- When data is insufficient, say so explicitly and answer qualitatively.\n"
        "- Keep answers concise and focused on PMO decision-making.\n"
    )

    user_content = (
        "DATA SNAPSHOT (CSV-style tables):\n"
        "---------------------------------\n"
        f"{tables_block}\n\n"
        "QUESTION:\n"
        f"{question}\n\n"
        "Please provide:\n"
        "- 2–4 bullet points answering the question.\n"
        "- Call out any assumptions or data gaps.\n"
    )

    return llm.complete(system_prompt=system_prompt, user_content=user_content, temperature=0.1)

