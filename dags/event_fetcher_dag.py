from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to import fetchers
dag_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(dag_dir, ".."))
sys.path.append(parent_dir)

logger.info(f"DAG directory: {dag_dir}")
logger.info(f"Parent directory: {parent_dir}")
logger.info(f"Python path: {sys.path}")

try:
    from fetchers.eventbrite import EventbriteFetcher
    logger.info("Successfully imported EventbriteFetcher")
except Exception as e:
    logger.error(f"Failed to import EventbriteFetcher: {str(e)}")
    raise

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['gatherup.usa@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'eventbrite_scraper',
    default_args=default_args,
    description='Scrapes events from Eventbrite',
    schedule_interval='0 0 * * *',  # Runs at midnight
    catchup=False  # Don't run for past dates
)

cities = {
    "New York": "ny--new-york",
    "Los Angeles": "ca--los-angeles",
    "Chicago": "il--chicago",
    "Austin": "tx--austin",
    "San Francisco": "ca--san-francisco",
    "Seattle": "wa--seattle",
    "Miami": "fl--miami",
    "Denver": "co--denver",
    "Boston": "ma--boston",
    "Atlanta": "ga--atlanta"
}

def scrape_eventbrite_multiple_cities(max_events=50):
    logger.info("Starting Eventbrite scraping for multiple cities")
    for city_name, slug in cities.items():
        try:
            logger.info(f"Fetching Eventbrite events for {city_name} ({slug})")
            eventbrite_fetcher = EventbriteFetcher(city=slug)
            eventbrite_fetcher.fetch_events(max_events)
            logger.info(f"Successfully fetched for {city_name}")
        except Exception as e:
            logger.error(f"Failed for {city_name}: {str(e)}")
    return "Eventbrite scraping completed for all cities."

scrape_eventbrite_task = PythonOperator(
    task_id='scrape_eventbrite_multiple_cities',
    python_callable=scrape_eventbrite_multiple_cities,
    op_kwargs={'max_events': 50},
    dag=dag,
)

logger.info("DAG has been configured successfully")

# For testing purposes
if __name__ == "__main__":
    logger.info("Testing DAG file")
    dag.test() 