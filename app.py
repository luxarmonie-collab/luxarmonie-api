import time
import hmac
import hashlib
import requests

ALI_APP_KEY = "522122"
ALI_APP_SECRET = "cWIAoD3ZXW9T3JSW4Tua7WL6zOhG6p1M"   # 
CODE = "3_522122_57QBAHfT94bx9GdwJ512EDZM1783"            # param `code` de /callback OAuth

def build_aliexpress_signature(path: str, params: dict, app_secret: str) -> str:
    """
    Signature pour System Interface AliExpress (/auth/token/create)
    sign = UPPERCASE( HMAC-SHA256(path + concat(key+value sorted by key), app_secret) )
    """
    # 1) Trier les paramètres par nom (ASCII)
    items = sorted(params.items())  # list[tuple(key, value)]

    # 2) Concaténer key+value
    concatenated = "".join(f"{k}{v}" for k, v in items)

    # 3) Prepend path
    sign_string = path + concatenated

    # 4) HMAC-SHA256
    digest = hmac.new(
        app_secret.encode("utf-8"),
        sign_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()

    return digest, sign_string


def get_access_token(app_key: str, app_secret: str, code: str):
    # timestamp en millisecondes
    timestamp = str(int(time.time() * 1000))

    # Params SANS `sign`
    params = {
        "app_key": app_key,
        "code": code,
        "sign_method": "sha256",
        "timestamp": timestamp,
    }

    path = "/auth/token/create"

    sign, sign_string = build_aliexpress_signature(path, params, app_secret)

    print("🧾 String à signer :")
    print(sign_string)
    print("\n✅ Signature calculée :")
    print(sign)

    url = "https://api-sg.aliexpress.com/rest/auth/token/create"

    resp = requests.post(
        url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={**params, "sign": sign},
        timeout=20
    )

    print("\n📡 Status code :", resp.status_code)
    print("📥 Réponse brute :")
    print(resp.text)

    try:
        data = resp.json()
        print("\n📥 JSON parsé :")
        from pprint import pprint
        pprint(data)
    except Exception:
        data = None

    return data


if __name__ == "__main__":
    result = get_access_token(ALI_APP_KEY, ALI_APP_SECRET, CODE)
