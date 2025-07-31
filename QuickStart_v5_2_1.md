# 🚀 Delegator v5.2.1 QuickStart Guide

大規模スケーリング対応状態監視型メンテナンス計画システムの素早いスタートアップガイド

## ⚡ 30秒で開始

### 1. 前提条件確認

```powershell
# Python バージョン確認（3.8以上が必要）
python --version

# 必要パッケージインストール
pip install pandas numpy streamlit plotly psutil joblib
```

### 2. ファイル確認

```powershell
# 必要ファイルの存在確認
ls delegator_v5_2_1.py
ls streamlit_app_v5_2_1.py
ls input_park_playequipment*.csv
ls inspectionList_parkEquipment*.csv
```

### 3. 即時実行

```powershell
# Streamlit UI起動（推奨）
streamlit run streamlit_app_v5_2_1.py
```

🎉 **完了！** ブラウザで `http://localhost:8501` にアクセス

---

## 📊 データセット選択ガイド

### スケール別推奨用途

| データセット                  | 遊具数 | 用途                    | 実行時間 | メモリ使用量 |
| ----------------------------- | ------ | ----------------------- | -------- | ------------ |
| **小規模 (5設備)**      | 5      | 🔰 初回テスト・動作確認 | 1.2秒    | 1.3MB        |
| **中規模 (100設備)**    | 100    | 📚 機能学習・デモ       | 0.071秒  | 0.1MB        |
| **大規模 (457遊具)**    | 457    | 🏢 実用規模テスト       | < 5秒    | < 10MB       |
| **超大規模 (1331遊具)** | 1331   | 🌟 本格運用・性能検証   | 1.946秒  | 0.9MB        |

### 推奨開始手順

1. **小規模**で動作確認 → 2. **中規模**で機能理解 → 3. **大規模**で実用テスト → 4. **超大規模**で本格運用

---

## 🎯 5分間クイックツアー

### Step 1: 起動と設定 (1分)

```powershell
streamlit run streamlit_app_v5_2_1.py
```

- サイドバーで「中規模データ (100設備)」を選択
- 年間予算: 400万円（デフォルト）
- 年間施工能力: 20件（デフォルト）

### Step 2: データ確認 (1分)

- **「📊 設備状況」タブ**をクリック
- 劣化状態分布を確認
- 統計サマリーをチェック

### Step 3: 最適化実行 (1分)

- サイドバーの「🚀 スケジュール実行」をクリック
- 自動最適化の実行（約0.1秒で完了）
- **「📅 スケジュール結果」タブ**で結果確認

### Step 4: 視覚化確認 (1分)

- **「📈 ガントチャート」タブ**でスケジュール可視化
- 劣化判定別の色分け確認
- **「⚡ パフォーマンス」タブ**で性能指標確認

### Step 5: 結果出力 (1分)

- **「📋 詳細レポート」タブ**でデータ出力
- CSV/JSON形式でのダウンロード
- システム情報の確認

🎉 **完了！** 基本機能を完全理解

---

## 🔧 コマンドライン使用法

### 基本実行

```python
from delegator_v5_2_1 import OptSeqSchedulerScalable

# スケジューラー初期化
scheduler = OptSeqSchedulerScalable(2025, 2040, max_equipment=100)

# データ読み込み
scheduler.load_equipment_data(
    'input_park_playequipment_100.csv',
    'inspectionList_parkEquipment_100.csv'
)

# 最適化実行
result = scheduler.solve_parallel('greedy_priority')

# 結果表示
print(f"成功率: {result['statistics']['scheduling_ratio']*100:.1f}%")
print(f"総コスト: ¥{result['statistics']['total_cost']:,.0f}")
print(f"実行時間: {result['performance']['solve_time']:.3f}秒")
```

### 大規模データ実行

```python
# 1331遊具対応
scheduler = OptSeqSchedulerScalable(2025, 2040, max_equipment=1500)

scheduler.load_equipment_data(
    'input_park_playequipment_241.csv',
    'inspectionList_parkEquipment_1331.csv'
)

result = scheduler.solve_parallel()
# 約2秒で1331遊具を処理
```

---

## 🛠️ カスタマイズ設定

### 予算・能力調整

```python
# カスタム制約条件
annual_budget = 10000000      # 1000万円
annual_capacity = 50          # 50件/年

# サイドバーで直接調整も可能
```

### 期間設定

```python
scheduler = OptSeqSchedulerScalable(
    start_year=2025,    # 開始年
    end_year=2050,      # 終了年（25年計画）
    max_equipment=1500  # 最大遊具数
)
```

### 戦略選択

```python
# 最適化戦略
strategies = [
    "greedy_priority",      # 優先度優先（推奨）
    "cost_optimal",         # コスト最適化
    "penalty_minimization"  # ペナルティ最小化
]

result = scheduler.solve_parallel(strategy="greedy_priority")
```

---

## 🔍 トラブルシューティング

### よくある問題と解決法

#### 1. 起動エラー

**エラー**: `ModuleNotFoundError: No module named 'streamlit'`

```powershell
# 解決法
pip install streamlit plotly pandas numpy psutil joblib
```

#### 2. データファイルエラー

**エラー**: `FileNotFoundError: input_park_playequipment.csv`

```powershell
# 確認
ls *.csv

# 小規模データから開始
# サイドバーで「小規模データ (5設備)」を選択
```

#### 3. メモリエラー

**問題**: 大規模データでメモリ不足

```python
# 解決法: max_equipment調整
scheduler = OptSeqSchedulerScalable(max_equipment=500)  # 制限を設定
```

#### 4. 実行時間長期化

**問題**: 処理が遅い

```python
# 解決法: 並列処理確認
import multiprocessing
print(f"CPU cores: {multiprocessing.cpu_count()}")

# サイドバーで「並列処理を有効化」をチェック
```

#### 5. 結果が表示されない

**問題**: スケジュール結果が空

- 予算・能力制約が厳しすぎる可能性
- 年間予算を増額
- 年間施工能力を増加

---

## 📈 パフォーマンス最適化Tips

### 高速実行のコツ

1. **並列処理有効化**: サイドバーでチェック
2. **適切なデータセット**: 用途に応じた規模選択
3. **メモリ監視**: パフォーマンスタブで確認
4. **バッチ処理**: 大規模データで自動適用

### メモリ効率化

```python
# バッチサイズ調整（内部で自動実行）
batch_size = max(1, len(equipment) // cpu_cores)
```

### 並列処理設定

```python
# CPU コア数確認
import psutil
print(f"利用可能コア: {psutil.cpu_count()}")

# 並列度自動調整（内部処理）
n_jobs = min(cpu_cores, equipment_count)
```

---

## 🎯 実用シナリオ別ガイド

### シナリオ1: 初回評価・デモ

```
目的: システム理解・機能確認
推奨: 中規模データ (100設備)
手順: UI起動 → 設備状況確認 → 実行 → 結果確認
時間: 5分
```

### シナリオ2: 実用規模テスト

```
目的: 実際の運用想定での検証
推奨: 大規模データ (457遊具)
手順: 制約調整 → 実行 → パフォーマンス確認 → 結果出力
時間: 10分
```

### シナリオ3: 本格運用・性能検証

```
目的: 最大規模での性能確認
推奨: 超大規模データ (1331遊具)
手順: 詳細設定 → 実行 → 全機能確認 → レポート生成
時間: 15分
```

### シナリオ4: 自動化・バッチ処理

```python
# 定期実行用スクリプト
import schedule
import time

def run_optimization():
    scheduler = OptSeqSchedulerScalable(max_equipment=1500)
    scheduler.load_equipment_data('latest_data.csv', 'latest_inspection.csv')
    result = scheduler.solve_parallel()
  
    # 結果保存
    with open(f'result_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

# 週次実行設定
schedule.every().monday.at("09:00").do(run_optimization)
```

---

## 📚 学習リソース

### 理解を深めるための順序

1. **README_v5_2_1.md**: 全体概要・技術仕様
2. **QuickStart_v5_2_1.md**: 本ガイド（実践方法）
3. **delegator_v5_2_1.py**: コア実装（ソースコード学習）
4. **streamlit_app_v5_2_1.py**: UI実装（カスタマイズ参考）

### 重要概念

- **劣化スコア**: 年数×0.6 + 点検結果×0.4
- **優先度**: 劣化度合いに応じた1-5段階
- **ペナルティ**: 遅延年数×係数×コスト×0.001
- **制約条件**: 年間予算・施工能力の上限

### アルゴリズム理解

```python
# 基本フロー
1. データ読み込み → 劣化スコア計算（並列）
2. タスク生成 → 優先度ソート
3. 制約満足スケジューリング → 結果出力
```

---

## 🚀 次のステップ

### 基本習得後の発展

1. **カスタムデータ**: 独自のCSVデータでテスト
2. **戦略比較**: 3つの最適化戦略の比較
3. **制約調整**: 予算・能力による結果変化の確認
4. **長期計画**: 25年計画での実行

### 応用開発

1. **API化**: REST API での呼び出し
2. **データベース連携**: PostgreSQL/MySQL接続
3. **リアルタイム更新**: IoTデータとの統合
4. **機械学習**: 劣化予測モデルの導入

### システム統合

1. **既存システム連携**: ERP/CMSとの統合
2. **モバイル対応**: アプリ化・レスポンシブ対応
3. **クラウド展開**: AWS/Azure でのスケールアウト
4. **CI/CD**: 自動テスト・自動デプロイ

---

## 📞 サポート・コミュニティ

### ヘルプ情報

- **GitHub Issues**: バグ報告・機能要望
- **README詳細版**: README_v5_2_1.md
- **ソースコメント**: 実装詳細の理解

### 貢献方法

1. **バグ報告**: 再現手順と環境情報
2. **機能要望**: 具体的な用途と期待値
3. **コード改善**: Pull Request歓迎
4. **ドキュメント**: 使用例・Tips共有

---

**🎉 Delegator v5.2.1で効率的なメンテナンス計画を！**

*このQuickStartガイドで、5分後には大規模遊具管理システムを実際に動かすことができます。*

---

*Last Updated: 2025-07-25*
*Version: v5.2.1*
*© 2025 CWD Agent*
