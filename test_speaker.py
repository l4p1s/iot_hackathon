from gtts import gTTS
from playsound import playsound
import os
import tempfile

def play_japanese_text(text):
    try:
        # 日本語テキストを音声合成
        tts = gTTS(text=text, lang='ja')

        # 一時ファイルを作成
        fd, path = tempfile.mkstemp(suffix=".mp3")
        try:
            # 一時ファイルに保存
            tts.save(path)
            # 音声ファイルを再生
            playsound(path)
        finally:
            # 再生後に一時ファイルを削除
            os.close(fd)
            os.remove(path)

    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 任意の日本語テキストを指定
play_japanese_text("こんにちは、世界。今日は良い天気ですね。")
print("再生しました")
