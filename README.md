# Translation Native App

This is a simple Snowflake Native App that demonstrates how to make external API call from a 
Native App using Snowflake's support for secrets and external network rules.

## Sample Native App script

Before you can test the app, please follow the instructions from the [Native Apps Framework](https://docs.snowflake.com/en/developer-guide/native-apps/tutorials/getting-started-tutorial#introduction) getting started tutorial.

The script below configures the application with a [DeepL](https://www.deepl.com) free tier API key.

After running the script, you should see the phrase "Hello, World!" translated into French, German, and Chinese.

``` sql
USE ROLE ACCOUNTADMIN;

CREATE DATABASE test;
CREATE SCHEMA test.test_schema;

USE DATABASE test;
USE SCHEMA test_schema;

CREATE OR REPLACE NETWORK RULE deepl_apis_network_rule
    MODE = EGRESS
    TYPE = HOST_PORT
    VALUE_LIST = ('api-free.deepl.com');

CREATE OR REPLACE SECRET deepl_auth_key
   TYPE = GENERIC_STRING
   SECRET_STRING = '<REPLACE_ME_WITH_DEEPL_AUTH_KEY>';

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION deepl_external_access_integration
    ALLOWED_NETWORK_RULES = (deepl_apis_network_rule)
    ALLOWED_AUTHENTICATION_SECRETS = (deepl_auth_key)
    ENABLED = true;

GRANT USAGE ON DATABASE TEST TO APPLICATION snowflake_translation_app;
GRANT USAGE ON SCHEMA TEST.TEST_SCHEMA TO APPLICATION snowflake_translation_app;
GRANT USAGE ON INTEGRATION deepl_external_access_integration TO APPLICATION snowflake_translation_app;
GRANT READ ON SECRET TEST.TEST_SCHEMA.deepl_auth_key TO APPLICATION snowflake_translation_app;

CALL snowflake_translation_app.code_schema.init_app(PARSE_JSON('{
        "secret_name": "TEST.TEST_SCHEMA.deepl_auth_key",
        "external_access_integration_name": "deepl_external_access_integration",
    }'));

SELECT snowflake_translation_app.code_schema.translate('Hello, World!', 'FR');
SELECT snowflake_translation_app.code_schema.translate('Hello, World!', 'DE');
SELECT snowflake_translation_app.code_schema.translate('Hello, World!', 'ZH');
```