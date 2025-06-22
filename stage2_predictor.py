"""
Stage2 Gait Phase Predictor - Support Labels 생성 버전
filtered_walking_data CSV 파일을 입력받아 support_labels CSV 파일을 출력

Author: AI Assistant
Date: 2024-12-19
Version: 4.1.0 (Pre-filtered Data Input)
"""

import os
import numpy as np
import pandas as pd
import tensorflow as tf
import keras
from pathlib import Path
import argparse
from tqdm import tqdm

# # Stage2 모델의 커스텀 클래스들을 import (데코레이터로 자동 등록)
try:
    from stage2_model import TCNBlock, CausalAttention
    print("✅ Stage2 모델 커스텀 클래스 로드 완료")
except ImportError as e:
    print(f"⚠️ Stage2 모델 클래스 import 실패: {e}")

class Stage2Predictor:
    """Stage2 모델을 사용한 보행 단계 예측 및 Support Labels 생성 클래스"""
    
    def __init__(self, model_path=None):
        """
        초기화
        
        Args:
            model_path (str, optional): 모델 파일 경로. None이면 자동 검색
        """
        self.model = None
        self.model_path = model_path
        self.class_names = ['DS', 'SSR', 'SSL']  # Double Support, Single Support Right, Single Support Left
        self.window_size = 30
        
        # 모델 로드
        if model_path:
            self.load_model(model_path)
    
    def find_best_model(self):
        """
        최적의 Stage2 모델을 자동으로 찾습니다.
        
        Returns:
            str: 찾은 모델 파일 경로
        """
        # 데코레이터 기반 모델 우선 검색
        search_paths = [
            "stage2_model2_decorator/overall_best.keras",  # 데코레이터 기반 모델
            "models_2/best_fold_5.keras",
            "stage2_model2/overall_best.keras"
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                print(f"✅ 모델 발견: {path}")
                return path
        
        raise FileNotFoundError("사용 가능한 Stage2 모델을 찾을 수 없습니다.")
    
    def load_model(self, model_path):
        """
        모델을 로드합니다 (데코레이터 기반).
        
        Args:
            model_path (str): 모델 파일 경로
        """
        self.model = keras.models.load_model(model_path, compile=False)
        self.model_path = model_path
    
    def load_filtered_data(self, csv_file_path):
        """
        이미 필터링된 센서 데이터를 로드합니다.
        
        Args:
            csv_file_path (str): 필터링된 CSV 파일 경로
            
        Returns:
            np.ndarray: 센서 데이터
        """
        # CSV 파일 읽기
        df = pd.read_csv(csv_file_path)
        
        # 필수 센서 컬럼 확인
        sensor_cols = ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
        missing_cols = [col for col in sensor_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"필수 센서 컬럼이 없습니다: {missing_cols}")
        
        # 센서 데이터 추출 (이미 필터링됨)
        sensor_data = df[sensor_cols].values
        
        return sensor_data
    
    def create_windows(self, data):
        """
        슬라이딩 윈도우 생성
        
        Args:
            data (np.ndarray): 센서 데이터 (frames, 6)
            
        Returns:
            tuple: (윈도우 데이터, 윈도우 인덱스)
        """
        n_frames = len(data)
        windows = []
        window_indices = []
        
        # 처음과 끝 30프레임 제외하고 윈도우 생성
        for start in range(30, n_frames - self.window_size - 29):
            end = start + self.window_size
            windows.append(data[start:end])
            window_indices.append((start, end))
        
        if windows:
            return np.array(windows), window_indices
        else:
            return np.array([]).reshape(0, self.window_size, 6), []
    
    def predict_gait_phases(self, csv_file_path):
        """
        보행 단계를 예측합니다.
        
        Args:
            csv_file_path (str): 필터링된 CSV 파일 경로
            
        Returns:
            list: 프레임별 클래스 이름 리스트
        """
        if self.model is None:
            # 자동으로 모델 찾기
            model_path = self.find_best_model()
            self.load_model(model_path)
        
        # 필터링된 데이터 로드
        filtered_data = self.load_filtered_data(csv_file_path)
        
        # 윈도우 생성
        windows, window_indices = self.create_windows(filtered_data)
        
        if len(windows) == 0:
            raise ValueError("윈도우를 생성할 수 없습니다. 데이터가 너무 짧습니다.")
        
        # 모델 예측
        predictions = self.model.predict(windows, verbose=0)
        
        # Softmax 적용 (모델이 logits를 출력하는 경우)
        if predictions.max() > 1.0:  # logits 형태인 경우
            predictions = tf.nn.softmax(predictions, axis=-1).numpy()
        
        # 프레임별 예측 결과 생성
        frame_predictions = self._reconstruct_frame_predictions(
            predictions, window_indices, len(filtered_data)
        )
        
        return frame_predictions
    
    def _reconstruct_frame_predictions(self, window_predictions, window_indices, total_frames):
        """
        윈도우 예측을 프레임별 예측으로 재구성
        """
        # 프레임별 확률 누적 및 카운트
        frame_probs = np.zeros((total_frames, 3))  # DS, SSR, SSL
        frame_counts = np.zeros(total_frames)
        
        # 라벨링 제외 구간 설정 (초반 1초와 마지막 1초)
        exclude_start_frames = 30  # 30프레임 (1초)
        exclude_end_frames = 30    # 30프레임 (1초)
        
        # 각 윈도우의 예측을 해당 프레임에 누적
        for window_idx, (start, end) in enumerate(window_indices):
            for frame_offset in range(self.window_size):
                frame_idx = start + frame_offset
                
                # 초반 1초와 마지막 1초는 제외
                if (frame_idx < exclude_start_frames or 
                    frame_idx >= total_frames - exclude_end_frames):
                    continue
                
                if frame_idx < total_frames:
                    frame_probs[frame_idx] += window_predictions[window_idx, frame_offset]
                    frame_counts[frame_idx] += 1
        
        # 평균 확률 계산 (라벨링 구간만)
        valid_mask = frame_counts > 0
        frame_probs[valid_mask] /= frame_counts[valid_mask, np.newaxis]
        
        # 클래스 예측 생성
        class_names_predictions = ['No Label'] * total_frames
        
        # 유효한 프레임에 대해서만 예측 수행
        if valid_mask.any():
            valid_indices = np.where(valid_mask)[0]
            class_predictions = np.argmax(frame_probs[valid_indices], axis=1)
            
            # 클래스 이름 할당
            for i, idx in enumerate(valid_indices):
                class_names_predictions[idx] = self.class_names[class_predictions[i]]
        
        return class_names_predictions
    
    def convert_to_support_labels(self, class_names):
        """
        프레임별 예측을 support labels 형태로 변환
        
        Args:
            class_names (list): 프레임별 클래스 이름 리스트
            
        Returns:
            pd.DataFrame: support labels 형태의 DataFrame
        """
        # 라벨 매핑
        label_mapping = {
            'No Label': 'non_gait',
            'DS': 'double_support', 
            'SSL': 'single_support_left',
            'SSR': 'single_support_right'
        }
        
        # 연속된 같은 라벨들을 그룹화
        segments = []
        
        if len(class_names) == 0:
            return pd.DataFrame(columns=['start_frame', 'end_frame', 'phase'])
        
        current_phase = label_mapping.get(class_names[0], 'non_gait')
        start_frame = 0
        
        for i in range(1, len(class_names)):
            mapped_phase = label_mapping.get(class_names[i], 'non_gait')
            
            if mapped_phase != current_phase:
                # 이전 세그먼트 종료
                segments.append({
                    'start_frame': int(start_frame),
                    'end_frame': int(i-1),
                    'phase': current_phase
                })
                
                # 새 세그먼트 시작
                current_phase = mapped_phase
                start_frame = i
        
        # 마지막 세그먼트 추가
        segments.append({
            'start_frame': int(start_frame),
            'end_frame': int(len(class_names)-1),
            'phase': current_phase
        })
        
        # DataFrame 생성
        result_df = pd.DataFrame(segments)
        result_df = result_df[['start_frame', 'end_frame', 'phase']]
        
        return result_df
    
    def process_single_file(self, input_file, output_file=None):
        """
        단일 파일 처리
        
        Args:
            input_file (str): 입력 파일 경로 (필터링된 데이터)
            output_file (str, optional): 출력 파일 경로
            
        Returns:
            str: 출력 파일 경로
        """
        # 출력 파일명 자동 생성
        if output_file is None:
            input_path = Path(input_file)
            filename = input_path.stem  # 확장자 제거
            output_file = f"predicted_support_label_data/{input_path.parent.name}/{filename}_support_labels.csv"
        
        # 예측 수행
        class_names = self.predict_gait_phases(input_file)
        
        # Support labels 형태로 변환
        support_df = self.convert_to_support_labels(class_names)
        
        # 출력 디렉토리 생성 (Path 객체 사용)
        output_path = Path(output_file)
        if output_path.parent != Path('.'):  # 현재 디렉토리가 아닌 경우만
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 파일 저장
        support_df.to_csv(output_file, index=False)
        
        return output_file
    
    def process_directory(self, input_dir="filtered_walking_data", output_dir="predicted_support_label_data"):
        """
        디렉토리 내 모든 파일 처리
        
        Args:
            input_dir (str): 입력 디렉토리 (필터링된 데이터)
            output_dir (str): 출력 디렉토리
            
        Returns:
            dict: 처리 결과 통계
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"입력 디렉토리가 존재하지 않습니다: {input_dir}")
        
        # CSV 파일 목록 수집
        csv_files = []
        for subject_dir in input_path.iterdir():
            if subject_dir.is_dir():
                for csv_file in subject_dir.glob("*.csv"):
                    relative_path = csv_file.relative_to(input_path)
                    filename = csv_file.stem
                    # Path 객체를 사용하여 올바른 경로 생성
                    output_file = output_path / relative_path.parent / f"{filename}_support_labels.csv"
                    csv_files.append((str(csv_file), str(output_file)))
        
        if not csv_files:
            return {'total': 0, 'success': 0, 'failed': 0}
        
        # 파일 처리
        success_count = 0
        failed_count = 0
        
        for input_file, output_file in tqdm(csv_files, desc="처리 진행 중", unit="파일"):
            try:
                self.process_single_file(input_file, output_file)
                success_count += 1
            except Exception as e:
                print(f"파일 처리 실패 ({input_file}): {e}")
                failed_count += 1
        
        # 결과 통계
        stats = {
            'total': len(csv_files),
            'success': success_count,
            'failed': failed_count
        }
        
        return stats