import io, os, re, json, secrets, smtplib, statistics
import psycopg
from psycopg.rows import dict_row
from datetime import datetime, timedelta
from email.message import EmailMessage
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-change-me")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 31536000
DATABASE_URL = os.getenv("NEXA_DATABASE_URL") or os.getenv("DATABASE_URL")

# These are the actual interview branches in NEXA.
BRANCHES = ["AIML", "CSE", "Data Science", "Cyber Security", "ECE", "EEE"]
LEVELS = ["Beginner", "Intermediate", "Advanced"]
MODES = ["Text + typing", "Voice + typing", "Video + voice"]

BRANCH_TOPICS = {
    "AIML": [
        "supervised learning", "unsupervised learning", "reinforcement learning", "linear regression", "logistic regression",
        "decision trees", "random forests", "gradient boosting", "support vector machines", "k-nearest neighbors",
        "naive Bayes", "clustering", "k-means", "hierarchical clustering", "PCA", "feature engineering", "feature scaling",
        "one-hot encoding", "label encoding", "missing values", "outliers", "data leakage", "train-validation-test split",
        "cross-validation", "bias and variance", "overfitting", "underfitting", "regularization", "L1 and L2 regularization",
        "hyperparameter tuning", "grid search", "random search", "model evaluation", "confusion matrix", "precision and recall",
        "F1 score", "ROC-AUC", "class imbalance", "ensemble learning", "bagging", "boosting", "neural networks", "perceptron",
        "activation functions", "backpropagation", "gradient descent", "learning rate", "batch normalization", "dropout",
        "CNNs", "RNNs", "LSTMs", "GRUs", "attention", "transformers", "embeddings", "transfer learning", "fine-tuning",
        "computer vision", "image classification", "object detection", "image segmentation", "NLP", "tokenization", "text embeddings",
        "sequence modeling", "large language models", "prompt design", "retrieval augmented generation", "vector databases", "AI agents",
        "model deployment", "model serving", "MLOps", "model monitoring", "data drift", "concept drift", "explainable AI",
        "SHAP", "fairness", "privacy", "AI security", "experiment tracking", "reproducibility", "synthetic data", "active learning",
        "time-series forecasting", "anomaly detection", "recommendation systems", "reinforcement policy", "reward shaping", "AI system architecture",
        "model compression", "quantization", "edge AI", "responsible AI", "production ML troubleshooting"
    ],
    "CSE": [
        "arrays", "strings", "linked lists", "stacks", "queues", "hash tables", "binary trees", "binary search trees", "AVL trees",
        "heaps", "priority queues", "graphs", "B-trees", "tries", "recursion", "dynamic programming", "greedy algorithms", "backtracking",
        "binary search", "sorting algorithms", "merge sort", "quick sort", "time complexity", "space complexity", "amortized analysis", "processes",
        "threads", "concurrency", "deadlocks", "CPU scheduling", "memory management", "virtual memory", "paging", "file systems", "system calls",
        "computer networks", "OSI model", "TCP/IP", "HTTP", "DNS", "routing", "switching", "sockets", "databases", "SQL",
        "normalization", "transactions", "ACID", "indexes", "query optimization", "NoSQL", "distributed databases", "operating systems",
        "compilers", "lexical analysis", "parsing", "object-oriented programming", "inheritance", "polymorphism", "encapsulation", "abstraction",
        "design patterns", "SOLID principles", "software architecture", "REST APIs", "microservices", "caching", "load balancing", "message queues",
        "distributed systems", "consensus", "CAP theorem", "event-driven architecture", "cloud-native systems", "containers", "Docker", "Kubernetes",
        "Git", "CI/CD", "testing", "unit testing", "integration testing", "debugging", "security", "authentication", "authorization", "encryption",
        "performance optimization", "memory leaks", "garbage collection", "multithreading", "async programming", "system design", "scalability", "availability", "reliability", "observability"
    ],
    "Data Science": [
        "data collection", "data cleaning", "exploratory data analysis", "descriptive statistics", "mean median mode", "variance and standard deviation",
        "probability", "conditional probability", "Bayes theorem", "random variables", "distributions", "normal distribution", "binomial distribution",
        "sampling", "central limit theorem", "confidence intervals", "hypothesis testing", "p-values", "statistical power", "correlation", "covariance",
        "linear regression", "multiple regression", "logistic regression", "regularization", "feature engineering", "feature selection", "dimensionality reduction",
        "PCA", "clustering", "k-means", "hierarchical clustering", "classification", "decision trees", "random forests", "gradient boosting", "SVM",
        "nearest neighbors", "model validation", "cross-validation", "train-test split", "bias variance", "overfitting", "underfitting", "data leakage",
        "class imbalance", "precision recall", "F1 score", "ROC-AUC", "confusion matrix", "missing data", "outlier detection", "data transformation",
        "encoding categorical data", "scaling", "feature pipelines", "time series", "trend analysis", "seasonality", "forecasting", "ARIMA",
        "anomaly detection", "recommendation systems", "natural language processing", "text preprocessing", "TF-IDF", "embeddings", "sentiment analysis",
        "data visualization", "matplotlib", "dashboard design", "business intelligence", "SQL analytics", "window functions", "ETL", "ELT", "data warehouses",
        "data lakes", "Spark", "pandas", "NumPy", "scikit-learn", "experiment tracking", "model deployment", "MLOps", "data governance", "data privacy",
        "data quality", "reproducibility", "A/B testing", "causal inference", "feature stores", "stream processing", "real-time analytics", "data architecture",
        "stakeholder communication", "metric design", "KPI analysis", "forecast evaluation", "model interpretability", "responsible analytics", "production troubleshooting"
    ],
    "Cyber Security": [
        "CIA triad", "threat modeling", "risk assessment", "phishing", "social engineering", "password security", "multi-factor authentication",
        "authentication", "authorization", "access control", "least privilege", "network security", "firewalls", "IDS and IPS", "VPNs", "DNS security",
        "HTTP security", "TLS", "PKI", "digital certificates", "encryption", "hashing", "digital signatures", "key management", "secure coding",
        "input validation", "SQL injection", "XSS", "CSRF", "command injection", "path traversal", "SSRF", "buffer overflow", "memory safety",
        "malware", "ransomware", "trojans", "worms", "botnets", "endpoint security", "EDR", "zero trust", "network segmentation", "security monitoring",
        "SIEM", "log analysis", "incident response", "forensics", "credential compromise", "insider threats", "data loss prevention", "backup security",
        "vulnerability management", "penetration testing", "security scanning", "CVSS", "patch management", "secure configuration", "cloud security", "container security",
        "Kubernetes security", "API security", "OAuth", "OpenID Connect", "JWT", "secure sessions", "web security", "mobile security", "IoT security",
        "wireless security", "secure Wi-Fi", "network attacks", "DDoS", "ARP spoofing", "DNS attacks", "man-in-the-middle attacks", "zero-day vulnerabilities",
        "threat intelligence", "MITRE ATT&CK", "security policies", "security awareness", "compliance", "privacy", "cryptographic protocols", "secure SDLC",
        "DevSecOps", "code review", "dependency security", "software supply chain", "secrets management", "security automation", "risk prioritization", "business continuity",
        "disaster recovery", "security architecture", "identity governance", "privileged access", "security metrics", "SOC operations", "red team", "blue team",
        "purple team", "security incident communication", "forensic evidence handling", "production security troubleshooting"
    ],
    "ECE": [
        "semiconductor basics", "PN junction", "diodes", "Zener diodes", "rectifiers", "transistors", "BJT", "MOSFET", "amplifiers", "oscillators",
        "operational amplifiers", "feedback", "filters", "analog modulation", "AM", "FM", "PM", "sampling theorem", "ADC", "DAC",
        "digital electronics", "logic gates", "Boolean algebra", "Karnaugh maps", "combinational circuits", "multiplexers", "demultiplexers", "encoders", "decoders", "adders",
        "flip-flops", "registers", "counters", "finite state machines", "memory devices", "microprocessors", "microcontrollers", "interrupts", "timers", "serial communication",
        "UART", "SPI", "I2C", "CAN", "embedded systems", "real-time systems", "RTOS", "embedded C", "PCB design", "signal integrity",
        "digital signal processing", "discrete signals", "convolution", "correlation", "DFT", "FFT", "FIR filters", "IIR filters", "control systems", "feedback control",
        "Laplace transform", "transfer functions", "stability", "PID control", "communication systems", "channel capacity", "noise", "SNR", "Shannon theorem", "coding",
        "error detection", "error correction", "line coding", "multiplexing", "optical communication", "antenna basics", "RF systems", "radar", "satellite communication", "wireless communication",
        "cellular networks", "5G concepts", "IoT hardware", "sensors", "actuators", "robotics electronics", "power electronics", "DC-DC converters", "inverters", "motor drives",
        "VLSI", "CMOS", "ASIC", "FPGA", "HDL", "Verilog", "digital system design", "hardware debugging", "measurement instruments", "oscilloscopes",
        "electromagnetic compatibility", "low-power design", "embedded security", "hardware-software co-design", "edge devices", "industrial electronics", "automotive electronics", "medical electronics", "production troubleshooting", "system architecture"
    ],
    "EEE": [
        "electrical circuits", "Ohm's law", "Kirchhoff laws", "Thevenin theorem", "Norton theorem", "superposition theorem", "AC circuits", "phasors", "resonance", "power factor",
        "three-phase systems", "transformers", "transformer losses", "induction motors", "synchronous motors", "DC machines", "generators", "motor starting", "speed control", "electrical drives",
        "power electronics", "diodes", "thyristors", "MOSFETs", "IGBTs", "rectifiers", "choppers", "inverters", "cycloconverters", "PWM",
        "power systems", "generation", "transmission", "distribution", "load flow", "fault analysis", "short circuits", "protection systems", "relays", "circuit breakers",
        "earthing", "power quality", "harmonics", "voltage regulation", "frequency control", "economic dispatch", "smart grids", "microgrids", "renewable energy", "solar PV",
        "wind energy", "battery systems", "energy storage", "electric vehicles", "charging systems", "power factor correction", "SCADA", "substations", "high voltage engineering", "insulation",
        "electrical measurements", "multimeters", "oscilloscopes", "CTs and PTs", "instrument transformers", "transducers", "control systems", "feedback", "transfer functions", "stability",
        "PID control", "PLC", "industrial automation", "sensors", "actuators", "embedded controllers", "signal conditioning", "digital electronics", "logic gates", "microcontrollers",
        "electromagnetics", "magnetic circuits", "electrical safety", "arc flash", "maintenance", "condition monitoring", "predictive maintenance", "asset management", "reliability", "power electronics thermal design",
        "energy efficiency", "building electrical systems", "industrial power systems", "motor protection", "generator protection", "grid integration", "power system stability", "distributed generation", "energy forecasting", "production troubleshooting"
    ]
}

QUESTION_FORMS = {
    "Beginner": [
        "What is {topic}? Explain it in simple terms and give one practical example.",
        "Why is {topic} important in {branch}? Mention a common real-world use.",
        "What are the main parts or ideas involved in {topic}? Explain each briefly.",
        "How would you explain {topic} to a first-year engineering student?",
        "What problem does {topic} solve? Give a simple example.",
        "What is one common mistake beginners make with {topic}, and how can it be avoided?",
        "Compare {topic} with a closely related concept and state when each is useful.",
        "Describe a basic workflow involving {topic} from input to result.",
        "What are two advantages and one limitation of {topic}?"
    ],
    "Intermediate": [
        "How does {topic} work internally? Walk through the important steps.",
        "Compare two practical approaches for implementing {topic}. When would you choose each?",
        "What trade-offs should an engineer consider when using {topic} in a real system?",
        "How would you debug a system where {topic} is producing incorrect results?",
        "Give a practical design example using {topic} and explain your choices.",
        "What performance or reliability issues can arise with {topic}, and how would you address them?",
        "How does changing a key parameter affect {topic}? Explain with an example.",
        "What tests would you write to validate an implementation of {topic}?",
        "How would you integrate {topic} with another component in a production application?"
    ],
    "Advanced": [
        "Design a production-grade solution centered on {topic}. Explain architecture, trade-offs and failure handling.",
        "Analyze the hardest scalability or reliability challenge associated with {topic} and propose a robust solution.",
        "How would you optimize a large-scale system that depends heavily on {topic}? Explain your reasoning.",
        "Suppose a production system using {topic} is failing intermittently. Give a structured investigation plan.",
        "Compare competing architectural strategies for {topic} and defend one for a high-traffic system.",
        "What edge cases and failure modes would you expect with {topic}, and how would you mitigate them?",
        "How would security, privacy or safety requirements change the design of a system using {topic}?",
        "Design an evaluation strategy for a solution involving {topic}. Which metrics and experiments matter most?",
        "Describe how you would evolve a prototype using {topic} into a maintainable production system."
    ]
}


def now():
    return datetime.now().isoformat(timespec="seconds")

class HybridRow(dict):
    """Dictionary-style row that also supports SQLite-style numeric indexing."""
    def __init__(self, cursor, values):
        super().__init__(zip((column.name for column in cursor.description), values))
        self._values = values

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return super().__getitem__(key)


def hybrid_row_factory(cursor):
    return lambda values: HybridRow(cursor, values)

class PostgresConnection:
    """Compatibility layer for SQLite-style SQL calls."""

    def __init__(self, connection):
        self.connection = connection
        self.cursor = None

    @staticmethod
    def _adapt(sql):
        query = sql.strip()

        ignore = query.upper().startswith("INSERT OR IGNORE INTO ")
        replace = query.upper().startswith("INSERT OR REPLACE INTO ")

        if ignore:
            query = re.sub(
                r"^INSERT\s+OR\s+IGNORE\s+INTO",
                "INSERT INTO", query, flags=re.I
            )
        elif replace:
            query = re.sub(
                r"^INSERT\s+OR\s+REPLACE\s+INTO",
                "INSERT INTO", query, flags=re.I
            )

        query = query.replace("last_insert_rowid()", "lastval() AS id")
        query = query.replace("?", "%s")

        if ignore and "ON CONFLICT" not in query.upper():
            query += " ON CONFLICT DO NOTHING"

        if replace:
            match = re.search(
                r"INSERT INTO\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]+)\)\s*VALUES",
                query, flags=re.I
            )
            if match:
                columns = [x.strip() for x in match.group(2).split(",")]
                key = "answer_id" if "answer_id" in columns else columns[0]
                updates = [
                    x for x in columns
                    if x != key and x.lower() != "id"
                ]

                if updates:
                    assignments = ", ".join(
                        f"{x}=EXCLUDED.{x}" for x in updates
                    )
                    query += f" ON CONFLICT ({key}) DO UPDATE SET {assignments}"
                else:
                    query += f" ON CONFLICT ({key}) DO NOTHING"

        return query

    def execute(self, sql, params=None):
        self.cursor = self.connection.execute(
            self._adapt(sql), params or ()
        )
        return self.cursor

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def executescript(self, script):
        for statement in script.split(";"):
            statement = statement.strip()
            if statement:
                self.execute(statement)
        return self

    def __getattr__(self, name):
        return getattr(self.connection, name)
    
def executescript(self, script):
    for statement in script.split(";"):
        statement = statement.strip()
        if statement:
            self.execute(statement)
    return self


def db():
    if not DATABASE_URL:
        raise RuntimeError("NEXA_DATABASE_URL is not configured.")
    connection = psycopg.connect(
        DATABASE_URL,
        row_factory=hybrid_row_factory,
        sslmode="require",
    )
    return PostgresConnection(connection)

def table_columns(c, table):
    c.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s",
        (table,)
    )
    return {r["column_name"] for r in c.fetchall()}


def migrate_schema(c):
    c.execute("""
    CREATE TABLE IF NOT EXISTS master_admins (
        id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        password_hash TEXT,
        name TEXT,
        role_label TEXT DEFAULT 'Master'
    )
""")
    cols = table_columns(c, "master_admins")
    if "password_hash" not in cols:
        c.execute("ALTER TABLE master_admins ADD COLUMN password_hash TEXT")
    if "name" not in cols:
        c.execute("ALTER TABLE master_admins ADD COLUMN name TEXT")
    if "role_label" not in cols:
        c.execute("ALTER TABLE master_admins ADD COLUMN role_label TEXT DEFAULT 'Master'")
    c.execute("CREATE TABLE IF NOT EXISTS master_revocations(email TEXT PRIMARY KEY, revoked_at TEXT NOT NULL)")
    resume_cols = table_columns(c, "resumes")
    if "ats_checked_at" not in resume_cols:
        c.execute("ALTER TABLE resumes ADD COLUMN ats_checked_at TEXT")
    c.execute("CREATE TABLE IF NOT EXISTS admin_profiles(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,user_id INTEGER UNIQUE NOT NULL,department TEXT,designation TEXT,university TEXT,faculty_id TEXT,created_at TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)")
    c.execute("CREATE TABLE IF NOT EXISTS question_bank_meta(branch TEXT PRIMARY KEY,target_count INTEGER NOT NULL,updated_at TEXT NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS answer_metrics(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,answer_id INTEGER UNIQUE NOT NULL,correctness REAL DEFAULT 0,clarity REAL DEFAULT 0,structure REAL DEFAULT 0,depth REAL DEFAULT 0,confidence REAL DEFAULT 0,follow_up TEXT,created_at TEXT,FOREIGN KEY(answer_id) REFERENCES answers(id) ON DELETE CASCADE)")
    c.execute("CREATE TABLE IF NOT EXISTS interview_codes(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,code TEXT UNIQUE NOT NULL,creator_id INTEGER NOT NULL,branch TEXT NOT NULL,level TEXT NOT NULL,mode TEXT NOT NULL,strict_mode INTEGER DEFAULT 1,disabled INTEGER DEFAULT 0,created_at TEXT NOT NULL,FOREIGN KEY(creator_id) REFERENCES users(id) ON DELETE CASCADE)")
    qcols=table_columns(c,"questions")
    if "is_self_intro" not in qcols: c.execute("ALTER TABLE questions ADD COLUMN is_self_intro INTEGER DEFAULT 0")
    cols=table_columns(c,"interviews")
    if "access_code_id" not in cols: c.execute("ALTER TABLE interviews ADD COLUMN access_code_id INTEGER")
    if "creator_id" not in cols: c.execute("ALTER TABLE interviews ADD COLUMN creator_id INTEGER")
    c.execute("CREATE INDEX IF NOT EXISTS idx_interview_codes_code ON interview_codes(code)")
    c.execute("CREATE TABLE IF NOT EXISTS creator_permissions(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,creator_id INTEGER NOT NULL,permission TEXT NOT NULL,enabled INTEGER DEFAULT 1,UNIQUE(creator_id,permission),FOREIGN KEY(creator_id) REFERENCES users(id) ON DELETE CASCADE)")
    c.execute("CREATE TABLE IF NOT EXISTS behavioral_events(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,interview_id INTEGER NOT NULL,event_type TEXT NOT NULL,event_data TEXT,created_at TEXT NOT NULL,FOREIGN KEY(interview_id) REFERENCES interviews(id) ON DELETE CASCADE)")


def ensure_master_users(c):
    emails = [
        x.strip().lower()
        for x in os.getenv("MASTER_EMAILS", "").split(",")
        if x.strip()
    ]

    env_pw = os.getenv("MASTER_PASSWORD", "")

    for email in emails:

        # Check whether this Master account has been revoked
        revoked = c.execute(
            "SELECT 1 FROM master_revocations WHERE lower(email)=%s",
            (email,)
        ).fetchone()

        if revoked:
            continue

        # Find the existing user
        user = c.execute(
            "SELECT * FROM users WHERE lower(email)=%s",
            (email,)
        ).fetchone()

        # Create the user if it does not exist
        if not user:
            uid = c.execute(
                """
                INSERT INTO users
                (email, name, password_hash, role, approved,
                 email_verified, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    email,
                    "Master Administrator",
                    generate_password_hash(
                        env_pw or secrets.token_urlsafe(24)
                    ),
                    "master",
                    1,
                    1,
                    now()
                )
            ).fetchone()["id"]

        else:
            uid = user["id"]

            c.execute(
                """
                UPDATE users
                SET role='master',
                    approved=1,
                    email_verified=1
                WHERE id=%s
                """,
                (uid,)
            )

        # Create the Master admin record if it does not exist
        c.execute(
            """
            INSERT INTO master_admins
            (email, created_at, password_hash, name, role_label)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT(email) DO NOTHING
            """,
            (
                email,
                now(),
                generate_password_hash(env_pw) if env_pw else None,
                "Master Administrator",
                "Master"
            )
        )

        # Synchronize the Master password when configured
        if env_pw:
            c.execute(
                """
                UPDATE master_admins
                SET password_hash=%s,
                    name=COALESCE(name, 'Master Administrator')
                WHERE lower(email)=lower(%s)
                """,
                (
                    generate_password_hash(env_pw),
                    email
                )
            )
def generate_question_bank(c):
    # Remove questions belonging to old branches
    c.execute(
        "DELETE FROM questions WHERE NOT (branch = ANY(%s))",
        (BRANCHES,)
    )

    for branch in BRANCHES:
        topics = BRANCH_TOPICS[branch]

        for level in LEVELS:
            count = c.execute(
                """
                SELECT COUNT(*) AS count
                FROM questions
                WHERE branch=%s AND level=%s
                """,
                (branch, level)
            ).fetchone()["count"]

            target = 300

            if count < target:
                forms = QUESTION_FORMS[level]

                rows = c.execute(
                    """
                    SELECT question
                    FROM questions
                    WHERE branch=%s AND level=%s
                    """,
                    (branch, level)
                ).fetchall()

                existing = {row["question"] for row in rows}
                new_questions = []

                for idx in range(count, target):
                    topic = topics[idx % len(topics)]
                    form = forms[idx % len(forms)]
                    cycle = idx // len(forms)

                    question = form.format(
                        topic=topic,
                        branch=branch
                    )

                    if cycle:
                        question += (
                            f" Focus on scenario variant {cycle + 1}: "
                            "explain a different context, constraint "
                            "or failure case."
                        )

                    if question not in existing:
                        new_questions.append((
                            branch,
                            level,
                            question,
                            now()
                        ))
                        existing.add(question)

                # Insert questions in a single batch
                if new_questions:
                    cursor = c.connection.cursor()

                    cursor.executemany(
                        """
                        INSERT INTO questions
                        (branch, level, question, created_at)
                        VALUES (%s, %s, %s, %s)
                        """,
                        new_questions
                    )

                    cursor.close()

            c.execute(
                """
                INSERT INTO question_bank_meta
                (branch, target_count, updated_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (branch)
                DO UPDATE SET
                    target_count = EXCLUDED.target_count,
                    updated_at = EXCLUDED.updated_at
                """,
                (branch, 900, now())
            )
def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,email TEXT UNIQUE NOT NULL,name TEXT NOT NULL,password_hash TEXT NOT NULL,role TEXT DEFAULT 'student',section_id INTEGER,approved INTEGER DEFAULT 1,email_verified INTEGER DEFAULT 0,created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS admins(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,user_id INTEGER UNIQUE NOT NULL,department TEXT,created_at TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS master_admins(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,email TEXT UNIQUE NOT NULL,created_at TEXT NOT NULL,password_hash TEXT,name TEXT,role_label TEXT DEFAULT 'Master');
    CREATE TABLE IF NOT EXISTS sections(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,admin_id INTEGER NOT NULL,name TEXT NOT NULL,invite_code TEXT UNIQUE NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(admin_id) REFERENCES admins(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS questions(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,branch TEXT NOT NULL,level TEXT NOT NULL,question TEXT NOT NULL,created_at TEXT NOT NULL,is_self_intro INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS resumes(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,user_id INTEGER NOT NULL,filename TEXT NOT NULL,file_data BYTEA NOT NULL,extracted_text TEXT,ats_score REAL,feedback TEXT,created_at TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS interviews(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,user_id INTEGER NOT NULL,branch TEXT,level TEXT,mode TEXT,strict_mode INTEGER DEFAULT 0,score REAL,feedback TEXT,started_at TEXT,completed_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS answers(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,interview_id INTEGER NOT NULL,question_id INTEGER NOT NULL,answer TEXT,score REAL,feedback TEXT,FOREIGN KEY(interview_id) REFERENCES interviews(id) ON DELETE CASCADE,FOREIGN KEY(question_id) REFERENCES questions(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS reports(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,user_id INTEGER NOT NULL,interview_id INTEGER,title TEXT,report_data BYTEA,summary TEXT,created_at TEXT,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS otp_codes(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,email TEXT,code_hash TEXT,purpose TEXT,expires_at TEXT,used INTEGER DEFAULT 0,created_at TEXT);
    CREATE TABLE IF NOT EXISTS audit_logs(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,actor TEXT,action TEXT,target TEXT,created_at TEXT);
    CREATE TABLE IF NOT EXISTS answer_metrics(id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,answer_id INTEGER UNIQUE NOT NULL,correctness REAL DEFAULT 0,clarity REAL DEFAULT 0,structure REAL DEFAULT 0,depth REAL DEFAULT 0,confidence REAL DEFAULT 0,follow_up TEXT,created_at TEXT,FOREIGN KEY(answer_id) REFERENCES answers(id) ON DELETE CASCADE);
    """)
    migrate_schema(c)
    ensure_master_users(c)
    generate_question_bank(c)
    c.execute("UPDATE questions SET is_self_intro=0 WHERE is_self_intro=1")
    c.execute("INSERT INTO questions(branch,level,question,created_at,is_self_intro) SELECT 'General','Beginner','Tell me about yourself. Please introduce yourself, including your education, skills, projects, achievements and career goals.',?,1 WHERE NOT EXISTS (SELECT 1 FROM questions WHERE lower(question)=lower('Tell me about yourself. Please introduce yourself, including your education, skills, projects, achievements and career goals.'))", (now(),))
    c.commit(); c.close()


def get_user_by_email(email):
    if not email:
        return None
    c = db(); u = c.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (email.strip(),)).fetchone(); c.close(); return u


def me():
    uid = session.get("uid") or session.get("user_id")
    if not uid:
        return None
    c = db(); u = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone(); c.close(); return u


def master():
    u = me()
    if not u:
        return False
    if u["role"] == "master":
        return True
    c = db(); ok = bool(c.execute("SELECT 1 FROM master_admins WHERE lower(email)=?", (u["email"].lower(),)).fetchone()); c.close(); return ok


def req(f):
    @wraps(f)
    def w(*a, **k):
        if not me(): return redirect(url_for("login"))
        return f(*a, **k)
    return w


def role(r):
    def d(f):
        @wraps(f)
        def w(*a, **k):
            if not me() or me()["role"] != r: abort(403)
            return f(*a, **k)
        return w
    return d


def has_permission(user_id, permission):
    c=db(); r=c.execute("SELECT enabled FROM creator_permissions WHERE creator_id=? AND permission=?",(user_id,permission)).fetchone(); c.close()
    return True if r is None else bool(r["enabled"])

def send_otp(email, code, purpose="verify"):
    host = os.getenv("SMTP_HOST","smtp.gmail.com"); user = os.getenv("SMTP_USERNAME"); pwd = os.getenv("SMTP_PASSWORD"); sender = os.getenv("SMTP_FROM") or user
    if not (host and user and pwd and sender):
        print(f"\n[DEV OTP] {email}: {code}\n"); return
    subject = "NEXA Interview verification code" if purpose == "verify" else "NEXA Interview password reset code"
    m = EmailMessage(); m["Subject"] = subject; m["From"] = sender; m["To"] = email
    action = "verify your NEXA account" if purpose == "verify" else "reset your NEXA password"
    m.set_content(f"Your NEXA code is {code}. Use it to {action}. It expires in 10 minutes.")
    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=15) as smtp:
        smtp.starttls(); smtp.login(user, pwd); smtp.send_message(m)

def otp(email, purpose="verify"):
    code = f"{secrets.randbelow(1000000):06d}"
    c = db(); c.execute("UPDATE otp_codes SET used=1 WHERE email=? AND purpose=?", (email, purpose)); c.execute("INSERT INTO otp_codes(email,code_hash,purpose,expires_at,created_at) VALUES(?,?,?,?,?)", (email, generate_password_hash(code), purpose, (datetime.now()+timedelta(minutes=10)).isoformat(), now())); c.commit(); c.close(); send_otp(email, code, purpose)

def master_credentials_ok(c, email, password):
    email = (email or "").strip().lower()
    env_emails = [e.strip().lower() for e in os.getenv("MASTER_EMAILS", "").split(",") if e.strip()]
    env_pw = os.getenv("MASTER_PASSWORD", "")
    # Built-in Masters are authenticated directly from the existing .env.
    if email in env_emails and env_pw and password == env_pw:
        return not c.execute("SELECT 1 FROM master_revocations WHERE lower(email)=?", (email,)).fetchone()
    row = c.execute("SELECT * FROM master_admins WHERE lower(email)=?", (email,)).fetchone()
    return bool(row and row["password_hash"] and check_password_hash(row["password_hash"], password))

def start_master_session(c, email, password):
    email = email.strip().lower()
    row = c.execute("SELECT * FROM master_admins WHERE lower(email)=?", (email,)).fetchone()
    user = c.execute("SELECT * FROM users WHERE lower(email)=?", (email,)).fetchone()
    if not user:
        name = row["name"] if row and row["name"] else "Master Administrator"
        c.execute("INSERT INTO users(email,name,password_hash,role,approved,email_verified,created_at) VALUES(?,?,?,?,?,?,?)", (email,name,generate_password_hash(password),"master",1,1,now()))
        uid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    else:
        uid = user["id"]
        c.execute("UPDATE users SET role='master',approved=1,email_verified=1 WHERE id=?", (uid,))
    c.execute("INSERT OR IGNORE INTO master_admins(email,created_at,password_hash,name,role_label) VALUES(?,?,?,?,?)", (email,now(),generate_password_hash(password),row["name"] if row and row["name"] else "Master Administrator","Master"))
    # For a DB-created Master, keep the dashboard password synchronized with the
    # password used to enter it. For .env Masters this simply refreshes the hash.
    c.execute("UPDATE master_admins SET password_hash=? WHERE lower(email)=lower(?)", (generate_password_hash(password), email))
    c.commit()
    session.clear(); session["uid"] = uid; session["user_id"] = uid; session["role"] = "master"; session["master_email"] = email
    return uid


def ats(text):
    skills = ["python","java","c++","sql","machine learning","deep learning","tensorflow","pytorch","pandas","numpy","flask","django","react","javascript","html","css","azure","aws","gcp","docker","kubernetes","git","linux","data structures","algorithms"]
    found = [x for x in skills if x in text.lower()]
    score = min(100, 35 + len(found) * 4)
    return score, json.dumps({"matched_skills": found, "suggestion": "Add measurable project outcomes, role-specific keywords and concise achievement bullets."})


def pdf_text(data):
    try:
        from pypdf import PdfReader
        return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)
    except Exception:
        return ""


def is_meaningless_answer(text):
    t=(text or "").strip().lower()
    if not t: return True
    words=re.findall(r"[a-zA-Z]{2,}", t)
    if not words: return True
    fillers={"hello","hi","hey","okay","ok","yes","no","nothing","something","dududus","asdf","asdfgh","test","testing","blah","blahblah","hmm","hmmm"}
    if len(words)<=2 and all(w in fillers for w in words): return True
    if len(set(words))==1 and len(words[0])>=5 and not any(v in words[0] for v in "aeiou"): return True
    compact=re.sub(r"[^a-z]","",t)
    if len(compact)>=6 and re.search(r"(.)\1{3,}", compact): return True
    vowels=sum(ch in "aeiou" for ch in compact)
    if len(compact)>=8 and vowels/len(compact)<0.15: return True
    return False

def question_keywords(question):
    q=(question or "").lower()
    if "tell me about yourself" in q or "introduce yourself" in q:
        return {"education","study","student","skills","skill","python","java","project","projects","achievement","achievements","career","goal","goals","experience","internship","technology","team","interest","interests","learning"}
    stop={"what","what's","explain","describe","define","how","why","give","with","example","difference","between","the","and","for","from","this","that","would","you","your","can","could","should","does","doesn","are","is","of","to","in","on","a","an"}
    return {w for w in re.findall(r"[a-zA-Z]{3,}", q) if w not in stop}

def local_evaluate(question, answer, branch, level):
    text=(answer or "").strip()
    if not text or is_meaningless_answer(text):
        return {"score":0,"correctness":0,"clarity":0,"structure":0,"depth":0,"confidence":0,"feedback":"0/100 — the response is empty, meaningless or not a valid answer to the interview question.","strengths":[],"weaknesses":["No meaningful answer","Relevance"],"follow_up":"Please give a direct answer to the question using the relevant technical concepts."}
    words=re.findall(r"[a-zA-Z]{2,}",text.lower()); unique=len(set(words)); length=len(words)
    qk=question_keywords(question); overlap=len(qk & set(words)); relevance=min(100, overlap*18 + min(25,length))
    if overlap==0 and length<12:
        return {"score":0,"correctness":0,"clarity":25,"structure":20,"depth":0,"confidence":20,"feedback":"0/100 — the answer does not contain meaningful concepts related to the question.","strengths":[],"weaknesses":["Relevance","Technical correctness"],"follow_up":"Answer the question directly and mention the key concept, mechanism and an example."}
    detail_words={"because","example","tradeoff","complexity","testing","security","scalable","model","data","design","impact","approach","reason","performance","latency","accuracy","architecture"}
    detail=sum(w in detail_words for w in words)
    structure=55+(12 if any(x in text.lower() for x in ["first","second","finally","because","therefore","however"]) else 0)
    clarity=min(95,48+min(35,unique*1.4))
    depth=min(95,40+min(42,length*1.2)+min(12,detail*2))
    correctness=min(95,35+min(35,overlap*8)+min(20,detail*2)+(8 if length>=35 else 0))
    confidence=min(95,48+min(40,length*1.0))
    score=round((correctness+clarity+structure+depth+confidence)/5)
    strengths=[]; weaknesses=[]
    for name,val,good in [("clarity",clarity,75),("structure",structure,70),("technical depth",depth,75),("technical correctness",correctness,75),("relevance",relevance,70)]:
        (strengths if val>=good else weaknesses).append(name)
    if score<60: follow="Explain the core concept again, then give one concrete example and one practical use case."
    elif score<80: follow="Follow-up: give a practical example and explain one limitation or trade-off."
    else: follow="Challenge follow-up: how would you implement this at production scale? Explain trade-offs and failure cases."
    return {"score":score,"correctness":round(correctness),"clarity":round(clarity),"structure":round(structure),"depth":round(depth),"confidence":round(confidence),"feedback":f"Relevant concepts detected: {overlap}. Rigorous evaluation completed across correctness, clarity, structure, depth and confidence.","strengths":strengths,"weaknesses":weaknesses,"follow_up":follow}


def ai_evaluate(question, answer, branch, level):
    if not answer.strip():
        return local_evaluate(question, answer, branch, level)
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return local_evaluate(question, answer, branch, level)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        prompt = f"""Branch: {branch}\nLevel: {level}\nQuestion: {question}\nCandidate answer: {answer}\n
Evaluate this interview answer. Return ONLY valid JSON with integer 0-100 values for score, correctness, clarity, structure, depth, confidence; arrays strengths and weaknesses; strings feedback and follow_up. Be rigorous but constructive. The follow_up must probe a weak area or increase difficulty when the answer is strong."""
        resp = client.responses.create(model=os.getenv("NEXA_AI_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini", input=[
            {"role":"system","content":"You are NEXA Interview AI, an adaptive human-like technical interviewer and coach."},
            {"role":"user","content":prompt}
        ])
        data=json.loads(resp.output_text.strip())
        for k in ["score","correctness","clarity","structure","depth","confidence"]:
            data[k]=max(0,min(100,int(float(data.get(k,0)))))
        data.setdefault("strengths",[]); data.setdefault("weaknesses",[]); data.setdefault("feedback",""); data.setdefault("follow_up","")
        return data
    except Exception:
        return local_evaluate(question, answer, branch, level)


def ai_grade(question, answer, branch, level):
    d=ai_evaluate(question, answer, branch, level)
    return d["score"], d["feedback"] + (f" Strengths: {', '.join(d['strengths'])}." if d.get('strengths') else "") + (f" Improve: {', '.join(d['weaknesses'])}." if d.get('weaknesses') else "")


def next_level(level, score):
    idx=LEVELS.index(level) if level in LEVELS else 0
    if score >= 82: return LEVELS[min(idx+1, len(LEVELS)-1)]
    if score < 55: return LEVELS[max(idx-1, 0)]
    return level


def build_report_pdf(interview, answers):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen.canvas import Canvas
    out = io.BytesIO(); p = Canvas(out, pagesize=A4); y = 800
    p.setFont("Helvetica-Bold", 18); p.drawString(50, y, "NEXA Interview Performance Report"); y -= 30
    p.setFont("Helvetica", 10); p.drawString(50, y, f"Candidate: {interview['name']} | Score: {interview['score']:.0f}/100"); y -= 16
    p.drawString(50, y, f"{interview['branch']} | {interview['level']} | {interview['mode']}"); y -= 28
    for n, x in enumerate(answers, 1):
        if y < 115: p.showPage(); y = 800
        p.setFont("Helvetica-Bold", 10); p.drawString(50, y, f"{n}. {x['question'][:105]}"); y -= 15
        p.setFont("Helvetica", 9); p.drawString(60, y, f"Score: {x['score']:.0f}/100 — {x['feedback'][:125]}"); y -= 15
        answer = (x['answer'] or "No answer provided.").replace("\n", " ")
        p.drawString(60, y, f"Answer: {answer[:145]}"); y -= 24
    p.save(); out.seek(0); return out




@app.after_request
def performance_headers(response):
    if request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=31536000"
    if response.mimetype == "text/html":
        response.headers.setdefault("Cache-Control", "no-cache")
    return response

@app.context_processor
def ctx(): return {"me": me(), "is_master": master(), "branches": BRANCHES, "levels": LEVELS, "modes": MODES}


@app.route("/")
def home(): return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        account_type = request.form.get("account_type", "student")
        name = request.form.get("name", "").strip(); email = request.form.get("email", "").strip().lower(); pw = request.form.get("password", "")
        invite = request.form.get("invite_code", "").strip(); department = request.form.get("department", "").strip(); designation = request.form.get("designation", "").strip(); university = request.form.get("university", "").strip(); faculty_id = request.form.get("faculty_id", "").strip()
        if not name or "@" not in email or len(pw) < 8:
            flash("Use a valid name/email and an 8+ character password.", "error"); return redirect(url_for("register"))
        c = db()
        if c.execute("SELECT 1 FROM users WHERE lower(email)=lower(?)", (email,)).fetchone():
            c.close(); flash("Email already registered.", "error"); return redirect(url_for("login"))
        if account_type == "admin":
            c.execute("INSERT INTO users(email,name,password_hash,role,approved,email_verified,created_at) VALUES(?,?,?,?,?,?,?)", (email,name,generate_password_hash(pw),"admin",1,0,now()))
            uid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
            c.execute("INSERT INTO admins(user_id,department,created_at) VALUES(?,?,?)", (uid,department,now()))
            c.execute("INSERT INTO admin_profiles(user_id,department,designation,university,faculty_id,created_at) VALUES(?,?,?,?,?,?)", (uid,department,designation,university,faculty_id,now()))
            c.commit(); c.close(); session["pending"] = email; otp(email); return redirect(url_for("verify"))
        sec = c.execute("SELECT * FROM sections WHERE upper(invite_code)=upper(?)", (invite,)).fetchone() if invite else None
        if invite and not sec:
            c.close(); flash("That Join Code is invalid or expired.", "error"); return redirect(url_for("register"))
        c.execute("INSERT INTO users(email,name,password_hash,section_id,approved,created_at) VALUES(?,?,?,?,?,?)", (email,name,generate_password_hash(pw),sec["id"] if sec else None,1 if sec else 1,now()))
        c.commit(); c.close(); session["pending"] = email; otp(email); return redirect(url_for("verify"))
    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        account_type = request.form.get("account_type", "student")
        join_code = request.form.get("join_code", "").strip().upper()
        c = db()

        if account_type == "admin" and master_credentials_ok(c, email, password):
            start_master_session(c, email, password); c.close(); return redirect(url_for("master_page"))

        user = c.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (email,)).fetchone()
        join_code = request.form.get("join_code", "").strip().upper()
        if account_type == "student" and user and user["role"] == "student" and join_code:
            section_row = c.execute("SELECT * FROM sections WHERE upper(invite_code)=?", (join_code,)).fetchone()
            if not section_row:
                c.close(); flash("Invalid Student Join Code. Ask your Admin / Faculty for the current code.", "error"); return redirect(url_for("login"))
            if not check_password_hash(user["password_hash"], password):
                c.close(); flash("Incorrect email or password.", "error"); return redirect(url_for("login"))
            c.execute("UPDATE users SET section_id=?, approved=1 WHERE id=?", (section_row["id"], user["id"]))
            c.commit()
            user = c.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
        if not user or user["role"] not in ("student", "admin", "master") or not check_password_hash(user["password_hash"], password):
            c.close(); flash("Incorrect email or password.", "error"); return redirect(url_for("login"))
        if account_type == "admin" and user["role"] != "admin":
            c.close(); flash("This account is not an Admin / Faculty account.", "error"); return redirect(url_for("login"))
        if account_type == "student" and user["role"] != "student":
            c.close(); flash("This account is not a User / Student account.", "error"); return redirect(url_for("login"))

        # Student Join Code: the student account must already exist. The code is
        # generated by Admin/Faculty when they create a section.
        if account_type == "student" and join_code:
            sec = c.execute("SELECT * FROM sections WHERE upper(invite_code)=upper(?)", (join_code,)).fetchone()
            if not sec:
                c.close(); flash("Invalid Join Code. Ask your Admin/Faculty for the current code.", "error"); return redirect(url_for("login"))
            if user["section_id"] and user["section_id"] != sec["id"]:
                c.close(); flash("This student account is already linked to another section.", "error"); return redirect(url_for("login"))
            c.execute("UPDATE users SET section_id=?, approved=1 WHERE id=?", (sec["id"], user["id"]))
            c.commit(); user = c.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
            flash(f"Joined {sec['name']} successfully.", "success")

        if not user["email_verified"]:
            c.close(); session["pending"] = email; flash("Please verify your email first.", "info"); return redirect(url_for("verify"))
        if not user["approved"]:
            c.close(); flash("Your class account is waiting for Admin approval. Or enter a valid Join Code.", "info"); return redirect(url_for("login"))
        c.close(); session.clear(); session["uid"] = user["id"]; session["user_id"] = user["id"]; session["role"] = user["role"]
        return redirect(url_for("admin" if user["role"] == "admin" else "dashboard"))
    return render_template("auth.html", mode="login")


@app.route("/request-login-otp", methods=["POST"])
def request_login_otp():
    email=request.form.get("email","").strip().lower()
    user=get_user_by_email(email)
    # Same response regardless of account existence.
    if user and user["role"] in ("student","admin","master"):
        otp(email,"login")
    session["login_otp_email"]=email
    flash("If the account is eligible, a login OTP has been sent.","info")
    return redirect(url_for("login_otp_page"))

@app.route("/verify-login-otp", methods=["POST"])
def verify_login_otp():
    email=session.get("login_otp_email","").strip().lower(); code=request.form.get("code","").strip()
    c=db(); r=c.execute("SELECT * FROM otp_codes WHERE email=? AND purpose='login' AND used=0 ORDER BY id DESC LIMIT 1",(email,)).fetchone()
    ok=bool(r and datetime.fromisoformat(r["expires_at"])>datetime.now() and check_password_hash(r["code_hash"],code))
    if not ok:
        c.close(); flash("Invalid or expired OTP.","error"); return redirect(url_for("login_otp_page"))
    u=c.execute("SELECT * FROM users WHERE lower(email)=?",(email,)).fetchone(); c.execute("UPDATE otp_codes SET used=1 WHERE id=?",(r["id"],)); c.commit(); c.close()
    if not u or not u["email_verified"] or not u["approved"]:
        flash("Account verification or approval is required.","error"); return redirect(url_for("login",otp=1))
    session.clear(); session["uid"]=u["id"]; session["user_id"]=u["id"]; session["role"]=u["role"]
    return redirect(url_for("master_page" if u["role"]=="master" else "admin" if u["role"]=="admin" else "dashboard"))

@app.route("/nexa-core-access", methods=["GET", "POST"])
def master_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower(); password = request.form.get("password", "")
        c = db()
        if master_credentials_ok(c, email, password):
            start_master_session(c, email, password); c.close(); return redirect(url_for("master_page"))
        c.close(); flash("Master email or password is incorrect. Use the built-in credentials from your existing .env or a Master account created in the console.", "error")
    return render_template("master_login.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = get_user_by_email(email)
        if not user or user["role"] not in ("student", "admin", "master"):
            flash("If that User/Admin email exists, a reset code has been sent.", "info"); return redirect(url_for("forgot_password"))
        session["reset_pending"] = email
        otp(email, "reset")
        flash("A password reset code has been sent to your Gmail/email.", "success")
        return redirect(url_for("reset_password"))
    return render_template("forgot_password.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    email = session.get("reset_pending")
    if not email: return redirect(url_for("forgot_password"))
    if request.method == "POST":
        code = request.form.get("code", "").strip(); new_password = request.form.get("password", "")
        if len(new_password) < 8:
            flash("Password must be at least 8 characters.", "error"); return redirect(url_for("reset_password"))
        c = db(); r = c.execute("SELECT * FROM otp_codes WHERE email=? AND purpose='reset' AND used=0 ORDER BY id DESC LIMIT 1", (email,)).fetchone()
        ok = bool(r and datetime.fromisoformat(r["expires_at"]) > datetime.now() and check_password_hash(r["code_hash"], code))
        if ok:
            c.execute("UPDATE otp_codes SET used=1 WHERE id=?", (r["id"],)); c.execute("UPDATE users SET password_hash=? WHERE lower(email)=lower(?) AND role IN ('student','admin','master')", (generate_password_hash(new_password), email)); c.commit(); c.close(); session.pop("reset_pending", None); flash("Password reset successfully. You can now sign in.", "success"); return redirect(url_for("login"))
        c.close(); flash("Invalid or expired reset code.", "error")
    return render_template("reset_password.html", email=email)

@app.route("/verify", methods=["GET", "POST"])
def verify():
    email = session.get("pending")
    if not email: return redirect(url_for("login"))
    if request.method == "POST":
        code = request.form.get("code", ""); c = db(); r = c.execute("SELECT * FROM otp_codes WHERE email=? AND purpose='verify' AND used=0 ORDER BY id DESC LIMIT 1", (email,)).fetchone()
        ok = r and datetime.fromisoformat(r["expires_at"]) > datetime.now() and check_password_hash(r["code_hash"], code)
        if ok:
            c.execute("UPDATE otp_codes SET used=1 WHERE id=?", (r["id"],)); c.execute("UPDATE users SET email_verified=1 WHERE email=?", (email,)); c.commit(); u = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone(); c.close(); session.pop("pending", None); session["uid"] = u["id"]; session["role"] = u["role"]; return redirect(url_for("admin" if u["role"] == "admin" else "dashboard"))
        c.close(); flash("Invalid or expired code.", "error")
    return render_template("otp.html", email=email)


@app.route("/resend")
def resend():
    if session.get("pending"): otp(session["pending"]); flash("Fresh code sent.", "success")
    return redirect(url_for("verify"))


@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("home"))


@app.route("/dashboard")
@req
def dashboard():
    user = me()
    c = db()
    stats = [
        c.execute("SELECT COUNT(*) FROM interviews WHERE user_id=?", (user["id"],)).fetchone()[0],
        c.execute("SELECT COALESCE(AVG(score),0) FROM interviews WHERE user_id=? AND completed_at IS NOT NULL", (user["id"],)).fetchone()[0],
        c.execute("SELECT COUNT(*) FROM resumes WHERE user_id=?", (user["id"],)).fetchone()[0],
    ]
    recent = c.execute("SELECT * FROM interviews WHERE user_id=? ORDER BY id DESC LIMIT 6", (user["id"],)).fetchall()
    section = c.execute("SELECT s.* FROM sections s JOIN users u ON u.section_id=s.id WHERE u.id=?", (user["id"],)).fetchone()
    latest_resume = c.execute(
        "SELECT id,filename,ats_score,ats_checked_at,created_at FROM resumes WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (user["id"],),
    ).fetchone()
    c.close()
    return render_template("dashboard.html", stats=stats, recent=recent, section=section, latest_resume=latest_resume)


@app.route("/student/join", methods=["POST"])
@role("student")
def student_join():
    code = request.form.get("join_code", "").strip().upper()
    if not code:
        flash("Enter the Student Join Code from your Admin / Faculty.", "error")
        return redirect(url_for("dashboard"))
    c = db(); section_row = c.execute("SELECT * FROM sections WHERE upper(invite_code)=?", (code,)).fetchone()
    if not section_row:
        c.close(); flash("That Join Code is invalid. Check the code and try again.", "error"); return redirect(url_for("dashboard"))
    current_section = c.execute("SELECT section_id FROM users WHERE id=?", (me()["id"],)).fetchone()
    if current_section["section_id"] and current_section["section_id"] != section_row["id"]:
        c.close(); flash("Your account is already linked to another section.", "error"); return redirect(url_for("dashboard"))
    c.execute("UPDATE users SET section_id=?, approved=1 WHERE id=?", (section_row["id"], me()["id"]))
    c.execute("INSERT INTO audit_logs(actor,action,target,created_at) VALUES(?,?,?,?)", (me()["email"], "student joined section", section_row["name"], now()))
    c.commit(); c.close(); flash(f"Joined {section_row['name']} successfully.", "success"); return redirect(url_for("dashboard"))


@app.route("/resume", methods=["GET", "POST"])
@req
def resume():
    if request.method == "POST":
        f = request.files.get("resume")
        if not f or not f.filename or not f.filename.lower().endswith(".pdf"):
            flash("Please upload a PDF.", "error")
            return redirect(url_for("resume"))
        data = f.read()
        text = pdf_text(data)
        if not text.strip():
            flash("We couldn't read text from that PDF. Please upload a readable resume.", "error")
            return redirect(url_for("resume"))
        score, feedback = ats(text)
        checked_at = now()
        c = db()
        c.execute(
            "INSERT INTO resumes(user_id,filename,file_data,extracted_text,ats_score,feedback,created_at,ats_checked_at) VALUES(?,?,?,?,?,?,?,?)",
            (me()["id"], f.filename, data, text, score, feedback, checked_at, checked_at),
        )
        c.commit()
        c.close()
        flash(f"Resume stored. ATS score: {score}/100.", "success")
        return redirect(url_for("resume"))
    c = db()
    rows = [dict(row) for row in c.execute("SELECT * FROM resumes WHERE user_id=? ORDER BY id DESC", (me()["id"],)).fetchall()]
    c.close()
    for row in rows:
        ats_feedback = json.loads(row["feedback"] or "{}")
        row["matched_skills"] = ats_feedback.get("matched_skills", [])
        row["suggestion"] = ats_feedback.get("suggestion", "")
    return render_template("resume.html", rows=rows)


@app.route("/resume/<int:rid>/recheck", methods=["POST"])
@req
def resume_recheck(rid):
    c = db()
    row = c.execute("SELECT * FROM resumes WHERE id=? AND user_id=?", (rid, me()["id"])).fetchone()
    if not row:
        c.close()
        abort(404)
    text = pdf_text(row["file_data"])
    if not text.strip():
        c.close()
        flash("We couldn't read text from this stored PDF, so its ATS score was not changed.", "error")
        return redirect(url_for("resume"))
    score, feedback = ats(text)
    checked_at = now()
    c.execute(
        "UPDATE resumes SET extracted_text=?,ats_score=?,feedback=?,ats_checked_at=? WHERE id=? AND user_id=?",
        (text, score, feedback, checked_at, rid, me()["id"]),
    )
    c.commit()
    c.close()
    flash(f"ATS score checked again: {score}/100.", "success")
    return redirect(url_for("resume"))


@app.route("/resume/<int:rid>")
@req
def resume_file(rid):
    c = db(); r = c.execute("SELECT * FROM resumes WHERE id=? AND user_id=?", (rid,me()["id"])).fetchone(); c.close()
    if not r: abort(404)
    return send_file(io.BytesIO(r["file_data"]), download_name=r["filename"], as_attachment=True)


@app.route("/interview", methods=["GET", "POST"])
@role("student")
def interview():
    if request.method == "POST":
        practice_type = request.form.get("practice_type", "creator")
        c = db()
        if practice_type == "solo":
            branch = request.form.get("branch", "")
            level = request.form.get("level", "")
            interview_mode = request.form.get("mode", "")
            strict_mode = 1 if request.form.get("strict") else 0
            if branch not in BRANCHES or level not in LEVELS or interview_mode not in MODES:
                c.close()
                flash("Choose a valid branch, difficulty and interview mode.", "error")
                return redirect(url_for("interview"))
            creator_id = None
            access_code_id = None
            code = ""
        elif practice_type == "creator":
            code = request.form.get("interview_code", "").strip().upper()
            if not code:
                c.close()
                flash("Enter the Interview Access Code provided by your Creator.", "error")
                return redirect(url_for("interview"))
            ic = c.execute("SELECT * FROM interview_codes WHERE upper(code)=? AND disabled=0", (code,)).fetchone()
            if not ic:
                c.close()
                flash("Invalid or disabled interview code.", "error")
                return redirect(url_for("interview"))
            membership = c.execute(
                "SELECT a.user_id AS creator_id FROM users u JOIN sections s ON s.id=u.section_id JOIN admins a ON a.id=s.admin_id WHERE u.id=?",
                (me()["id"],),
            ).fetchone()
            if not membership or membership["creator_id"] != ic["creator_id"]:
                c.close()
                flash("Join the section belonging to this Creator before using their interview code.", "error")
                return redirect(url_for("interview"))
            branch = ic["branch"]
            level = ic["level"]
            interview_mode = ic["mode"]
            strict_mode = ic["strict_mode"]
            creator_id = ic["creator_id"]
            access_code_id = ic["id"]
        else:
            c.close()
            flash("Choose a valid interview option.", "error")
            return redirect(url_for("interview"))
        qs = c.execute(
            "SELECT * FROM questions WHERE is_self_intro=1 OR (branch=? AND level=?) ORDER BY CASE WHEN is_self_intro=1 THEN 0 ELSE 1 END, RANDOM() LIMIT 10",
            (branch, level),
        ).fetchall()
        if not qs:
            c.close()
            flash("No questions are configured for this interview.", "error")
            return redirect(url_for("interview"))
        c.execute(
            "INSERT INTO interviews(user_id,creator_id,access_code_id,branch,level,mode,strict_mode,started_at) VALUES(?,?,?,?,?,?,?,?)",
            (me()["id"], creator_id, access_code_id, branch, level, interview_mode, strict_mode, now()),
        )
        iid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
        c.commit()
        c.close()
        session["iid"] = iid
        session["qs"] = [dict(question) for question in qs]
        session["interview_mode"] = interview_mode
        session["strict_mode"] = strict_mode
        if code:
            session["access_code"] = code
        else:
            session.pop("access_code", None)
        return redirect(url_for("take"))
    c = db()
    section = c.execute(
        "SELECT s.name FROM users u JOIN sections s ON s.id=u.section_id JOIN admins a ON a.id=s.admin_id WHERE u.id=?",
        (me()["id"],),
    ).fetchone()
    c.close()
    return render_template("interview_setup.html", section=section)

@app.route("/creator/interview", methods=["POST"])
@role("admin")
def creator_interview():
    if not has_permission(me()["id"], "create_interviews"): abort(403)
    branch=request.form.get("branch",""); level=request.form.get("level",""); mode=request.form.get("mode",""); strict=1 if request.form.get("strict") else 0
    if branch not in BRANCHES or level not in LEVELS or mode not in MODES:
        flash("Choose a valid interview configuration.","error"); return redirect(url_for("admin"))
    c=db(); creator=me()["id"]
    while True:
        code=secrets.token_hex(4).upper()
        if not c.execute("SELECT 1 FROM interview_codes WHERE code=?",(code,)).fetchone(): break
    c.execute("INSERT INTO interview_codes(code,creator_id,branch,level,mode,strict_mode,created_at) VALUES(?,?,?,?,?,?,?)",(code,creator,branch,level,mode,strict,now()))
    c.execute("INSERT INTO audit_logs(actor,action,target,created_at) VALUES(?,?,?,?)",(me()["email"],"create interview access code",code,now())); c.commit(); c.close()
    flash(f"Interview created. Permanent access code: {code}","success"); return redirect(url_for("admin"))

@app.route("/creator/interview/<int:code_id>/disable", methods=["POST"])
@role("admin")
def creator_disable_interview(code_id):
    c=db(); c.execute("UPDATE interview_codes SET disabled=1 WHERE id=? AND creator_id=?",(code_id,me()["id"])); c.commit(); c.close(); flash("Interview code disabled.","success"); return redirect(url_for("admin"))

@app.route("/interview/take", methods=["GET", "POST"])
@req
def take():
    iid = session.get("iid"); qs = session.get("qs")
    if not iid or not qs: return redirect(url_for("interview"))
    c0=db(); active=c0.execute("SELECT * FROM interviews WHERE id=? AND user_id=? AND completed_at IS NULL",(iid,me()["id"])).fetchone(); c0.close()
    if not active: session.pop("iid",None); session.pop("qs",None); return redirect(url_for("interview"))
    if request.method == "POST":
        c = db(); scores = []
        submitted = [dict(q) for q in qs]
        for raw_id in request.form.getlist("adaptive_question_id"):
            try: qid=int(raw_id)
            except (TypeError,ValueError): continue
            qrow=c.execute("SELECT * FROM questions WHERE id=?",(qid,)).fetchone()
            if qrow: submitted.append(dict(qrow))
        seen=set()
        for q in submitted:
            if q["id"] in seen: continue
            seen.add(q["id"])
            a = request.form.get(f"a{q['id']}", ""); evaluation = ai_evaluate(q["question"], a, q["branch"], q["level"]); s = evaluation["score"]; fb = evaluation.get("feedback", ""); scores.append(float(s))
            c.execute("INSERT INTO answers(interview_id,question_id,answer,score,feedback) VALUES(?,?,?,?,?)", (iid,q["id"],a,s,fb))
            aid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
            c.execute("INSERT OR REPLACE INTO answer_metrics(answer_id,correctness,clarity,structure,depth,confidence,follow_up,created_at) VALUES(?,?,?,?,?,?,?,?)", (aid,evaluation.get("correctness",0),evaluation.get("clarity",0),evaluation.get("structure",0),evaluation.get("depth",0),evaluation.get("confidence",0),evaluation.get("follow_up", ""),now()))
        overall = round(statistics.mean(scores)) if scores else 0; strengths = sum(1 for s in scores if s >= 75); weaknesses = sum(1 for s in scores if s < 60)
        summary = f"Overall {overall}/100. Strong responses: {strengths}. Responses needing improvement: {weaknesses}. NEXA evaluated correctness, clarity, structure, depth and confidence, with adaptive follow-ups where applicable."
        c.execute("UPDATE interviews SET score=?,feedback=?,completed_at=? WHERE id=?", (overall,summary,now(),iid)); c.commit()
        interview_row = c.execute("SELECT i.*,u.name,u.email FROM interviews i JOIN users u ON u.id=i.user_id WHERE i.id=?", (iid,)).fetchone(); answers = c.execute("SELECT a.*,q.question FROM answers a JOIN questions q ON q.id=a.question_id WHERE a.interview_id=?", (iid,)).fetchall(); pdf = build_report_pdf(interview_row, answers); c.execute("INSERT INTO reports(user_id,interview_id,title,report_data,summary,created_at) VALUES(?,?,?,?,?,?)", (me()["id"],iid,"NEXA Interview Performance Report",pdf.getvalue(),summary,now())); c.commit(); c.close(); session.pop("iid",None); session.pop("qs",None); session.pop("interview_mode",None); session.pop("strict_mode",None); return redirect(url_for("result", iid=iid))
    return render_template("take.html", questions=qs, mode=session.get("interview_mode", "Text + typing"), strict=bool(session.get("strict_mode")))


@app.route("/api/behavior-event", methods=["POST"])
@req
def behavior_event():
    data=request.get_json(silent=True) or {}; iid=int(data.get("interview_id") or session.get("iid") or 0); event=str(data.get("event_type","")).strip()[:80]
    if not iid or not event: return jsonify(error="Invalid event."),400
    c=db(); ok=c.execute("SELECT 1 FROM interviews WHERE id=? AND user_id=? AND completed_at IS NULL",(iid,me()["id"])).fetchone()
    if not ok: c.close(); return jsonify(error="Invalid interview session."),403
    c.execute("INSERT INTO behavioral_events(interview_id,event_type,event_data,created_at) VALUES(?,?,?,?)",(iid,event,json.dumps(data.get("data",{}))[:2000],now())); c.commit(); c.close(); return jsonify(ok=True)

@app.route("/api/evaluate-answer", methods=["POST"])
@req
def evaluate_answer_api():
    data=request.get_json(silent=True) or {}
    question=str(data.get("question", "")).strip()
    answer=str(data.get("answer", "")).strip()
    branch=str(data.get("branch", "")).strip()
    level=str(data.get("level", "Beginner")).strip()
    if not question or not branch or not answer:
        return jsonify(error="Question and answer are required."), 400
    result=ai_evaluate(question, answer, branch, level)
    result["next_level"]=next_level(level, result["score"])
    return jsonify(result)


@app.route("/api/adaptive-question", methods=["POST"])
@req
def adaptive_question_api():
    data=request.get_json(silent=True) or {}
    question=str(data.get("question", "")).strip()
    answer=str(data.get("answer", "")).strip()
    branch=str(data.get("branch", "")).strip()
    level=str(data.get("level", "Beginner")).strip()
    score=float(data.get("score", 0) or 0)
    if not question or not branch or not answer:
        return jsonify(error="Question, answer and branch are required."), 400
    evaluation=ai_evaluate(question, answer, branch, level)
    follow=evaluation.get("follow_up") or ("Explain your reasoning with a practical example and one limitation." if score < 80 else "Design a production-scale version and discuss trade-offs and failure cases.")
    follow_level=next_level(level, score)
    c=db(); c.execute("INSERT INTO questions(branch,level,question,created_at) VALUES(?,?,?,?)", (branch,follow_level,follow,now())); qid=c.execute("SELECT last_insert_rowid()").fetchone()[0]; c.commit(); c.close()
    return jsonify(question=follow, level=follow_level, score=score, question_id=qid)


@app.route("/profile")
@req
def performance_profile():
    c=db(); rows=c.execute("SELECT a.score,m.correctness,m.clarity,m.structure,m.depth,m.confidence,i.branch,i.level FROM answers a JOIN interviews i ON i.id=a.interview_id LEFT JOIN answer_metrics m ON m.answer_id=a.id WHERE i.user_id=? ORDER BY a.id DESC LIMIT 100",(me()["id"],)).fetchall(); c.close()
    total=len(rows); avg=round(statistics.mean([float(r["score"] or 0) for r in rows])) if rows else 0
    def metric(name):
        vals=[float(r[name]) for r in rows if r[name] is not None]
        return round(statistics.mean(vals)) if vals else avg
    buckets={"Technical depth":metric("depth"),"Clarity":metric("clarity"),"Structure":metric("structure"),"Correctness":metric("correctness"),"Confidence":metric("confidence")}
    return render_template("profile.html",total=total,avg=avg,buckets=buckets)


@app.route("/result/<int:iid>")
@req
def result(iid):
    c = db(); i = c.execute("SELECT * FROM interviews WHERE id=? AND user_id=?", (iid,me()["id"])).fetchone(); a = c.execute("SELECT a.*,q.question FROM answers a JOIN questions q ON q.id=a.question_id WHERE a.interview_id=?", (iid,)).fetchall(); c.close()
    if not i: abort(404)
    return render_template("result.html", interview=i, answers=a)


@app.route("/report/<int:iid>")
@req
def report(iid):
    c = db(); r = c.execute("SELECT * FROM reports WHERE interview_id=? AND user_id=? ORDER BY id DESC LIMIT 1", (iid,me()["id"])).fetchone(); c.close()
    if not r: abort(404)
    return send_file(io.BytesIO(r["report_data"]), download_name=f"nexa-report-{iid}.pdf", as_attachment=True)


@app.route("/admin")
@role("admin")
def admin():
    c = db(); a = c.execute("SELECT * FROM admins WHERE user_id=?", (me()["id"],)).fetchone()
    if not a: abort(403)
    profile = c.execute("SELECT * FROM admin_profiles WHERE user_id=?", (me()["id"],)).fetchone(); sections = c.execute("SELECT * FROM sections WHERE admin_id=?", (a["id"],)).fetchall(); students = c.execute("SELECT u.*,s.name section_name FROM users u LEFT JOIN sections s ON s.id=u.section_id WHERE s.admin_id=?", (a["id"],)).fetchall(); codes = c.execute("SELECT * FROM interview_codes WHERE creator_id=? ORDER BY id DESC", (me()["id"],)).fetchall(); c.close(); return render_template("admin.html", sections=sections, students=students, profile=profile, codes=codes)


@app.route("/admin/section", methods=["POST"])
@role("admin")
def section():
    c = db(); a = c.execute("SELECT id FROM admins WHERE user_id=?", (me()["id"],)).fetchone(); code = secrets.token_urlsafe(7).upper(); c.execute("INSERT INTO sections(admin_id,name,invite_code,created_at) VALUES(?,?,?,?)", (a["id"],request.form["name"],code,now())); c.commit(); c.close(); flash(f"Section created. Student Join Code: {code}", "success"); return redirect(url_for("admin"))


@app.route("/admin/approve/<int:uid>", methods=["POST"])
@role("admin")
def approve(uid):
    c = db(); a = c.execute("SELECT id FROM admins WHERE user_id=?", (me()["id"],)).fetchone(); c.execute("UPDATE users SET approved=1 WHERE id=? AND section_id IN (SELECT id FROM sections WHERE admin_id=?)", (uid,a["id"])); c.commit(); c.close(); return redirect(url_for("admin"))


@app.route("/admin/question", methods=["POST"])
@role("admin")
def admin_question():
    if not has_permission(me()["id"], "manage_questions"): abort(403)
    branch=request.form.get("branch"); level=request.form.get("level"); question=request.form.get("question","").strip()
    if branch not in BRANCHES or level not in LEVELS or not question:
        flash("Choose a valid branch, level and question.","error"); return redirect(url_for("admin"))
    c=db(); c.execute("INSERT INTO questions(branch,level,question,created_at) VALUES(?,?,?,?)",(branch,level,question,now())); c.execute("INSERT INTO audit_logs(actor,action,target,created_at) VALUES(?,?,?,?)",(me()["email"],"admin add question",question,now())); c.commit(); c.close(); flash("Question added to the shared question bank.","success"); return redirect(url_for("admin"))


@app.route("/creator")
@role("admin")
def creator_page():
    return redirect(url_for("admin"))

@app.route("/master")
@req
def master_page():
    if not master(): abort(403)
    c = db(); tables = {n:c.execute(f"SELECT * FROM {n} ORDER BY id DESC").fetchall() for n in ["users","admins","admin_profiles","master_admins","creator_permissions","interview_codes","answer_metrics","sections","questions","resumes","interviews","reports","audit_logs"]}; counts = {b:c.execute("SELECT COUNT(*) FROM questions WHERE branch=?",(b,)).fetchone()[0] for b in BRANCHES}; creators=c.execute("SELECT u.id,u.name,u.email,COALESCE(ap.department,'') department FROM users u LEFT JOIN admin_profiles ap ON ap.user_id=u.id WHERE u.role='admin' ORDER BY u.id DESC").fetchall(); c.close(); return render_template("master.html", tables=tables, counts=counts, creators=creators)


@app.route("/master/create", methods=["POST"])
@req
def master_create():
    if not master(): abort(403)
    kind = request.form.get("kind", "student"); name = request.form.get("name", "").strip(); email = request.form.get("email", "").strip().lower(); password = request.form.get("password", ""); department = request.form.get("department", "").strip(); designation = request.form.get("designation", "").strip(); university = request.form.get("university", "").strip(); faculty_id = request.form.get("faculty_id", "").strip()
    if not name or "@" not in email or len(password) < 8: flash("Use a valid name/email and an 8+ character password.", "error"); return redirect(url_for("master_page"))
    c = db()
    if c.execute("SELECT 1 FROM users WHERE lower(email)=?", (email,)).fetchone(): c.close(); flash("That email already has an account.", "error"); return redirect(url_for("master_page"))
    if kind == "master":
        c.execute("DELETE FROM master_revocations WHERE lower(email)=?", (email,))
        c.execute("INSERT INTO users(email,name,password_hash,role,approved,email_verified,created_at) VALUES(?,?,?,?,?,?,?)", (email,name,generate_password_hash(password),"master",1,1,now())); c.execute("INSERT INTO master_admins(email,created_at,password_hash,name,role_label) VALUES(?,?,?,?,?)", (email,now(),generate_password_hash(password),name,"Master"))
    elif kind == "admin":
        c.execute("INSERT INTO users(email,name,password_hash,role,approved,email_verified,created_at) VALUES(?,?,?,?,?,?,?)", (email,name,generate_password_hash(password),"admin",1,1,now())); uid=c.execute("SELECT last_insert_rowid()").fetchone()[0]; c.execute("INSERT INTO admins(user_id,department,created_at) VALUES(?,?,?)",(uid,department,now())); c.execute("INSERT INTO admin_profiles(user_id,department,designation,university,faculty_id,created_at) VALUES(?,?,?,?,?,?)",(uid,department,designation,university,faculty_id,now()))
    else:
        c.execute("INSERT INTO users(email,name,password_hash,role,approved,email_verified,created_at) VALUES(?,?,?,?,?,?,?)", (email,name,generate_password_hash(password),"student",1,1,now()))
    c.execute("INSERT INTO audit_logs(actor,action,target,created_at) VALUES(?,?,?,?)", (me()["email"],f"create {kind}",email,now())); c.commit(); c.close(); flash(f"{kind.title()} account created successfully.","success"); return redirect(url_for("master_page"))


@app.route("/master/permissions", methods=["POST"])
@req
def master_permissions():
    if not master(): abort(403)
    try: creator_id=int(request.form.get("creator_id", "0"))
    except ValueError: abort(400)
    allowed={"create_interviews","manage_questions","manage_learners","view_results","export_reports"}
    selected=set(request.form.getlist("permission")) & allowed
    c=db(); c.execute("DELETE FROM creator_permissions WHERE creator_id=?",(creator_id,))
    for perm in allowed: c.execute("INSERT INTO creator_permissions(creator_id,permission,enabled) VALUES(?,?,?)",(creator_id,perm,1 if perm in selected else 0))
    c.execute("INSERT INTO audit_logs(actor,action,target,created_at) VALUES(?,?,?,?)",(me()["email"],"update creator permissions",str(creator_id),now())); c.commit(); c.close(); flash("Creator permissions updated.","success"); return redirect(url_for("master_page"))

@app.route("/master/question", methods=["POST"])
@req
def add_question():
    if not master(): abort(403)
    branch=request.form.get("branch"); level=request.form.get("level"); question=request.form.get("question","").strip()
    if branch not in BRANCHES or level not in LEVELS or not question: flash("Choose a valid branch and level.","error"); return redirect(url_for("master_page"))
    c=db(); c.execute("INSERT INTO questions(branch,level,question,created_at) VALUES(?,?,?,?)",(branch,level,question,now())); c.execute("INSERT INTO audit_logs(actor,action,target,created_at) VALUES(?,?,?,?)",(me()["email"],"add question",question,now())); c.commit(); c.close(); return redirect(url_for("master_page"))


@app.route("/master/delete/<table>/<int:rid>", methods=["POST"])
@req
def delete_row(table,rid):
    if not master() or table not in {"questions","resumes","reports","interviews","users","sections","admins","admin_profiles","master_admins","answer_metrics"}: abort(403)
    c=db()
    if table == "master_admins":
        row=c.execute("SELECT * FROM master_admins WHERE id=?",(rid,)).fetchone()
        if row:
            email=row["email"].lower()
            c.execute("INSERT OR IGNORE INTO master_revocations(email,revoked_at) VALUES(?,?)",(email,now()))
            c.execute("DELETE FROM master_admins WHERE id=?",(rid,))
            c.execute("DELETE FROM users WHERE lower(email)=? AND role='master'",(email,))
    elif table == "users":
        row=c.execute("SELECT * FROM users WHERE id=?",(rid,)).fetchone()
        if not row:
            c.close(); flash("That user account no longer exists.", "error"); return redirect(url_for("master_page"))
        if row["id"] == me()["id"]:
            c.close(); flash("The signed-in Master account cannot remove itself.", "error"); return redirect(url_for("master_page"))
        target = row["email"]
        if row["role"] == "master":
            c.execute("INSERT OR IGNORE INTO master_revocations(email,revoked_at) VALUES(?,?)",(target.lower(),now()))
            c.execute("DELETE FROM master_admins WHERE lower(email)=?",(target.lower(),))
        c.execute("DELETE FROM users WHERE id=?",(rid,))
    elif table in {"admins","admin_profiles"}:
        row=c.execute(f"SELECT user_id FROM {table} WHERE id=?",(rid,)).fetchone()
        if row: c.execute("DELETE FROM users WHERE id=?",(row["user_id"],))
    else:
        c.execute(f"DELETE FROM {table} WHERE id=?",(rid,))
    c.execute("INSERT INTO audit_logs(actor,action,target,created_at) VALUES(?,?,?,?)",(me()["email"],f"delete {table}",target if table == "users" else str(rid),now())); c.commit(); c.close()
    if table == "users": flash("User account and associated data removed.", "success")
    return redirect(url_for("master_page"))


@app.route("/help", methods=["POST"])
@req
def help_api():
    q=request.json.get("question","").lower(); ans="I can help with OTP, resumes, interviews, branches, voice/video mode, sections, Admin access and reports."
    for k,v in {"otp":"Use the latest six-digit code sent to your email. It expires after 10 minutes.","resume":"Upload a PDF on Resume ATS. The file, extracted text and analysis are stored with your account.","interview":"Choose one of the six NEXA branches, a level and Text, Voice or Video mode. Strict mode is designed to make the session exam-like.","voice":"Voice mode uses your browser speech tools and microphone permission.","video":"Video mode requests camera and microphone access and shows the NEXA AI interviewer.","admin":"Admin/Faculty accounts can register normally and manage their own sections and approved students.","master":"Master access is hidden at /nexa-core-access and uses the built-in .env master credentials or Master accounts created in the console.","join":"Students with an existing account can enter the Join Code generated by Admin/Faculty to link to their section.","adaptive":"NEXA evaluates correctness, clarity, structure, depth and confidence, then can generate follow-up questions and adjust difficulty."}.items():
        if k in q: ans=v; break
    return jsonify(answer=ans)


@app.errorhandler(403)
def e403(e): return render_template("error.html",code=403,message="This area is restricted."),403
@app.errorhandler(404)
def e404(e): return render_template("error.html",code=404,message="That page does not exist."),404

init_db()
if __name__ == "__main__": app.run(debug=True)
