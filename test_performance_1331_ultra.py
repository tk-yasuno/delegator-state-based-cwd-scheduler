"""
Delegator v5.2.1 超大規模1331遊具パフォーマンステスト
241公園1331遊具での極限スケーリング性能検証
"""

import time
import psutil
import os
from delegator_v5_2_1 import OptSeqSchedulerScalable
import json
from datetime import datetime
import pandas as pd
import gc

def ultra_scale_performance_test():
    """1331遊具での超大規模パフォーマンステスト"""
    
    print("🚀 Delegator v5.2.1 超大規模1331遊具パフォーマンステスト開始")
    print("=" * 80)
    
    # システムリソース確認
    print("💻 システムリソース確認中...")
    system_info = {
        "cpu_cores": psutil.cpu_count(),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        "memory_used_percent": psutil.virtual_memory().percent
    }
    
    print(f"  CPU: {system_info['cpu_cores']}コア")
    print(f"  メモリ: {system_info['memory_total_gb']:.1f}GB (使用率{system_info['memory_used_percent']:.1f}%)")
    print(f"  利用可能: {system_info['memory_available_gb']:.1f}GB")
    
    if system_info['memory_available_gb'] < 2.0:
        print("⚠️ 警告: 利用可能メモリが2GB未満です。パフォーマンスに影響する可能性があります。")
    
    # データセットの確認
    print("\n📊 データセット情報確認中...")
    try:
        equipment_df = pd.read_csv('input_park_playequipment_241.csv')
        inspection_df = pd.read_csv('inspectionList_parkEquipment_1331.csv')
        
        print(f"  📁 設備データ: {len(equipment_df)}公園")
        print(f"  📁 点検データ: {len(inspection_df)}遊具")
        
        # 実際の遊具数を確認
        print(f"  🎯 確認: {len(inspection_df)}遊具 (目標1331遊具)")
        
        if len(inspection_df) != 1331:
            print(f"⚠️ 注意: 実際の遊具数が目標と異なります ({len(inspection_df)} vs 1331)")
        
    except Exception as e:
        print(f"⚠️ データセット読み込みエラー: {e}")
        return None
    
    results = {
        "test_info": {
            "version": "v5.2.1 Ultra Scale",
            "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target_equipment": len(inspection_df),
            "target_parks": len(equipment_df),
            "system_info": system_info
        },
        "ultra_scale_tests": {},
        "memory_analysis": {},
        "performance_breakdown": {},
        "scalability_analysis": {}
    }
    
    # ガベージコレクション実行
    gc.collect()
    
    # 1. 超大規模テスト（1331遊具）
    print(f"\n🔥 {len(inspection_df)}遊具超大規模テスト実行中...")
    
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    available_memory_start = psutil.virtual_memory().available / 1024 / 1024  # MB
    
    # スケジューラー初期化（制限を1500に拡張）
    print("  ⚙️ スケジューラー初期化中...")
    start_time = time.time()
    scheduler = OptSeqSchedulerScalable(2025, 2035, max_equipment=1500)
    init_time = time.time() - start_time
    
    print(f"    ✅ 初期化完了: {init_time:.3f}秒")
    
    # メモリ使用量チェック（初期化後）
    memory_after_init = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    init_memory_usage = memory_after_init - start_memory
    
    print(f"    💾 初期化メモリ使用量: {init_memory_usage:.1f}MB")
    
    # データ読み込み
    print("  📥 データ読み込み中...")
    start_time = time.time()
    try:
        scheduler.load_equipment_data(
            'input_park_playequipment_241.csv',
            'inspectionList_parkEquipment_1331.csv'
        )
        load_time = time.time() - start_time
        
        actual_equipment_count = len(scheduler.equipment)
        actual_task_count = len(scheduler.tasks)
        
        print(f"    ✅ データ読み込み完了: {load_time:.3f}秒")
        print(f"       └ 実際読み込み: {actual_equipment_count}設備, {actual_task_count}タスク")
        
    except Exception as e:
        print(f"    ❌ データ読み込みエラー: {e}")
        return None
    
    # メモリ使用量チェック（読み込み後）
    memory_after_load = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    load_memory_usage = memory_after_load - memory_after_init
    
    print(f"    💾 読み込みメモリ使用量: {load_memory_usage:.1f}MB")
    
    # メモリ不足チェック
    current_available = psutil.virtual_memory().available / 1024 / 1024  # MB
    if current_available < 500:  # 500MB未満の場合
        print("    ⚠️ 警告: 利用可能メモリが500MB未満です。最適化実行を慎重に進めます...")
    
    # スケジュール実行
    print(f"  🧮 最適化実行開始... (対象: {actual_equipment_count}設備)")
    print("      ※ 大規模データのため時間がかかる場合があります")
    
    start_time = time.time()
    
    try:
        result = scheduler.solve_parallel()
        solve_time = time.time() - start_time
        
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        total_memory_usage = end_memory - start_memory
        solve_memory_usage = end_memory - memory_after_load
        
        print(f"  ✅ 最適化完了: {solve_time:.3f}秒")
        print(f"  💾 解決時メモリ使用量: {solve_memory_usage:.1f}MB")
        print(f"  📊 スケジュール結果:")
        print(f"     └ 成功率: {result['statistics']['scheduling_ratio']*100:.1f}%")
        print(f"     └ 総コスト: ¥{result['statistics']['total_cost']:,.0f}")
        print(f"     └ 総ペナルティ: ¥{result['statistics']['total_penalty']:,.0f}")
        
        success = True
        
    except Exception as e:
        print(f"  ❌ 最適化エラー: {e}")
        solve_time = 0
        total_memory_usage = memory_after_load - start_memory
        solve_memory_usage = 0
        result = None
        success = False
    
    # 結果記録
    results["ultra_scale_tests"]["1331_equipment"] = {
        "actual_equipment_count": actual_equipment_count if success else 0,
        "actual_task_count": actual_task_count if success else 0,
        "init_time": round(init_time, 4),
        "load_time": round(load_time, 4),
        "solve_time": round(solve_time, 4),
        "total_time": round(init_time + load_time + solve_time, 4),
        "init_memory_usage_mb": round(init_memory_usage, 2),
        "load_memory_usage_mb": round(load_memory_usage, 2),
        "solve_memory_usage_mb": round(solve_memory_usage, 2),
        "total_memory_usage_mb": round(total_memory_usage, 2),
        "success": success
    }
    
    if success:
        results["ultra_scale_tests"]["1331_equipment"].update({
            "scheduled_ratio": result['statistics']['scheduling_ratio'],
            "total_cost": result['statistics']['total_cost'],
            "total_penalty": result['statistics']['total_penalty'],
            "equipment_per_second": actual_equipment_count / solve_time if solve_time > 0 else float('inf'),
            "tasks_per_second": actual_task_count / solve_time if solve_time > 0 else float('inf')
        })
    
    # 2. メモリ効率分析
    print("\n🧠 メモリ効率分析実行中...")
    
    system_memory = psutil.virtual_memory()
    if success:
        memory_efficiency = {
            "memory_per_equipment_kb": (total_memory_usage * 1024) / actual_equipment_count,
            "memory_per_task_kb": (total_memory_usage * 1024) / actual_task_count,
            "memory_utilization_percent": (total_memory_usage / (system_memory.total / 1024 / 1024)) * 100,
            "peak_memory_mb": max(init_memory_usage, load_memory_usage, solve_memory_usage),
            "memory_efficiency_ratio": total_memory_usage / actual_equipment_count
        }
        
        results["memory_analysis"] = memory_efficiency
        
        print(f"  📏 設備あたりメモリ: {memory_efficiency['memory_per_equipment_kb']:.1f}KB")
        print(f"  📏 タスクあたりメモリ: {memory_efficiency['memory_per_task_kb']:.1f}KB")
        print(f"  📊 システムメモリ使用率: {memory_efficiency['memory_utilization_percent']:.2f}%")
        print(f"  💾 ピークメモリ: {memory_efficiency['peak_memory_mb']:.1f}MB")
    else:
        print("  ❌ 最適化失敗のためメモリ効率分析をスキップ")
    
    # 3. パフォーマンス内訳分析
    print("\n⚡ パフォーマンス内訳分析...")
    
    if success:
        total_time = init_time + load_time + solve_time
        performance_breakdown = {
            "init_percentage": (init_time / total_time) * 100,
            "load_percentage": (load_time / total_time) * 100,
            "solve_percentage": (solve_time / total_time) * 100,
            "bottleneck": "init" if init_time == max(init_time, load_time, solve_time) else 
                         "load" if load_time == max(init_time, load_time, solve_time) else "solve"
        }
        
        results["performance_breakdown"] = performance_breakdown
        
        print(f"  ⚙️ 初期化: {init_time:.3f}s ({performance_breakdown['init_percentage']:.1f}%)")
        print(f"  📥 読み込み: {load_time:.3f}s ({performance_breakdown['load_percentage']:.1f}%)")
        print(f"  🧮 最適化: {solve_time:.3f}s ({performance_breakdown['solve_percentage']:.1f}%)")
        print(f"  🎯 ボトルネック: {performance_breakdown['bottleneck']}フェーズ")
    else:
        print("  ❌ 最適化失敗のためパフォーマンス分析をスキップ")
    
    # 4. スケーラビリティ分析
    print("\n📈 スケーラビリティ分析...")
    
    if success:
        # 過去のテスト結果との比較
        scale_comparisons = {
            "100_equipment": {"time": 0.071, "memory": 0.1},
            "457_equipment": {"time": 0.000, "memory": 0.0}  # 457遊具の実行時間がほぼ0だった
        }
        
        scalability_metrics = {}
        for scale, baseline in scale_comparisons.items():
            equipment_ratio = actual_equipment_count / int(scale.split('_')[0])
            if baseline["time"] > 0:
                time_efficiency = (baseline["time"] * equipment_ratio) / solve_time
                scalability_metrics[scale] = {
                    "equipment_ratio": equipment_ratio,
                    "time_efficiency": time_efficiency,
                    "linear_scaling": time_efficiency >= 0.5
                }
        
        results["scalability_analysis"] = scalability_metrics
        
        for scale, metrics in scalability_metrics.items():
            print(f"  📊 vs {scale}: {metrics['equipment_ratio']:.1f}倍スケール, "
                  f"効率{metrics['time_efficiency']:.2f} → {'◯' if metrics['linear_scaling'] else '△'}")
    else:
        print("  ❌ 最適化失敗のためスケーラビリティ分析をスキップ")
    
    # 5. 最終評価
    print("\n" + "=" * 80)
    print("🎯 1331遊具超大規模パフォーマンス最終評価")
    print("=" * 80)
    
    test_result = results["ultra_scale_tests"]["1331_equipment"]
    
    if test_result["success"]:
        print(f"✅ 処理成功: {test_result['actual_equipment_count']}設備")
        print(f"⏱️ 総処理時間: {test_result['total_time']:.3f}秒")
        print(f"   ├ 初期化: {test_result['init_time']:.3f}秒")
        print(f"   ├ データ読み込み: {test_result['load_time']:.3f}秒")
        print(f"   └ 最適化実行: {test_result['solve_time']:.3f}秒")
        
        print(f"💾 メモリ使用量: {test_result['total_memory_usage_mb']:.1f}MB")
        print(f"   ├ 初期化時: {test_result['init_memory_usage_mb']:.1f}MB")
        print(f"   ├ 読み込み時: {test_result['load_memory_usage_mb']:.1f}MB")
        print(f"   └ 解決時: {test_result['solve_memory_usage_mb']:.1f}MB")
        
        print(f"📊 スケジュール結果:")
        print(f"   ├ 成功率: {test_result['scheduled_ratio']*100:.1f}%")
        print(f"   ├ 処理速度: {test_result['equipment_per_second']:.1f}設備/秒")
        print(f"   └ ペナルティ: ¥{test_result['total_penalty']:,.0f}")
        
        # 評価基準（1331遊具向けに調整）
        print(f"\n🏆 性能評価:")
        score = 0
        
        # 処理時間評価（30秒以内）
        if test_result['total_time'] <= 30:
            print(f"   ⏱️ 処理時間: ◯ ({test_result['total_time']:.3f}s ≤ 30s)")
            score += 1
        else:
            print(f"   ⏱️ 処理時間: △ ({test_result['total_time']:.3f}s > 30s)")
        
        # メモリ使用量評価（1GB以内）
        if test_result['total_memory_usage_mb'] <= 1024:
            print(f"   💾 メモリ効率: ◯ ({test_result['total_memory_usage_mb']:.1f}MB ≤ 1024MB)")
            score += 1
        else:
            print(f"   💾 メモリ効率: △ ({test_result['total_memory_usage_mb']:.1f}MB > 1024MB)")
        
        # スケジュール成功率評価（90%以上）
        if test_result['scheduled_ratio'] >= 0.9:
            print(f"   📈 スケジュール成功率: ◯ ({test_result['scheduled_ratio']*100:.1f}% ≥ 90%)")
            score += 1
        else:
            print(f"   📈 スケジュール成功率: △ ({test_result['scheduled_ratio']*100:.1f}% < 90%)")
        
        # 総合評価
        rating = ["D", "C", "B", "A", "S"][min(score, 4)]
        print(f"\n   🏆 総合評価: {rating}ランク ({score}/3)")
        
        # 特別評価
        if test_result['total_time'] <= 10 and test_result['total_memory_usage_mb'] <= 500:
            print(f"   🌟 特別評価: 超高効率達成！ (時間{test_result['total_time']:.3f}s, メモリ{test_result['total_memory_usage_mb']:.1f}MB)")
        
    else:
        print("❌ テスト失敗")
        print("   大規模データセットでの処理に問題が発生しました")
        print("   システムリソースまたはアルゴリズムの改善が必要です")
    
    # 6. レポート保存
    report_filename = f"delegator_v5_2_1_ultra_1331_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 詳細レポート保存: {report_filename}")
    print("✨ 1331遊具超大規模テスト完了！")
    
    # ガベージコレクション実行
    gc.collect()
    
    return results

if __name__ == "__main__":
    ultra_scale_performance_test()
