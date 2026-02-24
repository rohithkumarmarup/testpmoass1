from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal


ProjectPhase = Literal["Initiation", "Planning", "Execution", "Closure"]


@dataclass
class GovernanceChecklistItem:
    artefact: str
    mandatory: bool
    phase: ProjectPhase
    description: str


CHECKLIST: List[GovernanceChecklistItem] = [
    GovernanceChecklistItem(
        artefact="BRD",
        mandatory=True,
        phase="Initiation",
        description="Business Requirement Document capturing business problem, objectives, scope and stakeholders.",
    ),
    GovernanceChecklistItem(
        artefact="TDD",
        mandatory=True,
        phase="Planning",
        description="Technical Design Document aligned with BRD and platform guidelines.",
    ),
    GovernanceChecklistItem(
        artefact="Project Plan",
        mandatory=True,
        phase="Planning",
        description="Detailed plan including milestones, risks, assumptions, dependencies, estimation.",
    ),
    GovernanceChecklistItem(
        artefact="MoM – Kick-off",
        mandatory=True,
        phase="Initiation",
        description="Formal minutes of the project kick-off meeting.",
    ),
    GovernanceChecklistItem(
        artefact="Weekly Status Deck",
        mandatory=True,
        phase="Execution",
        description="Weekly status PPT shared with customer and internal stakeholders.",
    ),
    GovernanceChecklistItem(
        artefact="Test Cases",
        mandatory=True,
        phase="Execution",
        description="Test scenarios, test steps and results captured in test case workbook.",
    ),
    GovernanceChecklistItem(
        artefact="RCA for Red/Amber",
        mandatory=False,
        phase="Execution",
        description="Root Cause Analysis for any project that goes to RED or AMBER status.",
    ),
    GovernanceChecklistItem(
        artefact="Project Completion Certificate",
        mandatory=True,
        phase="Closure",
        description="Formal completion certificate signed off by the customer.",
    ),
    GovernanceChecklistItem(
        artefact="Proposal-to-Delivery Handover Deck",
        mandatory=True,
        phase="Initiation",
        description="Handover from presales/proposal team to delivery team.",
    ),
]


def get_checklist_for_phase(phase: ProjectPhase) -> List[GovernanceChecklistItem]:
    return [item for item in CHECKLIST if item.phase == phase]

