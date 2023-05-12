from aip import AipSpeech

""" 你的 APPID AK SK """
APP_ID = '28850651'
API_KEY = 'VUcnqZ5syH1iHTgMsHMIiqBW'
SECRET_KEY = 'wQt6FNNkTeCyfH77eG8zCUqi9p8ZiXsE'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

with open('b.text', mode='r', encoding='utf-8') as f:
    flag = 0
    while True:
        flag += 1
        text = f.read(500)
        if not text:
            break
        print(text)
        print('......')


        result = client.synthesis(text, 'zh', 1, {
            'vol': 5,
            'spd': 4,
        })

        # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
        if not isinstance(result, dict):
            with open('video\\{}.mp3'.format(str(flag)), 'wb') as file:
                file.write(result)
                print('正在生成第{}段语音...'.format(flag))