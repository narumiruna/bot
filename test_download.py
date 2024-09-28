import os
import pickle

import httpx

from bot.utils import download

# def save_cookies(client: httpx.Client):
#     with open("cookies.pk", "wb") as f:
#         pickle.dump(client.cookies.jar._cookies, f)


# def load_cookies():
#     if not os.path.isfile("cookies.pk"):
#         return None
#     cookies = httpx.Cookies()
#     with open("cookies.pk", "rb") as f:
#         jar_cookies = pickle.load(f)
#     for domain, pc in jar_cookies.items():
#         for path, c in pc.items():
#             for k, v in c.items():
#                 cookies.set(k, v.value, domain=domain, path=path)
#     return cookies


def main() -> None:
    # url = "https://www.nature.com/articles/s41586-024-07930-y"
    url = "https://www.nature.com/articles/s41586-024-07930-y.pdf"
    path = download(url)
    print(path)


if __name__ == "__main__":
    main()
