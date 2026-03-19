import streamlit as st
import random
import pandas as pd

# --- デッキデータ設定 ---
# メインボード
DECK_LIST = {
    "再点火、アシュリング": 4,
    "龍へと昇る者、サルカン": 4,
    "マグマのヘルカイト": 3,
    "うろつく玉座": 3,
    "北風の守護者": 4,
    "マラング川の執政": 2,
    "呪文嵌め": 2,
    "炎魔法": 2,
    "星間航路の助言": 4,
    "払拭の吐息": 3,
    "アシュリングの命令": 2,
    "紅蓮地獄": 3,
    "魂の洞窟": 4,
    "島": 3,
    "山": 1,
    "マルチバースへの通り道": 4,
    "リバーパイアーの境界": 4,
    "尖塔断の運河": 4,
    "蒸気孔": 4
}

# カードのタイプ分類（簡易版）
CARD_TYPES = {
    "再点火、アシュリング": "エレメンタル/加速",
    "龍へと昇る者、サルカン": "人間/加速",
    "マグマのヘルカイト": "ドラゴン/フィニッシャー",
    "うろつく玉座": "ゴーレム/シナジー",
    "北風の守護者": "ドラゴン/サーチ",
    "マラング川の執政": "ドラゴン/除去",
    "星間航路の助言": "サーチ",
    "紅蓮地獄": "除去",
    "アシュリングの命令": "除去/コピー",
    "魂の洞窟": "土地", "島": "土地", "山": "土地", "マルチバースへの通り道": "土地",
    "リバーパイアーの境界": "土地", "尖塔断の運河": "土地", "蒸気孔": "土地"
}

# --- アプリの関数 ---
def create_deck():
    full_deck = []
    for card, count in DECK_LIST.items():
        full_deck.extend([card] * count)
    random.shuffle(full_deck)
    return full_deck

def is_land(card_name):
    return CARD_TYPES.get(card_name, "") == "土地"

def check_3rd_turn_play(hand):
    # 3ターン目4マナ到達の簡易判定ロジック
    lands = [c for c in hand if is_land(c)]
    has_ashling = "再点火、アシュリング" in hand
    has_sarkhan = "龍へと昇る者、サルカン" in hand
    has_magma = "マグマのヘルカイト" in hand
    has_throne = "うろつく玉座" in hand
    
    status = []
    if len(lands) >= 3:
        if has_ashling or has_sarkhan:
            if has_magma:
                status.append("🔥 3Tヘルカイト可能です！")
            if has_throne:
                status.append("🤖 3T玉座可能です！")
            if not status:
                status.append("✨ 3T4マナ加速は可能ですが、4マナ域がありません。")
        else:
            status.append("⚠️ 3T4マナ加速パーツ（アシュリング/サルカン）がありません。")
    else:
        status.append(f"💧 土地が足りません（現在{len(lands)}枚）。")
        
    return status

# --- アプリの画面構成（UI） ---
st.set_page_config(page_title="イゼット・マグマ・ドラゴン テスター", page_icon="🐉")
st.title("🐉 イゼット・マグマ・ドラゴン専用テスター")
st.markdown("Windows/Android対応 | ジャパンスタンダードカップ2026仕様")

# セッション状態の初期化
if 'deck' not in st.session_state:
    st.session_state.deck = create_deck()
    st.session_state.hand = st.session_state.deck[:7]
    st.session_state.mulligan_count = 0
    st.session_state.turn = 1
    st.session_state.battlefield = []

# --- サイドバー（操作パネル） ---
with st.sidebar:
    st.header("操作パネル")
    if st.button("🔄 最初からやり直す（リセット）"):
        st.session_state.deck = create_deck()
        st.session_state.hand = st.session_state.deck[:7]
        st.session_state.mulligan_count = 0
        st.session_state.turn = 1
        st.session_state.battlefield = []
        st.experimental_rerun()
        
    if st.button("🃏 マリガンする"):
        st.session_state.mulligan_count += 1
        st.session_state.deck = create_deck()
        st.session_state.hand = st.session_state.deck[:7]
        st.write(f"マリガン回数: {st.session_state.mulligan_count}")
        st.experimental_rerun()

    st.markdown("---")
    if st.button("⏭️ 次のターン（ドロー）"):
        if len(st.session_state.deck) > (7 + st.session_state.turn):
            new_card = st.session_state.deck[7 + st.session_state.turn - 1]
            st.session_state.hand.append(new_card)
            st.session_state.turn += 1
            st.experimental_rerun()
        else:
            st.error("ライブラリーアウトです！")

# --- メインエリア ---
# 現在の状態表示
col1, col2 = st.columns(2)
with col1:
    st.metric(label="現在のターン", value=st.session_state.turn)
with col2:
    st.metric(label="マリガン回数", value=st.session_state.mulligan_count)

# 手札の表示
st.subheader("🃏 現在の手札")
hand_df = pd.DataFrame([{"カード名": card, "タイプ": CARD_TYPES.get(card, "不明")} for card in st.session_state.hand])
st.dataframe(hand_df, use_container_width=True)

# 3ターン目の動き判定
st.subheader("🎯 3ターン目の動き診断")
status_messages = check_3rd_turn_play(st.session_state.hand)
for msg in status_messages:
    if "🔥" in msg or "🤖" in msg:
        st.success(msg)
    elif "⚠️" in msg:
        st.warning(msg)
    else:
        st.info(msg)

# 戦場の展開（簡易版）
st.subheader("⚔️ 戦場の展開（テスト）")
lands_in_hand = [c for c in st.session_state.hand if is_land(c)]
spells_in_hand = [c for c in st.session_state.hand if not is_land(c)]

col3, col4 = st.columns(2)
with col3:
    land_to_play = st.selectbox("土地を置く", ["選択してください"] + list(set(lands_in_hand)))
    if st.button("土地を戦場に出す") and land_to_play != "選択してください":
        st.session_state.battlefield.append(f"⛺ {land_to_play}")
        st.session_state.hand.remove(land_to_play)
        st.experimental_rerun()

with col4:
    spell_to_cast = st.selectbox("呪文を唱える", ["選択してください"] + list(set(spells_in_hand)))
    if st.button("呪文をキャスト") and spell_to_cast != "選択してください":
        st.session_state.battlefield.append(f"✨ {spell_to_cast}")
        st.session_state.hand.remove(spell_to_cast)
        st.experimental_rerun()

st.write("▼ 現在の戦場 ▼")
st.write(st.session_state.battlefield)