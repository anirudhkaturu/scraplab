import re
from urllib.parse import urlparse, parse_qs, unquote

def extract_product_info(result):
    """Extract all required fields from a single search result selector."""
    asin = result.xpath('@data-asin').get()

    # Title
    title = (
        result.css('h2 a span::text').get() or
        result.css('h2 span::text').get() or
        result.css('a.a-link-normal h2 span::text').get()
    )

    # Current price
    price_whole = result.css('.a-price .a-price-whole::text').get()
    price_fraction = result.css('.a-price .a-price-fraction::text').get()
    price = f"{price_whole}{price_fraction}" if price_whole and price_fraction else price_whole

    # Original price (MRP) – strikethrough price
    original_price_whole = result.css('.a-text-price .a-price-whole::text').get()
    original_price_fraction = result.css('.a-text-price .a-price-fraction::text').get()
    original_price = None
    if original_price_whole:
        original_price = f"{original_price_whole}{original_price_fraction or ''}"
    # Alternative: some pages use .a-price.a-text-price with strike
    if not original_price:
        mrp_text = result.css('.a-price.a-text-price .a-offscreen::text').get()
        if mrp_text:
            original_price = re.search(r'[\d,]+\.?\d*', mrp_text).group() if re.search(r'[\d,]+\.?\d*', mrp_text) else None

    # Discount percentage
    discount = None
    if price and original_price:
        try:
            # Remove commas and convert to float
            price_num = float(price.replace(',', ''))
            original_num = float(original_price.replace(',', ''))
            if original_num > 0:
                discount = round(((original_num - price_num) / original_num) * 100)
        except:
            pass
    # Sometimes discount is written as text e.g., "(25% off)"
    if not discount:
        discount_text = result.xpath('.//span[contains(text(), "% off")]/text()').get()
        if discount_text:
            match = re.search(r'(\d+)%', discount_text)
            if match:
                discount = int(match.group(1))

    # Rating stars
    rating_text = result.css('.a-icon-star-mini .a-icon-alt::text').get()
    rating = None
    if rating_text:
        match = re.search(r'(\d+\.?\d*)', rating_text)
        if match:
            rating = match.group(1)

    # Rating count
    rating_count_text = (
        result.css('a[aria-label*="ratings"] span::text').get() or
        result.css('.a-size-mini.s-underline-text::text').get()
    )
    rating_count = None
    if rating_count_text:
        match = re.search(r'\((\d+)\)', rating_count_text)
        if match:
            rating_count = match.group(1)

    # Delivery date (e.g., "FREE delivery Thu, 18 Jun")
    delivery_element = result.css('.udm-primary-delivery-message .a-text-bold::text')
    delivery_date = delivery_element.get()
    if delivery_date:
        delivery_date = delivery_date.strip()

    # Product URL
    product_path = (
            result.css('h2 a::attr(href)').get() or
            result.css('a.a-link-normal::attr(href)').get()
    )
    product_url = None

    if product_path:
        # Check if this is an Amazon Sponsored Ad redirect link
        if '/sspa/click' in product_path:
            try:
                # Parse the query parameters from the ad link
                parsed_url = urlparse(product_path)
                query_params = parse_qs(parsed_url.query)

                # Extract the real destination URL hidden inside the 'url' parameter
                if 'url' in query_params:
                    # unquote converts '%2F' back into '/'
                    real_path = unquote(query_params['url'][0])
                    product_url = f"https://www.amazon.in{real_path.split('?')[0]}"
            except Exception:
                product_url = None  # Fallback to None if parsing fails

        # If it's a normal organic product link, handle it normally
        if not product_url:
            clean_path = product_path.split('?')[0] if '?' in product_path else product_path
            product_url = f"https://www.amazon.in{clean_path}"

    return {
        'asin': asin,
        'title': title,
        'price': price,
        'original_price': original_price,
        'discount_percent': discount,
        'rating': rating,
        'rating_count': rating_count,
        'delivery_date': delivery_date,
        'url': product_url,
    }
