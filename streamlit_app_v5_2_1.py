"""
Streamlit UI for Delegator v5.2.1
大規模スケーリング対応状態監視型メンテナンス計画システム
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import sys
import os
import time
import psutil

# パスの追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from delegator_v5_2_1 import OptSeqSchedulerScalable, State, Task, Equipment
except ImportError:
    st.error("delegator_v5_2_1.py が見つかりません。同じディレクトリに配置してください。")
    st.stop()

# ページ設定
st.set_page_config(
    page_title="Delegator v5.2.1 - 大規模スケーリング対応メンテナンス計画",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# メインタイトル
st.title("🚀 Delegator v5.2.1: 大規模スケーリング対応メンテナンス計画システム")
st.markdown("**OptSeqベース並列処理対応 - 最大1331遊具まで対応**")

# サイドバー設定
st.sidebar.title("⚙️ システム設定")

# データセット選択
st.sidebar.subheader("📊 データセット選択")
dataset_option = st.sidebar.selectbox(
    "使用するデータセット",
    [
        "小規模データ (5設備)",
        "中規模データ (100設備)", 
        "大規模データ (457遊具)",
        "超大規模データ (1331遊具)"
    ],
    index=1
)

# データセットに応じたファイル名とmax_equipment設定
dataset_config = {
    "小規模データ (5設備)": {
        "equipment_file": "input_park_playequipment.csv",
        "inspection_file": "inspectionList_parkEquipment.csv",
        "max_equipment": 10
    },
    "中規模データ (100設備)": {
        "equipment_file": "input_park_playequipment_100.csv",
        "inspection_file": "inspectionList_parkEquipment_100.csv",
        "max_equipment": 150
    },
    "大規模データ (457遊具)": {
        "equipment_file": "input_park_playequipment_100.csv",
        "inspection_file": "inspectionList_parkEquipment_100.csv",
        "max_equipment": 500
    },
    "超大規模データ (1331遊具)": {
        "equipment_file": "input_park_playequipment_241.csv",
        "inspection_file": "inspectionList_parkEquipment_1331.csv",
        "max_equipment": 1500
    }
}

config = dataset_config[dataset_option]

# 計画期間設定
start_year = st.sidebar.number_input("開始年", min_value=2025, max_value=2030, value=2025)
end_year = st.sidebar.number_input("終了年", min_value=2030, max_value=2050, value=2040)

# 制約条件設定（データセット規模に応じて自動調整）
st.sidebar.subheader("制約条件")

# 予算の自動調整
base_budget = {
    "小規模データ (5設備)": 2000000,
    "中規模データ (100設備)": 4000000,
    "大規模データ (457遊具)": 18000000,
    "超大規模データ (1331遊具)": 50000000
}

base_capacity = {
    "小規模データ (5設備)": 5,
    "中規模データ (100設備)": 20,
    "大規模データ (457遊具)": 80,
    "超大規模データ (1331遊具)": 200
}

annual_budget = st.sidebar.number_input(
    "年間予算（円）", 
    min_value=1000000, 
    value=base_budget[dataset_option], 
    step=1000000
)
annual_capacity = st.sidebar.number_input(
    "年間施工可能件数", 
    min_value=1, 
    value=base_capacity[dataset_option], 
    step=5
)

# スケジューリング戦略
strategy = st.sidebar.selectbox(
    "スケジューリング戦略",
    ["greedy_priority", "cost_optimal", "penalty_minimization"],
    index=0
)

# パフォーマンス設定
st.sidebar.subheader("🔧 パフォーマンス設定")
enable_parallel = st.sidebar.checkbox("並列処理を有効化", value=True)
show_performance = st.sidebar.checkbox("パフォーマンス詳細を表示", value=True)

# システム情報表示
if show_performance:
    st.sidebar.subheader("💻 システム情報")
    st.sidebar.write(f"CPU: {psutil.cpu_count()}コア")
    memory_gb = psutil.virtual_memory().total / (1024**3)
    st.sidebar.write(f"メモリ: {memory_gb:.1f}GB")
    memory_available = psutil.virtual_memory().available / (1024**3)
    st.sidebar.write(f"利用可能: {memory_available:.1f}GB")

# 実行ボタン
if st.sidebar.button("🚀 スケジュール実行", type="primary"):
    st.session_state.execute_scheduling = True
    st.session_state.dataset_option = dataset_option

# メインコンテンツ
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 設備状況", 
    "📅 スケジュール結果", 
    "📈 ガントチャート", 
    "⚡ パフォーマンス", 
    "📋 詳細レポート"
])

# データ読み込み関数
@st.cache_data
def load_scheduler_data(dataset_option, start_year, end_year):
    """データセットに応じたスケジューラーの初期化"""
    config = dataset_config[dataset_option]
    
    scheduler = OptSeqSchedulerScalable(
        start_year, 
        end_year, 
        max_equipment=config["max_equipment"]
    )
    
    # データファイルの確認
    equipment_file = config["equipment_file"]
    inspection_file = config["inspection_file"]
    
    if os.path.exists(equipment_file) and os.path.exists(inspection_file):
        try:
            start_time = time.time()
            scheduler.load_equipment_data(equipment_file, inspection_file)
            load_time = time.time() - start_time
            return scheduler, load_time, None
        except Exception as e:
            return None, 0, str(e)
    else:
        error_msg = f"データファイルが見つかりません: {equipment_file}, {inspection_file}"
        return None, 0, error_msg

# データ読み込み
scheduler, load_time, error_msg = load_scheduler_data(dataset_option, start_year, end_year)

if scheduler is None:
    st.error(f"データ読み込みエラー: {error_msg}")
    st.stop()

# 読み込み成功メッセージ
if show_performance:
    st.success(f"✅ {dataset_option} 読み込み完了 - {len(scheduler.equipment)}設備、{len(scheduler.tasks)}タスク（{load_time:.3f}秒）")

# Tab1: 設備状況
with tab1:
    st.header(f"🏞️ 公園遊具の状況 - {dataset_option}")
    
    # 設備概要
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("総設備数", len(scheduler.equipment))
    
    with col2:
        high_priority_count = sum(1 for eq in scheduler.equipment.values() 
                                 if eq.current_state and eq.current_state.grade in ['d', 'e'])
        st.metric("緊急対応必要", high_priority_count, delta="優先度D,E")
    
    with col3:
        total_repair_cost = sum(eq.repair_cost for eq in scheduler.equipment.values())
        st.metric("総修繕コスト", f"¥{total_repair_cost:,.0f}")
    
    with col4:
        if scheduler.equipment:
            avg_age = sum(2025 - eq.install_year for eq in scheduler.equipment.values()) / len(scheduler.equipment)
            st.metric("平均築年数", f"{avg_age:.1f}年")
        else:
            st.metric("平均築年数", "N/A")
    
    # 劣化状態分布
    st.subheader("劣化状態分布")
    
    # データ準備
    equipment_data = []
    for eq in scheduler.equipment.values():
        if eq.current_state:
            equipment_data.append({
                '設備ID': eq.id,
                '公園名': eq.park_name,
                '設備種類': eq.equipment_type,
                '設置年': eq.install_year,
                '築年数': 2025 - eq.install_year,
                '劣化判定': eq.current_state.grade.upper(),
                '劣化スコア': eq.current_state.score,
                '修繕コスト': eq.repair_cost
            })
    
    equipment_df = pd.DataFrame(equipment_data)
    
    if not equipment_df.empty:
        # 劣化状態のヒストグラム
        col1, col2 = st.columns(2)
        
        with col1:
            grade_counts = equipment_df['劣化判定'].value_counts()
            fig_bar = px.bar(
                x=grade_counts.index,
                y=grade_counts.values,
                title="劣化判定グレード分布",
                labels={'x': '劣化判定', 'y': '設備数'},
                color=grade_counts.values,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # サンプリング（1000件以上の場合）
            display_df = equipment_df.sample(min(1000, len(equipment_df))) if len(equipment_df) > 1000 else equipment_df
            
            fig_scatter = px.scatter(
                display_df,
                x='築年数',
                y='劣化スコア',
                color='劣化判定',
                size='修繕コスト',
                hover_data=['公園名', '設備種類'],
                title=f"築年数と劣化スコアの関係 {'(サンプル表示)' if len(equipment_df) > 1000 else ''}"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # 統計サマリー
        st.subheader("統計サマリー")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**劣化判定分布**")
            for grade, count in grade_counts.items():
                percentage = (count / len(equipment_df)) * 100
                st.write(f"{grade}: {count}件 ({percentage:.1f}%)")
        
        with col2:
            st.write("**築年数統計**")
            st.write(f"最小: {equipment_df['築年数'].min()}年")
            st.write(f"最大: {equipment_df['築年数'].max()}年")
            st.write(f"平均: {equipment_df['築年数'].mean():.1f}年")
            st.write(f"中央値: {equipment_df['築年数'].median():.1f}年")
        
        with col3:
            st.write("**コスト統計**")
            st.write(f"最小: ¥{equipment_df['修繕コスト'].min():,.0f}")
            st.write(f"最大: ¥{equipment_df['修繕コスト'].max():,.0f}")
            st.write(f"平均: ¥{equipment_df['修繕コスト'].mean():,.0f}")
            st.write(f"合計: ¥{equipment_df['修繕コスト'].sum():,.0f}")
        
        # 設備一覧表（ページング対応）
        st.subheader("設備詳細一覧")
        
        # 大規模データの場合はページング
        if len(equipment_df) > 100:
            st.write(f"総件数: {len(equipment_df)}件")
            page_size = 100
            total_pages = (len(equipment_df) - 1) // page_size + 1
            page = st.selectbox("ページ選択", range(1, total_pages + 1))
            
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(equipment_df))
            display_df = equipment_df.iloc[start_idx:end_idx]
            
            st.write(f"表示: {start_idx + 1} - {end_idx} / {len(equipment_df)}")
            st.dataframe(display_df, use_container_width=True)
        else:
            st.dataframe(equipment_df, use_container_width=True)
    else:
        st.warning("設備データがありません。")

# Tab2: スケジュール結果
with tab2:
    st.header("📅 最適化スケジュール結果")
    
    if 'execute_scheduling' in st.session_state and st.session_state.execute_scheduling:
        # データセットが変更された場合の警告
        if 'dataset_option' in st.session_state and st.session_state.dataset_option != dataset_option:
            st.warning("⚠️ データセットが変更されています。再度実行ボタンを押してください。")
            st.session_state.execute_scheduling = False
        else:
            with st.spinner(f"スケジュールを最適化中... ({dataset_option})"):
                try:
                    # パフォーマンス測定開始
                    start_time = time.time()
                    start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    
                    # スケジュール実行
                    if enable_parallel:
                        result = scheduler.solve_parallel(strategy)
                    else:
                        result = scheduler.solve(strategy)
                    
                    # パフォーマンス測定終了
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    
                    execution_time = end_time - start_time
                    memory_usage = end_memory - start_memory
                    
                    # 結果とパフォーマンス情報を保存
                    st.session_state.schedule_result = result
                    st.session_state.performance_info = {
                        'execution_time': execution_time,
                        'memory_usage': memory_usage,
                        'parallel_enabled': enable_parallel,
                        'dataset_size': len(scheduler.equipment)
                    }
                    st.session_state.execute_scheduling = False
                    
                    # 成功メッセージ
                    if show_performance:
                        st.success(f"✅ 最適化完了! 実行時間: {execution_time:.3f}秒、メモリ使用量: {memory_usage:.1f}MB")
                
                except Exception as e:
                    st.error(f"❌ スケジュール実行エラー: {str(e)}")
                    st.session_state.execute_scheduling = False
    
    if 'schedule_result' in st.session_state:
        result = st.session_state.schedule_result
        
        # 統計情報
        stats = result['statistics']
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("スケジュール済", f"{stats['scheduled_tasks']}/{stats['total_tasks']}")
        
        with col2:
            st.metric("総コスト", f"¥{stats['total_cost']:,.0f}")
        
        with col3:
            # 現実的なペナルティ表示
            penalty_million = stats['total_penalty'] / 1000000
            st.metric("遅延ペナルティ", f"¥{penalty_million:.1f}M", help="現実的な保険支払額レベル")
        
        with col4:
            scheduling_rate = stats['scheduling_ratio'] * 100
            st.metric("スケジュール成功率", f"{scheduling_rate:.1f}%")
        
        with col5:
            if 'performance_info' in st.session_state:
                perf = st.session_state.performance_info
                throughput = perf['dataset_size'] / perf['execution_time']
                st.metric("処理速度", f"{throughput:.0f}設備/秒")
        
        # パフォーマンス詳細
        if show_performance and 'performance_info' in st.session_state:
            st.subheader("⚡ パフォーマンス詳細")
            perf = st.session_state.performance_info
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(f"**実行時間**: {perf['execution_time']:.3f}秒")
            with col2:
                st.write(f"**メモリ使用量**: {perf['memory_usage']:.1f}MB")
            with col3:
                st.write(f"**並列処理**: {'有効' if perf['parallel_enabled'] else '無効'}")
            with col4:
                throughput = perf['dataset_size'] / perf['execution_time']
                st.write(f"**スループット**: {throughput:.0f}設備/秒")
        
        # 年度別予算・件数
        col1, col2 = st.columns(2)
        
        with col1:
            annual_cost_df = pd.DataFrame([
                {'年度': year, 'コスト': cost} 
                for year, cost in result['annual_cost'].items()
            ])
            fig_cost = px.bar(
                annual_cost_df,
                x='年度',
                y='コスト',
                title="年度別修繕コスト",
                labels={'コスト': 'コスト（円）'}
            )
            fig_cost.add_hline(y=annual_budget, line_dash="dash", line_color="red", 
                              annotation_text="予算上限")
            st.plotly_chart(fig_cost, use_container_width=True)
        
        with col2:
            annual_count_df = pd.DataFrame([
                {'年度': year, '件数': count} 
                for year, count in result['annual_count'].items()
            ])
            fig_count = px.bar(
                annual_count_df,
                x='年度',
                y='件数',
                title="年度別施工件数",
                labels={'件数': '施工件数'}
            )
            fig_count.add_hline(y=annual_capacity, line_dash="dash", line_color="red",
                               annotation_text="能力上限")
            st.plotly_chart(fig_count, use_container_width=True)
        
        # スケジュール詳細表
        st.subheader("スケジュール詳細")
        schedule_data = []
        for task_id, task_data in result['schedule'].items():
            # 設備IDの安全な取得
            equipment_id = task_data['equipment_id']
            if equipment_id not in scheduler.equipment:
                st.warning(f"設備ID {equipment_id} が見つかりません。スキップします。")
                continue
                
            equipment = scheduler.equipment[equipment_id]
            state = equipment.current_state
            
            schedule_data.append({
                '公園名': equipment.park_name,
                '設備種類': equipment.equipment_type,
                '劣化判定': state.grade.upper() if state else 'N/A',
                'スケジュール年': task_data['scheduled_year'],
                '優先度': task_data['priority'],
                'コスト': f"¥{task_data['cost']:,.0f}",
                '遅延年数': task_data['delay_years'],
                'ペナルティ': f"¥{task_data['penalty']:,.0f}"
            })
        
        schedule_df = pd.DataFrame(schedule_data)
        
        # 大規模データの場合はページング
        if len(schedule_df) > 50:
            st.write(f"総スケジュール件数: {len(schedule_df)}件")
            page_size = 50
            total_pages = (len(schedule_df) - 1) // page_size + 1
            page = st.selectbox("ページ選択", range(1, total_pages + 1), key="schedule_page")
            
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(schedule_df))
            display_schedule_df = schedule_df.iloc[start_idx:end_idx]
            
            st.write(f"表示: {start_idx + 1} - {end_idx} / {len(schedule_df)}")
            st.dataframe(display_schedule_df, use_container_width=True)
        else:
            st.dataframe(schedule_df, use_container_width=True)
    
    else:
        st.info("サイドバーの「スケジュール実行」ボタンを押してください。")

# Tab3: ガントチャート
with tab3:
    st.header("📈 ガントチャート")
    
    if 'schedule_result' in st.session_state:
        result = st.session_state.schedule_result
        gantt_data = scheduler.export_gantt_data(result)
        
        if gantt_data:
            # 大規模データの場合は表示件数を制限
            max_display = 200
            if len(gantt_data) > max_display:
                st.warning(f"⚠️ 表示件数制限: {len(gantt_data)}件中{max_display}件を表示")
                # 優先度の高いもの順にソート
                gantt_data_sorted = sorted(gantt_data, key=lambda x: x['Priority'], reverse=True)
                gantt_data_display = gantt_data_sorted[:max_display]
            else:
                gantt_data_display = gantt_data
            
            # Plotlyガントチャート
            fig = go.Figure()
            
            colors = {'A': 'green', 'B': 'blue', 'C': 'orange', 'D': 'red', 'E': 'darkred'}
            
            for i, task in enumerate(gantt_data_display):
                grade = task['Resource'].split('-')[1]
                color = colors.get(grade, 'gray')
                
                fig.add_trace(go.Scatter(
                    x=[task['Start'], task['Finish']],
                    y=[i, i],
                    mode='lines+markers',
                    line=dict(color=color, width=8),
                    name=f"{task['Task'][:30]}... ({grade})" if len(task['Task']) > 30 else f"{task['Task']} ({grade})",
                    hovertemplate=f"""
                    <b>{task['Task']}</b><br>
                    年度: {task['Start']}<br>
                    劣化判定: {grade}<br>
                    コスト: ¥{task['Cost']:,.0f}<br>
                    優先度: {task['Priority']}<br>
                    ペナルティ: ¥{task['Penalty']:,.0f}
                    <extra></extra>
                    """
                ))
            
            fig.update_layout(
                title=f"修繕スケジュール ガントチャート ({len(gantt_data_display)}件表示)",
                xaxis_title="年度",
                yaxis_title="設備",
                yaxis=dict(
                    tickmode='array',
                    tickvals=list(range(len(gantt_data_display))),
                    ticktext=[f"{i+1}. {task['Task'][:20]}..." if len(task['Task']) > 20 
                             else f"{i+1}. {task['Task']}" 
                             for i, task in enumerate(gantt_data_display)]
                ),
                height=max(400, min(len(gantt_data_display) * 25, 1200)),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 劣化判定別の凡例
            st.subheader("劣化判定凡例")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.markdown("🟢 **A判定**: 良好")
            with col2:
                st.markdown("🔵 **B判定**: やや劣化")
            with col3:
                st.markdown("🟠 **C判定**: 1年以内")
            with col4:
                st.markdown("🔴 **D判定**: 3ヶ月以内")
            with col5:
                st.markdown("🔴 **E判定**: 緊急対応")
            
            # 統計情報
            if len(gantt_data) != len(gantt_data_display):
                st.info(f"📊 全{len(gantt_data)}件中、優先度上位{len(gantt_data_display)}件を表示中")
        
        else:
            st.warning("ガントチャートデータがありません。")
    
    else:
        st.info("まずスケジュールを実行してください。")

# Tab4: パフォーマンス
with tab4:
    st.header("⚡ パフォーマンス分析")
    
    if 'schedule_result' in st.session_state and 'performance_info' in st.session_state:
        result = st.session_state.schedule_result
        perf = st.session_state.performance_info
        
        # パフォーマンスサマリー
        st.subheader("📊 パフォーマンスサマリー")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("実行時間", f"{perf['execution_time']:.3f}秒")
            st.metric("メモリ使用量", f"{perf['memory_usage']:.1f}MB")
        
        with col2:
            throughput = perf['dataset_size'] / perf['execution_time']
            st.metric("処理速度", f"{throughput:.0f}設備/秒")
            st.metric("並列処理", "有効" if perf['parallel_enabled'] else "無効")
        
        with col3:
            efficiency = perf['dataset_size'] / (perf['memory_usage'] if perf['memory_usage'] > 0 else 1)
            st.metric("メモリ効率", f"{efficiency:.0f}設備/MB")
            st.metric("データセット規模", f"{perf['dataset_size']}設備")
        
        # スケーラビリティ比較
        st.subheader("📈 スケーラビリティ比較")
        
        # 理論値との比較
        baseline_performance = {
            "小規模データ (5設備)": {"time": 1.2, "memory": 1.3},
            "中規模データ (100設備)": {"time": 0.071, "memory": 0.1},
            "大規模データ (457遊具)": {"time": 0.0, "memory": 0.0},  # 実測値を更新
            "超大規模データ (1331遊具)": {"time": 1.946, "memory": 0.9}
        }
        
        current_dataset = st.session_state.get('dataset_option', dataset_option)
        
        if current_dataset in baseline_performance:
            baseline = baseline_performance[current_dataset]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if baseline["time"] > 0 and perf['execution_time'] > 0:
                    time_efficiency = baseline["time"] / perf['execution_time']
                    st.metric(
                        "時間効率", 
                        f"{time_efficiency:.2f}x",
                        help="ベースライン比較 (>1.0が高効率)"
                    )
                else:
                    st.metric("時間効率", "初回測定")
            
            with col2:
                if baseline["memory"] > 0 and perf['memory_usage'] > 0:
                    memory_efficiency = baseline["memory"] / perf['memory_usage']
                    st.metric(
                        "メモリ効率", 
                        f"{memory_efficiency:.2f}x",
                        help="ベースライン比較 (>1.0が高効率)"
                    )
                else:
                    st.metric("メモリ効率", "初回測定")
        
        # パフォーマンスグラフ
        st.subheader("📊 処理時間内訳")
        
        if 'performance' in result:
            perf_data = result['performance']
            
            # 処理時間の内訳
            breakdown_data = {
                'フェーズ': ['データ読み込み', '最適化実行'],
                '時間(秒)': [
                    perf_data.get('load_time', 0),
                    perf_data.get('solve_time', 0)
                ]
            }
            
            fig_breakdown = px.bar(
                breakdown_data,
                x='フェーズ',
                y='時間(秒)',
                title="処理時間内訳",
                color='時間(秒)',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_breakdown, use_container_width=True)
        
        # システムリソース使用状況
        st.subheader("💻 システムリソース")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cpu_percent = psutil.cpu_percent(interval=1)
            st.metric("CPU使用率", f"{cpu_percent:.1f}%")
            
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            st.metric("メモリ使用率", f"{memory_percent:.1f}%")
        
        with col2:
            available_memory = memory.available / (1024**3)
            st.metric("利用可能メモリ", f"{available_memory:.1f}GB")
            
            cpu_cores = psutil.cpu_count()
            st.metric("CPUコア数", f"{cpu_cores}コア")
        
        # パフォーマンス評価
        st.subheader("🏆 パフォーマンス評価")
        
        # 評価基準
        score = 0
        evaluations = []
        
        # 処理時間評価
        time_thresholds = {
            "小規模データ (5設備)": 5,
            "中規模データ (100設備)": 5,
            "大規模データ (457遊具)": 10,
            "超大規模データ (1331遊具)": 30
        }
        
        time_threshold = time_thresholds.get(current_dataset, 10)
        if perf['execution_time'] <= time_threshold:
            evaluations.append("⏱️ 処理時間: ◯")
            score += 1
        else:
            evaluations.append("⏱️ 処理時間: △")
        
        # メモリ効率評価
        memory_thresholds = {
            "小規模データ (5設備)": 10,
            "中規模データ (100設備)": 100,
            "大規模データ (457遊具)": 500,
            "超大規模データ (1331遊具)": 1000
        }
        
        memory_threshold = memory_thresholds.get(current_dataset, 100)
        if perf['memory_usage'] <= memory_threshold:
            evaluations.append("💾 メモリ効率: ◯")
            score += 1
        else:
            evaluations.append("💾 メモリ効率: △")
        
        # スループット評価
        throughput = perf['dataset_size'] / perf['execution_time']
        if throughput >= 100:  # 100設備/秒以上
            evaluations.append("🚀 処理速度: ◯")
            score += 1
        else:
            evaluations.append("🚀 処理速度: △")
        
        # 総合評価
        rating = ["D", "C", "B", "A", "S"][min(score, 4)]
        
        st.success(f"**総合評価: {rating}ランク ({score}/3)**")
        for evaluation in evaluations:
            st.write(evaluation)
    
    else:
        st.info("スケジュール実行後にパフォーマンス情報が表示されます。")

# Tab5: 詳細レポート
with tab5:
    st.header("📋 詳細レポート")
    
    if 'schedule_result' in st.session_state:
        result = st.session_state.schedule_result
        
        # レポートサマリー
        st.subheader("📊 レポートサマリー")
        
        report_summary = {
            "システムバージョン": "v5.2.1",
            "データセット": dataset_option,
            "スケジューリング戦略": strategy,
            "計画期間": f"{start_year}-{end_year}",
            "総設備数": len(scheduler.equipment),
            "スケジュール済タスク": result['statistics']['scheduled_tasks'],
            "成功率": f"{result['statistics']['scheduling_ratio']*100:.1f}%",
            "総コスト": f"¥{result['statistics']['total_cost']:,.0f}",
            "総ペナルティ": f"¥{result['statistics']['total_penalty']:,.0f}",
            "実行日時": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        for key, value in report_summary.items():
            st.write(f"**{key}**: {value}")
        
        # JSON出力
        st.subheader("スケジュール結果（JSON）")
        with st.expander("JSON データを表示"):
            st.json(result)
        
        # CSV ダウンロード
        st.subheader("📥 データダウンロード")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 スケジュール結果をCSVでダウンロード"):
                schedule_data = []
                for task_id, task_data in result['schedule'].items():
                    equipment_id = task_data['equipment_id']
                    if equipment_id not in scheduler.equipment:
                        continue  # 見つからない設備IDはスキップ
                        
                    equipment = scheduler.equipment[equipment_id]
                    state = equipment.current_state
                    
                    schedule_data.append({
                        'task_id': task_id,
                        'equipment_id': task_data['equipment_id'],
                        'park_name': equipment.park_name,
                        'equipment_type': equipment.equipment_type,
                        'install_year': equipment.install_year,
                        'degradation_grade': state.grade.upper() if state else 'N/A',
                        'degradation_score': state.score if state else 0,
                        'scheduled_year': task_data['scheduled_year'],
                        'priority': task_data['priority'],
                        'cost': task_data['cost'],
                        'delay_years': task_data['delay_years'],
                        'penalty': task_data['penalty']
                    })
                
                schedule_csv = pd.DataFrame(schedule_data)
                csv_string = schedule_csv.to_csv(index=False, encoding='utf-8-sig')
                
                st.download_button(
                    label="📥 スケジュールCSVダウンロード",
                    data=csv_string,
                    file_name=f"delegator_v5.2.1_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📥 パフォーマンスレポートをJSONでダウンロード"):
                if 'performance_info' in st.session_state:
                    performance_report = {
                        "system_info": {
                            "version": "v5.2.1",
                            "dataset": dataset_option,
                            "timestamp": datetime.now().isoformat()
                        },
                        "performance": st.session_state.performance_info,
                        "results": {
                            "scheduled_tasks": result['statistics']['scheduled_tasks'],
                            "total_tasks": result['statistics']['total_tasks'],
                            "success_rate": result['statistics']['scheduling_ratio'],
                            "total_cost": result['statistics']['total_cost'],
                            "total_penalty": result['statistics']['total_penalty']
                        }
                    }
                    
                    json_string = json.dumps(performance_report, ensure_ascii=False, indent=2)
                    
                    st.download_button(
                        label="📥 パフォーマンスJSONダウンロード",
                        data=json_string,
                        file_name=f"delegator_v5.2.1_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        
        # システム情報
        st.subheader("💻 システム情報")
        system_info = {
            "バージョン": "v5.2.1 (大規模スケーリング対応)",
            "データセット": dataset_option,
            "最大対応設備数": config["max_equipment"],
            "スケジューリング戦略": strategy,
            "並列処理": "有効" if enable_parallel else "無効",
            "計画期間": f"{start_year}-{end_year}",
            "年間予算": f"¥{annual_budget:,.0f}",
            "年間施工能力": f"{annual_capacity}件",
            "システムCPU": f"{psutil.cpu_count()}コア",
            "システムメモリ": f"{psutil.virtual_memory().total / (1024**3):.1f}GB",
            "Python環境": f"Python {sys.version.split()[0]}",
            "実行日時": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        for key, value in system_info.items():
            st.write(f"**{key}**: {value}")
    
    else:
        st.info("スケジュール結果がありません。")

# フッター
st.markdown("---")
st.markdown("**Delegator v5.2.1** - 大規模スケーリング対応状態監視型メンテナンス計画システム | Powered by OptSeq & Streamlit")
st.markdown("最大1331遊具対応 | 並列処理対応 | 現実的ペナルティ設定")
