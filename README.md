# Base Django Architecture

A production-ready, highly modular Django REST framework boilerplate designed for scalability. This architecture enforces separation of concerns through Controller patterns, includes built-in primary/replica database routing, and comes pre-configured with centralized integrations for Kafka, Redis, and network requests.

---

## 🚀 Key Architectural Features

1. **Controller Pattern (`apps/core/controllers.py`)**  
   Business logic is decoupled from Django Views and moved into standalone Controllers. All API endpoints extend from base classes (`GetApiBaseView`, `CreateApiBaseView`) and execute logic via `controller_class(validated_data, user, headers).process()`.

2. **Master / Replica Database Routing**  
   All Database writes are automatically routed to the `default` MySQL instance, while reads are distributed dynamically (~50/50) between the `default` primary and `replica` databases using an `md5` hash-based custom router.

3. **Centralized Network Manager (`libs/network/`)**  
   All outgoing 3rd-party HTTP interactions route through a robust `NetworkManager` wrapper that guarantees thread safety, logs performance metrics, intelligently maps headers, and naturally prevents dangling database connections.

4. **Singleton Redis Manager (`libs/redis/`)**  
   A centralized, globally accessible `RedisClusterManager` ensures that background cache queries utilize one singular socket connection throughout the life of the application.

5. **Kafka Wrappers (`libs/kafka/`)**  
   Includes a ready-to-inherit `BaseConsumer` generic template completely pre-wired to commit offsets correctly and log errors safely. Built-in async/chunked producers make publishing topics instantaneous via python threading.

---

## 🛠️ Step-by-Step Environment Setup

Follow these instructions to safely bootstrap this repository on a new machine.

### 1. Prerequisites
- **Python 3.12+**
- **MySQL Server** (Primary mapped to `3306`, Replica mapped to `3307` locally)
- **Redis Server** (Mapped to `6379`)
- **Apache Kafka** (Optional, depending on modules ran)

### 2. Clone the Repository
```bash
git clone git@github.com:Levi-31/BASE_DJANGO_PROJECT.git
cd BASE_DJANGO_PROJECT
```

### 3. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
Ensure you are inside the active virtual environment, then run:
```bash
pip install -r requirements.txt
```

### 5. Environment Variables Structure
**CRITICAL:** For intense security practices in production, this codebase expects your `.env` file to be located **ONE FOLDER OUTSIDE** the project repository. 

For example, if your codebase lives at `~/Desktop/BASE_DJANGO_PROJECT`, your `.env` file must live exactly at `~/Desktop/.env`.

1. Copy the example configuration to your parent directory:
```bash
cp .env.example ../.env
```
2. Open `../.env` and populate it with your local `SECRET_KEY`, `REDIS_URL`, etc.

### 6. Run Migrations
Because we specify settings profiles globally, all framework commands should preferably be appended with your environment profile tag (e.g. `config.local` or `config.staging`).

```bash
python3 manage.py migrate --settings=config.local
```

### 7. Boot the Server
```bash
python3 manage.py runserver --settings=config.local
```
The boilerplate server should now be alive at `http://127.0.0.1:8000/`.

---

## 📁 Repository Structure Overview

```
BASE_DJANGO_PROJECT/
├── apps/                 # All Django application packages
│   └── core/             # Core business logic API, Models, and Views
├── config/               # Settings orchestrator
│   ├── base.py           # Universal settings overrides (Middleware/Apps)
│   ├── local.py          # Development profile 
│   ├── staging.py        # Sandbox profile
│   └── urls.py           # Global Routing Table
├── consumers/            # Kafka consumer startup scripts (`sample_consumer.py`)
├── credentials/          # Local JSON credentials (Google Sheets configs, etc.)
└── libs/                 # High Level Utilities & Wrappers
    ├── kafka/            # Kafka engine bindings
    ├── network/          # Global Request Client
    ├── redis/            # Singleton Database Cache Client
    └── utils/            # Raw Python helpers (Date manipulators, generic Responses)
```
