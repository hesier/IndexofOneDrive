# -*- coding: utf-8 -*-
import datetime
import urllib.parse

from apscheduler.schedulers.background import BackgroundScheduler
from gevent.pywsgi import WSGIServer
from gevent import monkey

monkey.patch_all()
from flask import Flask, redirect, render_template, abort
from flask_apscheduler import APScheduler
import requests
import yaml

from utils import format_path, format_size, format_time, render_markdown

ip = '127.0.0.1'
port = 5000
root_path = '/'  # 要列出的 onedrive 目录
is_consumers = True  # 默认为 工作/学校帐户，个人账号需要改为 True

config_path = 'config.yaml'
client_url = 'https://login.microsoftonline.com/common/oauth2/token'
consumers_client_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
client_data = {
    'client_id': '29770f3f-0583-4301-b622-3af9c1935a9c',
    'redirect_uri': 'http://localhost/myapp/',
    'client_secret': 'Bz9TD0J-K4vDp.oQA_CTqOK53g1t6N2__a',
    'grant_type': 'refresh_token',
    'scope': 'Files.Read.All offline_access'
}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
cache = {
    'access_token': '',
    'files': {}
}
cache_tmp = {'files': {}}


class Config(object):
    JOBS = [
        {
            'id': 'refresh_token',
            'func': '__main__:init_token',
            'trigger': 'interval',
            'seconds': 3000,
        }
    ]
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'


app = Flask(__name__)
app.config.from_object(Config())


def init_token(code=None):
    if code is None:
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' - init_token')
        load_data()
    else:
        # client_data['scope'] = 'User.Read Files.ReadWrite.All'
        client_data['grant_type'] = 'authorization_code'
        client_data['code'] = code
    r = requests.post(consumers_client_url if is_consumers else client_url,
                      data=urllib.parse.urlencode(client_data, doseq=True), headers=headers)
    res = eval(r.text)
    if "refresh_token" in res and "access_token" in res:
        cache['access_token'] = res["access_token"]
        refresh_token = res["refresh_token"]
        write_data(refresh_token)
        if code is None:
            refresh_file()
    else:
        raise Exception("refresh token 失效")


def refresh_file():
    path = root_path.rstrip('/') if root_path.endswith('/') else root_path
    init_files(path)
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' - init_files 完成')
    cache['files'] = cache_tmp['files']
    cache_tmp['files'] = {}


def init_files(path):
    new_path = format_path(path)
    headers_with_token = {'Authorization': 'Bearer ' + cache['access_token']}
    url = f'https://graph.microsoft.com/v1.0/me/drive/root{new_path}children'
    r = requests.get(url, headers=headers_with_token)
    file_data = eval(r.text)
    if "error" in file_data:
        print(file_data['error']['message'])
    else:
        values = {}
        for value in file_data['value']:
            if value['name'].lower().strip() == 'readme.md':
                readme = requests.get(value['@microsoft.graph.downloadUrl']).text
                values['readme.md'] = render_markdown(readme)
            elif value['name'].lower().strip() == 'head.md':
                readme = requests.get(value['@microsoft.graph.downloadUrl']).text
                values['head.md'] = render_markdown(readme)
            else:
                if 'folder' in value:
                    folder = {
                        'time': format_time(value['lastModifiedDateTime']),
                        'size': format_size(value['size'])
                    }
                    values[value['name']] = folder
                    init_files(path.rstrip('/') + '/' + value['name'])
                elif 'file' in value:
                    file = {
                        'time': format_time(value['lastModifiedDateTime']),
                        'size': format_size(value['size']),
                        'url': value['@microsoft.graph.downloadUrl']
                    }
                    values[value['name']] = file

        cache_tmp['files'][path] = values


def load_data():
    f = open(config_path, encoding='utf-8')
    config = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
    client_data['refresh_token'] = config['refresh_token']


def write_data(refresh_token):
    data = {'refresh_token': refresh_token}
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    head_path = root_path.rstrip('/') if root_path.endswith('/') else root_path
    file_path = (head_path + '/' + path.rstrip('/')).rstrip('/')
    try:
        if cache['files'].__contains__(file_path):
            return render_template('index.html', files=cache['files'][file_path])
        else:
            file_path = file_path.rsplit('/', 1)
            if cache['files'].__contains__(file_path[0]):
                if cache['files'][file_path[0]].__contains__(file_path[1]):
                    return redirect(cache['files'][file_path[0]][file_path[1]]['url'])
    except KeyError:
        return '404', 404
    return '404', 404


if __name__ == '__main__':
    init_token()

    scheduler = APScheduler(BackgroundScheduler(timezone="Asia/Shanghai"))
    scheduler.init_app(app)
    scheduler.start()
    http_server = WSGIServer((ip, port), app)
    http_server.serve_forever()
