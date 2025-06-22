"""
Error handling nodes for LangGraph-based gait analysis pipeline
"""
from typing import Dict, Any
from .base_node import BaseNode
from .graph_state import GraphState, StateManager, PipelineStages

class ErrorHandlerNode(BaseNode):
    """
    Handles errors that occur during pipeline execution
    Generates structured error response and ends the graph
    """
    
    def __init__(self):
        super().__init__(PipelineStages.ERROR_HANDLER)
    
    def get_system_prompt(self) -> str:
        return """You are an error handling specialist for the gait analysis pipeline.
        
        Your task is to analyze the error that occurred and create a comprehensive error response 
        that will be helpful for debugging and user feedback.
        
        Format the error information in a clear, structured way and provide appropriate 
        error codes and messages for the client application.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Process error state and create error response"""
        
        # Check if error response already exists
        if state.get("response") and not state.get("response", {}).get("success", True):
            self.logger.info("Error response already exists, skipping error handler")
            return state
        
        error_message = state.get("error", "Unknown error occurred")
        error_type = state.get("error_type", "general")
        session_id = state.get("session_id", "unknown")
        stage = state.get("stage", "unknown")
        
        try:
            # Create structured error response without LLM
            error_code_map = {
                "validation_error": "ERR_VALIDATION",
                "file_not_found_error": "ERR_FILE_NOT_FOUND", 
                "data_format_error": "ERR_DATA_FORMAT",
                "phase_prediction_error": "ERR_PHASE_PREDICTION",
                "stride_inference_error": "ERR_STRIDE_INFERENCE",
                "metrics_calculation_error": "ERR_METRICS_CALC",
                "storage_error": "ERR_STORAGE",
                "insufficient_data_error": "ERR_INSUFFICIENT_DATA",
                "general": "ERR_GENERAL"
            }
            
            user_message_map = {
                "validation_error": "Input validation failed. Please check your parameters.",
                "file_not_found_error": "Required data file not found.",
                "data_format_error": "Data format is invalid or corrupted.",
                "phase_prediction_error": "Gait phase prediction failed.",
                "stride_inference_error": "Stride analysis failed.",
                "metrics_calculation_error": "Gait metrics calculation failed.",
                "storage_error": "Failed to save analysis results.",
                "insufficient_data_error": "Insufficient data for reliable analysis.",
                "general": "An error occurred during processing."
            }
            
            action_map = {
                "validation_error": ["Check input parameters", "Verify data format"],
                "file_not_found_error": ["Verify file paths", "Check data availability"],
                "data_format_error": ["Check data file format", "Ensure IMU data is valid"],
                "phase_prediction_error": ["Check sensor data quality", "Try different time period"],
                "stride_inference_error": ["Verify gait phase data", "Check subject height"],
                "metrics_calculation_error": ["Check stride predictions", "Verify calculation inputs"],
                "storage_error": ["Check database connection", "Verify permissions"],
                "insufficient_data_error": ["Collect more walking data", "Use longer time period"],
                "general": ["Contact support", "Check system logs"]
            }
            
            error_analysis = {
                "error_code": error_code_map.get(error_type, "ERR_UNKNOWN"),
                "error_message": user_message_map.get(error_type, "An unknown error occurred"),
                "technical_details": error_message,
                "suggested_actions": action_map.get(error_type, ["Contact support"]),
                "session_info": {
                    "session_id": session_id,
                    "failed_stage": stage,
                    "timestamp": state.get("timestamp")
                }
            }
            
        except Exception as e:
            # Fallback error response
            self.logger.error(f"Error in error handler: {str(e)}")
            error_analysis = {
                "error_code": "ERR_SYSTEM",
                "error_message": "System error occurred during processing",
                "technical_details": f"Original error: {error_message}, Handler error: {str(e)}",
                "suggested_actions": ["Contact system administrator"],
                "session_info": {
                    "session_id": session_id,
                    "failed_stage": stage,
                    "timestamp": state.get("timestamp")
                }
            }
        
        # Clean up any temporary files
        StateManager.cleanup_temp_files(state)
        
        # Set final response
        state["response"] = {
            "success": False,
            "error": error_analysis,
            "processing_time": state.get("processing_time", 0.0)
        }
        
        self.logger.info(f"Error handled for session {session_id}: {error_analysis['error_code']}")
        
        return state

class NoDataHandlerNode(BaseNode):
    """
    Handles cases where no data is found for the requested date
    Creates appropriate response for data unavailability
    """
    
    def __init__(self):
        super().__init__(PipelineStages.NO_DATA_HANDLER)
    
    def get_system_prompt(self) -> str:
        return """You are a data availability specialist for the gait analysis pipeline.
        
        Your task is to handle cases where no IMU sensor data is available for the requested date
        and create an informative response for the user.
        
        Provide helpful information about data availability and suggest alternative actions.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Handle no data scenario"""
        
        # Check if response already exists
        if state.get("response"):
            self.logger.info("Response already exists, skipping no data handler")
            return state
        
        requested_date = state.get("date", "unknown")
        session_id = state.get("session_id", "unknown")
        
        try:
            # Create structured no data response without LLM
            user_id = state.get("user_id", "unknown")
            
            no_data_response = {
                "status": "no_data",
                "message": f"No gait analysis data available for user ID: {user_id}",
                "requested_user_id": user_id,
                "suggestions": [
                    "Check if the user ID is correct",
                    "Verify that walking data has been uploaded for this user",
                    "Try a different user ID",
                    "Contact administrator about data availability"
                ],
                "available_data": "Please check available user data in Storage"
            }
            
        except Exception as e:
            self.logger.error(f"Error in no data handler: {str(e)}")
            no_data_response = {
                "status": "no_data",
                "message": f"No data available for user: {user_id}",
                "requested_user_id": user_id,
                "suggestions": ["Try a different user ID"],
                "available_data": None
            }
        
        # Clean up any temporary files
        StateManager.cleanup_temp_files(state)
        
        # Set final response
        state["response"] = {
            "success": False,
            "data": no_data_response,
            "processing_time": state.get("processing_time", 0.0)
        }
        
        self.logger.info(f"No data response generated for session {session_id}, date {requested_date}")
        
        return state

def should_go_to_error_handler(state: GraphState) -> str:
    """
    Conditional routing function for LangGraph
    Determines if execution should go to error handler
    """
    if StateManager.is_error_state(state):
        return PipelineStages.ERROR_HANDLER
    return "continue"

def should_go_to_no_data_handler(state: GraphState) -> str:
    """
    Conditional routing function for LangGraph
    Determines if execution should go to no data handler
    """
    # Check if CSV fetch resulted in no data
    raw_csv_path = state.get("raw_csv_path")
    if not raw_csv_path:
        return PipelineStages.NO_DATA_HANDLER
    
    # Additional check for empty CSV files could be added here
    return "continue" 