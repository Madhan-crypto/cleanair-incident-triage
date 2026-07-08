"""Minimal graph_service module used by the API.

This provides a lightweight, deterministic `IncidentWorkflow` implementation
that can be used for local development and testing. It intentionally avoids
external dependencies and simulates a simple triage flow.
"""
import time
from typing import TypedDict, Dict


class IncidentState(TypedDict, total=False):
    incident_id: str
    gps_coordinates: Dict[str, float]
    raw_media_url: str
    is_anomaly: bool
    pollution_type: str
    dispatch_status: str


class IncidentWorkflow:
    """A tiny, synchronous workflow simulator.

    The real project likely integrates LangGraph or other agents; this
    implementation provides a predictable, fast substitute so the API can
    be exercised locally and tests can import without errors.
    """

    def invoke(self, state: IncidentState) -> IncidentState:
        # Simulate some processing latency
        time.sleep(0.05)

        url = (state.get("raw_media_url") or "").lower()
        if "smoke" in url or "fire" in url:
            pollution = "smoke"
        elif "oil" in url or "slick" in url:
            pollution = "oil_spill"
        else:
            pollution = "unknown"

        state["pollution_type"] = pollution
        state["is_anomaly"] = pollution != "unknown"
        state["dispatch_status"] = "ALERT_SENT" if state["is_anomaly"] else "NO_ACTION"

        return state


incident_workflow = IncidentWorkflow()
