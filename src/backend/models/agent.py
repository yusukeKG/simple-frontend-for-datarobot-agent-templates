import requests
import json
from typing import Dict, Any, Optional, Generator
from ..config.datarobot_config import config
import logging

logger = logging.getLogger(__name__)

class Agent:
    """Agent class for interacting with DataRobot deployments"""
    
    def __init__(self):
        self.config = config
        self.deployment_id = self.config.get_deployment_id()
    
    @staticmethod
    def chat(user_message: str, deployment_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a chat message to the DataRobot agent deployment
        
        Args:
            user_message: The message from the user
            deployment_id: Optional deployment ID to override the default
            
        Returns:
            Dict containing the agent's response and metadata
        """
        try:
            # Use provided deployment_id or fall back to config
            dep_id = deployment_id or config.get_deployment_id()
            if not dep_id:
                raise ValueError("Deployment ID is required")
            
            # Construct the chat endpoint URL
            chat_url = config.get_chat_endpoint()
            
            # Prepare the request
            headers = {
                'Authorization': f'Bearer {config.get_api_token()}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messages': [
                    {
                        'role': 'user',
                        'content': user_message
                    }
                ]
            }
            
            # Make the API call
            response = requests.post(
                chat_url,
                headers=headers,
                json=payload,
                timeout=180  # 3 minutes timeout for agent processing
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the response content
            if 'choices' in result and len(result['choices']) > 0:
                message_content = result['choices'][0].get('message', {}).get('content', '')
                return {
                    'success': True,
                    'message': message_content,
                    'full_response': result
                }
            else:
                return {
                    'success': False,
                    'error': 'No response from agent',
                    'full_response': result
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timed out. The agent may be processing a complex request.'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API request failed: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    @staticmethod
    def stream_chat(user_message: str, deployment_id: Optional[str] = None) -> Generator[str, None, None]:
        """Stream chat responses from DataRobot agent deployment
        
        Args:
            user_message: The message from the user
            deployment_id: Optional deployment ID to override the default
            
        Yields:
            Chunks of the agent's response as they arrive
        """
        import time
        import threading
        
        try:
            # Use provided deployment_id or fall back to config
            dep_id = deployment_id or config.get_deployment_id()
            if not dep_id:
                raise ValueError("Deployment ID is required")
            
            # Construct the chat endpoint URL using dep_id
            endpoint = config.get_endpoint()
            if not endpoint:
                raise ValueError("DATAROBOT_ENDPOINT is not configured")
            
            base_endpoint = endpoint.rstrip('/')
            if base_endpoint.endswith('/api/v2'):
                base_endpoint = base_endpoint[:-7]
            chat_url = f"{base_endpoint}/api/v2/deployments/{dep_id}/chat/completions"
            
            logger.info(f"Using deployment_id: {dep_id}")
            
            # Prepare the request
            headers = {
                'Authorization': f'Bearer {config.get_api_token()}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messages': [
                    {
                        'role': 'user',
                        'content': user_message
                    }
                ]
            }
            
            logger.info(f"Starting streaming request to {chat_url}")
            
            # レスポンスとエラーを保持する変数
            response_data = {'result': None, 'error': None, 'done': False}
            
            def fetch_response():
                """バックグラウンドでDataRobot APIを呼び出す"""
                try:
                    response = requests.post(
                        chat_url,
                        headers=headers,
                        json=payload,
                        timeout=300  # 5 minutes timeout
                    )
                    response.raise_for_status()
                    response_data['result'] = response.json()
                except Exception as e:
                    logger.error(f"API call failed: {str(e)}", exc_info=True)
                    response_data['error'] = e
                finally:
                    response_data['done'] = True
            
            # バックグラウンドスレッドでAPIリクエストを開始
            thread = threading.Thread(target=fetch_response)
            thread.daemon = True
            thread.start()
            
            # レスポンスを待つ間、定期的にハートビートを送信
            heartbeat_count = 0
            while not response_data['done']:
                # 5秒ごとにハートビートを送信してタイムアウトを防ぐ
                time.sleep(5)
                heartbeat_count += 1
                logger.debug(f"Sending heartbeat #{heartbeat_count}")
                yield ""  # 空のチャンクでキープアライブ
            
            # エラーチェック
            if response_data['error']:
                raise response_data['error']
            
            result = response_data['result']
            
            # DataRobotのレスポンスを処理
            if result and 'choices' in result and len(result['choices']) > 0:
                message_content = result['choices'][0].get('message', {}).get('content', '')
                logger.info(f"Received response with {len(message_content)} characters")
                
                # メッセージを小さなチャンクに分割してストリーミング
                chunk_size = 30  # 30文字ずつ送信
                for i in range(0, len(message_content), chunk_size):
                    chunk = message_content[i:i + chunk_size]
                    yield chunk
                    logger.debug(f"Streamed chunk {i//chunk_size + 1}: {chunk[:20]}...")
                    time.sleep(0.05)  # 50ms待機してストリーミング感を出す
            else:
                raise ValueError('No response from agent')
                    
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            raise Exception('Request timed out. The agent may be processing a complex request.')
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise Exception(f'API request failed: {str(e)}')
        except Exception as e:
            logger.error(f"Unexpected error in stream_chat: {str(e)}")
            raise Exception(f'Unexpected error: {str(e)}')