import pyttsx3  # テキスト読み上げライブラリ
import datetime
import paho.mqtt.client as mqtt
import json  # JSONを処理するためのライブラリ

# 現在の日時を取得
dt_now = datetime.datetime.now()

# MQTT Broker の設定
BROKER_ADDRESS = "******************.cloud.shiftr.io"
BROKER_PORT = 1883
TOPIC = "send"
USERNAME = "*****************"
PASSWORD = "**************"

# テキスト読み上げエンジンの初期化
engine = pyttsx3.init()

# MQTT 接続時のコールバック
def on_connect(client, userdata, flag, rc):
    if rc == 0:
        print("Connected successfully")
        client.subscribe(TOPIC)  # 購読するトピックを設定
    else:
        print(f"Connection failed with result code {rc}")

# MQTT メッセージ受信時のコールバック
def on_message(client, userdata, msg):
    try:
        # JSON形式のメッセージをデコード
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)  # JSON形式のデータを辞書型に変換

        print(data)

        # 日本語を含むメッセージの作成
        station = data["station"]
        get_on_people = data["get_on_people"]
        get_off_people = data["get_off_people"]

        message = (f"ご乗車ありがとうございました。"
                   f"{station} バス停です。"
                   f"{get_on_people} 人乗車されました。"
                   f"{get_off_people} 人降車されました。"
                   f"またのご利用をお待ちしております。")
        
        # メッセージの表示と読み上げ
        print(message)
        engine.say(message)
        engine.runAndWait()
    except Exception as e:
        print(f"Error processing message: {e}")

# MQTT クライアントのセットアップ
client = mqtt.Client()
client.username_pw_set(USERNAME, password=PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# ブローカーに接続し、ループを開始
client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
client.loop_forever()
