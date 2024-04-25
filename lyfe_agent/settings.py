import logging
import os
import random
import time
from typing import Dict, List, Optional
from dotenv import dotenv_values
import json


logger = logging.getLogger(__name__)


def get_env_vars(
    env_file_path: str = None,
    aws_secret_name: str = None,
    aws_region_name: str = None,
) -> Dict[str, str]:
    """Gets environment variables needed for the project.

    It supports 2 ways of getting the environment variables:
    1. From a local .env file
    2. From AWS Secrets Manager
    Note that if both are provided, the .env file will be used.

    Args:
        env_file_path (str): path to .env file
        aws_secret_name (str): name of AWS secret
    """

    if env_file_path is None and aws_secret_name is None:
        raise ValueError("Either env_file_path or aws_secret_name must be provided")

    config: Dict[str, Optional[str]] = {}

    if env_file_path:
        # read a local .env file
        logger.warn(f"Trying to read .env file from {env_file_path}")
        if os.path.isfile(env_file_path):
            config = dotenv_values(env_file_path)
        else:
            raise ValueError("env_file_path is invalid")
    else:
        if aws_secret_name is None:
            raise ValueError("aws_secret_name must be provided")
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        max_retries = 3  # Maximum number of retries
        retry_delay = 10  # Delay in seconds between retries
        logger.warn(
            f"Trying to read AWS secret {aws_secret_name} from region {aws_region_name}"
        )
        for attempt in range(max_retries):
            try:
                # Create a Secrets Manager client
                session = boto3.session.Session()
                client = session.client(
                    service_name="secretsmanager", region_name=aws_region_name
                )

                # Attempt to get the secret value
                get_secret_value_response = client.get_secret_value(
                    SecretId=aws_secret_name
                )
                break  # Break the loop if successful
            except NoCredentialsError as e:
                if attempt < max_retries - 1:
                    print(
                        f"Failed to get credentials, retrying in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                else:
                    raise e
            except ClientError as e:
                raise e

        # Decrypts secret using the associated KMS key.
        secret = get_secret_value_response["SecretString"]

        try:
            # Parse JSON string into a Python dictionary
            open_ai_keys: List[str] = json.loads(secret).get("OPENAI_APIKEY", [])
            choice = random.choice(range(len(open_ai_keys)))
            logger.info(f"Using OpenAI API key {choice}")
            config["OPENAI_APIKEY"] = open_ai_keys[choice]
        except json.JSONDecodeError as e:
            logger.error("Could not parse JSON secret")
            raise e
        except Exception as e:
            logger.error("Failed to get OpenAI API key")
            raise e

    config["NONCE"] = [None, "", " ", "\n", "."]

    # Language Models API Keys
    openai_keys = config.get("OPENAI_APIKEY", None)
    palm_api_keys = config.get("PALM_APIKEY", None)

    # Setting environment variables for LangChain, note that the name is different due to convention
    if openai_keys:
        os.environ["OPENAI_API_KEY"] = openai_keys
    if palm_api_keys:
        os.environ["PALM_API_KEY"] = palm_api_keys
    # Huggingface tokenizers
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    return config
