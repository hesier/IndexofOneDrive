# IndexofOneDrive
Index of OneDrive，支持工作/学校帐户和个人账号，适合文件较少的场景，支持 HEAD.md 和 README.md，仅支持 python3 环境。


## 安装依赖
```
pip install -r requirements.txt
```

## 获取 code
[https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=29770f3f-0583-4301-b622-3af9c1935a9c&response_type=code&redirect_uri=http://localhost/myapp/&scope=Files.Read.All+offline_access](https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=29770f3f-0583-4301-b622-3af9c1935a9c&response_type=code&redirect_uri=http://localhost/myapp/&scope=Files.Read.All+offline_access)

访问该地址，获取重定向后地址中的 code 字段值，注意地址中可能包含 session_state 字段。

## 获取 refresh_token

如果为个人账号的话，需要修改 `onedrive.py` 中的 `is_consumers` 为 `True`。

```
python utils.py
```

粘贴进去上一步获取的 code，运行完成后会生成 `config.yaml` 配置文件。

## 运行

默认列出 onedrive 中所有文件，如果需要只列出单独文件夹，可以修改 `onedrive.py` 中的 `root_path`。

```
python onedrive.py
```

打印 `init_files 完成` 字样表示启动完成，默认地址为 `127.0.0.1:5000` ，可在 `onedrive.py` 中修改，外网访问需要将 ip 修改为 `0.0.0.0`，建议默认 `127.0.0.1` 配合 NGINX 或 Caddy 反向代理使用，注意缓存不能超过 10 分钟。