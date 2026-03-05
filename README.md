# Clara Automation Pipeline – Demo → Agent → Onboarding Update

## Overview

This project implements an automated pipeline that converts **customer conversations into structured AI voice agents**.

The system processes two stages of the Clara customer lifecycle:

1. **Demo Call → Preliminary Agent (v1)**
2. **Onboarding Call → Agent Updates (v2)**

The pipeline converts unstructured conversation transcripts into:

* Structured **Account Memo JSON**
* **Retell Agent Draft Specification**
* **Versioned configuration (v1 → v2)**
* **Changelog of updates**

All automation runs locally using **n8n workflows and a local LLM (Ollama)** with zero cost.

The goal is to simulate the real Clara onboarding process where messy conversations are transformed into structured operational rules and production-ready AI agents.

---

# Architecture

The system is built around **two workflows**:

```
Demo Call Workflow (Pipeline A)
Demo Transcript → Structured Memo → Agent Spec v1

Onboarding Workflow (Pipeline B)
Onboarding Transcript → Patch Extraction → Memo v2 → Agent Spec v2 → Changelog
```

Both workflows run inside **n8n**, which acts as the orchestration engine.

Key technologies:

* **n8n** – workflow orchestration
* **JavaScript Code Nodes** – extraction and transformation logic
* **Ollama (local LLM)** – structured information extraction
* **Local file storage** – versioned account artifacts

The system intentionally runs **fully locally** to satisfy the zero-cost constraint.

---

# Repository Structure

```
clara-automation/

dataset/
   demo_calls/
   onboarding_calls/

outputs/
   accounts/
      <account_id>/
         v1/
            memo.json
            agent_spec.json
         v2/
            memo.json
            agent_spec.json
         changes.json

workflows/
   demo_pipeline.json
   onboarding_pipeline.json

scripts/
   (python utilities used only for testing)

README.md
```

The **scripts directory is not required for the workflow execution**.
Those Python scripts were used only for **local testing and debugging during development**.

The actual automation logic lives entirely inside the **n8n JavaScript workflows** because this integrates natively with n8n and avoids external runtime dependencies.

---

# Pipeline A – Demo Call → Preliminary Agent

This workflow processes demo transcripts and generates the **initial Clara agent configuration**.

## Workflow Structure

```
Manual Trigger
      ↓
Ollama Extraction
      ↓
Validation Layer
      ↓
Memo Generation
      ↓
Agent Specification Generation
```

---

## Step 1 – Ollama Extraction

The first step sends the transcript to a **local LLM (Ollama)**.

The model extracts structured configuration data such as:

* company name
* services supported
* emergency definitions
* routing rules
* integration constraints

The output is expected to be **strict JSON** matching the account memo schema.

Reasoning:

Customer conversations are inherently unstructured.
Using a local LLM allows the system to convert conversational language into **structured operational configuration**.

---

## Step 2 – Validation Layer

Initially, the workflow directly parsed LLM output.
However, this approach created two problems:

1. **Hallucinated values**
2. **Invalid JSON responses**

To solve this, a **validation layer was introduced**.

The validation node:

* extracts the JSON block from the LLM response
* enforces the required schema
* replaces missing values with `null`
* generates `questions_or_unknowns` entries for missing data

Example:

Instead of guessing business hours, the system outputs:

```
business_hours: null
questions_or_unknowns:
  - "business hours not specified in transcript"
```

This prevents hallucination and aligns with the assignment requirement:

> Avoid inventing configuration details.

---

## Step 3 – Memo Generation

After validation, the workflow generates the **Account Memo JSON**.

The memo represents the **structured operational configuration of the client account**.

Example fields:

```
account_id
company_name
business_hours
services_supported
emergency_definition
routing_rules
integration_constraints
questions_or_unknowns
notes
```

This memo becomes the **single source of truth** for agent configuration.

The file is stored at:

```
outputs/accounts/<account_id>/v1/memo.json
```

---

## Step 4 – Agent Specification Generation

The final step generates a **Retell Agent Draft Specification**.

This includes:

* agent name
* voice style
* system prompt
* call flow rules
* transfer protocol
* fallback protocol

The generated prompt includes two operational flows:

### Business Hours Flow

```
greet caller
ask purpose
collect name and phone
route or transfer
fallback if transfer fails
confirm next steps
ask if anything else
close call
```

### After Hours Flow

```
greet caller
ask purpose
determine emergency
if emergency collect name phone address
attempt transfer
fallback if transfer fails
collect non-emergency details
close call
```

This file is stored at:

```
outputs/accounts/<account_id>/v1/agent_spec.json
```

---

# Pipeline B – Onboarding Call → Agent Update

The onboarding workflow updates the agent configuration once the client confirms operational details.

Unlike demo calls, onboarding conversations contain **precise configuration rules**.

---

## Workflow Structure

```
Manual Trigger
      ↓
Extract Onboarding Patch
      ↓
Patch Validation
      ↓
Merge With v1 Memo
      ↓
Generate Agent Spec v2
      ↓
Generate Changelog
```

---

## Step 1 – Extract Onboarding Patch

Instead of generating a full configuration again, this step extracts **only the updated fields**.

Example patch:

```
business_hours
emergency_definition
call_transfer_rules
integration_constraints
```

This avoids accidentally overwriting previously extracted fields.

---

## Step 2 – Patch Validation

The patch is validated to ensure that:

* only allowed fields are updated
* invalid or hallucinated fields are removed
* patch structure matches expected schema

This ensures that onboarding updates remain **controlled and predictable**.

---

## Step 3 – Merge With v1 Memo

The validated patch is merged with the existing configuration.

```
v1 memo + onboarding patch → v2 memo
```

The result is stored as:

```
outputs/accounts/<account_id>/v2/memo.json
```

This step ensures that onboarding **refines the configuration instead of replacing it**.

---

## Step 4 – Generate Agent Specification v2

Using the updated memo, the system regenerates the agent configuration.

The new specification includes updated business rules, routing logic, and emergency handling.

Stored at:

```
outputs/accounts/<account_id>/v2/agent_spec.json
```

---

## Step 5 – Changelog Generation

The system compares the previous and updated configurations.

Any differences are recorded in a changelog.

Example:

```
[
  {
    "field": "business_hours",
    "previous": null,
    "updated": {
      "days": ["Mon","Tue","Wed","Thu","Fri"],
      "start": "07:00",
      "end": "18:00"
    }
  }
]
```

Stored at:

```
outputs/accounts/<account_id>/changes.json   (here it trasnscript)
```

This provides clear traceability for configuration updates.

---

# Versioning Strategy

Each account maintains a versioned configuration.

```
v1 → created from demo call
v2 → updated from onboarding call
```

The versioned structure allows the system to:

* track configuration changes
* prevent accidental overwrites
* audit configuration evolution

---

# Design Decisions

## JavaScript Workflows

All workflow logic is implemented using **JavaScript Code nodes in n8n**.

Reason:

* n8n executes JavaScript natively
* avoids dependency management
* simplifies reproducibility
* easier workflow export

Python scripts were used only for testing during development.

---

## Validation Layer

The validation stage was added after observing common LLM issues:

* hallucinated values
* incomplete JSON
* incorrect assumptions

The validation layer ensures:

* schema enforcement
* missing data detection
* safe configuration generation

This significantly improves reliability.

---

## Patch-Based Updates

Instead of rewriting the full configuration during onboarding, the system uses **patch updates**.

Benefits:

* preserves demo insights
* avoids data loss
* enables precise changelog generation

This mirrors how production configuration systems handle updates.

---

# Key Strengths of the System

* Fully automated pipeline
* Zero-cost architecture
* Clear versioning
* Robust validation
* No hallucinated configuration
* Transparent change tracking

The system is designed to resemble a **small internal automation platform** rather than a simple script.

---

# Running the Workflows

1. Start n8n locally.
2. Import workflows from the `/workflows` folder.
3. Place transcripts inside:

```
dataset/demo_calls/
dataset/onboarding_calls/
```

4. Execute the workflows.

Outputs will be written to:

```
outputs/accounts/
```

---

# Future Improvements

With production access, the following improvements would be implemented:

* automated batch ingestion
* database storage (Supabase)
* dashboard for configuration review
* automatic Retell API integration
* structured onboarding form ingestion

---

# Conclusion

This system demonstrates how conversational data can be reliably converted into structured operational configuration and AI voice agents.

The architecture prioritizes:

* automation
* reliability
* traceability
* zero-cost execution

while maintaining a workflow structure that is reproducible and easy to extend.

