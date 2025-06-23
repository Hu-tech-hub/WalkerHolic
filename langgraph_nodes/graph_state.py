"""
GraphState definition for LangGraph-based gait analysis pipeline
"""
from typing import TypedDict, Optional, List, Dict, Any, Annotated
from datetime import datetime
from pathlib import Path
import uuid
import operator

class GraphState(TypedDict):
    """
    State object that flows between LangGraph nodes
    Contains all data needed for the gait analysis pipeline
    """
    # Session Management
    session_id: Optional[str]
    timestamp: Optional[str]
    stage: Optional[str]
    
    # Input Parameters
    user_id: Optional[str]  # User identifier
    date: Optional[str]  # Format: "YYYY-MM-DD" (optional, defaults to current date)
    height_cm: Optional[float]
    gender: Optional[str]  # male, female, other
    
    # SQL and Data Processing
    sql: Optional[str]
    raw_csv_path: Optional[str]
    filtered_csv_path: Optional[str]
    labels_csv_path: Optional[str]
    
    # AI Model Results
    stride_results: Optional[List[Dict[str, Any]]]
    
    # Calculated Metrics
    gait_metrics: Optional[Dict[str, float]]
    metrics_record_id: Optional[int]
    metrics_stored: Optional[bool]
    
    # 2-Stage RAG System Fields
    rag_query_stage1: Optional[str]  # Stage 1: Individual indicator analysis query
    rag_query_stage2_template: Optional[str]  # Stage 2: Overall assessment template
    patient_info: Optional[Dict[str, Any]]  # Patient information for RAG
    metrics_data: Optional[Dict[str, float]]  # Formatted metrics for RAG
    stage1_indicators: Optional[List[Dict[str, Any]]]  # Stage 1 analysis results
    stage1_response: Optional[str]  # Raw Stage 1 LLM response
    stage1_source_info: Optional[List[Dict[str, Any]]]  # Stage 1 retrieved documents info
    diagnosis_result: Optional[Dict[str, Any]]  # Final combined diagnosis result
    rag_diagnosis_completed: Optional[bool]  # RAG diagnosis completion flag
    
    # Legacy Diagnosis Fields (for backward compatibility)
    prompt_str: Optional[str]
    medical_diagnosis: Optional[str]
    medical_diagnosis_metadata: Optional[Dict[str, Any]]
    diagnosis_record_id: Optional[int]
    diagnosis_stored: Optional[bool]
    
    # Final Output
    response: Optional[Dict[str, Any]]
    final_response: Optional[Dict[str, Any]]  # Alternative final response field
    
    # Error Handling
    error: Optional[str]
    error_type: Optional[str]
    
    # Metadata
    processing_time: Optional[float]
    iterations: Optional[int]

class StateManager:
    """Utility class for managing GraphState operations"""
    
    @staticmethod
    def create_initial_state(user_id: str, height_cm: float, gender: str, date: str = None) -> GraphState:
        """Create initial GraphState from request parameters"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
            
        return GraphState(
            session_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            stage="initialized",
            user_id=user_id,
            date=date,
            height_cm=height_cm,
            gender=gender,
            sql=None,
            raw_csv_path=None,
            filtered_csv_path=None,
            labels_csv_path=None,
            stride_results=None,
            gait_metrics=None,
            metrics_record_id=None,
            metrics_stored=None,
            rag_query_stage1=None,
            rag_query_stage2_template=None,
            patient_info=None,
            metrics_data=None,
            stage1_indicators=None,
            stage1_response=None,
            stage1_source_info=None,
            diagnosis_result=None,
            rag_diagnosis_completed=None,
            prompt_str=None,
            medical_diagnosis=None,
            medical_diagnosis_metadata=None,
            diagnosis_record_id=None,
            diagnosis_stored=None,
            response=None,
            final_response=None,
            error=None,
            error_type=None,
            processing_time=0.0,
            iterations=0
        )
    
    @staticmethod
    def update_stage(state: GraphState, stage: str) -> GraphState:
        """Update the current processing stage"""
        state["stage"] = stage
        state["iterations"] = (state.get("iterations", 0) or 0) + 1
        return state
    
    @staticmethod
    def set_error(state: GraphState, error: str, error_type: str = "general") -> GraphState:
        """Set error information in state"""
        state["error"] = error
        state["error_type"] = error_type
        state["stage"] = "error"
        return state
    
    @staticmethod
    def is_error_state(state: GraphState) -> bool:
        """Check if state contains an error"""
        return bool(state.get("error"))
    
    @staticmethod
    def cleanup_temp_files(state: GraphState) -> None:
        """Clean up temporary files created during processing"""
        temp_paths = [
            state.get("raw_csv_path"),
            state.get("filtered_csv_path"), 
            state.get("labels_csv_path")
        ]
        
        for path_str in temp_paths:
            if path_str:
                try:
                    path = Path(path_str)
                    if path.exists():
                        path.unlink()
                except Exception:
                    pass  # Ignore cleanup errors

class PipelineStages:
    """Constants for pipeline stage names"""
    
    # Main Pipeline Stages
    RECEIVE_REQUEST = "receive_request"
    BUILD_QUERY = "build_query"
    FETCH_CSV = "fetch_csv"
    FILTER_DATA = "filter_data"
    PREDICT_PHASES = "predict_phases"
    PREDICT_STRIDE = "predict_stride"
    CALC_METRICS = "calc_metrics"
    STORE_METRICS = "store_metrics"
    COMPOSE_PROMPT = "compose_prompt"
    RAG_DIAGNOSIS = "rag_diagnosis"
    STORE_DIAGNOSIS = "store_diagnosis"
    FORMAT_RESPONSE = "format_response"
    
    # Special Stages
    NO_DATA_HANDLER = "no_data_handler"
    ERROR_HANDLER = "error_handler"
    END = "END"
    
    @classmethod
    def get_all_stages(cls) -> List[str]:
        """Get list of all pipeline stages"""
        return [
            cls.RECEIVE_REQUEST,
            cls.BUILD_QUERY,
            cls.FETCH_CSV,
            cls.FILTER_DATA,
            cls.PREDICT_PHASES,
            cls.PREDICT_STRIDE,
            cls.CALC_METRICS,
            cls.STORE_METRICS,
            cls.COMPOSE_PROMPT,
            cls.RAG_DIAGNOSIS,
            cls.STORE_DIAGNOSIS,
            cls.FORMAT_RESPONSE,
            cls.NO_DATA_HANDLER,
            cls.ERROR_HANDLER,
            cls.END
        ] 