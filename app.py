import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="脳レーシング AI予想＆自動学習", layout="wide")
st.title("🏇 脳レーシング 単勝AI学習＆予測サイト")

# 1. 学習データベースの読み込み・初期化
DATA_FILE = "brain_racing_learning_db.csv"

mark_scores = {
    '◎': 10, '◯': 8,  '△': 6,  '✕': 4,
    '⑳': 7,  '●': 5,  '▲': 4,  '✖': 2,
    '☆': 1.5, '★': 1.0, 'T': 1.0, '無印': 0
}

# サイドバー：過去学習データの管理
st.sidebar.header("📊 AIの学習データ状況")
if os.path.exists(DATA_FILE):
    db_df = pd.read_csv(DATA_FILE)
    st.sidebar.metric("蓄積データ数", f"{len(db_df)} 件")
    st.sidebar.dataframe(db_df.tail(10))
else:
    # 初期空データベース作成
    db_df = pd.DataFrame(columns=['car', 'pt', 'mark', 'mark_score', 'is_1st'])
    db_df.to_csv(DATA_FILE, index=False)
    st.sidebar.write("現在データは0件です。結果を登録してAIを育てましょう！")

# 2. メイン画面：出走表データ（スクショ確認 & データ確認）
st.header("1. 出走表スクショ & レースデータ設定")
uploaded_file = st.file_uploader("出走表のスクショを選択してください", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    col_img, col_data = st.columns([1, 2])
    with col_img:
        st.image(uploaded_file, caption="選択したスクショ", use_container_width=True)
    
    with col_data:
        st.subheader("📝 7車のデータ確認（競走得点・脳ルール印）")
        st.caption("※スクショを見ながら、各車の得点と脳ルール適用後の最終印を確認・調整します。")
        
        # デフォルト入力用のデータフレーム
        input_data = []
        for i in range(1, 8):
            c1, c2, c3 = st.columns([1, 2, 2])
            with c1:
                st.write(f"**{i}番車**")
            with c2:
                pt = st.number_input(f"得点 ({i}番)", value=80.0, step=0.1, key=f"pt_{i}")
            with c3:
                mark = st.selectbox(f"最終印 ({i}番)", list(mark_scores.keys()), index=0 if i==1 else 13, key=f"mark_{i}")
            
            input_data.append({"car": i, "pt": pt, "mark": mark, "mark_score": mark_scores[mark]})

        race_df = pd.DataFrame(input_data)

    # 3. AIによる1着予測（リアルタイム算出）
    st.divider()
    st.header("2. 🤖 AIの1着予測（可能性順）")

    # 学習済みデータがあればRandomForestで予測、無ければ初期ルールで算出
    if len(db_df) >= 10 and db_df['is_1st'].sum() > 0:
        X_train = db_df[['car', 'pt', 'mark_score']]
        y_train = db_df['is_1st']
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        # 1着確率の試算
        probs = model.predict_proba(race_df[['car', 'pt', 'mark_score']])[:, 1]
        race_df['AI1着確率'] = (probs * 100).round(1)
        race_df['ai_score'] = probs
    else:
        # データ蓄積初期のスコア算出ロジック（得点正規化 + 印スコア）
        pt_norm = (race_df['pt'] - race_df['pt'].min()) / (race_df['pt'].max() - race_df['pt'].min() + 0.001) * 10
        race_df['ai_score'] = pt_norm * 0.5 + race_df['mark_score'] * 0.5
        race_df['AI1着確率'] = (race_df['ai_score'] / race_df['ai_score'].sum() * 100).round(1)

    # ランキング順に並び替え
    ranking = race_df.sort_values(by='ai_score', ascending=False).reset_index(drop=True)
    
    st.subheader("🏆 1着可能性ランキング")
    for rank, row in ranking.iterrows():
        st.write(f"**{rank+1}位**: **{int(row['car'])}番車** （競走得点: {row['pt']} / 印: {row['mark']}） ── **1着予想確率: {row['AI1着確率']}%**")

    # 4. レース結果の登録と自動学習
    st.divider()
    st.header("3. 📝 レース結果の登録（AI自動学習）")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        win_car = st.number_input("1着の車番", min_value=1, max_value=7, value=int(ranking.iloc[0]['car']))
    
    if st.button("🚀 レース結果を登録してAIに学習させる！"):
        # レース結果フラグのセット
        race_df['is_1st'] = race_df['car'].apply(lambda x: 1 if x == win_car else 0)
        
        # 学習データベースに追加保存
        new_save_df = race_df[['car', 'pt', 'mark', 'mark_score', 'is_1st']]
        new_save_df.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)
        
        st.success(f"1着: {win_car}番車の結果を学習データベースに蓄積しました！AIが進化しました。")
        st.balloons()
