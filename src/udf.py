# import json
import simplejson as json
import requests
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import Row
import _snowflake
import pandas as pd

def init_app(session: Session, config) -> str:
  """
    Initializes function API endpoints with access to the secret and API integration.

    Args:
      session (Session): An active session object for authentication and communication.
      config (Any): The configuration settings for the connector.

    Returns:
      str: A status message indicating the result of the provisioning process.
   """
  secret_name = config['secret_name']
  external_access_integration_name = config['external_access_integration_name']

  alter_function_sql = f'''
    ALTER FUNCTION code_schema.translate(string, string) SET 
    SECRETS = ('token' = {secret_name}) 
    EXTERNAL_ACCESS_INTEGRATIONS = ({external_access_integration_name})'''
  
  session.sql(alter_function_sql).collect()

  return 'Snowflake translation app initialized'

def translate(text, target_language):
  """
    Translate the text value to the target language and return the translated text.


    Args:
      text (str): The text to translate.
      target_language (str): The two letter code representing the language to translate the text into.
    Returns:
      str: The translated text.
   """

  auth_key = _snowflake.get_generic_secret_string('token')

  body = {
    'text': [
      text
    ],
    'target_lang': target_language
  }

  url = 'https://api-free.deepl.com/v2/translate'
  headers = {
    'Authorization': 'DeepL-Auth-Key ' + auth_key
  }

  session = requests.Session()
  response = session.post(url, json=body, headers=headers)
  response_as_json = json.loads(response.text)

  return response_as_json['translations'][0]['text']