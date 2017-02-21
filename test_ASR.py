# encoding=utf-8
import wave
import urllib
import urllib2
import pycurl
import base64
import json
import os
import sys
import httplib
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from pydub import AudioSegment
reload(sys)
sys.setdefaultencoding('utf-8')
# 在 urllib2 上注册 http 流处理句柄
register_openers()
# get token
file_position = '/Users/riemann/Documents/riemann/test_ASR/lee1.opus'

def get_token():
    apiKey = "0XyzNfIwZeSqDN8oZWR54Qon"
    secretKey = "92971d401d3df1bd2869afebc04df63b"

    auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials" + \
        "&client_id=" + apiKey + "&client_secret=" + secretKey

    res = urllib2.urlopen(auth_url)
    json_data = res.read()
    return json.loads(json_data)['access_token']


def dump_res(buf):
    print buf

 # post audio to server
def get_audio():
    voice_wav = AudioSegment.from_file('/Users/riemann/Documents/riemann/test_ASR/lee1.wav')
    file_handle = voice_wav.export(file_position, format='opus', parameters=['-ar', '16000'])
    voice = AudioSegment.from_file(file_handle)
    voice = voice.set_frame_rate(16000)
    audio_data = voice.raw_data
    # audio_len = int(voice.frame_count() * 2)
    audio_len = os.path.getsize(file_position)
    # fp = wave.open('/Users/riemann/Documents/riemann/test_ASR/lee1.wav', 'rb')
    # nf = fp.getnframes()
    # audio_len = nf * 2
    # audio_data = fp.readframes(nf)
    print type(audio_data), audio_len, voice.frame_count(), voice.frame_width
    return (audio_data, audio_len)

def use_cloud(token):
    audio_data, audio_len= get_audio()
    print type(audio_data), audio_len
    cuid = "38:c9:86:13:93:1f"  # my Mac MAC
    srv_url = 'http://vop.baidu.com/server_api' + '?cuid=' + cuid + '&token=' + token
    http_header = [
        'Content-Type: audio/opus;rate=16000',
        'Content-Length: %d' % audio_len
    ]
    # http_header = {
    #     'Content-Type': 'audio/wav;rate=16000',
    #     'Content-Length': '%d' % f_len
    # }

    # datagen,headers = multipart_encode({'audio1':open('lee1.wav', 'rb')})
    # request = urllib2.Request(srv_url,datagen,http_header)
    # print urllib2.urlopen(request).read()

    # conn = httplib.HTTPConnection('vop.baidu.com/server_api')
    # conn.request(method="post", url=srv_url,
    #              body=audio_data, headers=http_header)
    # response = conn.getresponse()
    # res = response.read()
    # print res

    # post_data = urllib.urlencode(audio_data)
    # req = urllib2.Request(srv_url, audio_data)
    # req.add_header('Content-Type', 'audio/wav;rate=16000')
    # req.add_header('Content-Type', '%d' % f_len)
    # response = urllib2.urlopen(req)
    # print response.read()

    c = pycurl.Curl()
    c.setopt(pycurl.URL, str(srv_url))  # curl doesn't support unicode
    #c.setopt(c.RETURNTRANSFER, 1)
    c.setopt(c.HTTPHEADER, http_header)  # must be list, not dict
    c.setopt(c.POST, 1)
    c.setopt(c.CONNECTTIMEOUT, 300)
    c.setopt(c.TIMEOUT, 30)
    c.setopt(c.WRITEFUNCTION, dump_res)
    #File Upload
    values = [('upload_file[]',(c.FORM_FILE, file_position))]
    c.setopt(c.HTTPPOST, values)
    # c.setopt(c.POSTFIELDS, audio_data)
    # c.setopt(c.POSTFIELDSIZE, audio_len)
    c.setopt(c.VERBOSE, True)
    c.perform()  # pycurl.perform() has no return val
    c.close()

if __name__ == '__main__':
    token = get_token()
    use_cloud(token)
