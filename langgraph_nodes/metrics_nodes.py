"""
Metrics calculation and storage nodes for LangGraph-based gait analysis pipeline
Implements 2 nodes: calc_metrics, store_metrics
"""
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

import os
from dotenv import load_dotenv

from .base_node import BaseNode
from .graph_state import GraphState, StateManager, PipelineStages

# Load environment variables
load_dotenv()

class CalcMetricsNode(BaseNode):
    """
    Node 7: Calculate 12 gait metrics from stride results
    Computes comprehensive biomechanical parameters
    """
    
    def __init__(self):
        super().__init__(PipelineStages.CALC_METRICS)
    
    def get_system_prompt(self) -> str:
        return """You are a biomechanical analysis specialist calculating gait metrics.
        
        Your task is to analyze stride prediction results and calculate 12 key gait parameters:
        
        Temporal metrics:
        1. Average stride time (seconds)
        2. Stride time variability (CV%)
        3. Cadence (steps/minute)
        
        Spatial metrics:
        4. Average stride length (meters)
        5. Stride length variability (CV%)
        6. Step width (estimated from IMU patterns)
        
        Velocity metrics:
        7. Average walking speed (m/s)
        8. Walking speed variability (CV%)
        
        Asymmetry metrics:
        9. Left-right stride time asymmetry (%)
        10. Left-right stride length asymmetry (%)
        
        Stability metrics:
        11. Gait regularity index
        12. Gait stability ratio
        
        Ensure all calculations are biomechanically sound and handle edge cases.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Calculate comprehensive gait metrics from stride results"""
        
        if not self.validate_state_requirements(state, ["stride_results"]):
            return StateManager.set_error(state, "Missing required field: stride_results", "validation_error")
        
        stride_results = state["stride_results"]
        session_id = state.get("session_id", "unknown")
        
        # Validate stride results structure
        if not isinstance(stride_results, dict) or 'predictions' not in stride_results:
            return StateManager.set_error(state, "Invalid stride_results format", "data_format_error")
        
        predictions = stride_results['predictions']
        if not predictions or len(predictions) == 0:
            return StateManager.set_error(state, "No stride predictions available for metrics calculation", "no_data_error")
        
        try:
            # Validate data without LLM
            if len(predictions) < 3:
                return StateManager.set_error(state, f"Insufficient stride data: {len(predictions)} cycles (minimum 3 required)", "insufficient_data_error")
            
            # Extract data arrays for calculations
            stride_lengths = []
            stride_times = []
            velocities = []
            left_strides = []
            right_strides = []
            
            for pred in predictions:
                try:
                    length = float(pred.get('predicted_stride_length', 0))
                    time_val = float(pred.get('stride_time', 0))
                    velocity = float(pred.get('predicted_velocity', 0))
                    foot = pred.get('foot', '').lower()
                    
                    # Basic validation
                    if 0.2 <= length <= 3.0 and 0.5 <= time_val <= 3.0 and 0.1 <= velocity <= 5.0:
                        stride_lengths.append(length)
                        stride_times.append(time_val)
                        velocities.append(velocity)
                        
                        # Separate by foot
                        stride_data = {
                            'length': length,
                            'time': time_val,
                            'velocity': velocity
                        }
                        
                        if 'left' in foot:
                            left_strides.append(stride_data)
                        elif 'right' in foot:
                            right_strides.append(stride_data)
                    
                except (ValueError, TypeError):
                    continue
            
            # Check minimum data requirement
            if len(stride_lengths) < 3:
                return StateManager.set_error(state, f"Insufficient valid stride data: {len(stride_lengths)} cycles (minimum 3 required)", "insufficient_data_error")
            
            # Calculate phase ratios from support labels if available
            phase_ratios = self._calculate_phase_ratios_from_support_labels(state, predictions)
            
            # Calculate 12 gait metrics
            gait_metrics = {}
            
            # Convert to numpy arrays for calculations
            stride_lengths = np.array(stride_lengths)
            stride_times = np.array(stride_times)
            velocities = np.array(velocities)
            
            # 1. Average stride time (seconds)
            gait_metrics['avg_stride_time'] = round(float(np.mean(stride_times)), 3)
            
            # 2. Stride time variability (CV%)
            gait_metrics['stride_time_cv'] = round(float((np.std(stride_times) / np.mean(stride_times)) * 100) if np.mean(stride_times) > 0 else 0.0, 2)
            
            # 3. Cadence (steps/minute) - steps = 2 * strides
            avg_stride_time = np.mean(stride_times)
            gait_metrics['cadence'] = round(float(120.0 / avg_stride_time) if avg_stride_time > 0 else 0.0, 1)
            
            # 4. Average stride length (meters)
            gait_metrics['avg_stride_length'] = round(float(np.mean(stride_lengths)), 3)
            
            # 5. Stride length variability (CV%)
            gait_metrics['stride_length_cv'] = round(float((np.std(stride_lengths) / np.mean(stride_lengths)) * 100) if np.mean(stride_lengths) > 0 else 0.0, 2)
            
            # 6. Step width (improved estimation based on stride variability)
            gait_metrics['step_width'] = round(float(0.1 + 0.05 * np.std(stride_lengths)), 3)
            
            # 7. Average walking speed (m/s)
            gait_metrics['avg_walking_speed'] = round(float(np.mean(velocities)), 3)
            
            # 8. Walking speed variability (CV%)
            gait_metrics['walking_speed_cv'] = round(float((np.std(velocities) / np.mean(velocities)) * 100) if np.mean(velocities) > 0 else 0.0, 2)
            
            # 9-10. Left-right asymmetry metrics
            if len(left_strides) >= 2 and len(right_strides) >= 2:
                left_times = [s['time'] for s in left_strides]
                right_times = [s['time'] for s in right_strides]
                left_lengths = [s['length'] for s in left_strides]
                right_lengths = [s['length'] for s in right_strides]
                
                # 9. Stride time asymmetry (%)
                left_avg_time = np.mean(left_times)
                right_avg_time = np.mean(right_times)
                gait_metrics['stride_time_asymmetry'] = round(float(abs(left_avg_time - right_avg_time) / ((left_avg_time + right_avg_time) / 2) * 100), 2)
                
                # 10. Stride length asymmetry (%)
                left_avg_length = np.mean(left_lengths)
                right_avg_length = np.mean(right_lengths)
                gait_metrics['stride_length_asymmetry'] = round(float(abs(left_avg_length - right_avg_length) / ((left_avg_length + right_avg_length) / 2) * 100), 2)
            else:
                gait_metrics['stride_time_asymmetry'] = 0.0
                gait_metrics['stride_length_asymmetry'] = 0.0
            
            # 11. Gait regularity index (improved)
            time_regularity = 1.0 - (np.std(stride_times) / np.mean(stride_times)) if np.mean(stride_times) > 0 else 0.0
            gait_metrics['gait_regularity_index'] = round(float(max(0.0, min(1.0, time_regularity))), 3)
            
            # 12. Gait stability ratio (improved)
            velocity_stability = 1.0 - (np.std(velocities) / np.mean(velocities)) if np.mean(velocities) > 0 else 0.0
            gait_metrics['gait_stability_ratio'] = round(float(max(0.0, min(1.0, velocity_stability))), 3)
            
            # 13-15. Phase ratio metrics from support labels
            gait_metrics.update(phase_ratios)
            
            # Add metadata
            gait_metrics['total_strides'] = len(stride_lengths)
            gait_metrics['left_strides'] = len(left_strides)
            gait_metrics['right_strides'] = len(right_strides)
            gait_metrics['calculation_timestamp'] = datetime.now().isoformat()
            
            # Update state
            state["gait_metrics"] = gait_metrics
            
            self.logger.info(f"Gait metrics calculated: {len(gait_metrics)} parameters from {len(stride_lengths)} strides")
            
            return state
            
        except Exception as e:
            error_msg = f"Gait metrics calculation failed: {str(e)}"
            self.logger.error(error_msg)
            return StateManager.set_error(state, error_msg, "metrics_calculation_error")
    
    def _calculate_phase_ratios_from_support_labels(self, state: GraphState, predictions: list) -> dict:
        """Calculate phase ratios from actual support labels data"""
        
        try:
            # Get support labels file path from state
            labels_csv_path = state.get("labels_csv_path")
            if not labels_csv_path or not Path(labels_csv_path).exists():
                self.logger.warning("Support labels file not found, using estimated ratios")
                return self._get_estimated_phase_ratios(state)
            
            # Read support labels
            df_labels = pd.read_csv(labels_csv_path)
            if len(df_labels) == 0:
                self.logger.warning("Support labels file is empty, using estimated ratios")
                return self._get_estimated_phase_ratios(state)
            
            stance_ratios = []
            swing_ratios = []
            double_support_ratios = []
            
            # Calculate ratios for each stride
            for pred in predictions:
                start_frame = pred.get('start_frame', 0)
                end_frame = pred.get('end_frame', 0)
                
                if start_frame >= end_frame:
                    continue
                
                # Find support labels within this stride range
                stride_labels = df_labels[
                    (df_labels['start_frame'] >= start_frame) & 
                    (df_labels['end_frame'] <= end_frame)
                ]
                
                if len(stride_labels) == 0:
                    continue
                
                # Calculate total frames in stride
                total_frames = end_frame - start_frame
                
                # Count frames for each phase
                double_support_frames = 0
                single_support_frames = 0
                non_gait_frames = 0
                
                for _, label_row in stride_labels.iterrows():
                    phase = label_row['phase']
                    label_start = max(label_row['start_frame'], start_frame)
                    label_end = min(label_row['end_frame'], end_frame)
                    frame_count = max(0, label_end - label_start)
                    
                    if phase == 'double_support':
                        double_support_frames += frame_count
                    elif phase in ['single_support_left', 'single_support_right']:
                        single_support_frames += frame_count
                    elif phase == 'non_gait':
                        non_gait_frames += frame_count
                
                # Calculate ratios for this stride
                if total_frames > 0:
                    stance_frames = double_support_frames + single_support_frames
                    swing_frames = total_frames - stance_frames - non_gait_frames
                    
                    stance_ratio = stance_frames / total_frames
                    swing_ratio = max(0.0, swing_frames / total_frames)
                    double_support_ratio = double_support_frames / total_frames
                    
                    # Ensure ratios are reasonable
                    stance_ratio = max(0.0, min(1.0, stance_ratio))
                    swing_ratio = max(0.0, min(1.0, swing_ratio))
                    double_support_ratio = max(0.0, min(1.0, double_support_ratio))
                    
                    stance_ratios.append(stance_ratio)
                    swing_ratios.append(swing_ratio)
                    double_support_ratios.append(double_support_ratio)
            
            # Calculate averages
            if stance_ratios:
                avg_stance = np.mean(stance_ratios)
                avg_swing = np.mean(swing_ratios)
                avg_double_support = np.mean(double_support_ratios)
                
                self.logger.info(f"Calculated phase ratios from {len(stance_ratios)} strides")
                
                return {
                    'stance_phase_ratio': round(float(avg_stance), 3),
                    'swing_phase_ratio': round(float(avg_swing), 3),
                    'double_support_ratio': round(float(avg_double_support), 3)
                }
            else:
                self.logger.warning("No valid stride phase data found, using estimated ratios")
                return self._get_estimated_phase_ratios(state)
                
        except Exception as e:
            self.logger.error(f"Error calculating phase ratios: {str(e)}")
            return self._get_estimated_phase_ratios(state)
    
    def _get_estimated_phase_ratios(self, state: GraphState) -> dict:
        """Fallback method to estimate phase ratios when support labels are unavailable"""
        
        gait_metrics = state.get("gait_metrics", {})
        
        # Use stride variability to estimate phase ratios
        stride_time_cv = gait_metrics.get('stride_time_cv', 3.0)
        
        # Higher variability suggests more instability, higher double support
        base_stance = 0.60  # Normal stance is ~60% of gait cycle
        base_swing = 0.40   # Normal swing is ~40% of gait cycle
        base_double_support = 0.20  # Normal double support is ~20% of gait cycle
        
        # Adjust based on variability
        variability_factor = min(0.1, stride_time_cv / 100.0)
        
        estimated_stance = base_stance + variability_factor
        estimated_swing = base_swing - variability_factor
        estimated_double_support = base_double_support + (variability_factor * 0.5)
        
        # Ensure values are within realistic bounds
        estimated_stance = max(0.4, min(0.8, estimated_stance))
        estimated_swing = max(0.2, min(0.6, estimated_swing))
        estimated_double_support = max(0.1, min(0.4, estimated_double_support))
        
        return {
            'stance_phase_ratio': round(estimated_stance, 3),
            'swing_phase_ratio': round(estimated_swing, 3),
            'double_support_ratio': round(estimated_double_support, 3)
        }

class StoreMetricsNode(BaseNode):
    """
    Node 8: Store calculated gait metrics to Supabase
    Saves comprehensive biomechanical analysis results
    """
    
    def __init__(self):
        super().__init__(PipelineStages.STORE_METRICS)
    
    def get_system_prompt(self) -> str:
        return """You are a data management specialist for gait analysis results.
        
        Your task is to store calculated gait metrics in the Supabase database:
        
        Storage requirements:
        - Store all 12 calculated gait metrics
        - Include session metadata (date, height, session_id)
        - Add calculation timestamp and data quality indicators
        - Ensure data integrity and proper formatting
        - Handle database connection errors gracefully
        
        Database schema validation:
        - Verify all required fields are present
        - Check data types and value ranges
        - Ensure foreign key relationships are maintained
        
        Provide confirmation of successful storage with record ID.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Store gait metrics to Supabase database"""
        
        if not self.validate_state_requirements(state, ["gait_metrics", "user_id", "height_cm"]):
            return StateManager.set_error(state, "Missing required fields: gait_metrics, user_id, height_cm", "validation_error")
        
        gait_metrics = state["gait_metrics"]
        user_id = state["user_id"]
        height_cm = state["height_cm"]
        gender = state.get("gender", "unknown")
        session_id = state.get("session_id", "unknown")
        
        # Use current date for analysis_date if not provided
        analysis_date = state.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        try:
            # Validate metrics data without LLM
            required_metrics = [
                'avg_stride_time', 'stride_time_cv', 'cadence',
                'avg_stride_length', 'stride_length_cv', 'step_width',
                'avg_walking_speed', 'walking_speed_cv',
                'stride_time_asymmetry', 'stride_length_asymmetry',
                'gait_regularity_index', 'gait_stability_ratio',
                'stance_phase_ratio', 'swing_phase_ratio', 'double_support_ratio'
            ]
            
            missing_metrics = [metric for metric in required_metrics if metric not in gait_metrics or gait_metrics[metric] is None]
            if missing_metrics:
                return StateManager.set_error(state, f"Missing required metrics: {missing_metrics}", "metrics_validation_error")
            
            # Import Supabase client
            from supabase import create_client
            
            # Initialize Supabase client with Service Role key for RLS bypass
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                raise ValueError("Supabase credentials not found in environment variables")
                
            supabase = create_client(supabase_url, supabase_key)
            
            # Prepare data for storage
            storage_data = {
                'session_id': session_id,
                'user_id': user_id,
                'analysis_date': analysis_date,
                'subject_height_cm': height_cm,
                'gender': gender,
                
                # Core temporal metrics
                'avg_stride_time': gait_metrics.get('avg_stride_time'),
                'stride_time_cv': gait_metrics.get('stride_time_cv'),
                'cadence': gait_metrics.get('cadence'),
                
                # Core spatial metrics
                'avg_stride_length': gait_metrics.get('avg_stride_length'),
                'stride_length_cv': gait_metrics.get('stride_length_cv'),
                'step_width': gait_metrics.get('step_width'),
                
                # Core velocity metrics
                'avg_walking_speed': gait_metrics.get('avg_walking_speed'),
                'walking_speed_cv': gait_metrics.get('walking_speed_cv'),
                
                # Asymmetry metrics
                'stride_time_asymmetry': gait_metrics.get('stride_time_asymmetry'),
                'stride_length_asymmetry': gait_metrics.get('stride_length_asymmetry'),
                
                # Stability metrics
                'gait_regularity_index': gait_metrics.get('gait_regularity_index'),
                'gait_stability_ratio': gait_metrics.get('gait_stability_ratio'),
                
                # Phase ratio metrics (newly added)
                'stance_phase_ratio': gait_metrics.get('stance_phase_ratio'),
                'swing_phase_ratio': gait_metrics.get('swing_phase_ratio'),
                'double_support_ratio': gait_metrics.get('double_support_ratio'),
                
                # Metadata
                'total_strides': gait_metrics.get('total_strides'),
                'left_strides': gait_metrics.get('left_strides'),
                'right_strides': gait_metrics.get('right_strides'),
                'calculation_timestamp': gait_metrics.get('calculation_timestamp')
            }
            
            # Store to Supabase (assuming 'gait_metrics' table exists)
            result = supabase.table('gait_metrics').insert(storage_data).execute()
            
            if result.data:
                stored_record = result.data[0]
                record_id = stored_record.get('id')
                
                # Update state with storage confirmation
                state["metrics_record_id"] = record_id
                state["metrics_stored"] = True
                
                self.logger.info(f"Gait metrics stored successfully: Record ID {record_id}")
                
                return state
            else:
                return StateManager.set_error(state, "Failed to store gait metrics - no data returned", "storage_error")
            
        except Exception as e:
            error_msg = f"Gait metrics storage failed: {str(e)}"
            self.logger.error(error_msg)
            return StateManager.set_error(state, error_msg, "storage_execution_error") 
 