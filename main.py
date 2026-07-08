import os
import uuid
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from graph_service import incident_workflow, IncidentState

# Initialize FastAPI app
app = FastAPI(
    title="CleanAir Incident Triage API",
    description="Multi-agent AI workflow for pollution incident classification and dispatch",
    version="1.0.0"
)

# Request/Response Models
class PollutionReport(BaseModel):
    """Incoming citizen pollution report"""
    media_url: str = Field(..., description="URL to the pollution image")
    latitude: float = Field(..., description="GPS latitude coordinate")
    longitude: float = Field(..., description="GPS longitude coordinate")


class IncidentResponse(BaseModel):
    """API response payload"""
    incident_id: str
    status: str
    data: dict


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "service": "cleanair-incident-triage"}


@app.post("/webhook/report")
async def submit_pollution_report(report: PollutionReport) -> IncidentResponse:
    """
    Webhook endpoint to receive citizen pollution reports.
    
    Accepts a pollution report, initializes the LangGraph workflow,
    processes it asynchronously, and returns the triage result.
    """
    try:
        # Generate unique incident ID
        incident_id = f"INC-{uuid.uuid4().hex[:12].upper()}"
        
        print(f"\n[API] Received pollution report: {incident_id}")
        print(f"      Location: {report.latitude}, {report.longitude}")
        print(f"      Media: {report.media_url}")
        
        # Initialize incident state
        initial_state: IncidentState = {
            "incident_id": incident_id,
            "gps_coordinates": {
                "latitude": report.latitude,
                "longitude": report.longitude
            },
            "raw_media_url": report.media_url,
            "is_anomaly": False,
            "pollution_type": "pending",
            "dispatch_status": "QUEUED"
        }
        
        # Invoke the workflow asynchronously
        loop = asyncio.get_event_loop()
        final_state = await loop.run_in_executor(
            None,
            lambda: incident_workflow.invoke(initial_state)
        )
        
        print(f"[API] Workflow completed for {incident_id}")
        
        # Prepare response
        response_payload = {
            "incident_id": final_state["incident_id"],
            "is_anomaly": final_state["is_anomaly"],
            "pollution_type": final_state["pollution_type"],
            "gps_coordinates": final_state["gps_coordinates"],
            "dispatch_alert": final_state["dispatch_status"]
        }
        
        return IncidentResponse(
            incident_id=incident_id,
            status="completed",
            data=response_payload
        )
    
    except Exception as e:
        print(f"[API ERROR] {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Incident triage failed: {str(e)}"
        )


@app.post("/webhook/batch")
async def submit_batch_reports(reports: list[PollutionReport]):
    """
    Batch endpoint for multiple pollution reports.
    """
    results = []
    for report in reports:
        try:
            result = await submit_pollution_report(report)
            results.append(result)
        except HTTPException as e:
            results.append({
                "error": e.detail,
                "status": "failed"
            })
    
    return {"batch_size": len(reports), "results": results}


if __name__ == "__main__":
    import uvicorn
    
    # Read environment variables
    port = int(os.getenv("PORT", "8080"))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Run uvicorn server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )