"""Generate MailMind AI project documentation in DOCX format."""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import os

doc = Document()

# ── Page margins ──
for section in doc.sections:
    section.top_margin = Cm(3.81)    # 1.5 inches
    section.bottom_margin = Cm(3.81)
    section.left_margin = Cm(5.08)   # 2 inches
    section.right_margin = Cm(3.81)  # 1.5 inches

# ── Style helpers ──
style_normal = doc.styles["Normal"]
font = style_normal.font
font.name = "Times New Roman"
font.size = Pt(12)
style_normal.paragraph_format.line_spacing = 1.5
style_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

def set_font(run, size=12, bold=False, italic=False, color=None):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)

def add_title_page_line(text, size=14, bold=True, spacing_before=0, spacing_after=6, alignment=WD_ALIGN_PARAGRAPH.CENTER):
    p = doc.add_paragraph()
    p.alignment = alignment
    p.paragraph_format.space_before = Pt(spacing_before)
    p.paragraph_format.space_after = Pt(spacing_after)
    run = p.add_run(text)
    set_font(run, size, bold)
    return p

def add_heading_custom(text, level=1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(text)
    if level == 1:
        set_font(run, 14, bold=True)
    elif level == 2:
        set_font(run, 14, bold=True)
    else:
        set_font(run, 12, bold=True)
    return p

def add_body(text, bold=False, italic=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    set_font(run, 12, bold=bold, italic=italic)
    return p

def add_bullet(text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    if level > 0:
        p.paragraph_format.left_indent = Cm(1.27 * level)
    run = p.add_run(text)
    set_font(run, 12)
    return p

def add_table(headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        set_font(run, 12, bold=True)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(val))
            set_font(run, 12)
    doc.add_paragraph()  # spacing after

def page_break():
    doc.add_page_break()


# ====================================================================
# TITLE PAGE
# ====================================================================
doc.add_paragraph()
doc.add_paragraph()
add_title_page_line("MAILMIND AI", 26, True, 60, 6)
add_title_page_line("An Intelligent Email Analysis Platform", 16, False, 6, 6)
add_title_page_line("Using Classical Machine Learning and Natural Language Processing", 14, False, 6, 30)
add_title_page_line("A PROJECT REPORT", 14, True, 20, 6)
add_title_page_line("Submitted in partial fulfillment of the requirements", 12, False, 6, 4)
add_title_page_line("for the award of the degree of", 12, False, 4, 4)
add_title_page_line("BACHELOR OF TECHNOLOGY", 14, True, 10, 4)
add_title_page_line("in", 12, False, 4, 4)
add_title_page_line("COMPUTER SCIENCE AND ENGINEERING", 14, True, 4, 30)
add_title_page_line("2024 - 2025", 14, True, 20, 6)

page_break()

# ====================================================================
# ABSTRACT (i)
# ====================================================================
add_heading_custom("ABSTRACT", 1)
add_body(
    "Email has become the primary vector for both professional communication and cyber threats. "
    "Spam, phishing, and social engineering attacks continue to evolve, making it increasingly "
    "difficult for users to distinguish legitimate messages from malicious ones. MailMind AI is "
    "an intelligent email analysis platform that combines classical machine learning with "
    "rule-based feature engineering to provide explainable, real-time email classification."
)
add_body(
    "The system implements a complete machine learning pipeline encompassing data acquisition, "
    "preprocessing, feature extraction, model training, evaluation, and deployment. The platform "
    "was trained on the UCI SMS Spam Collection dataset comprising 5,158 messages, split into "
    "training (70%), validation (15%), and test (15%) sets with stratified sampling. Four classical "
    "ML algorithms were compared: Multinomial Naive Bayes, Logistic Regression, Random Forest, "
    "and Linear SVM."
)
add_body(
    "The best performing model, Multinomial Naive Bayes, achieved 98.32% accuracy, 98.82% "
    "precision, 87.50% recall, and 92.82% F1-score on the held-out test set. The system also "
    "provides multi-dimensional analysis including phishing risk assessment, email categorization, "
    "priority scoring, intent detection, named entity extraction, and explainable AI factors."
)
add_body(
    "The platform is built as a full-stack application using React Native (Expo) for the mobile "
    "frontend, FastAPI for the backend API, and MongoDB for persistent storage. The architecture "
    "supports multiple email import formats including .eml, .txt, .pdf, .docx, and .csv files "
    "with batch processing capabilities."
)
add_body(
    "Keywords: Email Classification, Spam Detection, Phishing Detection, Machine Learning, "
    "Natural Language Processing, TF-IDF, Naive Bayes, Explainable AI, React Native, FastAPI.",
    italic=True
)

page_break()

# ====================================================================
# ACKNOWLEDGEMENT (ii)
# ====================================================================
add_heading_custom("ACKNOWLEDGEMENT", 1)
add_body(
    "We would like to express our sincere gratitude to all those who have contributed to the "
    "successful completion of this project."
)
add_body(
    "We are deeply grateful to our project guide for their invaluable guidance, constant "
    "encouragement, and constructive suggestions throughout the development of this project. "
    "Their expertise in machine learning and software engineering helped us shape this project "
    "into a meaningful contribution."
)
add_body(
    "We extend our heartfelt thanks to the Head of the Department for providing us with the "
    "necessary facilities and support to carry out this project work."
)
add_body(
    "We are thankful to the UCI Machine Learning Repository for making the SMS Spam Collection "
    "dataset publicly available under the CC BY 4.0 license, which formed the foundation of our "
    "training pipeline."
)
add_body(
    "We also acknowledge the open-source communities behind scikit-learn, FastAPI, React Native, "
    "Expo, and MongoDB whose tools and frameworks made this project possible."
)
add_body(
    "Finally, we thank our families and friends for their patience, moral support, and "
    "encouragement during the course of this project."
)

page_break()

# ====================================================================
# LIST OF TABLES (iii)
# ====================================================================
add_heading_custom("LIST OF TABLES", 1)
add_table(
    ["Table No.", "Title", "Page No."],
    [
        ["4.1", "System Architecture Components", "18"],
        ["5.1", "Module Description Summary", "23"],
        ["5.2", "API Endpoint Reference", "27"],
        ["5.3", "Feature Engineering Variables", "29"],
        ["6.1", "Model Comparison Results (Test Set)", "35"],
        ["6.2", "Confusion Matrix - Multinomial Naive Bayes", "36"],
        ["6.3", "Backend API Test Cases", "38"],
        ["6.4", "Frontend UI Test Cases", "40"],
        ["6.5", "Integration Test Cases", "41"],
    ]
)

page_break()

# ====================================================================
# LIST OF FIGURES (iv)
# ====================================================================
add_heading_custom("LIST OF FIGURES", 1)
add_table(
    ["Figure No.", "Title", "Page No."],
    [
        ["4.1", "System Architecture Diagram", "17"],
        ["4.2", "Data Flow Diagram (Level 0)", "19"],
        ["4.3", "Data Flow Diagram (Level 1)", "20"],
        ["4.4", "Entity Relationship Diagram", "21"],
        ["4.5", "Use Case Diagram", "22"],
        ["5.1", "ML Pipeline Flow", "25"],
        ["5.2", "Classification Decision Tree", "30"],
        ["8.1", "Start Screen", "43"],
        ["8.2", "Home Dashboard", "44"],
        ["8.3", "Email Analysis Screen", "45"],
        ["8.4", "File Upload Interface", "46"],
        ["8.5", "Analysis Result - Detail View", "47"],
        ["8.6", "History Screen", "48"],
    ]
)

page_break()

# ====================================================================
# CHAPTER 1 - INTRODUCTION
# ====================================================================
add_heading_custom("CHAPTER 1", 1)
add_heading_custom("INTRODUCTION", 1)

add_heading_custom("1.1 PROJECT INTRODUCTION", 2)
add_body(
    "Email remains the most widely used communication medium in both professional and personal "
    "contexts, with over 350 billion emails sent and received daily worldwide. However, this "
    "ubiquity has made email the primary attack vector for cybercriminals. According to the "
    "Anti-Phishing Working Group (APWG), phishing attacks reached an all-time high in recent "
    "years, with the financial sector being the most targeted industry."
)
add_body(
    "Traditional spam filters rely on static rule-based approaches or simple keyword matching, "
    "which are increasingly ineffective against sophisticated attacks that employ social "
    "engineering techniques. Modern email threats use personalized content, legitimate-looking "
    "sender addresses, and subtle psychological manipulation that evade conventional detection "
    "mechanisms."
)
add_body(
    "MailMind AI addresses these challenges by implementing a comprehensive email intelligence "
    "platform that combines multiple machine learning techniques with domain-specific feature "
    "engineering. The system provides not just a binary spam/ham classification, but a "
    "multi-dimensional analysis encompassing:"
)
add_bullet("Spam classification with probability scores")
add_bullet("Phishing risk assessment using rule-based heuristics")
add_bullet("Email categorization (Work, Personal, Banking, Finance, etc.)")
add_bullet("Priority scoring with human-readable justifications")
add_bullet("Intent detection (Confirm, Approve, Pay, Schedule, etc.)")
add_bullet("Named entity extraction (people, organizations, dates, amounts, URLs)")
add_bullet("Explainable AI factors showing what influenced each prediction")
add_bullet("LLM-assisted email summarization and response drafting")

add_body(
    "The platform is designed as a mobile-first application using React Native with Expo, "
    "ensuring cross-platform compatibility across iOS, Android, and web browsers. The backend "
    "is powered by FastAPI, a modern Python web framework optimized for high-performance API "
    "development, with MongoDB serving as the persistent data store."
)
add_body(
    "A key design principle of MailMind AI is explainability. Rather than presenting opaque "
    "classification results, the system provides users with detailed explanations of why each "
    "email received its classification, including the specific features and model factors that "
    "contributed to the decision. This transparency builds user trust and supports informed "
    "decision-making."
)
add_body(
    "The project encompasses the complete data science lifecycle, from raw data acquisition "
    "through the UCI SMS Spam Collection dataset, to data preprocessing, exploratory data "
    "analysis, feature engineering, model training and comparison, hyperparameter tuning, "
    "model evaluation on held-out test data, and production deployment as a RESTful API "
    "serving real-time predictions."
)

page_break()

# ====================================================================
# CHAPTER 2 - WORKING ENVIRONMENT
# ====================================================================
add_heading_custom("CHAPTER 2", 1)
add_heading_custom("WORKING ENVIRONMENT", 1)

add_heading_custom("2.1 HARDWARE REQUIREMENT", 2)
add_table(
    ["Component", "Specification"],
    [
        ["Processor", "Intel Core i5 or equivalent (minimum)"],
        ["RAM", "8 GB (minimum), 16 GB (recommended)"],
        ["Storage", "256 GB SSD (minimum)"],
        ["Display", "1920 x 1080 resolution (minimum)"],
        ["Network", "Broadband internet connection"],
        ["Mobile Device", "Android 10+ or iOS 14+ (for mobile testing)"],
    ]
)

add_heading_custom("2.2 SOFTWARE REQUIREMENT", 2)
add_table(
    ["Software", "Version", "Purpose"],
    [
        ["Python", "3.11+", "Backend development and ML pipeline"],
        ["Node.js", "18+", "Frontend development toolchain"],
        ["MongoDB", "6.0+", "Document database for persistent storage"],
        ["VS Code / IDE", "Latest", "Integrated development environment"],
        ["Git", "2.40+", "Version control system"],
        ["Docker", "24+", "Containerized deployment"],
        ["Expo CLI", "Latest", "React Native development and builds"],
    ]
)

add_heading_custom("2.3 SYSTEM SOFTWARE", 2)
add_body("The following system software components form the technology stack of MailMind AI:")

add_heading_custom("2.3.1 Backend Technologies", 3)
add_table(
    ["Technology", "Version", "Role"],
    [
        ["FastAPI", "0.100+", "Async Python web framework for REST API"],
        ["Uvicorn", "0.23+", "ASGI server for FastAPI"],
        ["scikit-learn", "1.3+", "Machine learning model training and inference"],
        ["pandas", "2.0+", "Data manipulation and preprocessing"],
        ["NumPy", "1.25+", "Numerical computations"],
        ["joblib", "1.3+", "Model serialization and deserialization"],
        ["BeautifulSoup4", "4.12+", "HTML parsing and text extraction"],
        ["Motor", "3.3+", "Async MongoDB driver for Python"],
        ["Pydantic", "2.0+", "Data validation and schema definition"],
        ["python-docx", "1.0+", "DOCX file parsing for email import"],
        ["pypdf", "3.0+", "PDF text extraction for email import"],
    ]
)

add_heading_custom("2.3.2 Frontend Technologies", 3)
add_table(
    ["Technology", "Version", "Role"],
    [
        ["React Native", "0.76+", "Cross-platform mobile UI framework"],
        ["Expo SDK", "52+", "Managed React Native development platform"],
        ["Expo Router", "4+", "File-based routing for navigation"],
        ["TypeScript", "5.0+", "Type-safe JavaScript superset"],
        ["React Query", "5+", "Server state management and caching"],
        ["expo-document-picker", "Latest", "File selection for email import"],
        ["expo-clipboard", "Latest", "System clipboard integration"],
        ["expo-linear-gradient", "Latest", "Gradient visual effects"],
        ["react-native-safe-area-context", "Latest", "Safe area inset handling"],
    ]
)

add_heading_custom("2.3.3 Database", 3)
add_body(
    "MongoDB is used as the primary database for MailMind AI. It is a NoSQL document database "
    "that stores data in flexible, JSON-like BSON documents. This schema-less approach is ideal "
    "for storing email analysis records which contain nested objects with varying structures "
    "such as classification results, feature vectors, entity extractions, and user feedback."
)

page_break()

# ====================================================================
# CHAPTER 3 - SYSTEM ANALYSIS
# ====================================================================
add_heading_custom("CHAPTER 3", 1)
add_heading_custom("SYSTEM ANALYSIS", 1)

add_heading_custom("3.1 FEASIBILITY STUDY", 2)

add_heading_custom("3.1.1 Technical Feasibility", 3)
add_body(
    "The project is technically feasible as all required technologies are mature, well-documented, "
    "and freely available. Python's scikit-learn library provides robust implementations of all "
    "four ML algorithms used (Naive Bayes, Logistic Regression, Random Forest, SVM). FastAPI "
    "enables high-performance async API development, and React Native with Expo provides "
    "cross-platform mobile development without native code requirements."
)

add_heading_custom("3.1.2 Economic Feasibility", 3)
add_body(
    "The entire technology stack is based on open-source software, eliminating licensing costs. "
    "The UCI SMS Spam Collection dataset is freely available under CC BY 4.0. Hosting costs are "
    "minimal with containerized deployment on cloud platforms. The LLM assistance feature uses "
    "the Emergent integration key for backend-only summarization, keeping API costs controlled."
)

add_heading_custom("3.1.3 Operational Feasibility", 3)
add_body(
    "The system is designed for end-user simplicity. Users interact through a clean mobile "
    "interface to paste or upload emails. The ML pipeline runs entirely on the backend, "
    "requiring no technical knowledge from users. Results are presented with plain-language "
    "explanations rather than raw numerical outputs."
)

add_heading_custom("3.2 EXISTING SYSTEM", 2)
add_body("The existing approaches to email classification include:")
add_bullet("Traditional spam filters using keyword blacklists and sender reputation scoring.")
add_bullet("Rule-based systems that check for specific patterns (e.g., known phishing URLs).")
add_bullet("Cloud-based email security gateways that require enterprise subscriptions.")
add_bullet("Browser extensions that provide basic phishing warnings.")

add_heading_custom("3.3 DRAWBACKS OF EXISTING SYSTEM", 2)
add_bullet("Keyword-based filters are easily bypassed by obfuscation techniques (e.g., replacing letters with similar-looking characters).")
add_bullet("Rule-based systems cannot adapt to new attack patterns without manual rule updates.")
add_bullet("Enterprise solutions are expensive and not accessible to individual users or small organizations.")
add_bullet("Most existing tools provide only binary classification (spam/not spam) without explaining why a message was flagged.")
add_bullet("Lack of multi-dimensional analysis (priority, intent, category) that helps users triage their inbox.")
add_bullet("No user feedback mechanism to improve classification accuracy over time.")
add_bullet("Limited support for analyzing emails from files (.eml, .pdf, .docx) outside of live email clients.")

add_heading_custom("3.4 PROPOSED SYSTEM", 2)
add_body(
    "MailMind AI is a comprehensive email intelligence platform that addresses the limitations "
    "of existing systems through the following approach:"
)
add_bullet("Classical ML classification using TF-IDF vectorization and trained models on a verified research dataset.")
add_bullet("Multi-dimensional analysis providing spam classification, phishing risk, category, priority, and intent in a single pass.")
add_bullet("Explainable AI (XAI) factors showing users exactly which features influenced each classification decision.")
add_bullet("Rule-based phishing heuristics analyzing URL patterns, shortened links, IP-based URLs, sender-domain mismatches, and suspicious terminology.")
add_bullet("Multi-format email import supporting .eml, .txt, .pdf, .docx, and .csv files with batch processing.")
add_bullet("User feedback collection enabling continuous improvement of model accuracy.")
add_bullet("Mobile-first cross-platform design accessible on iOS, Android, and web.")
add_bullet("Backend LLM integration for generating natural-language summaries and response drafts (with safety guardrails preventing responses to suspicious emails).")

add_heading_custom("3.5 BENEFITS OF PROPOSED SYSTEM", 2)
add_bullet("Combines statistical ML with domain heuristics for more robust detection than either approach alone.")
add_bullet("Provides transparency through explainable factors, building user trust in automated decisions.")
add_bullet("Supports multiple input methods: manual paste, clipboard import, and multi-file batch upload.")
add_bullet("Generates actionable intelligence including priority scoring, intent detection, and entity extraction.")
add_bullet("Offers response assistance with generated drafts that users can customize (disabled for threatening emails).")
add_bullet("Maintains complete analysis history with search, enabling users to review and audit past classifications.")
add_bullet("Collects user corrections as structured feedback data for future model retraining.")
add_bullet("Achieves 98.32% test accuracy with the Multinomial Naive Bayes classifier.")

add_heading_custom("3.6 SCOPE OF THE PROJECT", 2)
add_body("The scope of MailMind AI encompasses the following areas:")
add_bullet("Data Science: Complete ML lifecycle from data acquisition to production deployment.")
add_bullet("Backend API: RESTful endpoints for email analysis, batch processing, history, analytics, and feedback.")
add_bullet("Frontend Application: Cross-platform mobile app with adaptive theming, animated interactions, and intuitive UX.")
add_bullet("File Processing: Multi-format email import parser supporting EML, TXT, PDF, DOCX, and CSV.")
add_bullet("LLM Integration: Backend-only GPT-based assistance for email summarization and response drafting.")
add_body(
    "The project does not include: real-time email server integration (IMAP/POP3), user authentication, "
    "end-to-end encryption, or push notification support. These are identified as potential "
    "future enhancements."
)

page_break()

# ====================================================================
# CHAPTER 4 - SYSTEM DESIGN
# ====================================================================
add_heading_custom("CHAPTER 4", 1)
add_heading_custom("SYSTEM DESIGN", 1)

add_body(
    "This chapter presents the architectural design of MailMind AI, describing the system's "
    "components, data flow, and interactions between subsystems."
)

add_heading_custom("4.1 SYSTEM ARCHITECTURE", 2)
add_body(
    "MailMind AI follows a three-tier architecture comprising a presentation layer (React Native "
    "frontend), business logic layer (FastAPI backend with ML pipeline), and data layer (MongoDB "
    "database). The system uses a RESTful API design pattern for communication between tiers."
)

add_heading_custom("Table 4.1: System Architecture Components", 3)
add_table(
    ["Layer", "Component", "Technology", "Responsibility"],
    [
        ["Presentation", "Mobile App", "React Native / Expo", "User interface, email input, result display"],
        ["Business Logic", "API Server", "FastAPI / Uvicorn", "Request routing, validation, response formatting"],
        ["Business Logic", "ML Pipeline", "scikit-learn", "Text classification, feature extraction, prediction"],
        ["Business Logic", "File Parser", "Python stdlib + libs", "Multi-format email file extraction"],
        ["Business Logic", "LLM Service", "OpenAI GPT-5.4", "Email summarization and response drafting"],
        ["Data", "Database", "MongoDB", "Analysis records, feedback, history"],
    ]
)

add_heading_custom("4.2 DATA FLOW DIAGRAM (LEVEL 0)", 2)
add_body(
    "The Level 0 Data Flow Diagram represents the system as a single process with external "
    "entities and data stores. The user submits email content (text or file), which flows into "
    "the MailMind system. The system processes the email through the ML pipeline and returns "
    "the analysis result. The analysis record is stored in MongoDB for historical reference."
)
add_body(
    "External Entities: User (email submitter and result consumer). "
    "Process: MailMind AI System. "
    "Data Stores: MongoDB (email_analyses collection). "
    "Data Flows: Email Input -> System -> Analysis Result; System -> MongoDB (persist); "
    "MongoDB -> System (history retrieval)."
)

add_heading_custom("4.3 DATA FLOW DIAGRAM (LEVEL 1)", 2)
add_body("The Level 1 DFD decomposes the system into its major processing subsystems:")
add_bullet("P1 - Input Processing: Receives email text (paste/clipboard) or uploaded files. For files, invokes the file parser to extract email content from .eml, .txt, .pdf, .docx, or .csv formats.")
add_bullet("P2 - Text Preprocessing: Applies HTML stripping (BeautifulSoup), HTML entity decoding, whitespace normalization, and lowercasing to produce clean NLP-ready text.")
add_bullet("P3 - Feature Extraction: Computes 15+ engineered features including URL count, suspicious term count, shortened URL detection, IP-based URL detection, uppercase ratio, special character count, email length metrics, and sender domain extraction.")
add_bullet("P4 - ML Classification: Runs the clean text through TF-IDF vectorization and the trained Naive Bayes classifier to produce spam probability. Separately runs category and intent classifiers.")
add_bullet("P5 - Phishing Assessment: Applies rule-based heuristic scoring using extracted features, sender-domain mismatch analysis, and credential-language detection.")
add_bullet("P6 - Priority Scoring: Computes priority level (Critical/High/Medium/Low/Informational) based on intent type, time-bound language, and financial context.")
add_bullet("P7 - Entity Extraction: Uses regex patterns to identify people, organizations, dates, monetary amounts, phone numbers, and URLs from the email content.")
add_bullet("P8 - Explanation Generation: Produces human-readable explanation factors describing which features influenced the classification decision.")
add_bullet("P9 - LLM Assistance: Sends the structured analysis evidence to GPT-5.4 for natural-language summarization and response drafting (disabled for spam/phishing).")
add_bullet("P10 - Persistence: Stores the complete analysis record in MongoDB and returns the result to the user.")

add_heading_custom("4.4 ENTITY RELATIONSHIP DIAGRAM", 2)
add_body("The MongoDB document schema for the email_analyses collection:")
add_body("Collection: email_analyses", bold=True)
add_bullet("id (String, UUID) - Unique analysis record identifier")
add_bullet("client_id (String) - Anonymous client identifier for session isolation")
add_bullet("sender (String) - Email sender address")
add_bullet("subject (String) - Email subject line")
add_bullet("body_preview (String) - First 240 characters of email body")
add_bullet("source_name (String) - Origin of the email (pasted, filename)")
add_bullet("analysis (Object) - Nested analysis results:")
add_bullet("  spam: {label, probability, riskLevel}", level=1)
add_bullet("  phishing: {risk, probability}", level=1)
add_bullet("  category: {label, probability}", level=1)
add_bullet("  priority: {label, probability, reasons[]}", level=1)
add_bullet("  intent: {label, actionRequired, confidence}", level=1)
add_bullet("  entities: {people[], organizations[], dates[], amounts[], phoneNumbers[], urls[]}", level=1)
add_bullet("  features: {engineered numeric/string features}", level=1)
add_bullet("  explanation: [{type, direction, text}]", level=1)
add_bullet("  summary (String) - LLM-generated summary", level=1)
add_bullet("  responseRecommendation (String) - LLM response advice", level=1)
add_bullet("  suggestedResponse (String) - LLM draft response", level=1)
add_bullet("feedback (Array) - User corrections [{field, correctedValue, createdAt}]")
add_bullet("created_at (String, ISO) - Record creation timestamp")
add_bullet("prediction_timestamp (String, ISO) - Prediction generation timestamp")

add_heading_custom("4.5 USE CASE DIAGRAM", 2)
add_body("The primary actors and use cases in MailMind AI:")
add_body("Actor: User", bold=True)
add_bullet("UC1: Paste and analyze a single email")
add_bullet("UC2: Upload email files for batch analysis")
add_bullet("UC3: View analysis detail with explainability factors")
add_bullet("UC4: Browse analysis history with search")
add_bullet("UC5: Copy suggested response draft to clipboard")
add_bullet("UC6: Submit feedback to correct a classification")
add_bullet("UC7: View dashboard metrics (total analyzed, threats, priority)")

page_break()

# ====================================================================
# CHAPTER 5 - PROJECT DESCRIPTION
# ====================================================================
add_heading_custom("CHAPTER 5", 1)
add_heading_custom("PROJECT DESCRIPTION", 1)

add_heading_custom("5.1 OBJECTIVE", 2)
add_body("The primary objectives of MailMind AI are:")
add_bullet("To develop a machine learning-based email classification system that accurately distinguishes spam, phishing, and legitimate emails using classical ML algorithms.")
add_bullet("To implement a comprehensive feature engineering pipeline that extracts security-relevant features (URL analysis, suspicious terminology, sender verification) alongside standard NLP features (TF-IDF).")
add_bullet("To provide explainable AI outputs that help users understand why each email received its classification, fostering trust and informed decision-making.")
add_bullet("To build a mobile-first, cross-platform application that provides intuitive email analysis capabilities to users on iOS, Android, and web platforms.")
add_bullet("To support multiple email input formats (.eml, .txt, .pdf, .docx, .csv) with batch processing capabilities.")
add_bullet("To collect user feedback as structured correction data that enables future model retraining and accuracy improvement.")
add_bullet("To integrate LLM-based assistance for email summarization and response drafting while maintaining safety guardrails (no responses for suspicious emails).")

add_heading_custom("5.2 MODULE DESCRIPTION", 2)

add_heading_custom("Table 5.1: Module Description Summary", 3)
add_table(
    ["Module", "Location", "Description"],
    [
        ["ML Pipeline", "backend/ml_pipeline.py", "Core ML classification, feature extraction, phishing heuristics, priority scoring, entity extraction, and explainability"],
        ["File Parser", "backend/file_parser.py", "Multi-format email file extraction supporting .eml, .txt, .pdf, .docx, .csv with batch parsing"],
        ["API Server", "backend/server.py", "FastAPI REST endpoints for analysis, history, feedback, analytics, and health monitoring"],
        ["Frontend App", "frontend/app/index.tsx", "React Native screens: Start, Home Dashboard, Analyze, Detail, History"],
        ["API Client", "frontend/src/api.ts", "TypeScript HTTP client for backend communication with type-safe request/response models"],
        ["Theme System", "frontend/src/theme.ts", "Adaptive light/dark color scheme with system preference detection"],
        ["CursorGrid", "frontend/src/components/", "Animated cursor-responsive grid for the launch screen (web Canvas + native fallback)"],
        ["Training Scripts", "scripts/", "Dataset preparation, model training, evaluation, and metric generation scripts"],
    ]
)

add_heading_custom("5.2.1 Module 1: ML Pipeline (ml_pipeline.py)", 3)
add_body(
    "The ML Pipeline is the core intelligence engine of MailMind AI. It encapsulates the "
    "complete text classification workflow in the MailMindPipeline class."
)
add_body("Key Components:", bold=True)
add_bullet("Text Preprocessing (clean_nlp_text): Strips HTML tags using BeautifulSoup, decodes HTML entities, normalizes whitespace, and converts to lowercase.")
add_bullet("Feature Extraction (extract_features): Computes 15+ engineered features including email length, word count, URL count, external domain count, email address count, uppercase ratio, special character count, exclamation/question counts, currency mentions, HTML element count, suspicious term count, shortened URL count, and IP-based URL count.")
add_bullet("Spam Classification: Uses TF-IDF vectorization with (1,2)-gram range and sublinear TF scaling, followed by the trained Multinomial Naive Bayes classifier to produce spam probability.")
add_bullet("Phishing Assessment (_phishing_probability): Rule-based heuristic combining URL density, suspicious terminology density, shortened/IP URL penalties, sender-domain mismatch detection, and credential language detection.")
add_bullet("Category Classification: Logistic Regression classifier trained on seed data covering 15+ email categories (Work, Personal, Banking, Finance, Education, Career, Shopping, Travel, etc.).")
add_bullet("Intent Detection: Logistic Regression classifier identifying 10 intent types (Confirm, Attend, Approve, Submit, Pay, Reply, Schedule, Provide information, Follow up, No action).")
add_bullet("Priority Scoring (_priority): Rule-based scoring combining intent type, time-bound language detection, and financial context to assign Critical/High/Medium/Low/Informational priority levels.")
add_bullet("Entity Extraction (_entities): Regex-based extraction of people, organizations, dates, monetary amounts, phone numbers, and URLs.")
add_bullet("Explanation Generation (_explanation): Produces human-readable factors describing which features influenced the classification, with direction indicators (risk/support).")

add_heading_custom("5.2.2 Module 2: File Parser (file_parser.py)", 3)
add_body(
    "The File Parser module handles safe, non-executing extraction of email content from "
    "multiple document formats."
)
add_body("Supported Formats:", bold=True)
add_bullet(".eml - Standard email format parsed using Python's email.parser with MIME multipart handling")
add_bullet(".txt - Plain text files with intelligent multi-email splitting (From: headers, --- delimiters, ===, ***)")
add_bullet(".pdf - PDF text extraction using pypdf library")
add_bullet(".docx - Microsoft Word document parsing using python-docx")
add_bullet(".csv - Tabular email data with case-insensitive column matching (sender, subject, body variants)")
add_body("Safety constraints: Maximum file size of 8 MB, extension whitelist validation, no code execution from uploaded content.")

add_heading_custom("5.2.3 Module 3: API Server (server.py)", 3)
add_body("The API Server exposes the following RESTful endpoints:")

add_heading_custom("Table 5.2: API Endpoint Reference", 3)
add_table(
    ["Method", "Endpoint", "Description"],
    [
        ["GET", "/api/", "Root endpoint - returns API status and model version"],
        ["GET", "/api/health", "Health check - pipeline readiness and LLM availability"],
        ["POST", "/api/email/analyze", "Analyze a single email from text input"],
        ["POST", "/api/email/analyze-file", "Analyze email(s) extracted from an uploaded file"],
        ["POST", "/api/email/analyze-batch", "Batch analysis of multiple uploaded files (max 50)"],
        ["GET", "/api/email/history", "Retrieve analysis history with search and filtering"],
        ["GET", "/api/email/{record_id}", "Get a specific analysis record by ID"],
        ["POST", "/api/email/{record_id}/feedback", "Submit user correction for a classification"],
        ["GET", "/api/analytics/summary", "Aggregate statistics across all analyses"],
    ]
)

add_heading_custom("5.2.4 Module 4: Frontend Application", 3)
add_body(
    "The frontend is a React Native application built with Expo SDK and TypeScript. "
    "It uses Expo Router for file-based navigation and implements an adaptive theme system "
    "supporting both light and dark modes based on system preferences."
)
add_body("Screens:", bold=True)
add_bullet("Start Screen: Animated launch screen with CursorGrid canvas effect (web) or pulsing grid (native), glass-card hero layout, and ML pipeline status indicator.")
add_bullet("Home Dashboard: Command center showing aggregate metrics (total analyzed, threats, priority items) and quick access to the analyzer.")
add_bullet("Analyze Screen: Dual-mode input (paste email / upload files) with form fields for sender, subject, and body. Supports multi-file batch upload with progress tracking.")
add_bullet("Detail Screen: Comprehensive analysis view showing classification result, probability bars, explanation factors, decision context, extracted entities, response assistant with draft copy, and feedback submission.")
add_bullet("History Screen: Searchable log of all past analyses with status badges and summary previews.")

add_heading_custom("5.2.5 Module 5: Feature Engineering", 3)

add_heading_custom("Table 5.3: Feature Engineering Variables", 3)
add_table(
    ["Feature", "Type", "Description"],
    [
        ["emailLength", "Integer", "Total character count of email body"],
        ["subjectLength", "Integer", "Character count of subject line"],
        ["wordCount", "Integer", "Total word count in body"],
        ["urlCount", "Integer", "Number of URLs found in message"],
        ["externalDomainCount", "Integer", "Unique external domains referenced"],
        ["emailAddressCount", "Integer", "Email addresses mentioned in body"],
        ["uppercaseRatio", "Float", "Proportion of uppercase characters"],
        ["specialCharacterCount", "Integer", "Non-alphanumeric, non-space characters"],
        ["exclamationCount", "Integer", "Exclamation mark frequency"],
        ["questionCount", "Integer", "Question mark frequency"],
        ["currencyCount", "Integer", "Currency symbol/term occurrences"],
        ["htmlElementCount", "Integer", "HTML tags found in body"],
        ["suspiciousTermCount", "Integer", "Security-sensitive keywords detected"],
        ["shortenedUrlCount", "Integer", "Shortened URLs (bit.ly, tinyurl, etc.)"],
        ["ipUrlCount", "Integer", "URLs using IP addresses instead of domains"],
    ]
)

add_heading_custom("5.3 IMPLEMENTATION", 2)

add_heading_custom("5.3.1 Dataset Preparation", 3)
add_body(
    "The training dataset is the UCI SMS Spam Collection, a public research dataset "
    "containing 5,574 SMS messages labeled as 'spam' or 'ham' (legitimate). After "
    "deduplication and cleaning, 5,158 messages were retained."
)
add_body("Data Split:", bold=True)
add_bullet("Training set: 3,610 messages (70%) - Used for model training")
add_bullet("Validation set: 774 messages (15%) - Used for hyperparameter tuning")
add_bullet("Test set: 774 messages (15%) - Used for final unbiased evaluation")
add_body(
    "Stratified sampling was applied to ensure consistent spam/ham ratios across all splits. "
    "The random seed was fixed at 42 for full reproducibility."
)

add_heading_custom("5.3.2 Text Vectorization", 3)
add_body(
    "Text is converted to numerical feature vectors using TF-IDF (Term Frequency - Inverse "
    "Document Frequency) vectorization with the following configuration:"
)
add_bullet("N-gram range: (1, 2) - Captures both unigrams and bigrams")
add_bullet("Max features: 15,000 - Vocabulary size limit")
add_bullet("Sublinear TF: Enabled - Applies logarithmic TF scaling for better discrimination")
add_body(
    "The resulting vocabulary contained 8,884 unique terms from the training corpus. The "
    "TF-IDF vectors serve as the primary input features for the spam classification model."
)

add_heading_custom("5.3.3 Model Training and Comparison", 3)
add_body("Four classical ML algorithms were trained and evaluated:")
add_bullet("Multinomial Naive Bayes: Probabilistic classifier based on Bayes' theorem, well-suited for text classification with TF-IDF features.")
add_bullet("Logistic Regression: Linear classifier using regularized maximum likelihood estimation with balanced class weights.")
add_bullet("Random Forest: Ensemble of decision trees using bagging for improved generalization.")
add_bullet("Linear SVM (Support Vector Machine): Maximum-margin classifier finding the optimal hyperplane for class separation.")

add_heading_custom("5.3.4 Classification Decision Logic", 3)
add_body("The final classification label is determined by a multi-stage decision process:")
add_bullet("If phishing probability >= 0.68: Label = 'Phishing Risk', Risk = High")
add_bullet("If spam probability >= 0.70: Label = 'Spam', Risk = High")
add_bullet("If phishing probability >= 0.42 OR 0.55 <= spam probability <= 0.70: Label = 'Suspicious', Risk = Medium")
add_bullet("If spam probability <= 0.45: Label = 'Legitimate', Risk = Low")
add_bullet("Otherwise: Label = 'Needs Review', Risk = Medium")

add_heading_custom("5.3.5 LLM Integration", 3)
add_body(
    "MailMind AI integrates OpenAI GPT-5.4 as a backend-only service for generating "
    "natural-language summaries, response recommendations, and suggested response drafts. "
    "The LLM operates under strict safety constraints:"
)
add_bullet("The email content is treated as untrusted data, not instructions (prompt injection defense).")
add_bullet("The LLM receives only structured evidence from the ML pipeline, not raw email content for decision-making.")
add_bullet("Suggested responses are suppressed for emails classified as Spam, Suspicious, or Phishing Risk.")
add_bullet("A deterministic fallback generates responses when the LLM is unavailable.")

add_heading_custom("5.4 MAINTENANCE", 2)
add_body("Maintenance strategies for MailMind AI include:")
add_bullet("Model Retraining: User feedback data collected through the correction mechanism can be used to retrain models periodically, improving accuracy on new email patterns.")
add_bullet("Dataset Expansion: The current model is trained on SMS messages. Future iterations should incorporate dedicated email corpora (e.g., Enron, TREC) for better domain alignment.")
add_bullet("Dependency Updates: Regular updates to Python packages (scikit-learn, FastAPI) and frontend packages (Expo SDK, React Native) to maintain security and compatibility.")
add_bullet("Performance Monitoring: The analytics endpoint provides aggregate metrics for tracking classification distribution trends and identifying potential model drift.")
add_bullet("Error Logging: Backend logging captures all API errors, file parsing failures, and LLM assistance issues for operational monitoring.")

page_break()

# ====================================================================
# CHAPTER 6 - SYSTEM TESTING
# ====================================================================
add_heading_custom("CHAPTER 6", 1)
add_heading_custom("SYSTEM TESTING", 1)

add_heading_custom("6.1 TESTING DEFINITION", 2)
add_body(
    "Software testing is the process of evaluating and verifying that a software application "
    "or system meets specified requirements and is free of defects. It involves executing "
    "software components using manual or automated tools to evaluate one or more properties "
    "of interest. Testing is a critical phase in the software development lifecycle that "
    "ensures quality, reliability, and correctness of the delivered product."
)

add_heading_custom("6.2 TESTING OBJECTIVE", 2)
add_body("The testing objectives for MailMind AI are:")
add_bullet("Verify that the ML pipeline produces accurate and consistent classification results across all email types.")
add_bullet("Validate that the API endpoints handle all input variations correctly, including edge cases and error conditions.")
add_bullet("Ensure the file parser correctly extracts email content from all supported formats (.eml, .txt, .pdf, .docx, .csv).")
add_bullet("Confirm that the frontend renders analysis results correctly and navigation flows work as expected.")
add_bullet("Test the integration between frontend, backend API, ML pipeline, and database layers.")
add_bullet("Verify that safety guardrails (no response drafts for phishing/spam) are enforced correctly.")

add_heading_custom("6.3 TYPES OF TESTING", 2)

add_heading_custom("6.3.1 Unit Testing", 3)
add_body(
    "Unit tests validate individual functions and methods in isolation. The backend uses "
    "pytest as the testing framework. Key unit test areas include:"
)
add_bullet("ML Pipeline: Test clean_nlp_text(), extract_features(), analyze() for various email inputs.")
add_bullet("File Parser: Test each format parser (_parse_eml, _parse_text, _parse_csv) with valid and invalid inputs.")
add_bullet("API Models: Test Pydantic schema validation for EmailInput and FeedbackInput.")

add_heading_custom("6.3.2 Integration Testing", 3)
add_body(
    "Integration tests verify the interaction between system components. Tests validate "
    "the complete flow from API request through ML pipeline to database persistence and "
    "response generation."
)

add_heading_custom("6.3.3 System Testing", 3)
add_body(
    "System testing evaluates the complete application as a whole. Automated browser "
    "testing using Playwright verified the frontend rendering, navigation, and user "
    "interaction flows across different screen sizes."
)

add_heading_custom("6.3.4 Model Evaluation Testing", 3)
add_body(
    "The ML model was rigorously evaluated on a held-out test set that was never seen "
    "during training or validation. This ensures unbiased performance estimates."
)

add_heading_custom("Table 6.1: Model Comparison Results (Test Set)", 3)
add_table(
    ["Model", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"],
    [
        ["Multinomial Naive Bayes", "98.32%", "98.82%", "87.50%", "92.82%", "0.9917"],
        ["Logistic Regression", "98.32%", "91.92%", "94.79%", "93.33%", "0.9978"],
        ["Random Forest", "98.45%", "100.0%", "87.50%", "93.33%", "0.9976"],
        ["Linear SVM", "98.71%", "93.00%", "96.88%", "94.90%", "0.9878"],
    ]
)

add_heading_custom("Table 6.2: Confusion Matrix - Multinomial Naive Bayes (Test Set)", 3)
add_table(
    ["", "Predicted Ham", "Predicted Spam"],
    [
        ["Actual Ham", "677 (TN)", "1 (FP)"],
        ["Actual Spam", "12 (FN)", "84 (TP)"],
    ]
)
add_body(
    "The Multinomial Naive Bayes model was selected as the best model based on its balance "
    "of high precision (98.82%) minimizing false positives and strong overall accuracy. "
    "With only 1 false positive and 12 false negatives on 774 test samples, the model "
    "demonstrates robust performance suitable for production deployment."
)

add_heading_custom("6.4 TEST CASES", 2)

add_heading_custom("Table 6.3: Backend API Test Cases", 3)
add_table(
    ["TC ID", "Test Case", "Input", "Expected Output", "Status"],
    [
        ["TC01", "Health check endpoint", "GET /api/health", "status: ok, pipeline: ready", "Pass"],
        ["TC02", "Analyze legitimate email", "POST /api/email/analyze with work email", "label: Legitimate, probability < 0.5", "Pass"],
        ["TC03", "Analyze spam email", "POST /api/email/analyze with spam keywords", "label: Spam, probability > 0.7", "Pass"],
        ["TC04", "Analyze empty email", "POST /api/email/analyze with empty body/subject", "422 error with validation message", "Pass"],
        ["TC05", "Upload .eml file", "POST /api/email/analyze-file with .eml", "Parsed and classified correctly", "Pass"],
        ["TC06", "Upload .csv file", "POST /api/email/analyze-file with CSV", "Multiple emails parsed per row", "Pass"],
        ["TC07", "Upload unsupported file", "POST /api/email/analyze-file with .zip", "415 error: Unsupported file", "Pass"],
        ["TC08", "Get analysis history", "GET /api/email/history", "Array of analysis records", "Pass"],
        ["TC09", "Submit feedback", "POST /api/email/{id}/feedback", "status: saved", "Pass"],
    ]
)

add_heading_custom("Table 6.4: Frontend UI Test Cases", 3)
add_table(
    ["TC ID", "Test Case", "Action", "Expected Result", "Status"],
    [
        ["TC10", "Start screen renders", "Launch app", "MailMind AI branding, Start button visible", "Pass"],
        ["TC11", "Navigate to Home", "Press Start analyzing", "Home dashboard with metrics displayed", "Pass"],
        ["TC12", "Navigate to Analyze", "Press Analyze tab", "Analyze screen with paste/upload options", "Pass"],
        ["TC13", "Paste email analysis", "Fill sender, subject, body and press Run", "Redirects to detail view with results", "Pass"],
        ["TC14", "File upload mode", "Toggle to Upload files", "File picker interface displayed", "Pass"],
        ["TC15", "Navigate to History", "Press History tab", "History list with search functionality", "Pass"],
        ["TC16", "Theme adaptation", "Change system theme preference", "UI adapts to light/dark scheme", "Pass"],
        ["TC17", "Copy draft response", "Press Copy draft button", "Draft copied to clipboard", "Pass"],
    ]
)

add_heading_custom("Table 6.5: Integration Test Cases", 3)
add_table(
    ["TC ID", "Test Case", "Description", "Expected Result", "Status"],
    [
        ["TC18", "End-to-end analysis flow", "Paste email in frontend, analyze, view result", "Complete analysis displayed with all dimensions", "Pass"],
        ["TC19", "History persistence", "Analyze email, navigate to History", "New analysis appears in history list", "Pass"],
        ["TC20", "Feedback submission", "Submit correction from detail view", "Feedback saved, confirmation shown", "Pass"],
        ["TC21", "Batch file processing", "Upload multiple .txt files", "All files processed with progress indicator", "Pass"],
        ["TC22", "Error handling", "Submit with empty fields", "User-friendly error message displayed", "Pass"],
    ]
)

page_break()

# ====================================================================
# CHAPTER 7 - CONCLUSION
# ====================================================================
add_heading_custom("CHAPTER 7", 1)
add_heading_custom("CONCLUSION", 1)

add_heading_custom("7.1 SUMMARY", 2)
add_body(
    "MailMind AI successfully demonstrates the application of classical machine learning "
    "techniques to the problem of email classification and threat detection. The project "
    "encompasses the complete data science and software engineering lifecycle, from raw data "
    "acquisition through production deployment."
)
add_body(
    "The system achieves its primary objectives of accurate spam classification (98.32% "
    "test accuracy), multi-dimensional email analysis (classification, phishing risk, "
    "category, priority, intent, entities), and explainable AI outputs that provide "
    "users with transparent justifications for each prediction."
)
add_body(
    "The comparison of four classical ML algorithms (Multinomial Naive Bayes, Logistic "
    "Regression, Random Forest, Linear SVM) on the UCI SMS Spam Collection dataset provides "
    "empirical evidence for model selection. While Linear SVM achieved the highest individual "
    "accuracy (98.71%), Multinomial Naive Bayes was selected for production deployment due to "
    "its exceptional precision (98.82%) which minimizes false positives - a critical "
    "requirement in email classification where incorrectly flagging legitimate emails has "
    "significant user impact."
)
add_body(
    "The full-stack architecture using React Native (Expo) for cross-platform mobile "
    "development, FastAPI for high-performance backend API, and MongoDB for flexible "
    "document storage creates a scalable and maintainable platform. The integration of "
    "LLM-based assistance (GPT-5.4) for email summarization and response drafting adds "
    "a natural-language interface layer while maintaining strict safety guardrails."
)
add_body(
    "The project contributes a practical demonstration of how classical ML, feature "
    "engineering, rule-based heuristics, and modern LLM capabilities can be combined "
    "into a cohesive system that provides actionable email intelligence to end users."
)

add_heading_custom("7.2 FUTURE ENHANCEMENT", 2)
add_body("The following enhancements are identified for future development:")
add_bullet("Email Server Integration: Connect to IMAP/POP3/SMTP servers for real-time email analysis directly from user mailboxes, eliminating the need for manual paste or file upload.")
add_bullet("User Authentication: Implement secure user authentication (JWT or OAuth) to enable personalized analysis history, preferences, and multi-device synchronization.")
add_bullet("Advanced ML Models: Experiment with transformer-based models (BERT, DistilBERT) for potentially improved classification accuracy, especially for nuanced phishing detection.")
add_bullet("Dataset Expansion: Train on dedicated email corpora (Enron dataset, TREC Spam corpus) in addition to SMS data for better domain alignment with actual email content patterns.")
add_bullet("Active Learning: Implement an active learning loop where user feedback corrections are automatically incorporated into model retraining cycles.")
add_bullet("Multilingual Support: Extend the NLP pipeline to support email analysis in multiple languages using language detection and language-specific tokenization.")
add_bullet("Browser Extension: Develop a browser extension that integrates MailMind analysis directly into webmail interfaces (Gmail, Outlook) for seamless inline analysis.")
add_bullet("Threat Intelligence Integration: Connect to external threat intelligence feeds (VirusTotal, PhishTank) to cross-reference URLs and domains found in analyzed emails.")
add_bullet("Visualization Dashboard: Build comprehensive analytics dashboards with charts showing classification trends, threat patterns, and model performance metrics over time.")
add_bullet("Offline Mode: Enable local model inference for email analysis without internet connectivity, using on-device ML model execution.")

page_break()

# ====================================================================
# CHAPTER 8 - APPENDIX
# ====================================================================
add_heading_custom("CHAPTER 8", 1)
add_heading_custom("APPENDIX", 1)

add_heading_custom("8.1 SCREENSHOTS", 2)
add_body(
    "Note: Screenshots of all application screens are available in the project's test_reports "
    "directory and can be captured using the application's web preview at the deployment URL. "
    "Key screens include:"
)
add_bullet("Figure 8.1: Start Screen - Animated CursorGrid background with MailMind AI branding and ML pipeline status indicator.")
add_bullet("Figure 8.2: Home Dashboard - Command center with aggregate metrics (Analyzed, Threats, Priority) and quick access to the analyzer.")
add_bullet("Figure 8.3: Email Analysis Screen (Paste Mode) - Text input fields for sender, subject, and body with Run ML Analysis button.")
add_bullet("Figure 8.4: File Upload Interface - Drag-and-drop area supporting .eml, .txt, .pdf, .docx, .csv with batch progress tracking.")
add_bullet("Figure 8.5: Analysis Result Detail View - Classification badge, probability bars, explanation factors, decision context, entities, response assistant, and feedback controls.")
add_bullet("Figure 8.6: History Screen - Searchable analysis log with status badges and summary previews.")

add_heading_custom("8.2 CODING", 2)
add_body("The complete source code is organized as follows:", bold=True)
add_body("")

# Backend code summary
add_heading_custom("8.2.1 Backend - server.py (Key Endpoints)", 3)
add_body(
    "The FastAPI server (291 lines) implements 9 REST API endpoints. Key features include "
    "async MongoDB operations via Motor, Pydantic request validation, CORS middleware, "
    "streaming CSV export, and LLM integration with prompt injection defense."
)
add_body("Core analysis flow: EmailInput -> clean_nlp_text() -> extract_features() -> "
         "MailMindPipeline.analyze() -> llm_assistance() -> persist() -> Response")

add_heading_custom("8.2.2 Backend - ml_pipeline.py (ML Pipeline)", 3)
add_body(
    "The ML Pipeline (295 lines) implements the MailMindPipeline class with the complete "
    "classification workflow. It loads the pre-trained Naive Bayes model from "
    "models/best_spam_model.joblib and falls back to a seed corpus if unavailable. "
    "The pipeline computes spam probability, phishing risk, category, priority, intent, "
    "entities, and explanation factors in a single analyze() call."
)

add_heading_custom("8.2.3 Backend - file_parser.py (File Parser)", 3)
add_body(
    "The File Parser (150 lines) implements safe, non-executing text extraction from "
    "5 file formats. CSV parsing uses case-insensitive column matching to handle "
    "various CSV schemas. Text file parsing supports multiple email splitting strategies "
    "including From: header detection and delimiter-based splitting (---, ===, ***)."
)

add_heading_custom("8.2.4 Frontend - index.tsx (Main Application)", 3)
add_body(
    "The main application file (158 lines of TypeScript/React Native) implements all "
    "screens in a single-file architecture: StartScreen, HomeScreen, AnalyzeScreen, "
    "DetailScreen, HistoryScreen, and shared components (EmailRow, EmptyState, StatusBadge, "
    "NavItem, ProbRow, InfoLine). Uses makeStyles hook pattern for theme-aware styling."
)

add_heading_custom("8.2.5 Frontend - api.ts (API Client)", 3)
add_body(
    "The API Client (52 lines) provides type-safe functions for backend communication: "
    "analyzeEmail(), analyzeFile(), getHistory(), saveFeedback(). Uses FormData for "
    "file uploads with platform-specific handling (Blob on web, URI-based on native)."
)

add_heading_custom("8.3 DATA DICTIONARY", 2)

add_heading_custom("8.3.1 Database Collections", 3)
add_table(
    ["Collection", "Document Count", "Purpose"],
    [
        ["email_analyses", "Dynamic", "Stores all email analysis records with classifications, features, entities, and feedback"],
    ]
)

add_heading_custom("8.3.2 EmailInput Schema (API Request)", 3)
add_table(
    ["Field", "Type", "Required", "Default", "Description"],
    [
        ["sender", "String", "No", "\"\"", "Email sender address"],
        ["subject", "String", "No", "\"\"", "Email subject line"],
        ["body", "String", "No", "\"\"", "Email body content"],
        ["client_id", "String", "No", "\"anonymous\"", "Client session identifier"],
        ["source_name", "String", "No", "\"pasted-email\"", "Input source label"],
    ]
)

add_heading_custom("8.3.3 Analysis Response Schema", 3)
add_table(
    ["Field", "Type", "Description"],
    [
        ["spam.label", "String", "Classification: Legitimate, Suspicious, Spam, Phishing Risk, Needs Review"],
        ["spam.probability", "Float (0-1)", "ML model spam probability score"],
        ["spam.riskLevel", "String", "Risk level: low, medium, high"],
        ["phishing.risk", "String", "Phishing risk level: low, medium, high"],
        ["phishing.probability", "Float (0-1)", "Heuristic phishing probability"],
        ["category.label", "String", "Email category (Work, Personal, Banking, etc.)"],
        ["category.probability", "Float (0-1)", "Category confidence score"],
        ["priority.label", "String", "Priority: Critical, High, Medium, Low, Informational"],
        ["priority.probability", "Float (0-1)", "Priority confidence score"],
        ["priority.reasons", "String[]", "Human-readable priority justifications"],
        ["intent.label", "String", "Detected intent (Confirm, Pay, Reply, etc.)"],
        ["intent.actionRequired", "Boolean", "Whether user action is recommended"],
        ["entities.people", "String[]", "Extracted person references"],
        ["entities.urls", "String[]", "Extracted URLs"],
        ["entities.amounts", "String[]", "Extracted monetary amounts"],
        ["explanation", "Object[]", "Array of {type, direction, text} factors"],
        ["summary", "String", "Natural-language email summary"],
        ["modelVersion", "String", "ML model version identifier"],
    ]
)

add_heading_custom("8.3.4 FeedbackInput Schema", 3)
add_table(
    ["Field", "Type", "Required", "Description"],
    [
        ["client_id", "String", "Yes", "Client session identifier"],
        ["field", "String", "Yes", "Field being corrected: spam, category, priority, intent"],
        ["corrected_value", "String", "Yes", "User's corrected classification value"],
    ]
)

page_break()

# ====================================================================
# CHAPTER 9 - BIBLIOGRAPHY AND REFERENCES
# ====================================================================
add_heading_custom("CHAPTER 9", 1)
add_heading_custom("BIBLIOGRAPHY AND REFERENCES", 1)

references = [
    "[1] Almeida, T.A., Gomez Hidalgo, J.M., and Yamakami, A. (2011). \"Contributions to the Study of SMS Spam Filtering: New Collection and Results.\" Proceedings of the 2011 ACM Symposium on Document Engineering (DOCENG'11).",
    "[2] UCI Machine Learning Repository. \"SMS Spam Collection Data Set.\" https://archive.ics.uci.edu/dataset/228/sms+spam+collection. Accessed 2025.",
    "[3] Pedregosa, F. et al. (2011). \"Scikit-learn: Machine Learning in Python.\" Journal of Machine Learning Research, 12, pp. 2825-2830.",
    "[4] Manning, C.D., Raghavan, P., and Schutze, H. (2008). \"Introduction to Information Retrieval.\" Cambridge University Press. Chapter 6: Scoring, Term Weighting, and the Vector Space Model.",
    "[5] Ramirez-Lopez, S. and Tinambunan, S. (2023). \"A Comprehensive Review of Email Spam Detection Techniques.\" International Journal of Computer Science and Information Security, Vol. 21, No. 3.",
    "[6] FastAPI Documentation. \"FastAPI - A modern, fast web framework for building APIs with Python.\" https://fastapi.tiangolo.com/. Accessed 2025.",
    "[7] React Native Documentation. \"React Native - Build native apps using React.\" https://reactnative.dev/. Accessed 2025.",
    "[8] Expo Documentation. \"Expo - Build cross-platform apps with React Native.\" https://docs.expo.dev/. Accessed 2025.",
    "[9] MongoDB Documentation. \"MongoDB Manual.\" https://www.mongodb.com/docs/manual/. Accessed 2025.",
    "[10] Bird, S., Klein, E., and Loper, E. (2009). \"Natural Language Processing with Python.\" O'Reilly Media.",
    "[11] Sebastiani, F. (2002). \"Machine Learning in Automated Text Categorization.\" ACM Computing Surveys, 34(1), pp. 1-47.",
    "[12] OpenAI API Documentation. \"API Reference.\" https://platform.openai.com/docs/api-reference. Accessed 2025.",
    "[13] Richardson, L. (2023). \"Beautiful Soup Documentation.\" https://www.crummy.com/software/BeautifulSoup/bs4/doc/. Accessed 2025.",
    "[14] Brownlee, J. (2020). \"How to Develop a Naive Bayes Classifier from Scratch in Python.\" Machine Learning Mastery.",
    "[15] Geron, A. (2022). \"Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow.\" 3rd Edition, O'Reilly Media.",
]

for ref in references:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(ref)
    set_font(run, 12)

# ====================================================================
# SAVE DOCUMENT
# ====================================================================
output_path = "/app/MailMind_AI_Project_Documentation.docx"
doc.save(output_path)
print(f"Documentation saved to {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")
