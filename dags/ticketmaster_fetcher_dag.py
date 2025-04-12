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
    from fetchers.ticketmaster import TicketmasterFetcher
    logger.info("Successfully imported TicketmasterFetcher")
except Exception as e:
    logger.error(f"Failed to import TicketmasterFetcher: {str(e)}")
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
    'ticketmaster_scraper',
    default_args=default_args,
    description='Scrapes events from Ticketmaster',
    schedule_interval='0 */24 * * *',  # Runs every 24 hours
    catchup=False  # Don't run for past dates
)

def scrape_ticketmaster(max_events=100):
   
    logger.info(f"Starting Ticketmaster scraping")
    try:
        # Initialize the fetcher
        ticketmaster_fetcher = TicketmasterFetcher()
        
        # Fetch and process events
        ticketmaster_fetcher.fetch_events(max_events)
        
        logger.info(f"Successfully scraped Ticketmaster events")
        return f"Successfully scraped Ticketmaster events"
        
    except Exception as e:
        logger.error(f"Error scraping Ticketmaster events: {str(e)}")
        raise

# Create task instance
scrape_ticketmaster_task = PythonOperator(
    task_id='scrape_ticketmaster',
    python_callable=scrape_ticketmaster,
    op_kwargs={
        'max_events': 100
    },
    dag=dag,
)

logger.info("DAG has been configured successfully")

# For testing purposes
if __name__ == "__main__":
    logger.info("Testing DAG file")
    dag.test() 