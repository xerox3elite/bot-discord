"""
🔄 Arsenal URL Redirect System 
Système de redirection vers le WebPanel Arsenal
Développé par XeRoX - Arsenal Bot V4.5.0
"""

from flask import Flask, redirect, render_template_string
import os

app = Flask(__name__)

# URLs de redirection
WEBPANEL_URL = "https://arsenal-webpanel.onrender.com"
BOT_STATUS_URL = "https://arsenal-bot-discord.onrender.com"

@app.route('/')
def home():
    """Page d'accueil avec redirection vers le WebPanel"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arsenal Bot - Redirection</title>
    <meta http-equiv="refresh" content="3;url={{ webpanel_url }}">
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            text-align: center;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            max-width: 500px;
        }
        .logo {
            font-size: 3em;
            margin-bottom: 20px;
        }
        .title {
            font-size: 2.2em;
            margin-bottom: 15px;
            font-weight: 700;
        }
        .subtitle {
            font-size: 1.2em;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        .redirect-info {
            margin: 30px 0;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        .btn {
            display: inline-block;
            background: #ff6b6b;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            transition: all 0.3s ease;
            margin: 10px;
        }
        .btn:hover {
            background: #ff5252;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
        }
        .loading {
            margin-top: 20px;
        }
        .dots {
            display: inline-block;
            animation: dots 1.5s infinite;
        }
        @keyframes dots {
            0%, 20% { content: ''; }
            40% { content: '.'; }
            60% { content: '..'; }
            90%, 100% { content: '...'; }
        }
        .countdown {
            font-size: 1.5em;
            color: #ffeb3b;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🚀</div>
        <h1 class="title">Arsenal Bot V4.5.0</h1>
        <p class="subtitle">Système de Bot Discord Avancé</p>
        
        <div class="redirect-info">
            <p><strong>🔄 Redirection automatique vers le WebPanel...</strong></p>
            <p class="countdown">Redirection dans <span id="countdown">3</span> secondes</p>
            <div class="loading">
                <span class="dots"></span>
            </div>
        </div>
        
        <a href="{{ webpanel_url }}" class="btn">
            🎛️ Accéder au WebPanel
        </a>
        
        <a href="/status" class="btn">
            📊 Status du Bot
        </a>
    </div>

    <script>
        let countdown = 3;
        const countdownElement = document.getElementById('countdown');
        
        const timer = setInterval(() => {
            countdown--;
            countdownElement.textContent = countdown;
            
            if (countdown <= 0) {
                clearInterval(timer);
                window.location.href = "{{ webpanel_url }}";
            }
        }, 1000);
    </script>
</body>
</html>
    """, webpanel_url=WEBPANEL_URL)

@app.route('/webpanel')
def webpanel():
    """Redirection directe vers le WebPanel"""
    return redirect(WEBPANEL_URL, code=301)

@app.route('/panel')
def panel():
    """Redirection directe vers le WebPanel (alias)"""
    return redirect(WEBPANEL_URL, code=301)

@app.route('/status')
def status():
    """Page de statut du bot"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arsenal Bot - Status</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        .status-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            display: flex;
            align-items: center;
        }
        .status-icon {
            font-size: 2em;
            margin-right: 20px;
        }
        .online { color: #4caf50; }
        .btn {
            display: inline-block;
            background: #ff6b6b;
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            margin: 10px 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Arsenal Bot V4.5.0 - Status</h1>
        
        <div class="status-card">
            <div class="status-icon online">✅</div>
            <div>
                <h3>Bot Discord</h3>
                <p>Status: <span class="online">En ligne</span></p>
                <p>Version: Arsenal V4.5.0</p>
            </div>
        </div>
        
        <div class="status-card">
            <div class="status-icon online">🎛️</div>
            <div>
                <h3>WebPanel Arsenal</h3>
                <p>Status: <span class="online">Opérationnel</span></p>
                <p>URL: <a href="{{ webpanel_url }}" style="color: #ffeb3b;">{{ webpanel_url }}</a></p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="{{ webpanel_url }}" class="btn">🎛️ WebPanel</a>
            <a href="/" class="btn">🏠 Accueil</a>
        </div>
    </div>
</body>
</html>
    """, webpanel_url=WEBPANEL_URL)

@app.route('/health')
def health():
    """Point de terminaison de santé pour Render"""
    return {"status": "healthy", "service": "Arsenal Bot Redirect", "version": "4.5.0"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

