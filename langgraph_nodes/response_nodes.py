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
    Integrates gait metrics, diagnosis, and metadata into final output
    """
    
    def __init__(self):
        super().__init__(PipelineStages.FORMAT_RESPONSE)
    
    def get_system_prompt(self) -> str:
        return """You are a medical report formatting specialist.
        
        Your task is to create a comprehensive, well-structured JSON response that combines:
        - Gait analysis metrics
        - Medical diagnosis from RAG system
        - Processing metadata
        - Quality indicators
        
        The response should be professional, clear, and suitable for healthcare providers.
        Structure the data logically with proper categorization and include confidence levels
        where applicable.
        
        Ensure all numerical values are properly formatted and clinical interpretations
        are clear and actionable.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Format final response JSON and cleanup temporary files"""
        
        required = ["gait_metrics", "medical_diagnosis", "medical_diagnosis_metadata", "session_id"]
        if not self.validate_state_requirements(state, required):
            return StateManager.set_error(state, f"Missing required fields for response formatting: {required}", "validation_error")
        
        gait_metrics = state["gait_metrics"]
        diagnosis_result = state["medical_diagnosis"]
        diagnosis_metadata = state["medical_diagnosis_metadata"]
        session_id = state["session_id"]
        date = state.get("date")
        height_cm = state.get("height_cm")
        processing_time = state.get("processing_time", 0)
        
        try:
            # Check if diagnosis is already in structured format
            if isinstance(diagnosis_result, dict) and diagnosis_result.get("success") is not None:
                # New structured JSON format - use as final response with enhancements
                response_json = self._enhance_structured_response(diagnosis_result, state)
            else:
                # Legacy format - convert to structured format
                response_json = self._create_fallback_response(state)
            
            # Add technical metadata
            response_json["metadata"] = response_json.get("metadata", {})
            response_json["metadata"].update({
                "session_id": session_id,
                "processing_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": round(processing_time, 2),
                "pipeline_version": "2.0.0",  # Updated version for new structured format
                "nodes_executed": state.get("iterations", 0),
                "api_version": "v2",
                "system_info": {
                    "analysis_date": date,
                    "patient_height_cm": height_cm,
                    "temp_files_processed": self._count_temp_files(session_id),
                    "metrics_record_id": state.get("metrics_record_id"),
                    "diagnosis_record_id": state.get("diagnosis_record_id")
                }
            })
            
            # Cleanup temporary files
            cleanup_summary = self._cleanup_temp_files(session_id)
            response_json["metadata"]["cleanup_summary"] = cleanup_summary
            
            # Update state with final response
            state["response"] = response_json
            state["final_response"] = response_json  # Alternative key for compatibility
            
            self.logger.info(f"Response formatted successfully: {len(json.dumps(response_json))} characters")
            
            return state
            
        except Exception as e:
            error_msg = f"Response formatting failed: {str(e)}"
            self.logger.error(error_msg)
            return StateManager.set_error(state, error_msg, "formatting_error")
    
    def _enhance_structured_response(self, diagnosis_result: dict, state: GraphState) -> dict:
        """Enhance the structured diagnosis response with additional metadata"""
        
        # Make a copy to avoid modifying the original
        enhanced_response = json.loads(json.dumps(diagnosis_result))
        
        # Add additional metadata to the response
        if "data" in enhanced_response:
            data = enhanced_response["data"]
            
            # Add session and processing info
            data["sessionId"] = state["session_id"]
            data["processingTime"] = state.get("processing_time", 0)
            
            # Add gait metrics summary for reference
            gait_metrics = state["gait_metrics"]
            data["rawMetrics"] = {
                "total_strides": gait_metrics.get("total_strides", 0),
                "analysis_duration": f"{gait_metrics.get('total_strides', 0) * gait_metrics.get('avg_stride_time', 1.0):.1f}s",
                "data_quality": self._assess_data_quality(gait_metrics)
            }
            
            # Enhance indicators with additional context
            if "indicators" in data:
                for indicator in data["indicators"]:
                    indicator["category"] = self._get_indicator_category(indicator["id"])
                    indicator["priority"] = self._get_indicator_priority(indicator["status"])
            
            # Add summary statistics
            data["summary"] = {
                "overall_assessment": data.get("status", "Unknown"),
                "risk_factors_count": self._count_risk_factors(data.get("indicators", [])),
                "normal_indicators_count": self._count_normal_indicators(data.get("indicators", [])),
                "recommendation_level": self._get_recommendation_level(data.get("riskLevel", "확인 필요"))
            }
        
        return enhanced_response
    
    def _create_fallback_response(self, state: GraphState) -> Dict[str, Any]:
        """Create a structured response for legacy diagnosis format"""
        
        gait_metrics = state["gait_metrics"]
        diagnosis_text = state["medical_diagnosis"]
        diagnosis_metadata = state["medical_diagnosis_metadata"]
        
        # Convert legacy text diagnosis to new structured format
        indicators = self._convert_metrics_to_indicators(gait_metrics)
        diseases = self._extract_diseases_from_text(diagnosis_text)
        
        # Calculate overall score based on indicators
        overall_score = self._calculate_fallback_score(indicators)
        status = self._get_status_from_score(overall_score)
        risk_level = self._get_risk_level_from_score(overall_score)
        
        return {
            "success": True,
            "data": {
                "indicators": indicators,
                "diseases": diseases,
                "score": overall_score,
                "status": status,
                "riskLevel": risk_level,
                "detailedReport": {
                    "summary": f"전체적인 보행 분석 결과는 {status}입니다.",
                    "keyFindings": self._extract_key_findings(gait_metrics),
                    "recommendations": [
                        "의료진과 상담하여 정확한 진단을 받으시기 바랍니다.",
                        "정기적인 보행 모니터링을 권장합니다.",
                        "운동 치료나 재활 프로그램을 고려해보세요."
                    ],
                    "technicalDetails": {
                        "rawDiagnosis": diagnosis_text,
                        "sourcesReferenced": diagnosis_metadata.get("retrieved_sources", 0),
                        "knowledgeBase": diagnosis_metadata.get("knowledge_base_used", "medical_pdfs")
                    }
                }
            }
        }
    
    def _convert_metrics_to_indicators(self, gait_metrics: dict) -> list:
        """Convert gait metrics to structured indicators format"""
        indicators = []
        
        # Stride time indicator
        avg_stride_time = gait_metrics.get("avg_stride_time", 1.0)
        stride_time_status = "정상" if 0.9 <= avg_stride_time <= 1.3 else "주의" if 0.7 <= avg_stride_time < 1.5 else "위험"
        indicators.append({
            "id": "stride-time",
            "name": "보행 주기",
            "value": f"{avg_stride_time:.2f}초",
            "status": stride_time_status,
            "description": "한 발의 접촉부터 다음 같은 발의 접촉까지의 시간"
        })
        
        # Double support indicator  
        double_support_time = gait_metrics.get("avg_double_support_time", 0.2)
        double_support_status = "정상" if double_support_time <= 0.25 else "주의" if double_support_time <= 0.35 else "위험"
        indicators.append({
            "id": "double-support",
            "name": "양발 지지기",
            "value": f"{double_support_time:.2f}초",
            "status": double_support_status,
            "description": "양발이 모두 지면에 접촉하는 시간"
        })
        
        # Stride difference indicator
        stride_asymmetry = gait_metrics.get("stride_length_asymmetry", 0)
        stride_diff_status = "정상" if stride_asymmetry < 5 else "주의" if stride_asymmetry < 10 else "위험"
        indicators.append({
            "id": "stride-difference", 
            "name": "보폭 차이",
            "value": f"{stride_asymmetry:.1f}%",
            "status": stride_diff_status,
            "description": "좌우 보폭의 비대칭성"
        })
        
        # Walking speed indicator
        walking_speed = gait_metrics.get("avg_walking_speed", 1.0)
        speed_status = "정상" if walking_speed >= 1.0 else "주의" if walking_speed >= 0.8 else "위험"
        indicators.append({
            "id": "walking-speed",
            "name": "보행 속도", 
            "value": f"{walking_speed:.2f}m/s",
            "status": speed_status,
            "description": "평균 보행 속도"
        })
        
        return indicators
    
    def _extract_diseases_from_text(self, diagnosis_text: str) -> list:
        """Extract disease probabilities from text diagnosis"""
        diseases = [
            {"name": "파킨슨병", "probability": 30},
            {"name": "뇌졸중", "probability": 25}
        ]
        
        if diagnosis_text:
            text_lower = diagnosis_text.lower()
            # Simple keyword-based probability adjustment
            if "파킨슨" in text_lower or "parkinson" in text_lower:
                diseases[0]["probability"] = 65
            if "뇌졸중" in text_lower or "stroke" in text_lower:
                diseases[1]["probability"] = 60
                
        return diseases
    
    def _calculate_fallback_score(self, indicators: list) -> int:
        """Calculate overall score from indicators"""
        normal_count = sum(1 for ind in indicators if ind["status"] == "정상")
        warning_count = sum(1 for ind in indicators if ind["status"] == "주의") 
        danger_count = sum(1 for ind in indicators if ind["status"] == "위험")
        
        # Score calculation: normal=100, warning=70, danger=40
        total_indicators = len(indicators)
        if total_indicators == 0:
            return 50
            
        score = (normal_count * 100 + warning_count * 70 + danger_count * 40) / total_indicators
        return int(score)
    
    def _get_status_from_score(self, score: int) -> str:
        """Get status from score"""
        if score >= 80:
            return "정상"
        elif score >= 60:
            return "주의 필요"
        else:
            return "위험"
    
    def _get_risk_level_from_score(self, score: int) -> str:
        """Get risk level from score"""
        if score >= 80:
            return "정상 단계"
        elif score >= 60:
            return "주의 단계"
        else:
            return "위험 단계"
    
    def _assess_data_quality(self, gait_metrics: dict) -> str:
        """Assess the quality of gait data"""
        total_strides = gait_metrics.get("total_strides", 0)
        
        if total_strides >= 20:
            return "High"
        elif total_strides >= 10:
            return "Medium"
        else:
            return "Low"
    
    def _get_indicator_category(self, indicator_id: str) -> str:
        """Get category for indicator"""
        categories = {
            "stride-time": "temporal",
            "double-support": "temporal", 
            "stride-difference": "spatial",
            "walking-speed": "kinematic"
        }
        return categories.get(indicator_id, "general")
    
    def _get_indicator_priority(self, status: str) -> str:
        """Get priority level for indicator status"""
        priorities = {
            "정상": "low",
            "주의": "medium",
            "위험": "high"
        }
        return priorities.get(status, "medium")
    
    def _count_risk_factors(self, indicators: list) -> int:
        """Count indicators with warning or danger status"""
        return sum(1 for ind in indicators if ind.get("status") in ["주의", "위험"])
    
    def _count_normal_indicators(self, indicators: list) -> int:
        """Count indicators with normal status"""
        return sum(1 for ind in indicators if ind.get("status") == "정상")
    
    def _get_recommendation_level(self, risk_level: str) -> str:
        """Get recommendation level based on risk level"""
        if "정상" in risk_level:
            return "routine"
        elif "주의" in risk_level:
            return "consultation"
        else:
            return "immediate"
    
    def _extract_key_findings(self, gait_metrics: Dict[str, Any]) -> list:
        """Extract key findings from gait metrics"""
        findings = []
        
        # Check walking speed
        speed = gait_metrics.get("avg_walking_speed")
        if speed and speed < 1.0:
            findings.append(f"Reduced walking speed: {speed:.2f} m/s")
        
        # Check stride length
        stride_length = gait_metrics.get("avg_stride_length")
        if stride_length and stride_length < 1.2:
            findings.append(f"Shortened stride length: {stride_length:.2f} m")
        
        # Check asymmetry
        asymmetry = gait_metrics.get("stride_length_asymmetry")
        if asymmetry and asymmetry > 5.0:
            findings.append(f"Gait asymmetry detected: {asymmetry:.1f}%")
        
        # Check variability
        variability = gait_metrics.get("stride_time_variability")
        if variability and variability > 10.0:
            findings.append(f"Increased gait variability: {variability:.1f}%")
        
        return findings if findings else ["Normal gait parameters within expected ranges"]
    
    def _count_temp_files(self, session_id: str) -> int:
        """Count temporary files for this session"""
        temp_dir = Path(os.getenv('TEMP_DIR', './temp_files'))
        if not temp_dir.exists():
            return 0
        
        # Count files containing session ID
        count = 0
        for file_path in temp_dir.glob("*"):
            if file_path.is_file() and session_id in file_path.name:
                count += 1
        
        return count
    
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