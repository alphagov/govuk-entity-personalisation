import google.auth
from google.cloud import bigquery


def create_bq_client(credentials: str = None, project_id: str = None) -> bigquery.Client:
    """
    Create client to connect to Google BigQuery

    :param credentials: String of credentials to pass to access BigQuery.
    :param project_id: String of project_id you want to work from in BigQuery.
    :return: Client for connecting to BigQuery.

    """
    if credentials is None and project_id is None:
        credentials, project_id = google.auth.default()

    return bigquery.Client(credentials=credentials,
                           project=project_id)
