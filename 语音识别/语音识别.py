import requests
import re



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
    with open('a.text', mode='w', encoding='utf-8') as f:
        f.write(result[0].replace('<p>', '').replace('</p>', ''))



num = int(input('请输入章节的序号（数字）:'))

get_novel(num)