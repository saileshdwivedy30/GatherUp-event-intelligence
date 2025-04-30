# **Event Scraper: AI-Driven Event Data Aggregation & Processing**  

**Event Scraper** is a modular system that fetches, processes, and stores event data from multiple sources (Ticketmaster and Eventbrite).

It utilizes **NLP & ML** techniques for **personalized recommendations, event similarity search duplicate detection & merging**.  



## 📌 **Features**
✅ **Multi-Source Event Fetching** (APIs like Ticketmaster, Eventbrite)  
✅ **Duplicate Detection & Merging** (Embedding Matching, Hashing)  
✅ **MongoDB Storage** with Multi-Source Merging  
✅ **Personalized Recommendations** (Content-Based)  

---

## 🚀 **How It Works**  

1️⃣ **Event Fetching**  
- The system **fetches events** from different sources (e.g., Ticketmaster API, Eventbrite) via fetcher classes.  
- Each fetcher extends `BaseFetcher` and standardizes event data.  

2️⃣ **Duplicate Detection & Merging**  
- Events are **deduplicated** using a combination of **MD5 hashing (name + date + venue)** and **embedding based matching**.  
- If a duplicate is found, the system **merges event details instead of creating duplicates**.  

3️⃣ **Storage in MongoDB**  
- Events are stored in **MongoDB** with support for **multi-source merging** (e.g., same event from different platforms is combined).  

4️⃣ **AI-Powered Processing**   
- **Event Recommendation:** Suggests events based on user preferences (content-based & collaborative filtering).  
- **Deduplication:** Finds similar events but duplicate events using **Sentence Transformer**.  

---

## 🔍 **Code Overview**  

### 📂 `fetchers/` – **Event Fetching**  
| File | Description |
|------|------------|
| `base_fetcher.py` | Defines the abstract class `BaseFetcher` for all event fetchers. Generates unique IDs based on name, date, and venue. |
| `ticketmaster.py` | Implements `TicketmasterFetcher` to fetch events from the **Ticketmaster API** and process them before inserting into the database. |
| `eventbrite.py` | Fetches events from the **Eventbrite** via web scraping (Beautiful Soup) |
| `meetup.py` | (Upcoming) Fetches events from the **Meetup API**. |

---

### 📂 `database/` – **Database Management**  
| File | Description |
|------|------------|
| `db_manager.py` | Handles **MongoDB connection**, **inserts events**, and **merges duplicates** efficiently. |
| `duplicate_handler.py` | Detects duplicate events using **MD5 hashes & sentence transformer embeddings** before passing them to `db_manager.py` for merging. |

---

### 📂 `ml/` – **AI & Machine Learning Components**  
| File | Description |
|------|------------|
| `recommender.py` | Implements **content-based & collaborative filtering** for personalized event recommendations. |
---

### 📂 `dags/` – **Airflow DAG Components**  
| File | Description |
|------|------------|
| `event_fetcher_dag.py` | DAG for Scraping from Eventbrite to run at 12 AM UTC |
| `ticketmaster_fetcher_dag.py` | DAG for Scraping from Eventbrite to run at 2 AM UTC |

---

### `app.py` – **Main Script**  
- This is the **entry point** to the application.  
- Fetches events using the selected fetcher (e.g., `TicketmasterFetcher`).  
- Handles **duplicate detection & merging** before inserting into MongoDB.  

---


