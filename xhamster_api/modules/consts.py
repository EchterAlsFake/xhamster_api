import re

REGEX_M3U8 = re.compile(r'https:\\/\\/[^"]+?_TPL_\.h264\.mp4\.m3u8')
REGEX_TITLE = re.compile(r'<meta property="og:title" content="(.*?)"')
REGEX_AUTHOR = re.compile(r'<div class="item-[^"]*?">.*?<img[^>]+?alt="([^"]+?)"[^>]*?>.*?<span class="body-[^"]*? label-[^"]*? label-[^"]*?">([^<]+?)</span>')
REGEX_THUMBNAIL = re.compile(r'<meta property="og:image" content="(.*?)">')
REGEX_LENGTH = re.compile(r'<span class="eta">(.*?)</span>')