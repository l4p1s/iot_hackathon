import pyttsx3

def speak_with_pyttsx3(text):
    # pyttsx3のエンジンを初期化
    engine = pyttsx3.init()
    # 声の速度を設定 (オプション)
    engine.setProperty('rate', 150)
    # 声の種類を設定 (オプション)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # 女性の声に設定

    # テキストを読み上げ
    engine.say(text)
    engine.runAndWait()

# 英語のテキストを再生
speak_with_pyttsx3("Hello, how are you?")
