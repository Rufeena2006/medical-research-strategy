"""Search strategy configuration for the GLP-1 / obesity literature plan.

All search blocks live here so the strategy is transparent and reproducible.
Edit this file to change the topic; the rest of the pipeline adapts.
"""
from datetime import date

TOPIC_TITLE = (
    "GLP-1 receptor agonists and dual incretin agonists for obesity: "
    "efficacy, cardiometabolic outcomes, safety and durability of effect"
)

START_YEAR = 2019
END_DATE = date.today().strftime("%Y/%m/%d")
START_DATE = f"{START_YEAR}/01/01"

# --- Concept blocks (PICO-style) -------------------------------------------
POPULATION = (
    '("Obesity"[Mesh] OR "Overweight"[Mesh] OR obesity[tiab] OR obese[tiab] '
    'OR overweight[tiab] OR "weight management"[tiab] OR "weight loss"[tiab])'
)

INTERVENTION = (
    '("Glucagon-Like Peptide-1 Receptor"[Mesh] OR semaglutide[tiab] '
    'OR tirzepatide[tiab] OR liraglutide[tiab] OR retatrutide[tiab] '
    'OR orforglipron[tiab] OR "GLP-1"[tiab] OR "glucagon-like peptide-1"[tiab] '
    'OR "glucagon like peptide 1"[tiab] OR incretin[tiab])'
)

CARDIORENAL = (
    '("cardiovascular"[tiab] OR "major adverse cardiovascular events"[tiab] '
    'OR MACE[tiab] OR "heart failure"[tiab] OR mortality[tiab] '
    'OR "chronic kidney disease"[tiab] OR "kidney outcomes"[tiab])'
)

DURABILITY = (
    '(discontinu*[tiab] OR withdraw*[tiab] OR "weight regain"[tiab] '
    'OR "weight maintenance"[tiab] OR cessation[tiab] OR persistence[tiab] '
    'OR adherence[tiab])'
)

SAFETY = (
    '("adverse events"[tiab] OR safety[tiab] OR pancreatitis[tiab] '
    'OR gallbladder[tiab] OR cholelithiasis[tiab] OR gastrointestinal[tiab] '
    'OR "optic neuropathy"[tiab] OR suicid*[tiab])'
)

REAL_WORLD = (
    '("real-world"[tiab] OR "real world"[tiab] OR "electronic health records"[tiab] '
    'OR "retrospective cohort"[tiab] OR "claims data"[tiab] '
    'OR "target trial emulation"[tiab])'
)

DESIGN = (
    '("Randomized Controlled Trial"[pt] OR "Meta-Analysis"[pt] '
    'OR "Systematic Review"[pt] OR "Clinical Trial, Phase III"[pt] '
    'OR "Cohort Studies"[Mesh] OR "Observational Study"[pt])'
)

LIMITS = "(humans[mh] AND english[lang])"

CORE = f"{POPULATION} AND {INTERVENTION}"

# Named queries run by run_search.py (name -> PubMed query string)
QUERIES = {
    "Q1_core": f"{CORE} AND {LIMITS}",
    "Q2_cardiorenal": f"{CORE} AND {CARDIORENAL} AND {LIMITS}",
    "Q3_durability": f"{CORE} AND {DURABILITY} AND {LIMITS}",
    "Q4_safety": f"{CORE} AND {SAFETY} AND {LIMITS}",
    "Q5_real_world": f"{CORE} AND {REAL_WORLD} AND {LIMITS}",
    "Q6_gap_durability_real_world": f"{CORE} AND {DURABILITY} AND {REAL_WORLD} AND {LIMITS}",
    "Q7_retrieval_set": f"{CORE} AND {DESIGN} AND {LIMITS}",
}

# The query whose records are downloaded and screened
RETRIEVAL_QUERY = "Q7_retrieval_set"

# --- Screening vocabulary ---------------------------------------------------
INTERVENTION_WORDS = [
    "semaglutide", "tirzepatide", "liraglutide", "retatrutide", "orforglipron",
    "glp-1", "glucagon-like peptide", "incretin",
]
OBESITY_WORDS = ["obes", "overweight", "weight loss", "weight management", "body weight"]
EXCLUDED_PUBTYPES = {
    "Editorial", "Comment", "Letter", "Case Reports", "News", "Retracted Publication",
    "Published Erratum", "Interview", "Biography",
}
