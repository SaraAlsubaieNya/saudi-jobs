SKILL_PATTERNS = {
    # --- Languages ---
    "Python":        [r"\bpython\b"],
    "SQL":           [r"\bsql\b", r"\bt-sql\b", r"\bpl/?sql\b"],
    "R":             [r"\bR\b(?=[\s,./)]|$)", r"\bR programming\b", r"\bRStudio\b"],
    "Scala":         [r"\bscala\b"],
    "Java":          [r"\bjava\b(?!script)"],

    # --- BI & Visualization ---
    "Power BI":      [r"\bpower\s?bi\b", r"\bpowerbi\b", r"\bDAX\b"],
    "Tableau":       [r"\btableau\b"],
    "Excel":         [r"\bexcel\b(?!lent|lence)", r"\bpivot tables?\b", r"\bvba\b"],
    "Looker":        [r"\blooker\b"],
    "Qlik":          [r"\bqlik\w*\b"],

    # --- Cloud ---
    "AWS":           [r"\baws\b", r"\bamazon web services\b", r"\bredshift\b", r"\bsagemaker\b"],
    "Azure":         [r"\bazure\b", r"\bsynapse\b", r"\bmicrosoft fabric\b"],
    "GCP":           [r"\bgcp\b", r"\bgoogle cloud\b", r"\bbigquery\b"],

    # --- Data Engineering ---
    "Spark":         [r"\b(py)?spark\b", r"\bdatabricks\b"],
    "Airflow":       [r"\bairflow\b"],
    "Kafka":         [r"\bkafka\b"],
    "dbt":           [r"\bdbt\b"],
    "ETL":           [r"\betl\b", r"\belt\b", r"\bdata pipelines?\b"],
    "Data Warehousing": [r"\bdata warehous\w*\b", r"\bsnowflake\b", r"\bdata marts?\b"],
    "Hadoop":        [r"\bhadoop\b", r"\bhive\b"],

    # --- ML / AI ---
    "Machine Learning": [r"\bmachine learning\b", r"\bML\b(?=[\s,./)]|$)", r"\bscikit-?learn\b", r"\bxgboost\b"],
    "Deep Learning":  [r"\bdeep learning\b", r"\btensorflow\b", r"\bpytorch\b", r"\bneural network"],
    "NLP":            [r"\bnlp\b", r"\bnatural language\b"],
    "GenAI / LLMs":   [r"\bllms?\b", r"\bgen(erative)?\s?ai\b", r"\bgpt\b", r"\brag\b", r"\bprompt engineering\b"],
    "Statistics":     [r"\bstatistic\w*\b", r"\ba/b test\w*\b", r"\bhypothesis test\w*\b", r"\bregression\b"],

    # --- Databases ---
    "NoSQL":         [r"\bnosql\b", r"\bmongodb\b", r"\bcassandra\b"],
    "PostgreSQL":    [r"\bpostgres\w*\b"],
    "Oracle":        [r"\boracle\b"],
    "SQL Server":    [r"\bsql server\b", r"\bssis\b", r"\bssrs\b", r"\bssas\b"],

    # --- Tools & Practices ---
    "Git":           [r"\bgit(hub|lab)?\b"],
    "Docker/K8s":    [r"\bdocker\b", r"\bkubernetes\b", r"\bk8s\b"],
    "Agile":         [r"\bagile\b", r"\bscrum\b", r"\bjira\b"],
    "SAP":           [r"\bsap\b"],
    "SAS":           [r"\bsas\b"],
    "Data Governance": [r"\bdata governance\b", r"\bdata quality\b", r"\bmaster data\b"],

    # --- Regional / soft-adjacent (valuable KSA signal) ---
    "Arabic":        [r"\barabic\b"],
    "Communication": [r"\bcommunication skills?\b", r"\bstakeholder\w*\b", r"\bpresentation skills?\b"],
    "Dashboards/Reporting": [r"\bdashboards?\b", r"\breport(ing)?\b", r"\bkpis?\b"],
}

# Seniority classification — checked against the job TITLE first, then description.
# Order matters: first match wins.
SENIORITY_PATTERNS = [
    ("Lead/Manager+", r"\b(lead|manager|head|director|principal|chief|vp)\b"),
    ("Senior",        r"\b(senior|sr\.?)\b"),
    ("Junior/Entry",  r"\b(junior|jr\.?|entry|graduate|intern|trainee|fresh(er)?)\b"),
    # 'Mid' is the default when nothing matches
]

# Role family classification from title
ROLE_PATTERNS = [
    ("Data Scientist",  r"\bdata scien\w*\b|\bml engineer\b|\bmachine learning\b|\bai\b"),
    ("Data Engineer",   r"\bdata engineer\w*\b|\bbig data\b"),
    ("BI Developer",    r"\bbi developer\b|\bpower ?bi\b|\bbusiness intelligence\b"),
    ("Data Analyst",    r"\bdata analy\w*\b|\banalytics\b|\banalyst\b"),
]

SEARCH_QUERIES = [
    "data analyst",
    "data scientist",
    "data engineer",
    "business intelligence",
    "machine learning engineer",
]
