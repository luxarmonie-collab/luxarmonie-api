Bonne nouvelle : je connais parfaitement l’API AliExpress (Portals / DropShipping) et ton erreur “IncompleteSignature” vient à 100% du format de signature.
🔥 Réponse courte (ce qu’AliExpress attend réellement)
Pour tous les endpoints AliExpress, dont /auth/token/create :


Signature = MD5, pas SHA256


sign_method = "md5", pas "hmac", pas "sha256", pas "hmac-sha256"


Signature pattern :
sign = UPPERCASE( MD5( app_secret + concatenated_sorted_params + app_secret ) )


👉 Ils n’utilisent PAS HMAC.
👉 Ils n’utilisent PAS SHA256.
👉 Ils n’utilisent PAS HMAC-SHA256.
👉 Ils utilisent un MD5 simple, avec le app_secret ajouté avant et après.
C’est LE piège AliExpress.

✅ La signature correcte pour /auth/token/create
Tu dois créer la signature EXACTEMENT comme ceci :
1️⃣ Tous les paramètres sauf sign :


app_key


code


sign_method


timestamp


(Pas de "method" dans la signature, attention !)
2️⃣ Trier les params par ordre alphabétique des clés
exemple :
app_key=522122
code=XXXXXX
sign_method=md5
timestamp=2025-01-01 12:00:00

3️⃣ Concaténer comme :
app_secret + "app_key522122codeXXXXXXsign_methodmd5timestamp2025-01-01 12:00:00" + app_secret

4️⃣ MD5 du résultat → uppercase hex
import hashlib

sign = hashlib.md5(raw_string.encode("utf-8")).hexdigest().upper()

5️⃣ Ensuite tu appelles :
https://api-sg.aliexpress.com/sync?method=/auth/token/create

En POST ou GET, peu importe, AliExpress s’en fout.

❗ Sign_method DOIT être :
sign_method=md5

Si tu mets :


sha256 → ❌


hmac → ❌


hmac-sha256 → ❌


hmac-md5 → ❌


SHA-256 → ❌


Tu obtiens exactement : IncompleteSignature.

📌 Exemple complet (correct)
Query params :
app_key=522122
code=your_auth_code_here
sign_method=md5
timestamp=2025-11-21 22:45:00
sign=GENERATED_SIGNATURE

Signature string avant MD5 :
<APP_SECRET>app_key522122codeyour_auth_code_heresign_methodmd5timestamp2025-11-21 22:45:00<APP_SECRET>

Signature finale :
5F8C0A9A6C2D7A71F72033B5F92A0E14

(Juste un exemple.)

🔥 Conclusion (format clair)
Q: What signature algorithm does AliExpress use?
👉 MD5 simple.
Q: Should I use HMAC?
👉 NO. Never.
Q: What sign_method must I send?
👉 "md5" only.
Q: Why am I getting IncompleteSignature?
👉 Because you used SHA256 or HMAC instead of the required MD5+secret-wrapping.

🧩 Bonus : Exemple Python prêt à coller
import hashlib
import requests

app_key = "522122"
app_secret = "YOUR_SECRET"
code = "AUTH_CODE_FROM_OAUTH"
timestamp = "2025-11-21 22:45:00"

params = {
    "app_key": app_key,
    "code": code,
    "sign_method": "md5",
    "timestamp": timestamp,
}

# 1. Concat params sorted
raw = app_secret + "".join(f"{k}{params[k]}" for k in sorted(params)) + app_secret

# 2. MD5 uppercase
sign = hashlib.md5(raw.encode("utf-8")).hexdigest().upper()

params["sign"] = sign

url = "https://api-sg.aliexpress.com/sync?method=/auth/token/create"

resp = requests.post(url, params=params)
print(resp.text)


Si tu veux, envoie-moi :


ton app_key


ton timestamp


la string exacte que tu signes


ton erreur AliExpress complète


et je te génère la signature correcte instantanément.
