#!/usr/bin/env python3
"""
WalkerHolic CSV Data Visualizer
temp_files 폴더의 모든 CSV 파일들을 시각화하는 도구

지원하는 파일 타입:
1. downloaded_*.csv - 원본 센서 데이터 (가속도계 + 자이로스코프)
2. filtered_*.csv - 필터링된 센서 데이터
3. support_labels_*.csv - 보행 phase 라벨 데이터
4. trimmed_*.csv - 트리밍된 센서 데이터

사용법:
python visualize_csv_data.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import glob
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
try:
    plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
except:
    try:
        plt.rcParams['font.family'] = 'AppleGothic'  # macOS
    except:
        plt.rcParams['font.family'] = 'DejaVu Sans'  # Linux/기본
plt.rcParams['axes.unicode_minus'] = False

class CSVVisualizer:
    def __init__(self, temp_files_dir="temp_files"):
        self.temp_files_dir = Path(temp_files_dir)
        self.csv_files = self._discover_csv_files()
        
        # 색상 팔레트 설정
        self.colors = {
            'accel_x': '#FF6B6B', 'accel_y': '#4ECDC4', 'accel_z': '#45B7D1',
            'gyro_x': '#96CEB4', 'gyro_y': '#FFEAA7', 'gyro_z': '#DDA0DD',
            'double_support': '#FF7675', 'single_support_left': '#74B9FF', 
            'single_support_right': '#00B894', 'non_gait': '#FDCB6E'
        }
    
    def _discover_csv_files(self):
        """temp_files 폴더의 모든 CSV 파일을 발견하고 분류"""
        if not self.temp_files_dir.exists():
            print(f"❌ {self.temp_files_dir} 폴더가 존재하지 않습니다!")
            return {}
        
        csv_files = {
            'downloaded': [],
            'filtered': [],
            'support_labels': [],
            'trimmed': []
        }
        
        for csv_file in self.temp_files_dir.glob("*.csv"):
            filename = csv_file.name
            if filename.startswith('downloaded_') and 'filtered' not in filename:
                csv_files['downloaded'].append(csv_file)
            elif filename.startswith('filtered_'):
                csv_files['filtered'].append(csv_file)
            elif filename.startswith('support_labels_'):
                csv_files['support_labels'].append(csv_file)
            elif filename.startswith('trimmed_'):
                csv_files['trimmed'].append(csv_file)
        
        return csv_files
    
    def print_file_summary(self):
        """발견된 파일들의 요약 정보 출력"""
        print("📊 WalkerHolic CSV Data Visualizer")
        print("=" * 60)
        
        total_files = sum(len(files) for files in self.csv_files.values())
        print(f"📁 총 {total_files}개 CSV 파일 발견:")
        
        for file_type, files in self.csv_files.items():
            if files:
                print(f"  📄 {file_type}: {len(files)}개")
                for file in files[:3]:  # 처음 3개만 표시
                    print(f"    - {file.name}")
                if len(files) > 3:
                    print(f"    - ... 외 {len(files)-3}개")
        print()
    
    def visualize_sensor_data(self, csv_file, data_type="downloaded"):
        """센서 데이터 시각화 (가속도계 + 자이로스코프)"""
        try:
            df = pd.read_csv(csv_file)
            
            # 사용자 이름 추출
            filename = csv_file.name
            user_name = filename.split('_')[1] if len(filename.split('_')) > 1 else "unknown"
            
            fig, axes = plt.subplots(2, 1, figsize=(15, 10))
            fig.suptitle(f'📱 {user_name} - {data_type.title()} 센서 데이터\\n{filename}', 
                        fontsize=16, fontweight='bold')
            
            # 가속도계 데이터
            axes[0].plot(df['sync_timestamp'], df['accel_x'], 
                        color=self.colors['accel_x'], label='X축', alpha=0.8, linewidth=1.5)
            axes[0].plot(df['sync_timestamp'], df['accel_y'], 
                        color=self.colors['accel_y'], label='Y축', alpha=0.8, linewidth=1.5)
            axes[0].plot(df['sync_timestamp'], df['accel_z'], 
                        color=self.colors['accel_z'], label='Z축', alpha=0.8, linewidth=1.5)
            
            axes[0].set_title('🏃‍♂️ 가속도계 데이터 (Accelerometer)', fontsize=14, fontweight='bold')
            axes[0].set_xlabel('시간 (초)')
            axes[0].set_ylabel('가속도 (m/s²)')
            axes[0].legend(loc='upper right')
            axes[0].grid(True, alpha=0.3)
            
            # 자이로스코프 데이터
            axes[1].plot(df['sync_timestamp'], df['gyro_x'], 
                        color=self.colors['gyro_x'], label='X축', alpha=0.8, linewidth=1.5)
            axes[1].plot(df['sync_timestamp'], df['gyro_y'], 
                        color=self.colors['gyro_y'], label='Y축', alpha=0.8, linewidth=1.5)
            axes[1].plot(df['sync_timestamp'], df['gyro_z'], 
                        color=self.colors['gyro_z'], label='Z축', alpha=0.8, linewidth=1.5)
            
            axes[1].set_title('🌀 자이로스코프 데이터 (Gyroscope)', fontsize=14, fontweight='bold')
            axes[1].set_xlabel('시간 (초)')
            axes[1].set_ylabel('각속도 (°/s)')
            axes[1].legend(loc='upper right')
            axes[1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 저장
            output_file = f"visualization_{data_type}_{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✅ 저장됨: {output_file}")
            
            plt.show()
            
            # 데이터 통계 정보
            self._print_sensor_stats(df, user_name, data_type)
            
        except Exception as e:
            print(f"❌ {csv_file.name} 시각화 실패: {e}")
    
    def visualize_support_labels(self, csv_file):
        """보행 phase 라벨 데이터 시각화"""
        try:
            df = pd.read_csv(csv_file)
            
            # 사용자 이름 추출
            filename = csv_file.name
            user_name = filename.split('_')[2] if len(filename.split('_')) > 2 else "unknown"
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
            fig.suptitle(f'👣 {user_name} - 보행 Phase 라벨링 결과\\n{filename}', 
                        fontsize=16, fontweight='bold')
            
            # Phase별 색상 매핑
            phase_colors = {
                'double_support': self.colors['double_support'],
                'single_support_left': self.colors['single_support_left'],
                'single_support_right': self.colors['single_support_right'],
                'non_gait': self.colors['non_gait']
            }
            
            # Phase 타임라인 시각화
            for idx, row in df.iterrows():
                start, end, phase = row['start_frame'], row['end_frame'], row['phase']
                duration = end - start + 1
                
                ax1.barh(0, duration, left=start, height=0.8, 
                        color=phase_colors.get(phase, '#95A5A6'), 
                        alpha=0.8, edgecolor='white', linewidth=0.5)
                
                # 텍스트 라벨 (긴 구간에만)
                if duration > 5:
                    ax1.text(start + duration/2, 0, phase.replace('_', '\\n'), 
                            ha='center', va='center', fontsize=8, fontweight='bold')
            
            ax1.set_title('🕐 보행 Phase 타임라인', fontsize=14, fontweight='bold')
            ax1.set_xlabel('프레임 번호')
            ax1.set_ylabel('')
            ax1.set_yticks([])
            ax1.grid(True, alpha=0.3, axis='x')
            
            # Phase별 통계
            phase_stats = df.groupby('phase').agg({
                'start_frame': 'count',
                'end_frame': lambda x: (df.loc[x.index, 'end_frame'] - df.loc[x.index, 'start_frame'] + 1).sum()
            }).rename(columns={'start_frame': 'count', 'end_frame': 'total_frames'})
            
            phase_stats['percentage'] = phase_stats['total_frames'] / phase_stats['total_frames'].sum() * 100
            
            # 파이 차트
            wedges, texts, autotexts = ax2.pie(phase_stats['total_frames'], 
                                              labels=phase_stats.index, 
                                              colors=[phase_colors.get(phase, '#95A5A6') for phase in phase_stats.index],
                                              autopct='%1.1f%%', startangle=90)
            
            ax2.set_title('📊 보행 Phase 비율', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            # 저장
            output_file = f"visualization_support_labels_{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✅ 저장됨: {output_file}")
            
            plt.show()
            
            # 통계 정보 출력
            self._print_phase_stats(phase_stats, user_name)
            
        except Exception as e:
            print(f"❌ {csv_file.name} 시각화 실패: {e}")
    
    def _print_sensor_stats(self, df, user_name, data_type):
        """센서 데이터 통계 정보 출력"""
        print(f"\\n📊 {user_name} - {data_type.title()} 데이터 통계:")
        print("-" * 50)
        print(f"📏 총 데이터 포인트: {len(df):,}개")
        print(f"⏱️  측정 시간: {df['sync_timestamp'].iloc[-1]:.2f}초")
        print(f"📈 샘플링 레이트: ~{len(df)/df['sync_timestamp'].iloc[-1]:.1f} Hz")
        
        print("\\n🏃‍♂️ 가속도계 통계:")
        for axis in ['accel_x', 'accel_y', 'accel_z']:
            mean_val = df[axis].mean()
            std_val = df[axis].std()
            print(f"  {axis}: 평균 {mean_val:6.2f} ± {std_val:5.2f} m/s²")
        
        print("\\n🌀 자이로스코프 통계:")
        for axis in ['gyro_x', 'gyro_y', 'gyro_z']:
            mean_val = df[axis].mean()
            std_val = df[axis].std()
            print(f"  {axis}: 평균 {mean_val:6.2f} ± {std_val:5.2f} °/s")
    
    def _print_phase_stats(self, phase_stats, user_name):
        """Phase 통계 정보 출력"""
        print(f"\\n👣 {user_name} - 보행 Phase 통계:")
        print("-" * 50)
        
        total_frames = phase_stats['total_frames'].sum()
        print(f"📏 총 프레임 수: {total_frames:,}개")
        
        for phase, stats in phase_stats.iterrows():
            print(f"  {phase:20s}: {stats['count']:3d}회, {stats['total_frames']:5.0f}프레임 ({stats['percentage']:5.1f}%)")
    
    def run_interactive_visualization(self):
        """대화형 시각화 실행"""
        self.print_file_summary()
        
        if not any(self.csv_files.values()):
            print("❌ 시각화할 CSV 파일이 없습니다!")
            return
        
        while True:
            print("\\n🎨 시각화 옵션:")
            print("1. 📱 원본 센서 데이터 (downloaded)")
            print("2. 🔧 필터링된 센서 데이터 (filtered)")
            print("3. 👣 보행 Phase 라벨 (support_labels)")
            print("4. ✂️  트리밍된 센서 데이터 (trimmed)")
            print("5. 🎯 모든 파일 자동 시각화")
            print("0. 🚪 종료")
            
            choice = input("\\n선택하세요 (0-5): ").strip()
            
            if choice == '0':
                print("👋 시각화를 종료합니다.")
                break
            elif choice == '1':
                self._visualize_file_type('downloaded')
            elif choice == '2':
                self._visualize_file_type('filtered')
            elif choice == '3':
                self._visualize_file_type('support_labels')
            elif choice == '4':
                self._visualize_file_type('trimmed')
            elif choice == '5':
                self._visualize_all_files()
            else:
                print("❌ 잘못된 선택입니다!")
    
    def _visualize_file_type(self, file_type):
        """특정 타입의 파일들 시각화"""
        files = self.csv_files.get(file_type, [])
        if not files:
            print(f"❌ {file_type} 타입의 파일이 없습니다!")
            return
        
        print(f"\\n📄 {file_type} 파일 목록:")
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file.name}")
        
        try:
            choice = int(input(f"\\n시각화할 파일 번호 (1-{len(files)}): "))
            if 1 <= choice <= len(files):
                selected_file = files[choice-1]
                
                if file_type == 'support_labels':
                    self.visualize_support_labels(selected_file)
                else:
                    self.visualize_sensor_data(selected_file, file_type)
            else:
                print("❌ 잘못된 번호입니다!")
        except ValueError:
            print("❌ 숫자를 입력해주세요!")
    
    def _visualize_all_files(self):
        """모든 파일 자동 시각화"""
        print("\\n🎯 모든 파일을 자동으로 시각화합니다...")
        
        # 각 타입별로 시각화
        for file_type, files in self.csv_files.items():
            if files:
                print(f"\\n📄 {file_type} 파일들 시각화 중...")
                for file in files:
                    if file_type == 'support_labels':
                        self.visualize_support_labels(file)
                    else:
                        self.visualize_sensor_data(file, file_type)
        
        print("\\n✅ 모든 파일 시각화 완료!")

def main():
    """메인 실행 함수"""
    print("🚀 WalkerHolic CSV Data Visualizer 시작!")
    
    # temp_files 폴더 확인
    temp_files_dir = Path("temp_files")
    if not temp_files_dir.exists():
        print(f"❌ {temp_files_dir} 폴더가 존재하지 않습니다!")
        return
    
    # 시각화 도구 초기화 및 실행
    visualizer = CSVVisualizer()
    visualizer.run_interactive_visualization()

if __name__ == "__main__":
    main() 