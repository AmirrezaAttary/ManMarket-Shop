import html
import re

_BLOCK_END = re.compile(r"(?i)<\s*(?:br\s*/?|/p|/div|/li)\s*>")
_TAG = re.compile(r"<[a-zA-Z/!][^>]*>")


def clean_review_text(text):
    """
    متن نظر را به متن ساده تبدیل می‌کند: تگ‌های HTML (مثل <p> و <br>) حذف و به خط جدید تبدیل می‌شوند
    و کاراکترهای escape شده (&quot; و ...) به شکل اصلی برمی‌گردند. چند بار اجرا شدن روی یک متن بی‌خطر است.
    """
    if not text:
        return text or ""
    text = _BLOCK_END.sub("\n", str(text))
    text = _TAG.sub("", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t\u00a0]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
