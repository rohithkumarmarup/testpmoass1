## PMO Assistant – Streamlit App (Groq + Agentic System)

This project is a **PMO Assistant** web app that helps the PMO team with:

- **Smart staffing / allocation** – find best-fit candidates for new / existing projects.
- **Template & document generation** – BRD, TDD, MoM, Weekly Status, Project Plan, RCA, Completion Certificate, Handover decks.
- **Portfolio & KPI insights** – high-level summaries from CSAT, utilization, allocations.
- **Governance support** – phase-wise artefact checklist and auto-draft generation.

The app runs locally as a **Streamlit** web application and uses **Groq** as the LLM backend, plus **Hugging Face embeddings** for semantic search over your templates and docs.

---

### 1. Project structure

At the top level (inside `Pmoxponnet/`):

- `app/`
  - `main.py` – Streamlit entry-point.
- `pmo_assistant/`
  - `config.py` – paths & model configuration.
  - `llm.py` – Groq client wrapper.
  - `embeddings.py` – Hugging Face embeddings helper.
  - `data_loader.py` – logic to read Excel/Word/PPT files.
  - `agents/`
    - `orchestrator.py` – routes user requests to agents.
    - `staffing_agent.py` – talent / allocation suggestions.
    - `template_agent.py` – BRD/TDD/MoM/Status/etc. drafting.
    - `portfolio_agent.py` – basic portfolio & KPI Q&A.
    - `governance_agent.py` – artefact checklist & actions.
- `requirements.txt` – Python dependencies.
- `.env.example` – example for environment variables.

The existing `processed/` folder (CSV/TXT) was used only to understand your data; the **runtime app reads the original `.xlsx`, `.docx`, `.pptx`** files from this folder.

---

### 2. Setup

1. **Create and activate a virtual environment** (recommended):

   ```bash
   cd C:\Users\rohit\Downloads\Pmoxponnet
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set the Groq API key**:

   - Copy `.env.example` to `.env` and fill in your key, **or** set an environment variable:

   ```bash
   set GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
   ```

   The default production model used is:

   - `llama-3.3-70b-versatile`

   You can change this in `pmo_assistant/config.py`.

4. **Ensure the original PMO files are present** in this folder:

   - `Hackhathon_Pool Details.xlsx`
   - `Hackhathon_Resource Allocation in Projects.xlsx`
   - `Hackhathon_Resources Utilization_2025.xlsx`
   - `Hackhathon_Third Party Employees.xlsx`
   - `Hackhathon_Resourcing and Enablement.xlsx`
   - `CSAT - Customer ID and Name V1.0.xlsx`
   - `Dashboard Data Dictionary - (DDIT).xlsx`
   - `Projects - Root Cause Analysis (RCA) for Projects in RED or AMBER Status.xlsx`
   - `Project ID - Project Name - Project Plan_V1.0.xlsx`
   - `Test Cases - Project ID -Project Name V1.0.xlsx`
   - `Reference BRD.docx`
   - `Reference TDD.docx`
   - `MoM - Customer Name-Monthly-Bi Weekly-Weekly-Meeting Title-YYYYMMDD.docx`
   - `Template -Project ID - Project Name  - Weekly Status for Customer Name.pptx`
   - `Project_Completion_Certificate.docx`
   - `OppID - Opp Description - Proposal to Delivery Team Handover V1.0.pptx`

---

### 3. Running the app

From the project root:

```bash
streamlit run app/main.py
```

Then open the URL shown in the console (by default `http://localhost:8501`) in your browser.

---

### 4. High-level usage

- **Staffing Assistant tab**
  - Enter role, skills, location, dates, and other filters.
  - The app combines:
    - Talent pool
    - Project allocations
    - Utilization
    - Third-party resources
  - Returns a ranked list of suggested candidates with reasoning.

- **Document Assistant tab**
  - Choose document type: BRD, TDD, MoM, Weekly Status, Project Plan, RCA, Completion Certificate, Handover, Test Cases.
  - Answer a short Q&A form.
  - The app uses reference templates + your answers to draft the document in your PMO’s style.

- **Portfolio / KPI tab**
  - Ask portfolio questions (e.g. CSAT, utilization, project mix).
  - The app runs simple aggregations and lets the LLM produce a narrative summary.

- **Governance tab**
  - Select project phase and context.
  - Shows expected artefacts and can call the Document Assistant to generate missing drafts.

- **Chat (Agentic) tab**
  - Free-form PMO chat.
  - Orchestrator agent decides which specialist agent(s) to call and returns a combined answer.

---

### 5. Notes and assumptions

- Sheet names in Excel are resolved **fuzzily** (e.g. any sheet whose name contains “talent” and “pool” will be treated as the Talent Pool) to reduce manual configuration.
- Date handling and utilization overlap checks are implemented with reasonable defaults; you may refine the logic in `pmo_assistant/agents/staffing_agent.py` based on how PMO actually makes decisions.
- This is designed as a **hackathon-ready MVP**: the architecture is clean and modular so that you can later:
  - Swap models.
  - Move from local CSV/Excel to a database.
  - Enhance the agents with more tools or business rules.

