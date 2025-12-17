from flask import Blueprint, request, jsonify
from ..models.agent import Agent
from ..config.datarobot_config import config
import logging

# Setup logging
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint for DataRobot"""
    logger.info("Health check endpoint called")
    return jsonify({
        'status': 'healthy',
        'message': 'DataRobot Agent Chat is running'
    }), 200

@api_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests to the DataRobot agent with streaming response"""
    from flask import Response, stream_with_context
    import json
    
    logger.info(f"Chat endpoint called. Path: {request.path}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    try:
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data or 'message' not in data:
            logger.error("Invalid request: no message provided")
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        user_message = data['message']
        deployment_id = data.get('deployment_id')  # Optional override
        
        logger.info(f"Processing chat message: {user_message[:50]}...")
        
        def generate():
            try:
                logger.info("Starting stream generation")
                # エージェントからのストリーミングレスポンスを取得
                chunk_count = 0
                for chunk in Agent.stream_chat(user_message, deployment_id):
                    chunk_count += 1
                    # ハートビート（空チャンク）もコメントとして送信
                    if chunk:
                        logger.debug(f"Sending content chunk #{chunk_count}: {chunk[:30]}...")
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                    else:
                        logger.debug(f"Sending heartbeat #{chunk_count}")
                        yield f": heartbeat\n\n"  # SSEコメント形式でハートビート送信
                yield "data: [DONE]\n\n"
                logger.info(f"Chat streaming completed successfully (total chunks: {chunk_count})")
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}", exc_info=True)
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@api_bp.route('/config', methods=['GET'])
def get_config():
    """Return deployment configuration info (without sensitive data)"""
    logger.info("=== /api/config endpoint called ===")
    
    try:
        api_token = config.get_api_token()
        endpoint = config.get_endpoint()
        deployment_id = config.get_deployment_id()
        
        # デバッグ用：各パラメーターの状態をログ出力
        logger.info(f"API Token exists: {bool(api_token)}, length: {len(api_token) if api_token else 0}")
        logger.info(f"Endpoint: '{endpoint}' (length: {len(endpoint) if endpoint else 0})")
        logger.info(f"Deployment ID: '{deployment_id}' (length: {len(deployment_id) if deployment_id else 0})")
        logger.info(f"Config is_valid: {config.is_valid()}")
        
        response_data = {
            'success': True,
            'has_deployment_id': bool(deployment_id and deployment_id.strip() != ''),
            'has_api_token': bool(api_token and api_token.strip() != ''),
            'has_endpoint': bool(endpoint and endpoint.strip() != '')
        }
        
        logger.info(f"Response data: {response_data}")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error in /api/config: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
