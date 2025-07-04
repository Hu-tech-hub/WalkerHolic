"""
Data processing nodes for LangGraph-based gait analysis pipeline
Implements 4 nodes: receive_request, file_metadata, download_csv, filter_data
"""
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import tempfile
import re

import os
from pathlib import Path
from dotenv import load_dotenv

from supabase import create_client, Client
from filter_walking_data import WalkingDataFilter

from .base_node import BaseNode
from .graph_state import GraphState, StateManager, PipelineStages

# Load environment variables
load_dotenv()

class ReceiveRequestNode(BaseNode):
    """
    Node 1: Receive and validate HTTP request
    Creates initial GraphState from user_id, height_cm, and gender parameters
    No LLM required - pure Python validation
    """
    
    def __init__(self):
        super().__init__(PipelineStages.RECEIVE_REQUEST)
    
    def get_system_prompt(self) -> str:
        # No LLM needed - pure validation logic
        return "Pure validation node - no LLM interaction required"
    
    def execute(self, state: GraphState) -> GraphState:
        """Validate request parameters and initialize state (no LLM)"""
        
        user_id = state.get("user_id")
        height_cm = state.get("height_cm") 
        gender = state.get("gender")
        
        # 1. user_id 검증
        if not user_id or not isinstance(user_id, str):
            return StateManager.set_error(state, "user_id must be a non-empty string", "validation_error")
        
        if len(user_id) < 3 or len(user_id) > 50:
            return StateManager.set_error(state, "user_id must be 3-50 characters long", "validation_error")
        
        # user_id는 알파벳, 숫자, 하이픈, 언더스코어, 한글 허용
        allowed_chars = True
        for char in user_id:
            if not (char.isalnum() or char in '_-' or '\uac00' <= char <= '\ud7a3'):
                allowed_chars = False
                break
        if not allowed_chars:
            return StateManager.set_error(state, "user_id can only contain letters, numbers, hyphens, underscores, and Korean characters", "validation_error")
        
        # 2. height_cm 검증
        if not isinstance(height_cm, (int, float)):
            return StateManager.set_error(state, "height_cm must be a number, not string", "validation_error")
        
        try:
            height = float(height_cm)
            if not (100 <= height <= 250):
                return StateManager.set_error(state, "height_cm must be between 100-250 cm", "validation_error")
        except (ValueError, TypeError):
            return StateManager.set_error(state, "height_cm must be a valid number", "validation_error")
        
        # 3. gender 검증
        if not gender or not isinstance(gender, str):
            return StateManager.set_error(state, "gender must be a non-empty string", "validation_error")
        
        valid_genders = ["male", "female", "other", "m", "f", "o"]
        if gender.lower() not in valid_genders:
            return StateManager.set_error(state, "gender must be one of: male, female, other (or m, f, o)", "validation_error")
        
        # Normalize gender
        gender_normalized = gender.lower()
        if gender_normalized in ["m", "male"]:
            gender_normalized = "male"
        elif gender_normalized in ["f", "female"]:
            gender_normalized = "female"
        elif gender_normalized in ["o", "other"]:
            gender_normalized = "other"
        
        # Update state with normalized values
        state["user_id"] = user_id
        state["height_cm"] = float(height_cm)
        state["gender"] = gender_normalized
        
        self.logger.info(f"Request validated successfully - User: {user_id}, Height: {height}cm, Gender: {gender_normalized}")
        
        return state

class FileMetadataNode(BaseNode):
    """
    Node 2: Search and list available CSV files in Supabase Storage
    Pure Python logic - no LLM needed
    """
    
    def __init__(self):
        super().__init__(PipelineStages.BUILD_QUERY)  # Keep same stage for compatibility
        self.supabase = None
    
    def get_system_prompt(self) -> str:
        # No LLM needed - pure file search logic
        return ""
    
    def _connect_storage(self):
        """Create Supabase client for storage access"""
        if self.supabase is None:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                raise ValueError("Supabase credentials not found in environment variables")
                
            self.supabase = create_client(supabase_url, supabase_key)
        return self.supabase
    
    def execute(self, state: GraphState) -> GraphState:
        """Search for available CSV files in Storage"""
        
        if not self.validate_state_requirements(state, ["user_id", "height_cm", "gender"]):
            return StateManager.set_error(state, "Missing required fields: user_id, height_cm, gender", "validation_error")
        
        user_id = state["user_id"]
        height_cm = state["height_cm"]
        gender = state["gender"]
        
        try:
            # Connect to Storage
            supabase = self._connect_storage()
            
            # List all files in gait-data bucket
            files = supabase.storage.from_("gait-data").list()
            
            # Filter CSV files and extract metadata
            csv_files = []
            for file in files:
                # Handle both dict and object file types
                if isinstance(file, dict):
                    file_name = file.get('name', '')
                    if file_name.lower().endswith('.csv'):
                        metadata = {
                            'name': file_name,
                            'size': file.get('metadata', {}).get('size', 0),
                            'last_modified': file.get('metadata', {}).get('lastModified', 'Unknown'),
                            'content_type': file.get('metadata', {}).get('mimetype', 'text/csv')
                        }
                        csv_files.append(metadata)
                elif hasattr(file, 'name') and file.name.lower().endswith('.csv'):
                    metadata = {
                        'name': file.name,
                        'size': getattr(file.metadata, 'size', 0) if hasattr(file, 'metadata') and file.metadata else 0,
                        'last_modified': getattr(file.metadata, 'lastModified', 'Unknown') if hasattr(file, 'metadata') and file.metadata else 'Unknown',
                        'content_type': getattr(file.metadata, 'mimetype', 'text/csv') if hasattr(file, 'metadata') and file.metadata else 'text/csv'
                    }
                    csv_files.append(metadata)
            
            # Store file list in state
            state["available_csv_files"] = csv_files
            
            # Select the best file (latest by default)
            if csv_files:
                # Sort by last_modified date and select the latest
                latest_file = max(csv_files, key=lambda f: f['last_modified'])
                state["selected_csv_file"] = latest_file
                state["file_selection_criteria"] = "latest"
                
                self.logger.info(f"Selected file: {latest_file['name']} (latest of {len(csv_files)} files)")
            else:
                self.logger.warning("No CSV files found in Storage")
                # Don't set selected_csv_file - this will trigger error handling downstream
            
            self.logger.info(f"Found {len(csv_files)} CSV files in Storage for user {user_id}")
            
            return state
            
        except Exception as e:
            return StateManager.set_error(state, f"Storage file search failed: {str(e)}", "storage_access_error")

class DownloadCsvNode(BaseNode):
    """
    Node 3: Download selected CSV file from Supabase Storage
    Pure Python logic - no LLM needed for file download
    """
    
    def __init__(self):
        super().__init__(PipelineStages.FETCH_CSV)  # Keep same stage for compatibility
        self.supabase = None
    
    def get_system_prompt(self) -> str:
        # No LLM needed - pure file download logic
        return ""
    
    def _connect_storage(self):
        """Create Supabase client for storage access"""
        if self.supabase is None:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                raise ValueError("Supabase credentials not found in environment variables")
                
            self.supabase = create_client(supabase_url, supabase_key)
        return self.supabase
    
    def execute(self, state: GraphState) -> GraphState:
        """Download selected CSV file from Storage"""
        
        if not self.validate_state_requirements(state, ["selected_csv_file", "user_id"]):
            return StateManager.set_error(state, "Missing required fields: selected_csv_file, user_id", "validation_error")
        
        selected_file = state["selected_csv_file"]
        user_id = state["user_id"]
        session_id = state.get("session_id", "unknown")
        
        try:
            # Connect to Storage
            supabase = self._connect_storage()
            
            # Download file from Storage
            file_name = selected_file["name"]
            
            self.logger.info(f"Downloading file: {file_name} ({selected_file.get('size', 0)} bytes)")
            
            # Download the file content
            response = supabase.storage.from_("gait-data").download(file_name)
            
            if not response:
                return StateManager.set_error(state, f"Failed to download file: {file_name}", "download_error")
            
            # Generate local filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            local_filename = f"downloaded_{user_id}_{timestamp}_{file_name}"
            temp_dir = Path(os.getenv('TEMP_DIR', './temp_files'))
            local_path = temp_dir / local_filename
            
            # Ensure temp directory exists
            temp_dir.mkdir(exist_ok=True)
            
            # Save downloaded content to local file
            with open(local_path, 'wb') as f:
                f.write(response)
            
            # Verify file was created and has content
            if not local_path.exists():
                return StateManager.set_error(state, f"Failed to create local file: {local_path}", "file_creation_error")
            
            file_size = local_path.stat().st_size
            if file_size == 0:
                return StateManager.set_error(state, f"Downloaded file is empty: {local_path}", "empty_file_error")
            
            # Update state with local file path
            state["raw_csv_path"] = str(local_path)
            state["downloaded_file_info"] = {
                "original_name": file_name,
                "local_path": str(local_path),
                "size": file_size,
                "download_timestamp": timestamp
            }
            
            self.logger.info(f"File downloaded successfully: {file_name} → {local_path} ({file_size} bytes)")
            
            return state
            
        except Exception as e:
            return StateManager.set_error(state, f"Storage download failed: {str(e)}", "storage_download_error")

class FilterDataNode(BaseNode):
    """
    Node 4: Apply Butterworth filter to raw IMU data
    Uses existing WalkingDataFilter from workflow (no LLM needed for signal processing)
    """
    
    def __init__(self):
        super().__init__(PipelineStages.FILTER_DATA)
        # Initialize filter with same parameters as workflow
        self.filter_processor = WalkingDataFilter(fs=30, cutoff=10, order=4)
    
    def get_system_prompt(self) -> str:
        # This node doesn't use LLM - pure signal processing
        return "Signal processing node - no LLM interaction required"
    
    def _trim_data_boundaries(self, df: pd.DataFrame, fs: int = 30) -> pd.DataFrame:
        """
        Remove first 2 seconds and last 3 seconds from the data
        Reset frame numbers and timestamps to start from 0
        
        Args:
            df: Input DataFrame with IMU data
            fs: Sampling frequency (default 30 Hz)
            
        Returns:
            Trimmed DataFrame with reset frame numbers and timestamps
        """
        total_rows = len(df)
        
        # Calculate indices to remove
        first_2sec_rows = 2 * fs  # 60 rows for first 2 seconds
        last_3sec_rows = 3 * fs   # 90 rows for last 3 seconds
        
        # Check if we have enough data
        min_required_rows = first_2sec_rows + last_3sec_rows + 30  # At least 1 second of data remaining
        if total_rows < min_required_rows:
            self.logger.warning(f"Data too short ({total_rows} rows) for boundary trimming. Minimum required: {min_required_rows}")
            return df  # Return original data if too short
        
        # Trim the data
        start_idx = first_2sec_rows
        end_idx = total_rows - last_3sec_rows
        
        trimmed_df = df.iloc[start_idx:end_idx].copy()
        
        # Reset index for clean sequential numbering
        trimmed_df.reset_index(drop=True, inplace=True)
        
        # Reset frame numbers to start from 0
        if 'frame' in trimmed_df.columns:
            trimmed_df['frame'] = range(len(trimmed_df))
        elif 'frame_number' in trimmed_df.columns:
            trimmed_df['frame_number'] = range(len(trimmed_df))
        
        # Reset timestamps to start from 0 with proper increments
        if 'sync_timestamp' in trimmed_df.columns:
            time_increment = 1.0 / fs  # Time per frame at given sampling rate
            trimmed_df['sync_timestamp'] = [i * time_increment for i in range(len(trimmed_df))]
        
        # Update unix_timestamp to be consistent (optional, for continuity)
        if 'unix_timestamp' in trimmed_df.columns:
            # Get the first unix timestamp as baseline
            base_unix_time = trimmed_df['unix_timestamp'].iloc[0]
            trimmed_df['unix_timestamp'] = [base_unix_time + (i * time_increment) for i in range(len(trimmed_df))]
        
        self.logger.info(f"Data trimmed and reset: {total_rows} → {len(trimmed_df)} rows (removed first {first_2sec_rows} and last {last_3sec_rows} rows)")
        self.logger.info("Frame numbers and timestamps reset to start from 0")
        
        return trimmed_df

    def execute(self, state: GraphState) -> GraphState:
        """Apply data trimming and Butterworth filter to raw data"""
        
        if not self.validate_state_requirements(state, ["raw_csv_path"]):
            return StateManager.set_error(state, "Missing required field: raw_csv_path", "validation_error")
        
        raw_csv_path = state["raw_csv_path"]
        session_id = state.get("session_id", "unknown")
        
        # Verify input file exists
        if not Path(raw_csv_path).exists():
            return StateManager.set_error(state, f"Raw CSV file not found: {raw_csv_path}", "file_not_found_error")
        
        try:
            # 1. Load and trim the raw data first
            self.logger.info(f"Loading raw data from: {raw_csv_path}")
            df_raw = pd.read_csv(raw_csv_path)
            
            if len(df_raw) == 0:
                return StateManager.set_error(state, "Raw CSV file is empty", "empty_file_error")
            
            self.logger.info(f"Original data shape: {df_raw.shape}")
            
            # 2. Trim first 2 seconds and last 3 seconds
            df_trimmed = self._trim_data_boundaries(df_raw, fs=30)
            
            if len(df_trimmed) == 0:
                return StateManager.set_error(state, "No data remaining after trimming", "trim_error")
            
            # 3. Save trimmed data to temporary file
            raw_path = Path(raw_csv_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trimmed_filename = f"trimmed_{raw_path.stem}_{timestamp}.csv"
            temp_dir = Path(os.getenv('TEMP_DIR', './temp_files'))
            trimmed_path = temp_dir / trimmed_filename
            
            df_trimmed.to_csv(trimmed_path, index=False)
            self.logger.info(f"Trimmed data saved: {trimmed_path}")
            
            # 4. Apply Butterworth filter to trimmed data
            filtered_filename = f"filtered_{raw_path.stem}_{timestamp}.csv"
            filtered_path = temp_dir / filtered_filename
            
            # Use existing WalkingDataFilter on trimmed data
            success = self.filter_processor.filter_csv_file(str(trimmed_path), str(filtered_path))
            
            if not success:
                return StateManager.set_error(state, "Butterworth filtering failed", "filter_processing_error")
            
            # Verify filtered file was created
            if not filtered_path.exists():
                return StateManager.set_error(state, f"Filtered CSV file not created: {filtered_path}", "file_creation_error")
            
            # Verify filtered file has data
            try:
                df_filtered = pd.read_csv(filtered_path)
                if len(df_filtered) == 0:
                    return StateManager.set_error(state, "Filtered file is empty", "filter_output_error")
                
                self.logger.info(f"Final filtered data shape: {df_filtered.shape}")
                
            except Exception as e:
                return StateManager.set_error(state, f"Cannot read filtered file: {str(e)}", "file_read_error")
            
            # Update state with processing info
            state["filtered_csv_path"] = str(filtered_path)
            state["trimmed_csv_path"] = str(trimmed_path)  # Keep trimmed data info
            state["data_processing_info"] = {
                "original_rows": len(df_raw),
                "trimmed_rows": len(df_trimmed),
                "filtered_rows": len(df_filtered),
                "trim_settings": {
                    "front_seconds": 2,
                    "back_seconds": 3,
                    "sampling_rate": 30
                }
            }
            
            self.logger.info(f"Data processing completed: {len(df_raw)} → {len(df_trimmed)} → {len(df_filtered)} rows")
            
            return state
            
        except Exception as e:
            error_msg = f"Data filtering failed: {str(e)}"
            self.logger.error(error_msg)
            return StateManager.set_error(state, error_msg, "filter_execution_error") 