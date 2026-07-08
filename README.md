# CleanAir Autonomous Orchestrator

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)
![Google Cloud](https://img.shields.io/badge/GCP-Cloud_Run-4285F4.svg)

## 📌 Executive Summary

The **CleanAir Autonomous Orchestrator** is a decentralized, serverless platform designed to eliminate the friction of traditional civic reporting pipelines. By leveraging an **Event-Driven Architecture (EDA)**, the system intercepts crowdsourced spatiotemporal data (images and GPS telemetry) directly from ubiquitous messaging protocols (e.g., WhatsApp, Telegram).

Upon ingestion, the payload is asynchronously processed through a **Directed Acyclic Graph (DAG)** of autonomous AI agents. These nodes execute real-time multimodal inference to mitigate spoofing, calculate predictive environmental drift, and programmatically route verified anomalies to municipal field crews via structured dispatch protocols. 

---

## 🏗️ System Architecture & Agentic DAG

The core intelligence is orchestrated via `LangGraph`, managing stateful transitions across three primary cognitive nodes:

1. **Cognitive Triage Node (Anti-Spoofing):** Executes zero-shot multimodal inference via **Google Gemini 1.5 Flash**. It validates semantic consistency between visual landmarks and telemetry, discarding anomalous data, memes, or non-hazardous weather patterns.
2. **Spatiotemporal Fusion Node:** Processes verified payloads through a spatial routing algorithm to calculate localized predictive drift and proximity heuristics, establishing the blast radius and ETA of the pollution pocket.
3. **Infrastructure Dispatch Node:** A deterministic routing agent that synthesizes a structured JSON dispatch manifest for outbound webhooks, deploying rapid-response municipal crews.

---

## ⚙️ Technology Stack

* **API Gateway / Middleware:** FastAPI, Uvicorn (ASGI), Pydantic v2 (Strict Schema Validation)
* **Orchestration & State Management:** LangGraph, LangChain Core
* **Multimodal Cognition:** Google Gemini 1.5 Flash (via `langchain-google-genai`)
* **Deployment Infrastructure:** Docker, Google Cloud Run (Knative-based serverless edge compute)
* **Integration Layer:** Zapier Central / Agentic Webhooks

---

## 🚀 Local Deployment Setup

### 1. Environment Initialization
Ensure Python 3.10+ is installed, then initialize a sandboxed environment:

```bash
git clone [https://github.com/Madhan-crypto/cleanair-incident-triage.git](https://github.com/Madhan-crypto/cleanair-incident-triage.git)
cd cleanair-incident-triage
python -m venv venv

# Windows
venv\Scripts\activate
# Unix/macOS
source venv/bin/activate
