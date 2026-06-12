from pathlib import Path
from datetime import datetime
from hashlib import sha256
import os

import scrapy

class BasicSpider(scrapy.Spider):
    name = "basic"

    start_urls = [
        # english & kashmir willow variations
        "https://www.amazon.in/s?k=english+willow+cricket+bat",
        "https://www.amazon.in/s?k=kashmir+willow+cricket+bat",
        "https://www.amazon.in/s?k=leather+cricket+bat",
        "https://www.amazon.in/s?k=tennis+cricket+bat",
        "https://www.amazon.in/s?k=plastic+cricket+bat",
        # bat accessories (huge submarket)
        "https://www.amazon.in/s?k=cricket+bat+grip",
        "https://www.amazon.in/s?k=cricket+bat+mallet",
        "https://www.amazon.in/s?k=cricket+bat+oil",
        "https://www.amazon.in/s?k=cricket+bat+anti+scuff+sheet",
        "https://www.amazon.in/s?k=cricket+bat+grip+cone",
        # balls type and material
        "https://www.amazon.in/s?k=leather+cricket+ball",
        "https://www.amazon.in/s?k=red+leather+cricket+ball",
        "https://www.amazon.in/s?k=white+leather+cricket+ball",
        "https://www.amazon.in/s?k=pink+cricket+ball",
        "https://www.amazon.in/s?k=tennis+cricket+ball+heavy",
        "https://www.amazon.in/s?k=light+tennis+cricket+ball",
        "https://www.amazon.in/s?k=cricket+hanging+ball",
        "https://www.amazon.in/s?k=wind+ball+cricket",
        # safety and protective gear
        "https://www.amazon.in/s?k=cricket+abdomen+guard",
        "https://www.amazon.in/s?k=cricket+abdominal+guard+supporter",
        "https://www.amazon.in/s?k=cricket+thigh+pad",
        "https://www.amazon.in/s?k=cricket+dual+thigh+guard",
        "https://www.amazon.in/s?k=cricket+chest+guard",
        "https://www.amazon.in/s?k=cricket+arm+guard",
        "https://www.amazon.in/s?k=cricket+inner+gloves",
        "https://www.amazon.in/s?k=wicket+keeping+inner+gloves",
        "https://www.amazon.in/s?k=cricket+helmet+neck+guard",
        # apparel and shoes
        "https://www.amazon.in/s?k=cricket+shoes+with+spikes",
        "https://www.amazon.in/s?k=cricket+rubber_stud+shoes",
        "https://www.amazon.in/s?k=cricket+white+dress+pant+shirt",
        "https://www.amazon.in/s?k=cricket+tshirt",
        "https://www.amazon.in/s?k=cricket+trousers",
        "https://www.amazon.in/s?k=cricket+socks",
        "https://www.amazon.in/s?k=cricket+sun+hat",
        "https://www.amazon.in/s?k=cricket+cap",
        # training equipment
        "https://www.amazon.in/s?k=cricket+bowling+machine",
        "https://www.amazon.in/s?k=cricket+sidearm+ball+thrower",
        "https://www.amazon.in/s?k=cricket+catching+net",
        "https://www.amazon.in/s?k=cricket+practice+net",
        "https://www.amazon.in/s?k=cricket+target+stumps",
        "https://www.amazon.in/s?k=cricket+rebound+ball",
        "https://www.amazon.in/s?k=cricket+fitness+training+kit",
        "https://www.amazon.in/s?k=cricket+umpire+counter",
        # ground infra ie pitch mats etc
        "https://www.amazon.in/s?k=cricket+bowling+machine",
        "https://www.amazon.in/s?k=cricket+sidearm+ball+thrower",
        "https://www.amazon.in/s?k=cricket+catching+net",
        "https://www.amazon.in/s?k=cricket+practice+net",
        "https://www.amazon.in/s?k=cricket+target+stumps",
        "https://www.amazon.in/s?k=cricket+rebound+ball",
        "https://www.amazon.in/s?k=cricket+fitness+training+kit",
        "https://www.amazon.in/s?k=cricket+umpire+counter",
        # bags and kits
        "https://www.amazon.in/s?k=cricket+kit+bag+with+wheels",
        "https://www.amazon.in/s?k=cricket+backpack",
        "https://www.amazon.in/s?k=full+cricket+kit+with+bat",
        "https://www.amazon.in/s?k=boys+cricket+kit",
        "https://www.amazon.in/s?k=mens+complete+cricket+kit",
        # top brands
        "https://www.amazon.in/s?k=sg+cricket+gear",
        "https://www.amazon.in/s?k=ss+cricket+equipment",
        "https://www.amazon.in/s?k=mrf+cricket+items",
        "https://www.amazon.in/s?k=dsc+cricket",
        "https://www.amazon.in/s?k=gm+gunn+and+moore+cricket",
        "https://www.amazon.in/s?k=kookaburra+cricket",
        "https://www.amazon.in/s?k=ceat+cricket",
        # New Balance Cricket Catalog
        "https://www.amazon.in/s?k=new+balance+cricket",
        "https://www.amazon.in/s?k=nb+cricket+bat",
        "https://www.amazon.in/s?k=new+balance+cricket+shoes",
        # Gray-Nicolls Cricket Catalog
        "https://www.amazon.in/s?k=gray+nicolls+cricket",
        "https://www.amazon.in/s?k=gray+nicolls+bat",
        "https://www.amazon.in/s?k=gn+cricket+gear",
    ]

    def parse(self, response):
        # save the current page
        data_dir = os.getenv("DATA_DIR", "/app/basic_spider_data")
        Path(data_dir).mkdir(parents=True, exist_ok=True)

        page_hash = sha256(str(response.url).encode()).hexdigest()
        filename = f"{page_hash}.html"
        file_path = os.path.join(data_dir, filename)

        with open(file_path, "wb") as f:
            f.write(response.body)
        self.log(f"{file_path} saved!")

        # create pipeline
        yield {
            "page_type": "search",
            "url": response.url,
            "filename": filename,
            "crawl_time": datetime.now().isoformat(),
        }

        # pagination -> moving to the next page
        next_page = response.css('a.s-pagination-next::attr(href)').get()

        if next_page:
            next_url = response.urljoin(next_page)
            self.log(f"FOOTPRINT: Crawling next page -> {next_url}")
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
            )
        else:
            self.log(f"⚠️ No pagination link found on: {response.url}", level=scrapy.log.WARNING)

    def handle_error(self, failure):
        print(f'{failure.url} FAILED!')