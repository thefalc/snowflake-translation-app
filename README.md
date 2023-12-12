# Skyflow Native App

Welcome to Skyflow's Native App for Snowflake. This application supports the tokenization and
detokenization API endpoints for Skyflow's APIs as build-in Snowflake UDFs.

## Test the installation

To test the installation, perform the following:

- In Skyflow Studio, create a quickstart vault and note the vault URL.
- Create a service account with the Vault Editor role and download the credentials.json file to your machine.
- Copy the code below and paste it into a SQL Snowsight sheet.
- Update the REPLACE_ME value for the **VAULT_URL** with your quickstart vault URL.
- Update the REPLACE_ME value for the **SECRET_STRING** with the contents of credentials.json.
- If the name of your app is different than `skyflow_data_privacy_vault`, then update all instances of `skyflow_data_privacy_vault` with your app name.
- Execute all SQL statements.

### Sample Skyflow Native App script

The script below configures the application with a vault secret for making API calls to Skyflow and grants access
to call the vault authentication and data APIs.

After running the script, you should see 9 records in your vault's person's table and 9 tokenized
records in your Snowflake **customers** table.

``` sql
USE ROLE ACCOUNTADMIN;

-- Variables for setting up app and testing integration
SET DATABASE_NAME = 'TEST';
SET SCHEMA_NAME = 'TEST_SCHEMA';
SET APP_NAME = 'skyflow_data_privacy_vault';
SET SECRET_NAME = $DATABASE_NAME || '.' || $SCHEMA_NAME || '.skyflow_vault_secret';

-- Skyflow specific variables for testing the installation
SET VAULT_URL = 'REPLACE_ME';
SET TABLE_NAME = 'persons';

USE DATABASE IDENTIFIER($DATABASE_NAME);
USE SCHEMA IDENTIFIER($SCHEMA_NAME);

CREATE OR REPLACE SECRET IDENTIFIER($SECRET_NAME)
        TYPE = GENERIC_STRING
        SECRET_STRING = 'REPLACE_ME';
    
-- Grant network access to the Skyflow APIs
CREATE OR REPLACE NETWORK RULE skyflow_apis_network_rule
 MODE = EGRESS
 TYPE = HOST_PORT
 VALUE_LIST = ('manage.skyflowapis.com', 'ebfc9bee4242.vault.skyflowapis.com');

-- Create a network integration based on the network rule
SET CREATE_INTEGRATION = 'CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION skyflow_external_access_integration
ALLOWED_NETWORK_RULES = (skyflow_apis_network_rule)
ALLOWED_AUTHENTICATION_SECRETS = (''' || $SECRET_NAME || ''')
ENABLED = TRUE';

SELECT $CREATE_INTEGRATION;
EXECUTE IMMEDIATE $CREATE_INTEGRATION;

GRANT USAGE ON DATABASE TEST TO APPLICATION IDENTIFIER($APP_NAME);
GRANT USAGE ON SCHEMA TEST.TEST_SCHEMA TO APPLICATION IDENTIFIER($APP_NAME);
GRANT USAGE ON INTEGRATION skyflow_external_access_integration TO APPLICATION IDENTIFIER($APP_NAME);
GRANT READ ON SECRET IDENTIFIER($SECRET_NAME) TO APPLICATION IDENTIFIER($APP_NAME);

-- Initialize the Skyflow app
CALL skyflow_data_privacy_vault.code_schema.init_app(PARSE_JSON('{
        "secret_name": "' || $SECRET_NAME || '",
        "external_access_integration_name": "skyflow_external_access_integration",
    }'));

-- Store tokenization response in a temporary table
CREATE OR REPLACE TEMPORARY TABLE customer_json (
  var variant 
)
AS select PARSE_JSON(SELECT skyflow_data_privacy_vault.code_schema.tokenize($VAULT_URL, $TABLE_NAME, PARSE_JSON('{
    "records": [{
        "fields": {
            "name": "Jane Doe",
            "email_address": "jane.doe@gmail.com",
            "state": "California",
            "date_of_birth": "1989-02-03",
            "ssn": "123-45-1212"
        }
    },
    {
        "fields": {
            "name": "John Doe",
            "email_address": "john.doe@gmail.com",
            "state": "New York",
            "date_of_birth": "1979-08-23",
            "ssn": "122-55-2233"
        }
    },
    {
        "fields": {
            "name": "Sally Smith",
            "email_address": "sally.smith@gmail.com",
            "state": "California",
            "date_of_birth": "1985-07-15",
            "ssn": "342-23-5467"
        }
    },
    {
        "fields": {
            "name": "Jim Anderson",
            "email_address": "jim.anderson@gmail.com",
            "state": "New York",
            "date_of_birth": "1995-10-25",
            "ssn": "678-54-2138"
        }
    },
    {
        "fields": {
            "name": "Sean Finkelston",
            "email_address": "sean.finkelston@gmail.com",
            "state": "Maine",
            "date_of_birth": "2000-02-07",
            "ssn": "342-98-3243"
        }
    },
    {
        "fields": {
            "name": "Sandy Finkelston",
            "email_address": "sandy.finkelston@gmail.com",
            "state": "Maine",
            "date_of_birth": "2002-04-17",
            "ssn": "234-23-8945"
        }
    },
    {
        "fields": {
            "name": "John Johnson",
            "email_address": "john.johnson@gmail.com",
            "state": "California",
            "date_of_birth": "1962-12-17",
            "ssn": "111-32-4353"
        }
    },
    {
        "fields": {
            "name": "Danielle Fields",
            "email_address": "danielle.fields@gmail.com",
            "state": "California",
            "date_of_birth": "1975-03-14",
            "ssn": "995-23-9963"
        }
    },
    {
        "fields": {
            "name": "Nedi Marquess",
            "email_address": "nedi.marquess@gmail.com",
            "state": "New York",
            "date_of_birth": "1964-05-11",
            "ssn": "812-91-8963"
        }
    }]
}')));

SELECT * FROM customer_json;

-- Convert JSON response into individual rows and columns
CREATE OR REPLACE TABLE customers AS
    SELECT
        Y.value:"name"::VARCHAR AS name,
        Y.value:"email_address"::VARCHAR AS email_address,
        Y.value:"ssn"::VARCHAR AS ssn,
        Y.value:"state"::VARCHAR AS state,
        Y.value:"date_of_birth"::VARCHAR AS date_of_birth
   FROM customer_json, LATERAL FLATTEN(input => var) Y;

SELECT * FROM customers;

-- Customers by state
SELECT skyflow_data_privacy_vault.code_schema.detokenize($VAULT_URL, state) AS state, COUNT(*) FROM customers GROUP BY state;

-- Detokenize names and emails
SELECT skyflow_data_privacy_vault.code_schema.detokenize($VAULT_URL, name) AS name, skyflow_data_privacy_vault.code_schema.detokenize($VAULT_URLs, email_address) AS email_address FROM customers;
```