import websocket
import speech_recognition as sr
import threading
import uuid
import json
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
import ssl
import requests
import re
import cn2an
from aip import AipSpeech
"""
1. 连接 ws_app.run_forever()           # 主函数
2. 连接成功后发送数据 on_open()          
2.1 发送开始参数帧 send_start_params()
2.2 发送音频数据帧 send_audio()
2.3 库接收识别结果 on_message()
2.4 发送结束帧 send_finish()
3. 关闭语音识别连接 on_close()
4. 获取 情感识别的token                 # get_token()
5. 调用情感识别API                      # get_label_baidu()
"""
def get_novel(number):
    url = "http://ssbiqu.com/book/6699/"
    response = requests.get(url=url)
    response.encoding = response.apparent_encoding
    # 自动识别编码
    html_data = response.text

    result_list = re.findall('<li><a href="(.*?)" title=".*">.*</a></li>', html_data)
    # print(result_list)
    count = result_list[number+11]
    all_url = 'http://ssbiqu.com'+count
    # print(all_url)
    response_2 = requests.get(url=all_url)
    response_2.encoding = response_2.apparent_encoding
    # 自动识别编码
    html_data_2 = response_2.text
    # print(html_data_2)
    result = re.findall(' <article id="article" class="content">(.*?)</article>', html_data_2)
    print(result)
    with open('b.text', mode='w', encoding='utf-8') as f:
        f.write(result[0].replace('<p>', '').replace('</p>', ''))
    # make_audio()
        
def send_start_params(ws):
    """
    开始参数帧
    :param websocket.WebSocket ws:
    :return:
    """
    req = {
        "type": "START",
        "data": {
            "appid": Voc_2_text_APPID,  
            "appkey": Voc_2_text_APPKEY,  
            "dev_pid": DEV_PID,  # 识别模型
            "cuid": "1234",  
            "sample": 16000,  # 固定参数
            "format": "pcm"  # 固定参数
        }
    }
    body = json.dumps(req)
    ws.send(body, websocket.ABNF.OPCODE_TEXT)

def send_audio(ws):

    # while True:
        r = sr.Recognizer()
        # 启用麦克风
        mic = sr.Microphone()
        print("***************正在录音*****************")
        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        body = audio.get_wav_data(convert_rate=16000)
        ws.send(body, websocket.ABNF.OPCODE_BINARY)

def send_finish(ws):
    """
    发送结束帧
    :param websocket.WebSocket ws:
    :return:
    """
    req = {"type": "FINISH"}
    body = json.dumps(req)
    ws.send(body, websocket.ABNF.OPCODE_TEXT)

def on_open(ws):
    """
    连接后发送数据帧
    """
    def run(*args):
        send_start_params(ws)
        send_audio(ws)
        send_finish(ws)
    threading.Thread(target=run).start()

def on_message(ws, message):
    """
    接收服务端返回的消息
    :param ws:
    :param message: json格式，自行解析
    :return:
    """
    message = json.loads(message)
    text = message["result"]
    
    if message["type"] == "FIN_TEXT" and text:

        print(text)
        token = get_token()
        if token:
            get_label_baidu(text,token)
        else:
            print("获取token失败!")
    shuzi_hanzi = re.findall('第(.*?)张', text)
    print(shuzi_hanzi[0])
    shuzi = cn2an.cn2an(shuzi_hanzi[0], "strict")
    get_novel(shuzi)
    # make_audio()


def get_token():
    ssl._create_default_https_context = ssl._create_unverified_context
    # OCR_URL = "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify"
    TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'
    params = {'grant_type': 'client_credentials',
              'client_id': E_analy_API_KEY,
              'client_secret': E_analy_SECRET_KEY}
    post_data = urlencode(params)
    result_str = ''
    post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    result_str = result_str.decode()
    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print('please ensure has check the  ability')
            exit()
        token = result['access_token']
        return token
    return None

def get_label_baidu(text,token):
    # 将文本数据保存在变量new_each中
    new_each = {'text': text }
    new_each = json.dumps(new_each)

    url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?charset=UTF-8&access_token={}'.format(token)
    res = requests.post(url, data=new_each)  # 利用URL请求百度情感分析API
    if res.status_code == 200:# 返回成功
        res_text = res.text
        result = res_text.find('items')
        if result == -1:
            print("请求错误")
            return 0
        else:
            json_data = json.loads(res.text)
            value = (json_data['items'][0]['positive_prob'])  # 得到情感指数值
            if value > 0.5:
                print("正面语句" , value)
            else:
                print("负面语句",value)
    else:
        print("请求错误")
        return 0

# def make_audio():
#     APP_ID = '28850651'
#     API_KEY = 'VUcnqZ5syH1iHTgMsHMIiqBW'
#     SECRET_KEY = 'wQt6FNNkTeCyfH77eG8zCUqi9p8ZiXsE'

#     client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

#     with open('a.text', mode='r', encoding='utf-8') as f:
#         flag = 0
#         while True:
#             flag += 1
#             text = f.read(500)
#             if not text:
#                 break
#             print(text)
#             print('......')


#             result = client.synthesis(text, 'zh', 1, {
#                 'vol': 5,
#                 'spd': 4,
#             })

#         # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
#         if not isinstance(result, dict):
#             with open('video\\{}.mp3'.format(str(flag)), 'wb') as file:
#                 file.write(result)
#                 print('正在生成第{}段语音...'.format(flag))


if __name__ == "__main__":
    # https://ai.baidu.com/      # 百度AI首页
    # https://github.com/Baidu-AIP/speech_realtime_api   demo下载地址
    # https://cloud.baidu.com/doc/NLP/s/zk6z52hds

    Voc_2_text_APPID = 28878115    # 语音识别的 APPID
    Voc_2_text_APPKEY = "k4hViNgqbfbHwHV5DYDDECUG" # 语音识别的 APPKEY
    E_analy_API_KEY = "k4hViNgqbfbHwHV5DYDDECUG"   # 情感分析的APIKEY
    E_analy_SECRET_KEY = "VedybA6h2mC0muuwUsRvPdxHmTihRwuL" # 情感分析的Secret key

    # 语言模型 ， 可以修改为其它语言模型测试，如远场普通话19362
    DEV_PID = 15372
    URI = "ws://vop.baidu.com/realtime_asr"

    uri = URI + "?sn=" + str(uuid.uuid1())
    ws_app = websocket.WebSocketApp(uri,
                                    on_open=on_open,        # 连接建立后的回调
                                    on_message=on_message)  # 关闭后的回调
  
    ws_app.run_forever()