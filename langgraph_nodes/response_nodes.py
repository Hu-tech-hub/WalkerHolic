"""
Response formatting nodes for LangGraph-based gait analysis pipeline
Contains FormatResponseNode for final output formatting and cleanup
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

import os
from dotenv import load_dotenv

from .base_node import BaseNode
from .graph_state import GraphState, StateManager, PipelineStages

# Load environment variables
load_dotenv()

class FormatResponseNode(BaseNode):
    """
    Node 12: Format final response JSON and cleanup temporary files
    Optimized for 2-Stage RAG diagnosis_result structure
    """
    
    def __init__(self):
        super().__init__(PipelineStages.FORMAT_RESPONSE)
    
    def execute(self, state: GraphState) -> GraphState:
        """Format final response JSON using diagnosis_result directly"""
        
        # Check for new simplified structure
        if "diagnosis_result" not in state:
            return StateManager.set_error(state, "Missing diagnosis_result from RAG analysis", "validation_error")
        
        diagnosis_result = state["diagnosis_result"]
        session_id = state.get("session_id", "unknown")
        processing_time = state.get("processing_time", 0)
        
        try:
            print("🔄 2-Stage RAG diagnosis_result 기반 응답 포맷팅...")
            
            # Use diagnosis_result directly (already in perfect format from 2-Stage RAG)
            response_json = diagnosis_result.copy()
            
            # Ensure required fields for API compatibility
            if "userId" not in response_json:
                response_json["userId"] = state.get("user_id", "unknown")
            if "analyzedAt" not in response_json:
                response_json["analyzedAt"] = datetime.now().isoformat()
            
            # Validate and normalize diseases probability format
            diseases = response_json.get("diseases", [])
            if diseases:
                for disease in diseases:
                    if "probability" in disease:
                        prob = disease["probability"]
                        # Ensure probability is in 0.0-1.0 range (not percentage)
                        if prob > 1.0:
                            disease["probability"] = prob / 100.0
                        # Ensure required fields exist
                        if "trend" not in disease:
                            disease["trend"] = "stable"
            
            # Add comprehensive metadata
            response_json["metadata"] = {
                "session_id": session_id,
                "processing_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": round(processing_time, 2),
                "pipeline_version": "5.0.0",  # 2-Stage RAG version
                "api_version": "v5",
                "rag_system": {
                    "stage1_completed": state.get("stage1_indicators") is not None,
                    "stage2_completed": "detailedReport" in diagnosis_result,
                    "indicators_count": len(diagnosis_result.get("indicators", [])),
                    "diseases_count": len(diseases)
                },
                "system_info": {
                    "analysis_date": state.get("date"),
                    "patient_height_cm": state.get("height_cm"),
                    "patient_gender": state.get("gender"),
                    "metrics_record_id": state.get("metrics_record_id"),
                    "diagnosis_record_id": state.get("diagnosis_record_id")
                }
            }
            
            # Cleanup temporary files
            cleanup_summary = self._cleanup_temp_files(session_id)
            response_json["metadata"]["cleanup_summary"] = cleanup_summary
            
            # Update state with formatted response
            state["response"] = response_json
            state["final_response"] = response_json  # For backward compatibility
            
            # Success logging
            indicators_count = len(response_json.get("indicators", []))
            score = response_json.get("score", "N/A")
            diseases_count = len(diseases)
            
            print(f"✅ 2-Stage RAG 응답 포맷팅 완료!")
            print(f"   📊 Stage 1 지표: {indicators_count}개")
            print(f"   📈 Stage 2 점수: {score}")
            print(f"   🦠 질병 평가: {diseases_count}개")
            print(f"   📄 응답 크기: {len(json.dumps(response_json, ensure_ascii=False)):,} 문자")
            
            return state
            
        except Exception as e:
            error_msg = f"Response formatting failed: {str(e)}"
            print(f"❌ 응답 포맷팅 실패: {error_msg}")
            return StateManager.set_error(state, error_msg, "formatting_error")
    
    def _cleanup_temp_files(self, session_id: str) -> Dict[str, Any]:
        """Clean up temporary files for this session"""
        temp_dir = Path(os.getenv('TEMP_DIR', './temp_files'))
        cleanup_summary = {
            "files_deleted": 0,
            "files_failed": 0,
            "deleted_files": [],
            "failed_files": []
        }
        
        if not temp_dir.exists():
            return cleanup_summary
        
        # Find and delete files containing session ID
        for file_path in temp_dir.glob("*"):
            if file_path.is_file() and session_id in file_path.name:
                try:
                    file_path.unlink()
                    cleanup_summary["files_deleted"] += 1
                    cleanup_summary["deleted_files"].append(file_path.name)
                    self.logger.debug(f"Deleted temp file: {file_path.name}")
                except Exception as e:
                    cleanup_summary["files_failed"] += 1
                    cleanup_summary["failed_files"].append({
                        "file": file_path.name,
                        "error": str(e)
                    })
                    self.logger.warning(f"Failed to delete {file_path.name}: {e}")
        
        self.logger.info(f"Cleanup complete: {cleanup_summary['files_deleted']} files deleted, {cleanup_summary['files_failed']} failed")
        
        return cleanup_summary


class ErrorHandlerNode(BaseNode):
    """
    Helper node for handling errors and creating error responses
    """
    
    def __init__(self):
        super().__init__("error_handler")
    
    def get_system_prompt(self) -> str:
        return """You are an error handling specialist for medical gait analysis systems.
        
        Your task is to create informative, professional error responses that:
        - Explain what went wrong in non-technical terms
        - Suggest possible solutions or next steps
        - Maintain patient confidence while being transparent about issues
        - Include appropriate contact information for support
        
        Always prioritize patient safety and clear communication.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Handle errors and create appropriate error response"""
        
        error_message = state.get("error", "Unknown error occurred")
        error_type = state.get("error_type", "general_error")
        session_id = state.get("session_id", "unknown")
        
        # Create LLM prompt for error formatting
        llm_prompt = self.create_llm_prompt(
            state,
            f"""
            Create a professional error response for a gait analysis system failure.
            
            Error Details:
            - Error Type: {error_type}
            - Error Message: {error_message}
            - Session ID: {session_id}
            
            Create a JSON response that includes:
            1. Clear explanation of what happened
            2. Suggested next steps for the user
            3. Technical details for support (if needed)
            4. Contact information or escalation path
            5. Session information for tracking
            
            Keep the tone professional and reassuring while being honest about the issue.
            
            Return only JSON format.
            """
        )
        
        try:
            error_response = self.invoke_llm(llm_prompt)
            
            # Try to parse as JSON
            try:
                response_json = json.loads(error_response)
            except json.JSONDecodeError:
                # Fallback error response
                response_json = {
                    "status": "error",
                    "error_type": error_type,
                    "message": "An error occurred during gait analysis processing",
                    "details": error_message,
                    "session_id": session_id,
                    "next_steps": [
                        "Please try again with the same data",
                        "Contact support if the issue persists",
                        "Ensure input data meets system requirements"
                    ],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Cleanup temp files even in error case
            cleanup_summary = self._cleanup_temp_files(session_id)
            response_json["cleanup_summary"] = cleanup_summary
            
            state["response"] = response_json
            
            self.logger.info(f"Error response created for {error_type}: {session_id}")
            
            return state
            
        except Exception as e:
            # Last resort error response
            state["response"] = {
                "status": "critical_error",
                "message": "Critical system error occurred",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "support_contact": "system_administrator"
            }
            
            self.logger.error(f"Critical error in error handler: {e}")
            return state
    
    def _cleanup_temp_files(self, session_id: str) -> Dict[str, Any]:
        """Clean up temporary files (same as FormatResponseNode)"""
        temp_dir = Path(os.getenv('TEMP_DIR', './temp_files'))
        cleanup_summary = {"files_deleted": 0, "files_failed": 0}
        
        if not temp_dir.exists():
            return cleanup_summary
        
        for file_path in temp_dir.glob("*"):
            if file_path.is_file() and session_id in file_path.name:
                try:
                    file_path.unlink()
                    cleanup_summary["files_deleted"] += 1
                except Exception:
                    cleanup_summary["files_failed"] += 1
        
        return cleanup_summary


class NoDataHandlerNode(BaseNode):
    """
    Helper node for handling cases with no data available
    """
    
    def __init__(self):
        super().__init__("no_data_handler")
    
    def get_system_prompt(self) -> str:
        return """You are a data availability specialist for medical gait analysis systems.
        
        Your task is to create informative responses when no data is available for analysis.
        
        Explain what data is needed, how to obtain it, and alternative options.
        Maintain a helpful and professional tone while guiding users toward successful analysis.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Handle no data scenarios"""
        
        session_id = state.get("session_id", "unknown")
        date = state.get("date")
        
        response_json = {
            "status": "no_data",
            "message": "No gait analysis data available for the specified criteria",
            "session_id": session_id,
            "requested_date": date,
            "suggestions": [
                "Verify the date format (YYYY-MM-DD)",
                "Check if data exists for this date",
                "Try a different date within the available range",
                "Contact data provider to ensure data upload"
            ],
            "available_options": [
                "Query available dates",
                "Upload new data",
                "Use sample data for demonstration"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        state["response"] = response_json
        
        self.logger.info(f"No data response created for date {date}: {session_id}")
        
        return state 