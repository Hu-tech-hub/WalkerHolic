"""
AI model nodes for LangGraph-based gait analysis pipeline
Implements 2 nodes: predict_phases, predict_stride
"""
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

import os
from pathlib import Path
from dotenv import load_dotenv

from stage2_predictor import Stage2Predictor
from stride_inference_pipeline import StrideInferencePipeline

from .base_node import BaseNode
from .graph_state import GraphState, StateManager, PipelineStages

# Load environment variables
load_dotenv()

class PredictPhasesNode(BaseNode):
    """
    Node 5: Predict gait phases using Stage-2 model
    Uses existing Stage2Predictor from workflow
    """
    
    def __init__(self):
        super().__init__(PipelineStages.PREDICT_PHASES)
        # Initialize Stage2 predictor
        self.stage2_predictor = Stage2Predictor()
    
    def get_system_prompt(self) -> str:
        return """You are a gait phase analysis specialist using deep learning models.
        
        Your task is to analyze filtered IMU sensor data and predict gait phases:
        - non_gait: Not walking periods
        - double_support: Both feet on ground
        - single_support_left: Left foot stance phase
        - single_support_right: Right foot stance phase
        
        The Stage-2 model will output support labels with start/end frame numbers
        for each phase segment, which are crucial for subsequent stride analysis.
        
        Validate the model predictions and ensure output format consistency.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Predict gait phases using Stage-2 model"""
        
        if not self.validate_state_requirements(state, ["filtered_csv_path"]):
            return StateManager.set_error(state, "Missing required field: filtered_csv_path", "validation_error")
        
        filtered_csv_path = state["filtered_csv_path"]
        session_id = state.get("session_id", "unknown")
        
        # Verify input file exists
        if not Path(filtered_csv_path).exists():
            return StateManager.set_error(state, f"Filtered CSV file not found: {filtered_csv_path}", "file_not_found_error")
        
        try:
            # Validate input data format without LLM
            try:
                df_filtered = pd.read_csv(filtered_csv_path)
                if len(df_filtered) < 30:  # Minimum 1 second of data at 30Hz
                    return StateManager.set_error(state, "Insufficient data for phase prediction (< 1 second)", "phase_data_error")
                    
                # Check required IMU columns
                required_columns = ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
                missing_columns = [col for col in required_columns if col not in df_filtered.columns]
                if missing_columns:
                    return StateManager.set_error(state, f"Missing IMU columns: {missing_columns}", "phase_format_error")
                    
            except Exception as e:
                return StateManager.set_error(state, f"Cannot validate input data: {str(e)}", "phase_data_error")
            
            # Generate support labels filename
            filtered_path = Path(filtered_csv_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            labels_filename = f"support_labels_{filtered_path.stem}_{timestamp}.csv"
            temp_dir = Path(os.getenv('TEMP_DIR', './temp_files'))
            labels_path = temp_dir / labels_filename
            
            # Run Stage-2 prediction
            output_file = self.stage2_predictor.process_single_file(filtered_csv_path, str(labels_path))
            
            if not Path(output_file).exists():
                return StateManager.set_error(state, "Stage-2 phase prediction failed - no output file generated", "phase_prediction_error")
            
            # Verify support labels file has data
            try:
                df_labels = pd.read_csv(output_file)
                if len(df_labels) == 0:
                    return StateManager.set_error(state, "Support labels file is empty", "phase_output_error")
                
                # Validate required columns
                required_columns = ['phase', 'start_frame', 'end_frame']
                missing_columns = [col for col in required_columns if col not in df_labels.columns]
                
                if missing_columns:
                    return StateManager.set_error(state, f"Missing columns in support labels: {missing_columns}", "phase_format_error")
                
            except Exception as e:
                return StateManager.set_error(state, f"Cannot read support labels file: {str(e)}", "file_read_error")
            
            # Update state
            state["labels_csv_path"] = output_file
            
            self.logger.info(f"Gait phase prediction completed: {len(df_labels)} segments in {output_file}")
            
            return state
            
        except Exception as e:
            error_msg = f"Gait phase prediction failed: {str(e)}"
            self.logger.error(error_msg)
            return StateManager.set_error(state, error_msg, "phase_execution_error")

class PredictStrideNode(BaseNode):
    """
    Node 6: Predict stride metrics using StrideInferencePipeline
    Uses existing StrideInferencePipeline from workflow
    """
    
    def __init__(self):
        super().__init__(PipelineStages.PREDICT_STRIDE)
        # Initialize stride inference pipeline
        self.stride_pipeline = StrideInferencePipeline()
    
    def get_system_prompt(self) -> str:
        return """You are a stride analysis specialist using AI-powered biomechanical models.
        
        Your task is to analyze gait phase data and predict stride characteristics:
        - Stride length (meters)
        - Stride velocity (m/s) 
        - Stride time (seconds)
        - Foot identification (left/right)
        
        The StrideInferencePipeline uses the support labels to identify stride cycles
        and applies trained models to predict biomechanical parameters based on
        IMU sensor patterns and subject height.
        
        Validate predictions and ensure realistic biomechanical values.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Predict stride metrics using StrideInferencePipeline"""
        
        
        if not self.validate_state_requirements(state, ["labels_csv_path", "filtered_csv_path", "height_cm"]):
            return StateManager.set_error(state, "Missing required fields: labels_csv_path, filtered_csv_path, height_cm", "validation_error")
        
        labels_csv_path = state["labels_csv_path"]
        filtered_csv_path = state["filtered_csv_path"]
        height_cm = state["height_cm"]
        session_id = state.get("session_id", "unknown")
        
        # Verify input files exist
        if not Path(labels_csv_path).exists():
            return StateManager.set_error(state, f"Support labels file not found: {labels_csv_path}", "file_not_found_error")
        
        if not Path(filtered_csv_path).exists():
            return StateManager.set_error(state, f"Filtered CSV file not found: {filtered_csv_path}", "file_not_found_error")
        
        try:
            # Validate inputs without LLM
            if not (100 <= height_cm <= 250):
                return StateManager.set_error(state, f"Invalid height: {height_cm}cm (expected 100-250cm)", "stride_validation_error")
            
            # Check support labels format
            try:
                df_labels = pd.read_csv(labels_csv_path)
                if len(df_labels) == 0:
                    return StateManager.set_error(state, "Support labels file is empty", "stride_data_error")
                    
                required_label_columns = ['phase', 'start_frame', 'end_frame']
                missing_columns = [col for col in required_label_columns if col not in df_labels.columns]
                if missing_columns:
                    return StateManager.set_error(state, f"Missing columns in support labels: {missing_columns}", "stride_format_error")
                    
            except Exception as e:
                return StateManager.set_error(state, f"Cannot validate support labels: {str(e)}", "stride_data_error")
            
            # Set subject height in pipeline (temporary override for this session)
            # Use SA01 as default subject ID for pipeline compatibility
            original_height = self.stride_pipeline.subject_heights.get('SA01', 175)
            self.stride_pipeline.subject_heights['SA01'] = height_cm
            
            try:
                # Run stride inference
                results = self.stride_pipeline.run_inference(labels_csv_path, filtered_csv_path)
                
                # Check if results is None
                if results is None:
                    return StateManager.set_error(state, "Stride inference returned None", "stride_inference_error")
                
                if 'error' in results:
                    return StateManager.set_error(state, f"Stride inference failed: {results['error']}", "stride_inference_error")
                
                # Validate results structure
                if 'predictions' not in results or not results['predictions']:
                    return StateManager.set_error(state, "No stride predictions generated", "stride_output_error")
                
                # Validate prediction data
                predictions = results['predictions']
                total_cycles = results.get('total_cycles', 0)
                
                # Basic validation of prediction values
                for i, pred in enumerate(predictions):
                    # Check required fields
                    required_fields = ['predicted_stride_length', 'predicted_velocity', 'stride_time', 'foot']
                    missing_fields = [field for field in required_fields if field not in pred]
                    
                    if missing_fields:
                        return StateManager.set_error(state, f"Missing fields in prediction {i}: {missing_fields}", "stride_format_error")
                    
                    # Validate realistic ranges
                    stride_length = pred.get('predicted_stride_length', 0)
                    velocity = pred.get('predicted_velocity', 0)
                    stride_time = pred.get('stride_time', 0)
                    
                    if not (0.3 <= stride_length <= 3.0):  # Reasonable stride length range
                        self.logger.warning(f"Unusual stride length in prediction {i}: {stride_length}m")
                    
                    if not (0.2 <= velocity <= 5.0):  # Reasonable velocity range
                        self.logger.warning(f"Unusual velocity in prediction {i}: {velocity}m/s")
                    
                    if not (0.5 <= stride_time <= 3.0):  # Reasonable stride time range
                        self.logger.warning(f"Unusual stride time in prediction {i}: {stride_time}s")
                
                # Update state
                state["stride_results"] = results
                
                self.logger.info(f"Stride prediction completed: {total_cycles} cycles, {len(predictions)} predictions")
                
                return state
                
            finally:
                # Restore original height
                self.stride_pipeline.subject_heights['SA01'] = original_height
            
        except Exception as e:
            error_msg = f"Stride prediction failed: {str(e)}"
            self.logger.error(error_msg)
            return StateManager.set_error(state, error_msg, "stride_execution_error") 