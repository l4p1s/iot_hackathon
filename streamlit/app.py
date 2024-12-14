import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# データベース接続
def connect_db(db_path="../iot_hack.db"):
    """SQLiteデータベースに接続する"""
    conn = sqlite3.connect(db_path)
    return conn

# データの取得
def fetch_data(conn, query="SELECT * FROM bus_stop_data"):
    """クエリを実行してデータを取得する"""
    return pd.read_sql_query(query, conn)

# Streamlitアプリケーション
def main():
    st.title("バス停データ可視化アプリ")

    # サイドバーで設定
    st.sidebar.header("設定")
    db_path = st.sidebar.text_input("データベースパス", value="../iot_hack.db")
    query = st.sidebar.text_area("SQLクエリ", value="SELECT * FROM bus_stop_data")

    # データベース接続とデータ取得
    try:
        conn = connect_db(db_path)
        data = fetch_data(conn, query)

        # タイムスタンプをdatetime型に変換
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])

        # データを表示
        st.write("### データベースデータ")
        # st.dataframe(data)

        # フィルタリング
        if 'timestamp' in data.columns:
            st.sidebar.write("\n**データのフィルタリング**")
            min_date = data['timestamp'].min().date()
            max_date = data['timestamp'].max().date()
            start_date = st.sidebar.date_input("開始日", value=min_date, min_value=min_date, max_value=max_date)
            end_date = st.sidebar.date_input("終了日", value=max_date, min_value=min_date, max_value=max_date)

            filtered_data = data[(data['timestamp'] >= pd.Timestamp(start_date)) & (data['timestamp'] <= pd.Timestamp(end_date))]
        else:
            filtered_data = data

        # グラフ化
        st.write("### グラフ化")
        options = [col for col in ['passengers_boarded', 'passengers_alighted'] if col in filtered_data.columns]

        if options:
            metric = st.selectbox("グラフ化する項目を選択", options)

            # Plotlyによる時系列プロット
            fig = px.line(
                filtered_data, 
                x='timestamp', 
                y=metric, 
                title=f"{metric} の時系列プロット",
                labels={
                    'timestamp': '日時',
                    metric: metric
                },
                template='plotly_white',
                markers=True
            )

            fig.update_traces(line_shape='linear', marker=dict(size=8))
            fig.update_layout(
                xaxis_title="日時",
                yaxis_title=metric,
                font=dict(size=14)
            )

            st.plotly_chart(fig)

        else:
            st.info("可視化可能な数値データがありません。")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
