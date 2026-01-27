# 🧾 KnowYourWorth – Empowering Workers in Italy

**KnowYourWorth** is a web platform developed to support workers, especially migrants, youth, and rural laborers in identifying labor exploitation, verifying their employment conditions, and receiving personalized, actionable guidance.

Developed during a Perplexity Hackathon, the platform integrates AI-powered tools with structured legal knowledge to provide a virtual assistant-like experience, even for users with limited legal or digital literacy.

---

## 🚀 Key Features

- **📋 Contract & Salary Check**  
  Users can input their job role, contract type, and salary to automatically compare against official CCNL (National Collective Labor Agreements) standards using a Retrieval-Augmented Generation (RAG) system.

- **🧭 Decision Support Quiz**  
  A guided decision-making quiz dynamically adapts to user responses and provides context-sensitive advice on whether and how to seek help.

- **📝 Action Plan Generator**  
  For at-risk cases, the system produces a customized document outlining next steps and relevant contacts (e.g., unions, labor inspectors).

- **🧠 AI-Powered Insights**  
  User data is processed with AI-enhanced logic to improve recommendation relevance and legal accuracy while preserving privacy.

---

## 🛠️ Tech Stack

- **Frontend**:  
  Built using **Streamlit** for a fast, accessible, and mobile-friendly interface.

- **Backend**:  
  Developed with **Python 3.12.3** and **Flask**, enabling modular logic, secure user sessions, and on-demand document generation.

- **RAG Pipeline**:  
  - **LlamaIndex** for document indexing and query orchestration  
  - **OpenAI Embeddings** for vector similarity search on CCNL clauses  
  - Compatible with **Hugging Face** models for future self-hosted or multilingual support

- **Perplexity API**:  
  Used for intelligent input expansion, legal language simplification, and generating legally-aware advice through controlled prompting.


---

## 🧩 Architecture

- **Modular Design**:  
  Each feature is containerized and independently deployable for scalability and maintenance.

- **Knowledge Base**:  
  Legal texts (CCNLs) are preprocessed into a searchable index, supporting fast and transparent comparisons between user input and contract clauses.

- **AI Layers**:  
  Multi-step refinement pipeline combining user input → semantic enrichment → query generation → document retrieval → advice synthesis.

---

## ⚙️ Challenges Addressed

- Bridging the complexity of Italian labor law with a simplified user experience.
- Building a CCNL-based legal comparison engine from unstructured documents.
- Designing inclusive UX flows for users unfamiliar with legal systems or digital tools.
- Handling API rate limitations without compromising on performance or safety.

---

## 📈 Future Development

- Sector-specific expansion (agriculture, logistics, hospitality)
- Interactive **Statistics Dashboard** for aggregated, anonymized data insights
- **Wage Benchmarking Tool** to contextualize salaries across regions and roles
- Partnerships with unions and NGOs for field testing and feedback
- **Anonymous reporting** and **encrypted session storage** for long-term user support

---
## Demo
[![Guarda il video](https://img.youtube.com/vi/7feNQiUdOLs/0.jpg)](https://www.youtube.com/watch?v=7feNQiUdOLs)



**KnowYourWorth** is more than an app: it's a digital ally for workers, promoting labor transparency and justice through ethical, inclusive AI.

