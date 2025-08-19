import os

from dotenv import load_dotenv
from google.cloud import bigquery
from typing import List
from google.api_core.exceptions import GoogleAPIError as GoogleCloudError
import re
from rapidfuzz import fuzz, process
from google.cloud.exceptions import GoogleCloudError


from logger_setup import logger

# When deploying on Render, credentials can be provided as a secret file.
# This sets the necessary environment variable if the secret file exists.
# The Google Cloud client library automatically detects this variable.
load_dotenv()

if os.getenv("ENV") == 'local':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GCP_KEY")
    logger.info(f"GOOGLE_APPLICATION_CREDENTIALS set to: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")

def get_client():
    """
    Initialize and return a BigQuery client.

    Returns:
        bigquery.Client: Configured BigQuery client

    Raises:
        GoogleCloudError: If client initialization fails
    """
    try:
        client = bigquery.Client()
        logger.info("BigQuery client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize BigQuery client: {str(e)}")
        raise GoogleCloudError(f"BigQuery client initialization failed: {str(e)}")


def run_query(sql_query, explanation):
    """
    Execute a SQL query on BigQuery and return formatted results.

    Args:
        sql_query (str): The SQL query to execute
        explanation (str): Explanation of what the query does

    Returns:
        str: Formatted results with explanation and table data

    Raises:
        GoogleCloudError: If query execution fails
    """
    try:
        client = get_client()
        logger.info(
            f"Executing query: {sql_query[:100]}..." if len(sql_query) > 100 else f"Executing query: {sql_query}")

        # Run the query and get a QueryJob
        query_job = client.query(sql_query)  # API request

        # Wait for the job to complete and fetch results
        results = query_job.result()  # Waits for job to complete.

        # Log query statistics
        if query_job.total_bytes_processed:
            logger.info(f"Query processed {query_job.total_bytes_processed} bytes")
        if query_job.total_bytes_billed:
            logger.info(f"Query billed for {query_job.total_bytes_billed} bytes")

        formatted_results = explanation + "\n\n**Table Data:**\n\n" + format_results_for_llm(results)
        logger.info(f"Query completed successfully, returned {results.total_rows} rows")

        return formatted_results

    except Exception as e:
        error_msg = f"Query execution failed: {str(e)}"
        logger.error(error_msg)
        raise GoogleCloudError(error_msg)


def get_table_headers(dataset_id, table_id):
    """
    Get column headers for a specific BigQuery table.

    Args:
        dataset_id (str): BigQuery dataset ID
        table_id (str): BigQuery table ID

    Returns:
        list: List of column names

    Raises:
        GoogleCloudError: If table access fails
    """
    try:
        client = get_client()
        # Get the table
        table = client.get_table(f"{dataset_id}.{table_id}")
        headers = [field.name for field in table.schema]
        logger.info(f"Retrieved {len(headers)} column headers for {dataset_id}.{table_id}")
        return headers

    except Exception as e:
        error_msg = f"Failed to get table headers for {dataset_id}.{table_id}: {str(e)}"
        logger.error(error_msg)
        raise GoogleCloudError(error_msg)


def format_results_for_llm(results) -> str:
    """
    Format BigQuery results into a structured Markdown table format suitable for LLM processing.

    Args:
        results: BigQuery query results object

    Returns:
        str: Formatted string with headers and data in a Markdown table structure
    """

    formatted_results: List[str] = []
    try:
        # Get column names from the schema
        if results and results.total_rows > 0:
            # Get the schema from the results
            schema = results.schema
            column_names = [field.name for field in schema]

            # Create Markdown-formatted header row
            header_row = "| " + " | ".join(column_names) + " |"
            separator_row = "| " + " | ".join(["---"] * len(column_names)) + " |"

            formatted_results.append(header_row)
            formatted_results.append(separator_row)

            # Format each data row in Markdown
            row_count = 0
            formatted_results = []
            for row in results:
                # Handle None values and convert all values to strings
                row_values = []
                for value in row:
                    if value is None:
                        row_values.append("NULL")
                    else:
                        # Escape pipe characters in data to avoid breaking Markdown table
                        escaped_value = str(value).replace("|", "\\|")
                        row_values.append(escaped_value)

                formatted_row = "| " + " | ".join(row_values) + " |"
                formatted_results.append(formatted_row)
                row_count += 1

                # Limit results to prevent overwhelming output (configurable)
                if row_count >= 1000:  # Limit to 1000 rows
                    formatted_results.append(
                        f"| ... | (showing first 1000 rows out of {results.total_rows} total) | ... |")
                    break

            logger.info(f"Formatted {row_count} rows for LLM processing")

        else:
            formatted_results.append("| No Data | Query returned no results |")
            formatted_results.append("| --- | --- |")
            logger.info("Query returned no results")

        # Join all formatted rows with newlines
        return "\n".join(formatted_results)

    except Exception as e:
        logger.error(f"Failed to format results: {str(e)}")
        return f"Error formatting results: {str(e)}"

def normalize_string(s: str) -> str:
    """
    Normalizes a string to be case-insensitive, space-insensitive, and special character-insensitive.
    """
    s = s.lower()
    s = re.sub(r'[^a-z]', '', s)  # Remove special characters
    return s.strip()


def resolve_name_tool(user_input: str, column: str, table: str) -> str | None:
    try:
        client = get_client()
        sql_query = f"SELECT DISTINCT {column} FROM {table}"
        logger.info(
            f"Executing query: {sql_query[:100]}..." if len(sql_query) > 100 else f"Executing query: {sql_query}"
        )

        query_job = client.query(sql_query)
        results = query_job.result()

        raw_values = [row[column] for row in results if row[column]]

        if not raw_values:
            logger.warning(f"No values found in table {table} for column '{column}'")
            return None

        # Map of normalized -> original
        norm_to_original = {normalize_string(v): v for v in raw_values}
        norm_values = list(norm_to_original.keys())

        user_input_normalized = normalize_string(user_input)
        match = process.extractOne(query=user_input_normalized, choices=norm_values, scorer=fuzz.token_sort_ratio)

        if match and isinstance(match, tuple) and len(match) >= 2:
            norm_best_match, score, key = match
            best_match = norm_to_original[norm_best_match]
            logger.info(f"✅ Best fuzzy match for '{user_input}': '{best_match}' with score {score}")
            return best_match
        else:
            logger.warning(f"⚠️ No fuzzy match found or unexpected format: {match}")
            return None

    except Exception as e:
        error_msg = f"Query execution failed: {str(e)}"
        logger.error(error_msg)
        raise GoogleCloudError(error_msg)

