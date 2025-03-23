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
    'email': ['saadhvirayasam10@gmail.com'],
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
    schedule_interval='0 */12 * * *',  # Runs every 12 hours
    catchup=False  # Don't run for past dates
)

def scrape_eventbrite(max_events=100, city="co--boulder"):
    """
    Scrape events from Eventbrite using the EventbriteFetcher
    """
    logger.info(f"Starting Eventbrite scraping for {city}")
    try:
        # Initialize the fetcher
        eventbrite_fetcher = EventbriteFetcher(city=city)
        
        # Fetch and process events
        eventbrite_fetcher.fetch_events(max_events)
        
        logger.info(f"Successfully scraped Eventbrite events for {city}")
        return f"Successfully scraped Eventbrite events for {city}"
        
    except Exception as e:
        logger.error(f"Error scraping Eventbrite events: {str(e)}")
        raise

# Create task instance
scrape_eventbrite_task = PythonOperator(
    task_id='scrape_eventbrite',
    python_callable=scrape_eventbrite,
    op_kwargs={
        'max_events': 100,
        'city': 'co--boulder'
    },
    dag=dag,
)

logger.info("DAG has been configured successfully")

# For testing purposes
if __name__ == "__main__":
    logger.info("Testing DAG file")
    dag.test() 