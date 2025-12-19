import os
import logging

logger = logging.getLogger(__name__)

# ローカル開発用: .envファイルがあれば読み込む
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # DataRobot環境ではdotenvパッケージは不要
    pass

class DataRobotConfig:
    def __init__(self):
        logger.info("=== DataRobotConfig Initialization ===")
        
        # DataRobot環境ではMLOPS_RUNTIME_PARAM_DATAROBOT_*を優先、
        # ローカル開発ではDATAROBOT_*を使用
        self.api_token = (
            os.environ.get('MLOPS_RUNTIME_PARAM_DATAROBOT_API_TOKEN', '') or 
            os.environ.get('DATAROBOT_API_TOKEN', '')
        ).strip()
        
        self.endpoint = (
            os.environ.get('MLOPS_RUNTIME_PARAM_DATAROBOT_ENDPOINT', '') or 
            os.environ.get('DATAROBOT_ENDPOINT', '')
        ).strip()
        
        self.deployment_id = (
            os.environ.get('MLOPS_RUNTIME_PARAM_DATAROBOT_DEPLOYMENT_ID', '') or 
            os.environ.get('DATAROBOT_DEPLOYMENT_ID', '')
        ).strip()
        
        logger.info(f"API Token: {'[SET]' if self.api_token else '[NOT SET]'}")
        logger.info(f"Endpoint: {self.endpoint or '[NOT SET]'}")
        logger.info(f"Deployment ID: {self.deployment_id or '[NOT SET]'}")
        logger.info("=" * 50)
        
    def get_api_token(self):
        return self.api_token

    def get_endpoint(self):
        return self.endpoint

    def get_deployment_id(self):
        return self.deployment_id
    
    def is_valid(self):
        """Check if all required configuration is present"""
        return bool(
            self.api_token and self.api_token != '' and
            self.endpoint and self.endpoint != '' and
            self.deployment_id and self.deployment_id != ''
        )
    
    def get_chat_endpoint(self):
        """Returns the full chat endpoint URL for the deployment"""
        if not self.endpoint or not self.deployment_id:
            raise ValueError("Missing DATAROBOT_ENDPOINT or DATAROBOT_DEPLOYMENT_ID")
        # Remove /api/v2 suffix if present
        base_endpoint = self.endpoint.rstrip('/')
        if base_endpoint.endswith('/api/v2'):
            base_endpoint = base_endpoint[:-7]
        return f"{base_endpoint}/api/v2/deployments/{self.deployment_id}/chat/completions"

config = DataRobotConfig()