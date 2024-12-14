import sqlite3
import json
import requests
import paho.mqtt.client as mqtt
from threading import Timer, Lock

# MQTT設定
BROKER_ADDRESS = "***********.cloud.shiftr.io"
BROKER_PORT = 1883
TOPIC1 = "sample"
TOPIC2 = "send"
username = "****************"
password = "***************"

# バス停データ累積用
bus_stop_data = {}
lock = Lock()

# タイマー管理用
pending_timers = {}

# データを挿入
def insert_data(bus_stop_name, passengers_boarded, passengers_alighted):
    conn = sqlite3.connect("iot_hack.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bus_stop_data (bus_stop_name, passengers_boarded, passengers_alighted)
        VALUES (?, ?, ?)
    """, (bus_stop_name, passengers_boarded, passengers_alighted))
    conn.commit()
    conn.close()

# データを送信
def publish_data(client, topic, bus_stop_name, passengers_boarded, passengers_alighted):
    send_data = {
        "station": bus_stop_name,
        "get_on_people": passengers_boarded,
        "get_off_people": passengers_alighted,
    }
    payload = json.dumps(send_data)
    try:
        client.publish(topic, payload)
        print(f"Published data to topic '{topic}': {payload}")
    except Exception as e:
        print(f"Failed to publish data: {e}")

# タイマー処理
def handle_timer(client, bus_stop_name):
    global bus_stop_data, pending_timers

    with lock:
        if bus_stop_name in bus_stop_data:
            boarded = bus_stop_data[bus_stop_name]["boarded"]
            alighted = bus_stop_data[bus_stop_name]["alighted"]

            # データベースに保存
            insert_data(bus_stop_name, boarded, alighted)

            # データ送信
            publish_data(client, TOPIC2, bus_stop_name, boarded, alighted)

            # データをリセット
            del bus_stop_data[bus_stop_name]
            if bus_stop_name in pending_timers:
                del pending_timers[bus_stop_name]

# MQTTコールバック関数
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(TOPIC1)

def on_message(client, userdata, msg):
    global bus_stop_data, pending_timers

    # デバッグ用にトピックとペイロードを表示
    print(f"Received on topic '{msg.topic}': {msg.payload.decode()}")

    message = msg.payload.decode()
    try:
        change = int(message.strip())
    except ValueError:
        print("Invalid data format, ignoring message.")
        return

    # バス停情報を取得する処理（簡略化）
    url = "https://komelabo.sakura.ne.jp/utazu/api/orion.php?type=Bus&id=jp.kagawa.utazu.Bus.592"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data and "location" in data[0]:
            location_value = data[0]["location"]["value"]
            latitude, longitude = location_value.split(",")
            print(f"Latitude: {latitude}, Longitude: {longitude}")
        else:
            print("Location data not found in response.")
            return
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return

    # 近隣バス停情報の取得
    api_url = f"https://komelabo.sakura.ne.jp/utazu/api/orion.php?type=BusStop&q=is_visible==true&georel=near;maxDistance:100&geometry=point&coords={latitude},{longitude}"
    response = requests.get(api_url)
    if response.status_code == 200:
        try:
            location_data = response.json()
            if location_data:  # バス停情報がある場合
                bus_stop_name = location_data[0]["title"]["value"]
            else:  # バス停情報がない場合
                bus_stop_name = "non exist bus stop station"
        except (ValueError, KeyError, TypeError) as e:
            print("Error processing location data:", e)
            return
    else:
        print("Failed to retrieve location data, status code:", response.status_code)
        return

    # 累計データの更新
    with lock:
        # バス停名が変わった場合、即時保存と送信
        if bus_stop_name not in bus_stop_data or (pending_timers.get(bus_stop_name) and not pending_timers[bus_stop_name].is_alive()):
            if bus_stop_name in bus_stop_data:
                boarded = bus_stop_data[bus_stop_name]["boarded"]
                alighted = bus_stop_data[bus_stop_name]["alighted"]
                insert_data(bus_stop_name, boarded, alighted)
                publish_data(client, TOPIC2, bus_stop_name, boarded, alighted)
                del bus_stop_data[bus_stop_name]
                if bus_stop_name in pending_timers:
                    del pending_timers[bus_stop_name]

        if bus_stop_name not in bus_stop_data:
            bus_stop_data[bus_stop_name] = {"boarded": 0, "alighted": 0}

        if change > 0:
            bus_stop_data[bus_stop_name]["boarded"] += abs(change)
        elif change < 0:
            bus_stop_data[bus_stop_name]["alighted"] += abs(change)

        # タイマーのセット
        if bus_stop_name not in pending_timers:
            timer = Timer(120, handle_timer, args=(client, bus_stop_name))
            pending_timers[bus_stop_name] = timer
            timer.start()

        # 累計データの表示
        boarded = bus_stop_data[bus_stop_name]["boarded"]
        alighted = bus_stop_data[bus_stop_name]["alighted"]
        print(f"Bus Stop: {bus_stop_name}, Boarded: {boarded}, Alighted: {alighted}")

# メイン処理
if __name__ == "__main__":
    client = mqtt.Client()
    client.username_pw_set(username, password=password)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
    client.loop_forever()
