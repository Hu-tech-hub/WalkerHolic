#!/usr/bin/env python3
"""
Walking Data Filter
walking_data 폴더의 IMU 센서 데이터에 버터워스 로우패스 필터를 적용하여
filtered_walking_data 폴더에 저장하는 스크립트

Usage:
    python filter_walking_data.py

Author: AI Assistant
Date: 2024-12-19
"""

import os
import sys
import pandas as pd
import numpy as np
from scipy import signal
from pathlib import Path
from tqdm import tqdm


class WalkingDataFilter:
    """IMU 센서 데이터 필터링 클래스"""
    
    def __init__(self, fs=30, cutoff=10, order=4):
        """
        초기화
        
        Args:
            fs (int): 샘플링 주파수 (Hz)
            cutoff (int): 로우패스 필터 컷오프 주파수 (Hz)
            order (int): 필터 차수
        """
        self.fs = fs
        self.cutoff = cutoff
        self.order = order
        self.sensor_cols = ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
        
    def butter_lowpass_filter(self, data):
        """
        버터워스 로우패스 필터 적용
        
        Args:
            data (np.ndarray): 센서 데이터 (frames, channels)
            
        Returns:
            np.ndarray: 필터링된 데이터
        """
        nyq = 0.5 * self.fs
        normal_cutoff = self.cutoff / nyq
        b, a = signal.butter(self.order, normal_cutoff, btype='low', analog=False)
        
        # 각 채널별로 필터 적용
        filtered_data = np.zeros_like(data)
        for i in range(data.shape[1]):
            filtered_data[:, i] = signal.filtfilt(b, a, data[:, i], axis=0)
        
        return filtered_data
    
    def filter_csv_file(self, input_file, output_file):
        """
        단일 CSV 파일 필터링
        
        Args:
            input_file (str): 입력 파일 경로
            output_file (str): 출력 파일 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            # CSV 파일 읽기
            df = pd.read_csv(input_file)
            
            # 필수 컬럼 확인
            missing_cols = [col for col in self.sensor_cols if col not in df.columns]
            if missing_cols:
                print(f"필수 센서 컬럼 누락 ({input_file}): {missing_cols}")
                return False
            
            # 센서 데이터 추출
            sensor_data = df[self.sensor_cols].values
            
            # 데이터 유효성 검사
            if len(sensor_data) < 10:  # 최소 데이터 길이 체크
                print(f"데이터 길이 부족 ({input_file}): {len(sensor_data)} frames")
                return False
            
            # 버터워스 필터 적용
            filtered_data = self.butter_lowpass_filter(sensor_data)
            
            # 필터링된 데이터로 DataFrame 업데이트
            df_filtered = df.copy()
            df_filtered[self.sensor_cols] = filtered_data
            
            # 출력 디렉토리 생성
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 필터링된 데이터 저장
            df_filtered.to_csv(output_file, index=False)
            
            return True
            
        except Exception as e:
            print(f"파일 필터링 실패 ({input_file}): {e}")
            return False
    
    def filter_directory(self, input_dir, output_dir):
        """
        디렉토리 내 모든 CSV 파일 필터링
        
        Args:
            input_dir (str): 입력 디렉토리
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
                    output_file = output_path / relative_path
                    csv_files.append((str(csv_file), str(output_file)))
        
        if not csv_files:
            print(f"처리할 CSV 파일이 없습니다: {input_dir}")
            return {'total': 0, 'success': 0, 'failed': 0}
        
        print(f"총 {len(csv_files)}개 파일 처리 시작...")
        
        # 진행률 표시와 함께 파일 처리
        success_count = 0
        failed_count = 0
        
        for input_file, output_file in tqdm(csv_files, desc="필터링 진행"):
            if self.filter_csv_file(input_file, output_file):
                success_count += 1
            else:
                failed_count += 1
        
        # 결과 통계
        stats = {
            'total': len(csv_files),
            'success': success_count,
            'failed': failed_count
        }
        
        print(f"필터링 완료: {success_count}/{len(csv_files)} 성공, {failed_count} 실패")
        
        return stats


def main():
    """메인 실행 함수"""
    try:
        # 필터 초기화 (고정 설정: 컷오프 10Hz, 필터 차수 4)
        filter_processor = WalkingDataFilter(fs=30, cutoff=10, order=4)
        
        input_dir = "walking_data"
        output_dir = "filtered_walking_data"
        
        print(f"🔧 필터 설정: fs=30Hz, cutoff=10Hz, order=4")
        print(f"📂 입력 디렉토리: {input_dir}")
        print(f"📁 출력 디렉토리: {output_dir}")
        
        # 디렉토리 필터링 실행
        stats = filter_processor.filter_directory(input_dir, output_dir)
        
        # 결과 출력
        print(f"\n{'='*50}")
        print(f"WALKING DATA FILTERING RESULTS")
        print(f"{'='*50}")
        print(f"총 파일 수: {stats['total']}")
        print(f"성공: {stats['success']}")
        print(f"실패: {stats['failed']}")
        print(f"성공률: {stats['success']/stats['total']*100:.1f}%" if stats['total'] > 0 else "성공률: 0%")
        print(f"{'='*50}")
        
        if stats['failed'] > 0:
            print(f"{stats['failed']}개 파일 처리 실패.")
            sys.exit(1)
        else:
            print("✅ 모든 파일 필터링 완료!")
            
    except Exception as e:
        print(f"❌ 필터링 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 