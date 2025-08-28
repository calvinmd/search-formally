# On-site Coding Challenge

# **🛠 Onsite Challenge**

## **Search System at Scale**

### **1. Overview**

You will design and implement a scalable search system capable of retrieving the most relevant question(s) from a large dataset in response to a user query. The system should provide clear, relevant, and performant results while maintaining usability as the dataset size increases.

---

## **2. Objectives**

- **Primary:** Build a baseline keyword-based search solution.
    - Start with 10k question–key pairs (CSV provided).
    - Implement a keyword-based search method.
    - Display search results in a simple **Streamlit interface** (or equivalent)
- Secondary: Optimize it to handle large-scale datasets.
    - Midway through, 10x your data.
    - Update your implementation to maintain performance at scale.
- **Bonus (optional):** If time allows, extend functionality with other enhancements.

---

## **3. Core User Flow**

1. **Input**
    - User types a query into the search bar.
2. **Output**
    - Display the **top N** most relevant questions from the dataset, with matching terms or phrases highlighted.
    - **User Action:** The user can browse the results and click/select one.
    - **System Action:** When a question is selected, display or return the **key** associated with that specific question.

---

### **4. Functional Requirements:**

1. **Data:** Each dataset record contains: 
    - A **question** (string)
    - A context (string) for the question
    - A **key** (string) associated with that question
        
        [state_library.csv](attachment:e746a927-ba15-48f0-92d2-e1cc1db904f6:state_library.csv)
        
2. **UI:**
    - Search bar where user can type a question.
    - Show top-N most similar stored questions (highlight matches).
    - Show the retrieved key for the best match.
3. **Implementation Tools:**
    - **Frontend/UI:** You may use Streamlit for ease, but your choice.
    - **Backend logic:** Typescript / Python.
    - **Data storage:** Local file(s) or in-memory structures; SQLite/ElasticSearch/etc allowed, but **no managed hosted services** (e.g., Pinecone Cloud, Weaviate Cloud)
    - **Environment:** You can use Cursor or your own IDE
- Constraints
    - **Time:** ~2 hours coding, 30 min presentation
    - You should be prepared to explain **trade-offs** made in relevance ranking, performance optimization, and user experience.

---

### **5. Non-Functional Requirements**

| **Criterion** | **Target** |
| --- | --- |
| **Performance** | < 1 second average query time at full dataset scale |
| **Scalability** | Supports ≥ 1 million records without major architectural rewrite |
| **Usability** | Clear, readable results with visual highlights |
| **Maintainability** | Code structured for easy modification and extension |

---

### **6. Success Criteria**

| **Criterion** | **Target** |
| --- | --- |
| **Relevance** | Returns high-quality matches for both exact and partial queries. |
| **Performance** | < 1 second average query time at full dataset scale. |
| **Scalability** | Supports ≥ 2 million records without major architectural rewrite. |
| **Usability** | Clear, readable results with visual highlights and intuitive ranking. |
| **Maintainability** | Code is modular and documented for easy updates or enhancements. |
| **Cost** | Runs efficiently on a **local machine** with minimal compute/memory usage; avoids expensive external dependencies and paid hosted services. |

---

### **7. Deliverables**

1. **Source Code** for the search system.
2. **Instructions** to run locally (README).
3. **Short Justification** for:
    - Choice of N for top results.
    - Search algorithm(s) used.
    - Scaling and optimization strategies.
4. **Live Demo** during presentation (≈ 30 minutes).

---

### **8. Timeline**

- **Coding:** ~2.5 hours.
- **Presentation:** ~30 minutes.