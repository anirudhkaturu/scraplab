import pika
from parsel import Selector
import json
import os

# data scrapping function
from extract import extract_product_info

# database stuff
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert  # <-- ADDED for batch upsert
from models import Product, Base

# postgres database connection init
DATABASE_URL = os.getenv("DATABASE_URL", 'postgresql://postgres:ani@localhost/amazon_cricket')
# echo=False to stop logging every SQL (change to True only for debugging)
engine = create_engine(DATABASE_URL, echo=os.getenv("SQL_ECHO", "false").lower() == "true")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# rabbit mq init
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
)
channel = connection.channel()

QUEUE_NAME = "basic_spider"
channel.queue_declare(queue=QUEUE_NAME, durable=True)

def upsert_products_batch(session, products_data):
    """Insert or update multiple products in one database round trip.

    Returns:
        int: Number of rows actually inserted or updated.
    """
    if not products_data:
        return 0

    stmt = insert(Product).values(products_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=['asin'],  # uses the unique constraint on asin
        set_={
            'title': stmt.excluded.title,
            'price': stmt.excluded.price,
            'original_price': stmt.excluded.original_price,
            'discount_percent': stmt.excluded.discount_percent,
            'rating': stmt.excluded.rating,
            'rating_count': stmt.excluded.rating_count,
            'delivery_date': stmt.excluded.delivery_date,
            'scraped_at': stmt.excluded.scraped_at,
            'url': stmt.excluded.url,
        }
    )
    result = session.execute(stmt)
    session.commit()
    return result.rowcount


# callback function to use with basic_consume
def callback(ch, method, properties, body):
    print(f'Received {body.decode("utf-8")}')

    body_json = json.loads(body.decode("utf-8"))
    DATA_DIR = os.getenv("DATA_DIR", "/app/basic_spider_data")
    filename = os.path.join(DATA_DIR, body_json["filename"])

    # read the HTML file
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"{filename} not found!!!")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    session = SessionLocal()
    selector = Selector(text=html_content)
    result_li = selector.css('div[data-component-type="s-search-result"]')

    # Collect all valid products from this file into a batch
    products_batch = []
    for result in result_li:
        product_data = extract_product_info(result)
        if not product_data or not product_data.get("asin"):
            continue
        product_data["scraped_at"] = body_json["crawl_time"]
        if not product_data.get("url"):
            product_data["url"] = body_json["url"]
        products_batch.append(product_data)

    # If no products, just ack and close
    if not products_batch:
        print("No valid products found in file.")
        session.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Perform the batch upsert (insert or update)
    try:
        affected = upsert_products_batch(session, products_batch)
        print(f"UPSERTED {affected} products (new or updated) out of {len(products_batch)}")
    except Exception as e:
        # Full error details – this will finally show you why the rollback happened
        import traceback
        print(f"Batch upsert failed: {type(e).__name__} - {e}")
        traceback.print_exc()
        session.rollback()
        # If you want to retry the message later, uncomment the next line:
        # ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        # return
    finally:
        session.close()

    # Acknowledge the message (unless you chose to nack on error)
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)

print("Waiting for messages")
channel.start_consuming()