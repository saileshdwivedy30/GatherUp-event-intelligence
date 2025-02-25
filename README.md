Here's a **GitHub README** for your repository:  

---

# **Event Scraper: AI-Driven Event Data Aggregation & Processing**  

**Event Scraper** is a modular system that fetches, processes, and stores event data from multiple sources (e.g., Ticketmaster, Eventbrite, Meetup).

It utilizes **NLP & ML** techniques for **event categorization, personalized recommendations, event similarity search duplicate detection & merging**.  



## 📌 **Features**
✅ **Multi-Source Event Fetching** (APIs like Ticketmaster, Eventbrite, Meetup)  
✅ **Duplicate Detection & Merging** (Fuzzy Matching, MD5 Hashing)  
✅ **MongoDB Storage** with Multi-Source Merging  

In future: 

✅ **NLP-Based Event Categorization** (TF-IDF, BERT-based classification)  
✅ **Personalized Recommendations** (Content-Based & Collaborative Filtering)  
✅ **Event Similarity Search** (TF-IDF & BERT Embeddings)  

---

## 📂 **Project Structure**  

```
📂 event_scraper/
│── 📂 fetchers/          # Event source fetchers
│   ├── base_fetcher.py   # Base class for all fetchers
│   ├── ticketmaster.py   # Ticketmaster API fetcher
│   ├── eventbrite.py     # Eventbrite API fetcher (Future)
│   ├── meetup.py         # Meetup API fetcher (Future)
│
│── 📂 database/          # Database management
│   ├── db_manager.py         # MongoDB connection & operations
│   ├── duplicate_handler.py  # Handles duplicate detection & merging
│
│── 📂 ml/               # AI & ML Components (Upcoming)
│   ├── categorization.py   # NLP-based Event Categorization
│   ├── recommender.py      # Event Recommendation System
│   ├── similarity.py       # Event Similarity Search (TF-IDF & BERT)
│
│── app.py                # Main script to run the application
│── .env                  # API keys and config settings
│── requirements.txt       # Dependencies
```

---

## 🚀 **How It Works**  

1️⃣ **Event Fetching**  
- The system **fetches events** from different sources (e.g., Ticketmaster API) via fetcher classes.  
- Each fetcher extends `BaseFetcher` and standardizes event data.  

2️⃣ **Duplicate Detection & Merging**  
- Events are **deduplicated** using a combination of **MD5 hashing (name + date + venue)** and **fuzzy matching (FuzzyWuzzy)**.  
- If a duplicate is found, the system **merges event details instead of creating duplicates**.  

3️⃣ **Storage in MongoDB**  
- Events are stored in **MongoDB** with support for **multi-source merging** (e.g., same event from different platforms is combined).  

4️⃣ **AI-Powered Processing (Upcoming)**  
- **Event Categorization:** NLP model (TF-IDF, Naïve Bayes, BERT) to classify events.  
- **Event Recommendation:** Suggests events based on user preferences (content-based & collaborative filtering).  
- **Event Similarity Search:** Finds similar events using **TF-IDF & BERT embeddings**.  

---

## 🔍 **Code Overview**  

### 📂 `fetchers/` – **Event Fetching**  
| File | Description |
|------|------------|
| `base_fetcher.py` | Defines the abstract class `BaseFetcher` for all event fetchers. Generates unique IDs based on name, date, and venue. |
| `ticketmaster.py` | Implements `TicketmasterFetcher` to fetch events from the **Ticketmaster API** and process them before inserting into the database. |
| `eventbrite.py` | (Upcoming) Fetches events from the **Eventbrite API**. |
| `meetup.py` | (Upcoming) Fetches events from the **Meetup API**. |

---

### 📂 `database/` – **Database Management**  
| File | Description |
|------|------------|
| `db_manager.py` | Handles **MongoDB connection**, **inserts events**, and **merges duplicates** efficiently. |
| `duplicate_handler.py` | Detects duplicate events using **MD5 hashes & fuzzy matching** before passing them to `db_manager.py` for merging. |

---

### 📂 `ml/` – **AI & Machine Learning Components (Upcoming)**  
| File | Description |
|------|------------|
| `categorization.py` | Classifies events using **TF-IDF, Naïve Bayes, or BERT** based on event name & description. |
| `recommender.py` | Implements **content-based & collaborative filtering** for personalized event recommendations. |
| `similarity.py` | Finds **similar events** using **TF-IDF + Cosine Similarity** and **BERT embeddings**. |

---

### `app.py` – **Main Script**  
- This is the **entry point** to the application.  
- Fetches events using the selected fetcher (e.g., `TicketmasterFetcher`).  
- Handles **duplicate detection & merging** before inserting into MongoDB.  
- Runs **event processing (categorization, recommendations, similarity search)**.  

---

## 🛠 **To-Do List (Upcoming Features)**
- [x] **Event Fetching (Ticketmaster)**
- [x] **Duplicate Detection & Merging**
- [ ] **Event Fetching bugs and changes (Ticketmaster)**
- [ ] **Airflow automation (Ticketmaster)**
- [ ] **Add Eventbrite & Meetup Fetchers**
- [ ] **CI/CD**
- [ ] **Cloud Deployment**
- [ ] **Event Categorization (TF-IDF, BERT)**
- [ ] **Event Recommendation System**
- [ ] **Event Similarity Search**


