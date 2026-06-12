# ⛏️ Scraplab

> A minimalist, containerized web scraping infrastructure built with **Python 3.12**, **Scrapy**, and **Docker**.

Scraplab is designed around a **decoupled architecture** that separates crawling, parsing, data modeling, and extraction orchestration into independent layers. This architecture keeps scraping logic maintainable, testable, and scalable as requirements evolve.

---

## ✨ Features

* 🕷️ Scrapy-powered web crawling
* 📄 Dedicated HTML parsing layer
* 🏗️ Structured data models
* 🔄 Extraction orchestration pipeline
* 🐳 Dockerized deployment
* 🧪 Simple local development workflow
* 📦 Reproducible execution environments
* 🔌 Extensible architecture for additional data sources

---

## 🏗️ Architecture

Scraplab follows an asynchronous, queue-driven architecture that separates crawling from parsing. Crawlers focus solely on fetching and storing raw content, while parser workers independently process queued jobs.

```text
┌──────────────┐
│   Website    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Spider    │
│   (Scrapy)   │
└──────┬───────┘
       │
       │ Save raw page
       ▼
┌──────────────┐
│   Storage    │
│ HTML / Files │
└──────┬───────┘
       │
       │ Publish job
       ▼
┌──────────────┐
│   RabbitMQ   │
│    Queue     │
└──────┬───────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       │              │              │              │
       ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Parser 1 │  │ Parser 2 │  │ Parser 3 │  │ Parser N │
│ Process  │  │ Process  │  │ Process  │  │ Process  │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │             │
     └─────────────┴─────────────┴─────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │ parser.py    │
                   │ models.py    │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ PostgreSQL   │
                   └──────────────┘
```

### Workflow

1. The Scrapy spider crawls a target website.
2. Raw HTML or page content is stored in persistent storage.
3. A message containing the file path and associated metadata is published to RabbitMQ.
4. One available parser worker consumes the message.
5. The parser retrieves the stored file.
6. Content is parsed and transformed into structured models.
7. Extracted data is validated and persisted to PostgreSQL.

### Scalability

Parser workers are horizontally scalable.

* A single crawler can feed thousands of parsing jobs.
* Multiple parser processes can run concurrently across one or more machines.
* RabbitMQ distributes jobs among available workers.
* Parsing throughput scales independently of crawling throughput.
* New parser workers can be added without modifying crawler logic.

This architecture prevents CPU-intensive parsing from blocking crawling operations and allows each layer to scale according to workload demands.


## 📂 Project Structure

```text
scraplab/
├── .venv/
│
├── basic/
│   ├── basic/
│   │   ├── spiders/
│   │   │   ├── __init__.py
│   │   │   └── basic_spider.py
│   │   │
│   │   ├── __init__.py
│   │   ├── items.py
│   │   ├── middlewares.py
│   │   ├── pipelines.py
│   │   └── settings.py
│   │
│   └── scrapy.cfg
│
├── extract.py
├── parser.py
├── models.py
│
├── Dockerfile
├── compose.yaml
├── requirements.txt
│
├── .gitignore
└── .dockerignore
```

---

## 🔍 Components

### Spider Layer (`basic/spiders/`)

Responsible for:

* Sending requests
* Crawling target websites
* Handling responses
* Extracting raw HTML and metadata

### Parsing Layer (`parser.py`)

Responsible for:

* HTML parsing
* Structured content extraction
* Data normalization
* Text cleaning and preprocessing

### Data Models (`models.py`)

Defines application schemas used for:

* Validation
* Transformation
* Serialization
* Persistence

### Extraction Pipeline (`extract.py`)

Coordinates the complete workflow:

1. Receives crawler output
2. Parses raw content
3. Creates validated model instances
4. Persists structured records

---

## 🚀 Getting Started

### Prerequisites

Ensure the following are installed:

* Python 3.12+
* Docker
* Docker Compose

---

### Clone the Repository

```bash
git clone <repository-url>
cd scraplab
```

---

### Create a Virtual Environment

#### Linux / macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

#### Windows (CMD)

```cmd
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
```

#### Windows (PowerShell)

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

---

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🕷️ Running the Spider

Navigate to the Scrapy project directory and run the spider:

```bash
cd basic
scrapy crawl basic_spider
```

---

## ⚙️ Running the Extraction Pipeline

Execute the full extraction workflow:

```bash
python extract.py
```

---

## 🐳 Docker Usage

### Build Image

```bash
docker build -t scraplab-scraper .
```

### Start Containers

```bash
docker compose up -d
```

### View Logs

```bash
docker compose logs -f
```

### Stop Containers

```bash
docker compose down
```

---

## 🔒 Production Considerations

### Environment Variables

Keep secrets outside source control.

```yaml
environment:
  DATABASE_URL: ${DATABASE_URL}
  API_TOKEN: ${API_TOKEN}
```

### Recommended Practices

* Keep credentials out of repositories
* Configure retries and rate limiting
* Enable structured logging
* Rotate log files
* Monitor crawler failures
* Store data in dedicated persistence layers
* Add health checks for long-running jobs

---

## 🧪 Development

### Format Code

```bash
black .
```

### Lint Code

```bash
flake8 .
```

---

## 📖 Design Philosophy

Scraplab follows a simple principle:

> **Network operations, parsing logic, and persistence concerns should remain independent.**

Benefits include:

* Cleaner codebases
* Easier testing
* Better maintainability
* Improved scalability
* Faster onboarding for contributors

---

## 📄 License

```text
MIT License
```

---

<div align="center">

## ⛏️ Scraplab

**Extract • Transform • Structure**

Minimal infrastructure for building reliable scraping pipelines.

</div>
