<h1 align="center">XHamster API</h1> 

<div align="center">
    <a href="https://pepy.tech/project/xhamster_api"><img src="https://static.pepy.tech/badge/xhamster_api" alt="Downloads"></a>
    <a href="https://github.com/EchterAlsFake/xhamster_api/workflows/"><img src="https://github.com/EchterAlsFake/xhamster_api/workflows/CodeQL/badge.svg" alt="CodeQL Analysis"/></a>
    <a href="https://github.com/EchterAlsFake/xhamster_api/actions/workflows/sync-tests.yml"><img src="https://github.com/EchterAlsFake/xhamster_api/actions/workflows/sync-tests.yml/badge.svg" alt="Sync API Tests"/></a>
</div>

# Description
XHamster API is an API for xhamster.com. It allows you to fetch information from videos using regexes and requests.

# Disclaimer
> [!IMPORTANT] 
> XHamster API is in violation to the ToS of xhamster.com!
> If you are the website owner of xhamster.com, contact me at my E-Mail, and I'll take this repository immediately offline.
> EchterAlsFake@proton.me

# Quickstart

### Have a look at the [Documentation](https://github.com/EchterAlsFake/API_Docs/blob/master/Porn_APIs/XHamster.md) for more details
- Install the library with `pip install xhamster_api`


```python
from xhamster_api import Client
# Initialize a Client object
client = Client()

# Fetch a video
video_object = client.get_video("<insert_url_here>")

# Information from Video objects
print(video_object.title)
print(video_object.likes)
# Download the video

video_object.download(downloader="threaded", quality="best", path="your_output_path + filename")

# SEE DOCUMENTATION FOR MORE
```

# Support (Donations)
I am developing all my projects entirely for free. I do that because I have fun and I don't want
to charge 30€ like other people do.

However, if you find my work useful, please consider donating something. A tiny amount such as 1€
means a lot to me.

Paypal: https://paypal.me/EchterAlsFake
<br>XMR (Monero): `42XwGZYbSxpMvhn9eeP4DwMwZV91tQgAm3UQr6Zwb2wzBf5HcuZCHrsVxa4aV2jhP4gLHsWWELxSoNjfnkt4rMfDDwXy9jR`


# Contribution
Do you see any issues or having some feature requests? Simply open an Issue or talk
in the discussions.

Pull requests are also welcome.

# License
Licensed under the LGPLv3 License
<br>Copyright (C) 2023–2025 Johannes Habel
