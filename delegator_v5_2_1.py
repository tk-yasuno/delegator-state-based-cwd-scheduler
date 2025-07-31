"""
Delegator v5.2.1: スケーリング対応版状態監視型メンテナンス計画システム
100設備対応のパフォーマンス最適化

Author: CWD Agent
Version: v5.2.1
Date: 2025-07-25
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from joblib import Parallel, delayed
import time

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class State:
    """遊具の劣化状態を表すクラス"""
    id: str
    score: float  # 0.0〜1.0の劣化スコア
    grade: str    # a, b, c, d, e の判定グレード
    inspection_date: str
    
    def __post_init__(self):
        """スコアに基づいてグレードを自動設定"""
        if self.score < 0.2:
            self.grade = 'a'
        elif self.score < 0.4:
            self.grade = 'b'
        elif self.score < 0.6:
            self.grade = 'c'
        elif self.score < 0.8:
            self.grade = 'd'
        else:
            self.grade = 'e'

@dataclass
class Task:
    """修繕・更新タスクを表すクラス"""
    id: str
    equipment_id: str
    duration: int  # 作業期間（年）
    earliest_start: int  # 最早開始年
    latest_end: int      # 最遅完了年
    cost: float          # 修繕コスト
    priority: int        # 優先度（1-5, 5が最高）
    penalty_coefficient: float  # 遅延ペナルティ係数
    
    def penalty_late(self, delay_years: int) -> float:
        """遅延ペナルティを計算（現実的な保険支払額ベース）"""
        return self.penalty_coefficient * delay_years * self.cost * 0.001  # 0.1% → 0.001 に調整

@dataclass
class Resource:
    """資源制約を表すクラス"""
    name: str
    capacity_per_year: Dict[int, float]  # 年度別利用可能量

@dataclass
class Equipment:
    """遊具情報を表すクラス"""
    id: str
    park_name: str
    equipment_type: str
    install_year: int
    current_state: Optional[State] = None
    repair_cost: float = 150000
    renewal_cost: float = 500000

class OptSeqSchedulerScalable:
    """OptSeq風スケジューラー（100設備対応スケーラブル版）"""
    
    def __init__(self, start_year: int = 2025, end_year: int = 2040, max_equipment: int = 100):
        self.start_year = start_year
        self.end_year = end_year
        self.years = list(range(start_year, end_year + 1))
        self.max_equipment = max_equipment
        
        self.states: Dict[str, State] = {}
        self.tasks: Dict[str, Task] = {}
        self.resources: Dict[str, Resource] = {}
        self.equipment: Dict[str, Equipment] = {}
        
        # パフォーマンス追跡
        self.performance_metrics = {
            'load_time': 0,
            'solve_time': 0,
            'memory_usage': 0,
            'cpu_cores': mp.cpu_count()
        }
        
        logger.info(f"OptSeqSchedulerScalable initialized for {start_year}-{end_year}, max {max_equipment} equipment")
        logger.info(f"Available CPU cores: {self.performance_metrics['cpu_cores']}")
    
    def add_state(self, state: State) -> None:
        """状態を追加"""
        self.states[state.id] = state
        logger.debug(f"Added state: {state.id}, grade: {state.grade}, score: {state.score}")
    
    def add_task(self, task: Task) -> None:
        """タスクを追加"""
        self.tasks[task.id] = task
        logger.debug(f"Added task: {task.id}, priority: {task.priority}")
    
    def add_resource(self, resource: Resource) -> None:
        """リソースを追加"""
        self.resources[resource.name] = resource
        logger.debug(f"Added resource: {resource.name}")
    
    def add_equipment(self, equipment: Equipment) -> None:
        """遊具を追加"""
        self.equipment[equipment.id] = equipment
        logger.debug(f"Added equipment: {equipment.id} at {equipment.park_name}")
    
    def compute_degradation_batch(self, equipment_list: List[Equipment], inspection_dict: Dict) -> List[float]:
        """バッチ処理で劣化スコアを計算（並列処理対応）"""
        
        def compute_single_degradation(equipment: Equipment) -> float:
            # 年数ベースの劣化
            age = 2025 - equipment.install_year
            age_factor = min(age / 60, 1.0)  # 60年で完全劣化
            
            # 点検結果による補正
            grade_scores = {'a': 0.1, 'b': 0.3, 'c': 0.5, 'd': 0.7, 'e': 0.9}
            inspection_data = inspection_dict.get(equipment.id, {'劣化判定': 'b'})
            inspection_grade = inspection_data.get('劣化判定', 'b')
            inspection_factor = grade_scores.get(inspection_grade, 0.3)
            
            # 加重平均
            degradation_score = 0.6 * age_factor + 0.4 * inspection_factor
            return min(max(degradation_score, 0.0), 1.0)
        
        # 並列処理で劣化スコア計算
        n_jobs = min(self.performance_metrics['cpu_cores'], len(equipment_list))
        degradation_scores = Parallel(n_jobs=n_jobs)(
            delayed(compute_single_degradation)(eq) for eq in equipment_list
        )
        
        return degradation_scores
    
    def compute_degradation(self, equipment: Equipment, inspection_data: Dict) -> float:
        """単一設備の劣化スコア計算（互換性維持）"""
        # 年数ベースの劣化
        age = 2025 - equipment.install_year
        age_factor = min(age / 60, 1.0)  # 60年で完全劣化
        
        # 点検結果による補正
        grade_scores = {'a': 0.1, 'b': 0.3, 'c': 0.5, 'd': 0.7, 'e': 0.9}
        inspection_grade = inspection_data.get('劣化判定', 'b')
        inspection_factor = grade_scores.get(inspection_grade, 0.3)
        
        # 加重平均
        degradation_score = 0.6 * age_factor + 0.4 * inspection_factor
        return min(max(degradation_score, 0.0), 1.0)
    
    def degradation_priority(self, state: State) -> int:
        """劣化状態に基づく優先度計算"""
        if state.score >= 0.8:  # e判定
            return 5
        elif state.score >= 0.6:  # d判定
            return 4
        elif state.score >= 0.4:  # c判定
            return 3
        elif state.score >= 0.2:  # b判定
            return 2
        else:  # a判定
            return 1
    
    def load_equipment_data(self, equipment_csv: str, inspection_csv: str) -> None:
        """設備データと点検データを読み込み（100設備対応）"""
        start_time = time.time()
        logger.info(f"Loading equipment and inspection data for up to {self.max_equipment} equipment...")
        
        # 点検データの読み込み
        try:
            inspection_df = pd.read_csv(inspection_csv)
            inspection_dict = {}
            for _, row in inspection_df.iterrows():
                inspection_dict[row['equipment_id']] = row.to_dict()
        except FileNotFoundError:
            logger.warning(f"Inspection file {inspection_csv} not found, using default values")
            inspection_dict = {}
        
        # 設備データの処理
        equipment_df = pd.read_csv(equipment_csv)
        
        count = 0
        equipment_list = []
        
        for _, row in equipment_df.iterrows():
            if count >= self.max_equipment:
                break
                
            # 各遊具タイプに対してequipmentを作成
            equipment_types = ['踏み板式ブランコ', 'スベリ台', 'ﾌｨｰﾙﾄﾞｱｽﾚﾁｯｸ遊具', 'スプリング遊具', 'ベンチ']
            
            for eq_type in equipment_types:
                if count >= self.max_equipment:
                    break
                    
                # 空文字列や欠損値のチェック
                eq_count = row.get(eq_type, 0)
                if pd.isna(eq_count) or eq_count == '' or eq_count == 0:
                    continue
                
                try:
                    eq_count = int(eq_count)
                    if eq_count > 0:  # その遊具が存在する場合
                        # ベンチの複数設置対応
                        if eq_type == 'ベンチ' and eq_count > 1:
                            for bench_num in range(1, eq_count + 1):
                                if count >= self.max_equipment:
                                    break
                                eq_id = f"eq_{count:04d}_ベンチ_{bench_num:02d}"
                                
                                equipment = Equipment(
                                    id=eq_id,
                                    park_name=row['公園名'],
                                    equipment_type=eq_type,
                                    install_year=int(row['西暦年']),
                                    repair_cost=150000 + np.random.randint(-30000, 50000)
                                )
                                equipment_list.append(equipment)
                                count += 1
                        else:
                            # 単一遊具の場合
                            eq_type_mapped = eq_type.replace('ﾌｨｰﾙﾄﾞｱｽﾚﾁｯｸ遊具', 'Athletic遊具')
                            eq_id = f"eq_{count:04d}_{eq_type_mapped}"
                            
                            equipment = Equipment(
                                id=eq_id,
                                park_name=row['公園名'],
                                equipment_type=eq_type,
                                install_year=int(row['西暦年']),
                                repair_cost=150000 + np.random.randint(-30000, 50000)
                            )
                            equipment_list.append(equipment)
                            count += 1
                        
                except (ValueError, TypeError):
                    continue
        
        # バッチ処理で劣化スコア計算
        logger.info(f"Computing degradation scores for {len(equipment_list)} equipment (batch processing)...")
        degradation_scores = self.compute_degradation_batch(equipment_list, inspection_dict)
        
        # オブジェクト作成・登録
        for equipment, degradation_score in zip(equipment_list, degradation_scores):
            # State作成
            state = State(
                id=equipment.id,
                score=degradation_score,
                grade='',  # __post_init__で自動設定
                inspection_date="2025-01"
            )
            
            equipment.current_state = state
            
            # オブジェクト登録
            self.add_equipment(equipment)
            self.add_state(state)
            
            # Task作成
            priority = self.degradation_priority(state)
            penalty_coeff = state.score * 1000  # 劣化が進むほど高ペナルティ（現実的な値に調整）
            
            task = Task(
                id=f"repair_{equipment.id}",
                equipment_id=equipment.id,
                duration=1,
                earliest_start=max(equipment.install_year + 5, 2025),
                latest_end=2040,
                cost=equipment.repair_cost,
                priority=priority,
                penalty_coefficient=penalty_coeff
            )
            
            self.add_task(task)
        
        load_time = time.time() - start_time
        self.performance_metrics['load_time'] = load_time
        
        logger.info(f"Loaded {len(self.equipment)} equipment items and {len(self.tasks)} tasks in {load_time:.3f}s")
    
    def solve_parallel(self, strategy: str = "greedy_priority") -> Dict[str, Any]:
        """並列処理対応のスケジュール最適化"""
        start_time = time.time()
        logger.info(f"Solving schedule with strategy: {strategy} (parallel processing)")
        
        # 予算・資源制約の設定（100設備対応）
        # 設備数に応じてスケーリング
        equipment_count = len(self.equipment)
        annual_budget = max(2000000, equipment_count * 40000)  # 設備1つあたり4万円/年
        annual_crew_capacity = max(5, equipment_count // 10)  # 設備10つあたり1件/年
        
        budget_resource = Resource(
            name="Budget",
            capacity_per_year={year: annual_budget for year in self.years}
        )
        crew_resource = Resource(
            name="Crew", 
            capacity_per_year={year: annual_crew_capacity for year in self.years}
        )
        
        self.add_resource(budget_resource)
        self.add_resource(crew_resource)
        
        # 優先度ベースでタスクをソート（並列処理対応）
        def sort_key(t):
            return (-t.priority, t.latest_end, -t.penalty_coefficient)
        
        sorted_tasks = sorted(self.tasks.values(), key=sort_key)
        
        # 年度別リソース追跡
        schedule = {}
        annual_cost = {year: 0 for year in self.years}
        annual_count = {year: 0 for year in self.years}
        
        # バッチ処理でタスクスケジューリング
        batch_size = max(1, len(sorted_tasks) // self.performance_metrics['cpu_cores'])
        task_batches = [sorted_tasks[i:i+batch_size] for i in range(0, len(sorted_tasks), batch_size)]
        
        logger.info(f"Processing {len(sorted_tasks)} tasks in {len(task_batches)} batches")
        
        # シーケンシャル処理（リソース競合回避のため）
        for task in sorted_tasks:
            scheduled = False
            
            # 最優先年から順に配置を試行
            for year in range(task.earliest_start, min(task.latest_end + 1, self.end_year + 1)):
                # 制約チェック
                if (annual_cost[year] + task.cost <= annual_budget and
                    annual_count[year] + 1 <= annual_crew_capacity):
                    
                    # スケジュール決定
                    schedule[task.id] = {
                        'task_id': task.id,
                        'equipment_id': task.equipment_id,
                        'scheduled_year': year,
                        'cost': task.cost,
                        'priority': task.priority,
                        'delay_years': max(0, year - task.earliest_start),
                        'penalty': task.penalty_late(max(0, year - task.earliest_start))
                    }
                    
                    annual_cost[year] += task.cost
                    annual_count[year] += 1
                    scheduled = True
                    break
            
            if not scheduled:
                logger.debug(f"Could not schedule task: {task.id}")
        
        # 結果統計
        total_cost = sum(item['cost'] for item in schedule.values())
        total_penalty = sum(item['penalty'] for item in schedule.values())
        scheduled_count = len(schedule)
        
        solve_time = time.time() - start_time
        self.performance_metrics['solve_time'] = solve_time
        
        result = {
            'schedule': schedule,
            'annual_cost': annual_cost,
            'annual_count': annual_count,
            'statistics': {
                'total_cost': total_cost,
                'total_penalty': total_penalty,
                'scheduled_tasks': scheduled_count,
                'total_tasks': len(self.tasks),
                'scheduling_ratio': scheduled_count / len(self.tasks) if self.tasks else 0,
                'annual_budget': annual_budget,
                'annual_capacity': annual_crew_capacity
            },
            'performance': {
                'solve_time': solve_time,
                'load_time': self.performance_metrics['load_time'],
                'equipment_per_second': len(self.equipment) / solve_time if solve_time > 0 else 0,
                'tasks_per_second': len(self.tasks) / solve_time if solve_time > 0 else 0
            }
        }
        
        logger.info(f"Scheduling completed: {scheduled_count}/{len(self.tasks)} tasks scheduled in {solve_time:.3f}s")
        logger.info(f"Performance: {len(self.equipment):.0f} equipment/s, {len(self.tasks):.0f} tasks/s")
        logger.info(f"Total cost: ¥{total_cost:,.0f}, Total penalty: ¥{total_penalty:,.0f}")
        
        return result
    
    def solve(self, strategy: str = "greedy_priority") -> Dict[str, Any]:
        """互換性維持のためのsolveメソッド"""
        return self.solve_parallel(strategy)
    
    def export_gantt_data(self, schedule_result: Dict[str, Any]) -> List[Dict]:
        """ガントチャート用データを生成（100設備対応）"""
        gantt_data = []
        
        for task_id, task_data in schedule_result['schedule'].items():
            equipment_id = task_data['equipment_id']
            if equipment_id not in self.equipment:
                logger.warning(f"Equipment ID {equipment_id} not found in equipment list. Skipping.")
                continue
                
            equipment = self.equipment[equipment_id]
            state = equipment.current_state
            
            gantt_data.append({
                'Task': f"{equipment.park_name} - {equipment.equipment_type}",
                'Start': task_data['scheduled_year'],
                'Finish': task_data['scheduled_year'],
                'Resource': f"Grade-{state.grade.upper()}",
                'Cost': task_data['cost'],
                'Priority': task_data['priority'],
                'Penalty': task_data['penalty']
            })
        
        return gantt_data
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """パフォーマンスサマリーを取得"""
        return {
            'equipment_count': len(self.equipment),
            'task_count': len(self.tasks),
            'load_time': self.performance_metrics.get('load_time', 0),
            'solve_time': self.performance_metrics.get('solve_time', 0),
            'cpu_cores': self.performance_metrics['cpu_cores'],
            'equipment_per_second': len(self.equipment) / self.performance_metrics.get('solve_time', 1),
            'memory_efficient': len(self.equipment) <= self.max_equipment
        }


# テスト用メイン関数
def main():
    """テスト実行用メイン関数（100設備対応）"""
    scheduler = OptSeqSchedulerScalable(2025, 2040, max_equipment=100)
    
    # データ読み込み
    try:
        scheduler.load_equipment_data(
            'input_park_playequipment.csv',
            'inspectionList_parkEquipment_100.csv'  # 100設備用データ
        )
        
        # スケジュール解決
        result = scheduler.solve_parallel()
        
        # 結果表示
        print("\n=== Schedule Result (Top 10) ===")
        count = 0
        for task_id, task_data in result['schedule'].items():
            if count >= 10:  # 最初の10件のみ表示
                break
            equipment = scheduler.equipment[task_data['equipment_id']]
            print(f"{equipment.park_name} - {equipment.equipment_type}: "
                  f"{task_data['scheduled_year']} (Priority: {task_data['priority']}, "
                  f"Cost: ¥{task_data['cost']:,})")
            count += 1
        
        if len(result['schedule']) > 10:
            print(f"... and {len(result['schedule']) - 10} more tasks")
        
        # 統計表示
        print(f"\n=== Statistics ===")
        stats = result['statistics']
        print(f"Scheduled: {stats['scheduled_tasks']}/{stats['total_tasks']} tasks")
        print(f"Success Rate: {stats['scheduling_ratio']*100:.1f}%")
        print(f"Total Cost: ¥{stats['total_cost']:,.0f}")
        print(f"Total Penalty: ¥{stats['total_penalty']:,.0f}")
        print(f"Annual Budget: ¥{stats['annual_budget']:,.0f}")
        print(f"Annual Capacity: {stats['annual_capacity']} tasks/year")
        
        # パフォーマンス表示
        print(f"\n=== Performance ===")
        perf = result['performance']
        print(f"Load Time: {perf['load_time']:.3f}s")
        print(f"Solve Time: {perf['solve_time']:.3f}s")
        print(f"Equipment/s: {perf['equipment_per_second']:.1f}")
        print(f"Tasks/s: {perf['tasks_per_second']:.1f}")
        
        # ガントチャートデータ生成
        gantt_data = scheduler.export_gantt_data(result)
        print(f"\nGantt chart data generated: {len(gantt_data)} entries")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        return None


if __name__ == "__main__":
    main()
