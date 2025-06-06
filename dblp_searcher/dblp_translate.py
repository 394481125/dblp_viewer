import asyncio
import aiohttp
import hashlib
import random
import requests

def baidu_translate(text, from_lang='auto', to_lang='zh'):
    """调用百度翻译 API 进行翻译"""
    appid = ''  # 替换为你的 APP ID
    secret_key = ''  # 替换为你的密钥

    # 生成随机数和签名
    salt = random.randint(32768, 65536)
    sign = appid + text + str(salt) + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()

    # 发送请求
    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    params = {
        'q': text,
        'from': from_lang,
        'to': to_lang,
        'appid': appid,
        'salt': salt,
        'sign': sign
    }

    response = requests.get(url, params=params)
    result = response.json()

    # 处理结果
    if 'trans_result' in result:
        return '\n'.join([item['dst'] for item in result['trans_result']])
    else:
        print(f"翻译失败: {result.get('error_msg', '未知错误')}")
        return text


# 使用示例
if __name__ == "__main__":
    english_text = "Hello, this is a test sentence for translation."
    chinese_text = baidu_translate(english_text)
    print(chinese_text)  # 输出: 你好，这是一个用于翻译的测试句子。