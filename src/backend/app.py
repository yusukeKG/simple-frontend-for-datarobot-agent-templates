from flask import Flask, send_from_directory, redirect, request, jsonify
from flask_cors import CORS
from src.backend.api.routes import api_bp
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Enable CORS for all routes
CORS(app)

# Get the script name from environment variable for DataRobot Custom Apps
SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')
logger.info(f"SCRIPT_NAME environment variable: '{SCRIPT_NAME}'")

# Support for DataRobot's reverse proxy setup
if SCRIPT_NAME:
    app.config['APPLICATION_ROOT'] = SCRIPT_NAME
    app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)
    logger.info(f"Configured APPLICATION_ROOT: {SCRIPT_NAME}")

# Register API Blueprint with script name prefix
app.register_blueprint(api_bp)
logger.info("API Blueprint registered")

# Redirect handler to add trailing slash (required for DataRobot Custom Apps)
@app.before_request
def add_trailing():
    rp = request.path
    if SCRIPT_NAME and not rp.endswith('/') and '.' not in rp.split('/')[-1]:
        return redirect(rp + '/')

# Serve frontend static files with base path injection
@app.route(f'{SCRIPT_NAME}/')
def serve_index():
    """Serve the main page with base path injection"""
    logger.info(f"Serving index page. SCRIPT_NAME: '{SCRIPT_NAME}'")
    index_path = os.path.join(app.static_folder, 'index.html')
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Inject base path into HTML
        html_content = html_content.replace('{{ base_path }}', SCRIPT_NAME)
        logger.debug(f"Injected base_path: '{SCRIPT_NAME}'")
        
        return html_content
    except Exception as e:
        logger.error(f"Error serving index: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load page'}), 500

@app.route(f'{SCRIPT_NAME}/<path:path>')
def serve_static(path):
    if '.' in path:  # Static file
        return send_from_directory(app.static_folder, path)
    # For routes without extension, serve index.html (SPA behavior)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health')
def health_check():
    """Root level health check"""
    return jsonify({'status': 'healthy'}), 200

@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 error: {e}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 error: {e}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    
    # FLASK_DEBUGの判定を修正（'1', 'true', 'True', 'yes', 'on'のいずれかで有効）
    flask_debug = os.environ.get('FLASK_DEBUG', '').lower()
    debug = flask_debug in ('1', 'true', 'yes', 'on')
    
    logger.info("="*50)
    logger.info("Starting DataRobot Agent Chat Application")
    logger.info(f"Host: 0.0.0.0")
    logger.info(f"Port: {port}")
    logger.info(f"SCRIPT_NAME: {SCRIPT_NAME}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Static folder: {app.static_folder}")
    logger.info("="*50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )