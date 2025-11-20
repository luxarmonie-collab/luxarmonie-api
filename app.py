#!/usr/bin/env python3
"""
Luxarmonie API - Version Production
"""

from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS
import json
import os
import threading
from datetime import datetime
import requests
import hashlib
import time

# Import configuration depuis variables d'environnement
ALIEXPRESS_APP_KEY = os.getenv('ALIEXPRESS_APP_KEY', '522122')
ALIEXPRESS_APP_SECRET = os.getenv('ALIEXPRESS_APP_SECRET', '')
WOO_URL = os.getenv('WOO_URL', '')
WOO_CONSUMER_KEY = os.getenv('WOO_CONSUMER_KEY', '')
WOO_CONSUMER_SECRET = os.getenv('WOO_CONSUMER_SECRET', '')
USE_ALIEXPRESS_API = os.getenv('USE_ALIEXPRESS_API', 'True') == 'True'
DOMAIN = os.getenv('DOMAIN', 'http://localhost:5000')

app = Flask(__name__)
CORS(app)

CONFIG_FILE = "config.json"
HISTORY_FILE = "import_history.json"

import_status = {
    "current": None,
    "progress": 0,
    "message": "",
    "error": None
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def add_to_history(import_data):
    history = load_history()
    history.insert(0, {**import_data, "timestamp": datetime.now().isoformat()})
    history = history[:50]
    save_history(history)

@app.route('/')
def index():
    return f"""
    <html>
    <head>
        <title>🏮 Luxarmonie API</title>
        <style>
            body {{ font-family: Arial; padding: 50px; background: #f5f5f5; }}
            .container {{ background: white; padding: 40px; border-radius: 10px; max-width: 800px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            .status {{ background: #e8f5e9; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            .status.ok {{ background: #e8f5e9; border-left: 4px solid #4caf50; }}
            .status.warning {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
            .status.error {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
            .btn {{ display: inline-block; padding: 15px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }}
            .btn:hover {{ background: #0056b3; }}
            .btn-success {{ background: #28a745; }}
            .btn-success:hover {{ background: #218838; }}
            code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏮 Luxarmonie API</h1>
            <p>Système d'importation automatique AliExpress → WooCommerce</p>
            
            <div class="status {'ok' if ALIEXPRESS_APP_SECRET else 'warning'}">
                <h3>📊 Statut API AliExpress</h3>
                <p><strong>App Key:</strong> {ALIEXPRESS_APP_KEY}</p>
                <p><strong>App Secret:</strong> {'✅ Configuré' if ALIEXPRESS_APP_SECRET else '⚠️ Non configuré'}</p>
                <p><strong>Mode API:</strong> {'✅ Activé' if USE_ALIEXPRESS_API else '❌ Désactivé (Scraper)'}</p>
            </div>
            
            <div class="status {'ok' if WOO_URL else 'warning'}">
                <h3>🛒 Statut WooCommerce</h3>
                <p><strong>Site:</strong> {WOO_URL if WOO_URL else '⚠️ Non configuré'}</p>
                <p><strong>Clés API:</strong> {'✅ Configurées' if WOO_CONSUMER_KEY else '⚠️ Non configurées'}</p>
            </div>
            
            <h3>🔗 Actions</h3>
            <a href="/oauth/start" class="btn btn-success">🔐 Obtenir Access Token OAuth</a>
            <a href="/api/stats" class="btn">📊 Statistiques</a>
            <a href="/api/history" class="btn">📋 Historique</a>
            
            <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px;">
                <h3>📖 Documentation</h3>
                <p><strong>Base URL:</strong> <code>{DOMAIN}</code></p>
                <p><strong>Endpoints:</strong></p>
                <ul>
                    <li><code>GET /</code> - Cette page</li>
                    <li><code>GET /oauth/start</code> - Démarrer OAuth</li>
                    <li><code>GET /callback</code> - Callback OAuth</li>
                    <li><code>POST /api/import/single</code> - Importer un produit</li>
                    <li><code>GET /api/stats</code> - Statistiques</li>
                    <li><code>GET /api/history</code> - Historique</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    if request.method == 'GET':
        config = load_config()
        return jsonify(config)
    else:
        data = request.json
        config = load_config()
        config.update(data)
        save_config(config)
        return jsonify({"success": True})

@app.route('/api/import/single', methods=['POST'])
def api_import_single():
    global import_status
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({"success": False, "error": "URL manquante"}), 400
    
    import_status = {"current": url, "progress": 0, "message": "Démarrage...", "error": None}
    
    def run_import():
        global import_status
        try:
            import_status["message"] = "Extraction..."
            import_status["progress"] = 10
            
            # Simuler import pour test
            time.sleep(2)
            result = {"success": True, "message": "Import simulé"}
            
            import_status["progress"] = 100
            import_status["message"] = "Terminé !"
            add_to_history({"url": url, "success": True, **result})
        except Exception as e:
            import_status["error"] = str(e)
            import_status["message"] = f"Erreur: {str(e)}"
            add_to_history({"url": url, "success": False, "error": str(e)})
    
    thread = threading.Thread(target=run_import)
    thread.start()
    return jsonify({"success": True})

@app.route('/api/import/status')
def api_import_status():
    return jsonify(import_status)

@app.route('/api/history')
def api_history():
    return jsonify(load_history())

@app.route('/api/stats')
def api_stats():
    history = load_history()
    total = len(history)
    success = sum(1 for item in history if item.get("success"))
    return jsonify({
        "total_imports": total,
        "success_count": success,
        "failed_count": total - success,
        "success_rate": round((success / total * 100) if total > 0 else 0, 1),
        "recent_imports": history[:5]
    })

@app.route('/oauth/start')
def oauth_start():
    """Lance OAuth"""
    callback_url = f"{DOMAIN}/callback"
    oauth_url = (
        "https://api-sg.aliexpress.com/oauth/authorize?"
        "response_type=code&"
        f"client_id={ALIEXPRESS_APP_KEY}&"
        f"redirect_uri={callback_url}&"
        "state=luxarmonie&sp=ae"
    )
    print(f"\n🔐 OAuth: {oauth_url}\n")
    return redirect(oauth_url)

@app.route('/callback')
def oauth_callback():
    """Récupère le code et génère le token"""
    code = request.args.get('code')
    
    if not code:
        return "<h1>❌ Pas de code</h1>"
    
    print(f"\n🎉 CODE REÇU: {code}\n")
    
    timestamp = str(int(time.time() * 1000))
    
    params = {
        "app_key": ALIEXPRESS_APP_KEY,
        "code": code,
        "sign_method": "md5",
        "timestamp": timestamp
    }
    
    # Signature MD5 (CORRECT selon ChatGPT et doc AliExpress)
    sorted_params = sorted(params.items())
    params_string = "".join([f"{k}{v}" for k, v in sorted_params])
    
    # MD5: secret + params + secret
    sign_string = ALIEXPRESS_APP_SECRET + params_string + ALIEXPRESS_APP_SECRET
    signature = hashlib.md5(sign_string.encode()).hexdigest().upper()
    
    print(f"📋 Sign string: {sign_string[:80]}...")
    print(f"✅ Signature MD5: {signature}\n")
    
    try:
        response = requests.post(
            "https://api-sg.aliexpress.com/sync?method=/auth/token/create",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={**params, "sign": signature},
            timeout=15
        )
        
        result = response.json()
        print(f"📥 Réponse API:\n{json.dumps(result, indent=2)}\n")
        
        # Chercher le token
        access_token = None
        refresh_token = None
        
        if isinstance(result, dict):
            if "access_token" in result:
                access_token = result["access_token"]
                refresh_token = result.get("refresh_token")
            else:
                for k, v in result.items():
                    if isinstance(v, dict) and "access_token" in v:
                        access_token = v["access_token"]
                        refresh_token = v.get("refresh_token")
                        break
        
        if access_token:
            # Sauvegarder dans config
            config = load_config()
            config["aliexpress_access_token"] = access_token
            if refresh_token:
                config["aliexpress_refresh_token"] = refresh_token
            save_config(config)
            
            print(f"✅ TOKEN SAUVEGARDÉ: {access_token}\n")
            
            return f"""
            <html>
            <head><title>✅ Token Obtenu !</title></head>
            <body style="font-family: Arial; padding: 50px; background: #f0f0f0;">
                <div style="background: white; padding: 40px; border-radius: 10px; max-width: 900px; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                    <h1 style="color: #28a745;">🎉 TOKEN OBTENU AVEC SUCCÈS !</h1>
                    
                    <div style="background: #d4edda; padding: 20px; border-radius: 5px; border-left: 4px solid #28a745; margin: 20px 0;">
                        <h3>🔑 Access Token</h3>
                        <code style="word-break: break-all; background: #f8f9fa; padding: 10px; display: block; border-radius: 3px;">{access_token}</code>
                    </div>
                    
                    {f'<div style="background: #d1ecf1; padding: 20px; border-radius: 5px; border-left: 4px solid #17a2b8; margin: 20px 0;"><h3>🔄 Refresh Token</h3><code style="word-break: break-all; background: #f8f9fa; padding: 10px; display: block; border-radius: 3px;">{refresh_token}</code></div>' if refresh_token else ''}
                    
                    <div style="background: #fff3cd; padding: 20px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 20px 0;">
                        <h3>✅ Étape suivante</h3>
                        <p>Le token a été sauvegardé automatiquement dans <code>config.json</code></p>
                        <p>Pour l'utiliser dans votre code Python, ajoutez dans vos variables d'environnement Railway :</p>
                        <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto;">ALIEXPRESS_ACCESS_TOKEN={access_token}</pre>
                    </div>
                    
                    <div style="margin-top: 30px;">
                        <a href="/" style="display: inline-block; padding: 15px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">← Retour à l'accueil</a>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            return f"""
            <html>
            <head><title>❌ Erreur</title></head>
            <body style="font-family: Arial; padding: 50px; background: #f0f0f0;">
                <div style="background: white; padding: 40px; border-radius: 10px; max-width: 800px; margin: 0 auto;">
                    <h1 style="color: #dc3545;">❌ Erreur lors de l'obtention du token</h1>
                    <div style="background: #f8d7da; padding: 20px; border-radius: 5px; border-left: 4px solid #dc3545; margin: 20px 0;">
                        <h3>Réponse de l'API :</h3>
                        <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto;">{json.dumps(result, indent=2)}</pre>
                    </div>
                    <a href="/oauth/start" style="display: inline-block; padding: 15px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">🔄 Réessayer</a>
                </div>
            </body>
            </html>
            """
    
    except Exception as e:
        return f"""
        <html>
        <head><title>❌ Erreur</title></head>
        <body style="font-family: Arial; padding: 50px; background: #f0f0f0;">
            <div style="background: white; padding: 40px; border-radius: 10px; max-width: 800px; margin: 0 auto;">
                <h1 style="color: #dc3545;">❌ Erreur serveur</h1>
                <div style="background: #f8d7da; padding: 20px; border-radius: 5px; border-left: 4px solid #dc3545; margin: 20px 0;">
                    <pre>{str(e)}</pre>
                </div>
                <a href="/" style="display: inline-block; padding: 15px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">← Retour</a>
            </div>
        </body>
        </html>
        """

@app.route('/health')
def health():
    """Health check pour Railway"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*70)
    print("🏮 LUXARMONIE API - MODE PRODUCTION")
    print("="*70)
    print(f"\n🚀 Serveur démarré sur port {port}")
    print(f"📍 {DOMAIN}")
    print(f"🔐 App Key: {ALIEXPRESS_APP_KEY}")
    print(f"🔑 App Secret: {'✅ Configuré' if ALIEXPRESS_APP_SECRET else '❌ Non configuré'}")
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)
