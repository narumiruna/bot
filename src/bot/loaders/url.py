from urllib.parse import urlparse
from urllib.parse import urlunparse


def is_youtube_url(url: str) -> bool:
    return (
        url.startswith("https://www.youtube.com")
        or url.startswith("https://youtu.be")
        or url.startswith("https://m.youtube.com")
    )


def is_instagram_reel_url(url: str) -> bool:
    return url.startswith("https://www.instagram.com/reel/")


def is_x_url(url: str) -> bool:
    x_domains = {
        "https://x.com",
        "https://twitter.com",
        "https://fxtwitter.com",
        "https://vxtwitter.com",
        "https://fixvx.com",
        "https://twittpr.com",
        "https://fixupx.com",
    }
    return any(url.startswith(domain) for domain in x_domains)


def replace_domain(url: str) -> str:
    replacements = {
        # "twitter.com": "vxtwitter.com",
        # "x.com": "fixvx.com",
        # "twitter.com": "twittpr.com",
        # "x.com": "fixupx.com",
        "twitter.com": "api.fxtwitter.com",
        "x.com": "api.fxtwitter.com",
    }

    parsed_url = urlparse(url)
    if parsed_url.netloc in replacements:
        new_netloc = replacements[parsed_url.netloc]
        fixed_url = parsed_url._replace(netloc=new_netloc)
        return urlunparse(fixed_url)

    return url
