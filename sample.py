import json
import paho.mqtt.client as mqtt
import time

# ブローカーの設定      

BROKER_ADDRESS = "**************"  # Broker address
BROKER_PORT = 1883                                 # Broker port
TOPIC = "sample"                                     # Topic to subscribe to
username = "*************"
password = "***********"

# 送信する位置情報
people_data = {
    "get_on": 3,      # 緯度
    "get_off": 1     # 経度
}

# クライアントの初期設定
client = mqtt.Client()

client.username_pw_set(username, password=password)
# ブローカーに接続
client.connect(BROKER_ADDRESS, BROKER_PORT, 60)

# JSON形式の位置情報データを文字列に変換
payload = json.dumps(people_data)

# トピックにデータを送信
client.publish(TOPIC, "1")
client.publish(TOPIC, "1")
time.sleep(10)
client.publish(TOPIC, "1")
client.publish(TOPIC, "-1")
time.sleep(10)
client.publish(TOPIC, "-1")
print(f"Published: {payload} to topic {TOPIC}")

# 切断
client.disconnect()
