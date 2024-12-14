import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# データベース接続
def connect_db(db_path="iot_hack.db"):
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
    st.sidebar.text_area("データベースパス", value="../iot_hack.db", disabled=True, height=68)
    st.sidebar.text_area("SQLクエリ", value="SELECT * FROM bus_stop_data", disabled=True, height=100)

    # データベース接続とデータ取得
    try:
        db_path = "../iot_hack.db"
        query = "SELECT * FROM bus_stop_data"
        conn = connect_db(db_path)
        data = fetch_data(conn, query)

        # タイムスタンプをdatetime型に変換
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])

        # データを表示
        st.write("### データベースデータ")
        st.dataframe(data)

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
        graph_type = st.radio("グラフの種類を選択", ("時系列プロット", "バス停名別棒グラフ"))

        options_dict = {
            'passengers_boarded': '乗車人数',
            'passengers_alighted': '降車人数'
        }
        options = [col for col in options_dict.keys() if col in filtered_data.columns]

        display_options = [options_dict[col] for col in options]
        if options:
            selected_option = st.selectbox("グラフ化する項目を選択", display_options)
            metric = [key for key, value in options_dict.items() if value == selected_option][0]

            if graph_type == "時系列プロット":
                # Plotlyによる時系列プロット
                fig = px.line(
                    filtered_data,
                    x='timestamp',
                    y=metric,
                    title=f"{selected_option} の時系列プロット",
                    labels={
                        'timestamp': '日時',
                        metric: selected_option
                    },
                    template='plotly_white',
                    markers=True
                )

                fig.update_traces(line_shape='linear', marker=dict(size=8))
                fig.update_layout(
                    xaxis_title="日時",
                    yaxis_title=selected_option,
                    font=dict(size=14)
                )

                st.plotly_chart(fig)

            elif graph_type == "バス停名別棒グラフ":
                # バス停名ごとにデータを集計
                if 'bus_stop_name' in filtered_data.columns:
                    grouped_data = filtered_data.groupby('bus_stop_name')[metric].sum().reset_index()

                    fig = px.bar(
                        grouped_data,
                        x='bus_stop_name',
                        y=metric,
                        title=f"{selected_option} のバス停名別棒グラフ",
                        labels={
                            'bus_stop_name': 'バス停名',
                            metric: selected_option
                        },
                        template='plotly_white'
                    )

                    fig.update_layout(
                        xaxis_title="バス停名",
                        yaxis_title=selected_option,
                        font=dict(size=14)
                    )

                    st.plotly_chart(fig)
                else:
                    st.warning("バス停名データが存在しません。")
        else:
            st.info("可視化可能な数値データがありません。")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
