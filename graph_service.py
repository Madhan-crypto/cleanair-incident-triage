import os
import json
import math
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize Gemini model
gemini_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3
)

# Define the state schema
class IncidentState(TypedDict):
    incident_id: str
    gps_coordinates: dict  # {"latitude": float, "longitude": float}
    raw_media_url: str
    is_anomaly: bool
    pollution_type: str
    dispatch_status: str


def triage_node(state: IncidentState) -> IncidentState:
    """
    Validates if the image shows real pollution using Gemini 1.5 Flash.
    Returns updated state with is_anomaly and pollution_type.
    """
    print(f"[TRIAGE NODE] Processing incident: {state['incident_id']}")
    
    # Construct prompt for Gemini
    triage_prompt = f"""
    Analyze the following image URL for pollution indicators.
    Image URL: {state['raw_media_url']}
    
    Determine if this image shows:
    1. Real pollution (smoke, dust, haze, industrial emissions, vehicle exhaust, etc.)
    2. NOT a meme, clear sky, or unrelated content
    
    Respond with JSON format:
    {{
        "is_real_pollution": boolean,
        "pollution_type": "string or null",
        "confidence": 0-1,
        "reasoning": "brief explanation"
    }}
    """
    
    try:
        response = gemini_model.invoke([HumanMessage(content=triage_prompt)])
        response_text = response.content
        
        # Parse JSON from response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            triage_result = json.loads(json_str)
        else:
            # Fallback if JSON parsing fails
            triage_result = {
                "is_real_pollution": False,
                "pollution_type": None,
                "confidence": 0.0,
                "reasoning": "Failed to parse response"
            }
        
        state["is_anomaly"] = triage_result.get("is_real_pollution", False)
        state["pollution_type"] = triage_result.get("pollution_type", "unknown")
        
        print(f"[TRIAGE NODE] Anomaly detected: {state['is_anomaly']}, Type: {state['pollution_type']}")
        
    except Exception as e:
        print(f"[TRIAGE NODE] Error during triage: {str(e)}")
        state["is_anomaly"] = False
        state["pollution_type"] = "error"
    
    return state


def spatial_analysis_node(state: IncidentState) -> IncidentState:
    """
    Performs spatial analysis including dummy predictive drift calculation.
    Updates dispatch_status based on proximity analysis.
    """
    print(f"[SPATIAL ANALYSIS NODE] Analyzing coordinates: {state['gps_coordinates']}")
    
    # Dummy predictive drift calculation
    # In production, this would integrate with weather APIs and atmospheric models
    lat = state["gps_coordinates"].get("latitude", 0)
    lon = state["gps_coordinates"].get("longitude", 0)
    
    # Calculate dummy drift vector based on pollution type
    pollution_type = state.get("pollution_type", "unknown").lower()
    
    if "industrial" in pollution_type or "smoke" in pollution_type:
        drift_magnitude = 2.5  # km
        drift_direction = 45  # degrees (northeast)
    elif "dust" in pollution_type or "haze" in pollution_type:
        drift_magnitude = 1.8  # km
        drift_direction = 270  # degrees (west)
    else:
        drift_magnitude = 1.0  # km
        drift_direction = 0  # degrees (north)
    
    # Calculate estimated affected area radius (km)
    radius_km = 5.0 + (drift_magnitude * 0.5)
    
    # Dummy proximity check to nearest dispatch center
    # In production, this would query a geospatial database
    nearest_dispatch_distance_km = 2.3
    estimated_response_time_min = int(nearest_dispatch_distance_km * 2.5)
    
    state["dispatch_status"] = (
        f"ANALYSIS_COMPLETE | "
        f"Drift: {drift_magnitude}km @ {drift_direction}° | "
        f"Affected radius: {radius_km}km | "
        f"Nearest dispatch: {nearest_dispatch_distance_km}km | "
        f"ETA: {estimated_response_time_min} min"
    )
    
    print(f"[SPATIAL ANALYSIS NODE] {state['dispatch_status']}")
    
    return state


def dispatch_node(state: IncidentState) -> IncidentState:
    """
    Formats a field crew alert with all incident details.
    """
    print(f"[DISPATCH NODE] Formatting alert for incident: {state['incident_id']}")
    
    alert_payload = {
        "alert_type": "POLLUTION_INCIDENT",
        "incident_id": state["incident_id"],
        "severity": "HIGH" if state["is_anomaly"] else "LOW",
        "pollution_type": state["pollution_type"],
        "location": {
            "latitude": state["gps_coordinates"].get("latitude"),
            "longitude": state["gps_coordinates"].get("longitude"),
            "google_maps_url": f"https://maps.google.com/?q={state['gps_coordinates'].get('latitude')},{state['gps_coordinates'].get('longitude')}"
        },
        "media_evidence": state["raw_media_url"],
        "spatial_analysis": state["dispatch_status"],
        "dispatch_action": "SEND_CREW" if state["is_anomaly"] else "ARCHIVE_REPORT",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }
    
    state["dispatch_status"] = json.dumps(alert_payload, indent=2)
    
    print(f"[DISPATCH NODE] Alert ready for crew dispatch")
    
    return state


def conditional_router(state: IncidentState) -> Literal["spatial_analysis_node", END]:
    """
    Routes to END if is_anomaly is True (false positive), otherwise continues to spatial analysis.
    """
    if state["is_anomaly"]:
        print(f"[ROUTER] Real pollution detected. Routing to SPATIAL_ANALYSIS")
        return "spatial_analysis_node"
    else:
        print(f"[ROUTER] No pollution detected. Routing to END")
        return END


# Build the LangGraph StateGraph
def create_incident_graph():
    """
    Constructs the incident triage workflow graph.
    """
    graph = StateGraph(IncidentState)
    
    # Add nodes
    graph.add_node("triage_node", triage_node)
    graph.add_node("spatial_analysis_node", spatial_analysis_node)
    graph.add_node("dispatch_node", dispatch_node)
    
    # Set entry point
    graph.set_entry_point("triage_node")
    
    # Add conditional edge from triage_node
    graph.add_conditional_edges(
        "triage_node",
        conditional_router
    )
    
    # Add regular edges
    graph.add_edge("spatial_analysis_node", "dispatch_node")
    graph.add_edge("dispatch_node", END)
    
    return graph.compile()


# Initialize compiled graph
incident_workflow = create_incident_graph()