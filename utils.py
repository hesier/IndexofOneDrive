import datetime
import markdown

extensions = [
    'markdown.extensions.extra',  # 常用扩展，插入html代码块等
    'markdown.extensions.codehilite',  # 代码高亮
    'markdown.extensions.toc',  # 目录
]


def render_markdown(content: str):
    content = markdown.markdown(content, extensions=extensions)
    return content


def format_path(path):
    path = str(path).strip(':').split(':', 1)[-1]
    if path == '/' or path == '':
        return '/'
    else:
        return f':/{path.strip("/")}:/'


def format_size(size, dot=1):
    unit = (
        ('B', 2 ** 0),
        ('K', 2 ** 10),
        ('M', 2 ** 20),
        ('G', 2 ** 30),
        ('T', 2 ** 40),
        ('P', 2 ** 50),
    )

    for k, v in unit:
        if size <= v * 1024:
            return f'{round(size / v, dot)}{k}'


def format_time(time_data, time_format='%Y-%m-%dT%H:%M:%SZ'):
    dt = datetime.datetime.strptime(time_data, time_format) + datetime.timedelta(hours=8)
    return dt.strftime("%Y-%m-%d %H:%M")


if __name__ == '__main__':
    code = input("请输入 code: ")
    if code.strip():
        from onedrive import init_token
        init_token(code.strip())
        print('获取 refresh_token 完成')
    else:
        print('code 输入为空！')
