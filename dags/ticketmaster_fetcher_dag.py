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
    schedule_interval='0 0 * * *',  # Runs at midnight
    catchup=False  # Don't run for past dates
)

cities = [
    "New York", "Los Angeles", "Chicago", "Austin", "San Francisco",
    "Seattle", "Miami", "Denver", "Boston", "Atlanta"
]

def scrape_ticketmaster_multiple_cities(max_events=50, total_days=10):
    logger.info("Starting Ticketmaster scraping for multiple cities and days")
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for city in cities:
        logger.info(f"City: {city}")
        for i in range(total_days):
            current_date = base_date + timedelta(days=i)
            start_date_str = current_date.strftime("%Y-%m-%dT00:00:00Z")
            end_date_str = current_date.strftime("%Y-%m-%dT23:59:59Z")

            logger.info(f"Date: {start_date_str} to {end_date_str}")
            try:
                fetcher = TicketmasterFetcher(
                    city=city,
                    start_date=start_date_str,
                    end_date=end_date_str
                )
                fetcher.fetch_events(max_events)
                logger.info(f"Success: {city} on {start_date_str}")
            except Exception as e:
                logger.error(f"Failed: {city} on {start_date_str}: {str(e)}")

    return "Ticketmaster scraping completed for all cities and days."

scrape_ticketmaster_task = PythonOperator(
    task_id='scrape_ticketmaster_multiple_cities',
    python_callable=scrape_ticketmaster_multiple_cities,
    op_kwargs={'max_events': 50, 'total_days': 10},
    dag=dag,
)

logger.info("DAG has been configured successfully")

# For testing purposes
if __name__ == "__main__":
    logger.info("Testing DAG file")
    dag.test() 