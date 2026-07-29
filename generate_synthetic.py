#!/usr/bin/env python3
"""
Generate a fully synthetic sample CSV for the NoteViewer demo.

No real patient data is used. Every original_note_text is authored from fake
building blocks, and every results[].span is a verbatim quote from that
synthetic prose, so the AI-pipeline view renders correctly with zero PHI.

Schema matches the original results_flat.csv exactly:
  note_id, patient_id, procedure_id, steatosis, steatohepatitis, cirrhosis,
  fibrosis_severity, fibrosis_severity_negated, fibrosis_stage,
  fibrosis_staging_scale, consistent_with, timeframe, note_text,
  original_note_text
"""
import csv, json, random

random.seed(20260728)  # deterministic output

HOSPITALS = [
    ("Lakeshore Regional Medical Center", "418 Maple Crossing Blvd", "Rivermont, IL 60188", "312-555-0142", "312-555-0198"),
    ("St. Aubin General Hospital", "77 Harborview Terrace", "Northgate, MA 02155", "617-555-0173", "617-555-0121"),
    ("Cedar Valley University Health", "2200 Fielding Avenue", "Greenspan, OH 44112", "440-555-0166", "440-555-0109"),
    ("Meridian Coastal Medical Center", "915 Palmetto Way", "Bayford, FL 33009", "305-555-0188", "305-555-0134"),
    ("Northwind Memorial Hospital", "630 Birchwood Parkway", "Kettering, MN 55044", "651-555-0155", "651-555-0117"),
]
PATHOLOGISTS = ["Adrienne Coyle", "Marcus Halloway", "Priya Venkataraman", "Devon Ashcroft",
                "Renata Solberg", "Tobias Whitfield", "Nadia Karim", "Elliot Ransome"]
CLINICIANS = ["Harold Merriweather", "Simone Delacroix", "Owen Castellano", "Imani Okoro",
              "Grant Fairbanks", "Lucia Montenegro", "Karl Ostrander", "Beatrice Nwosu"]
FIRST = ["Rowan", "Delia", "Marcus", "Yusuf", "Camille", "Theo", "Priscilla", "Hassan",
         "Louisa", "Emilio", "Greta", "Desmond", "Anaya", "Roland", "Petra", "Silas"]
LAST = ["Ashworth", "Bellamy", "Calderon", "Duquette", "Everhart", "Fontaine", "Grimaldi",
        "Holloway", "Ibarra", "Jessup", "Kowalczyk", "Larsson", "Mendez", "Novak", "Ophelia", "Prewitt"]
SPECIMENS = ["liver, needle biopsy", "liver, core biopsy", "liver, wedge biopsy", "liver biopsy"]

def mrn():        return str(random.randint(1000000000, 9999999999))
def dob():        return f"{random.randint(1,12)}/{random.randint(1,28)}/{random.randint(1948,1994)}"
def dt(y=2021):   return f"{random.randint(1,12)}/{random.randint(1,28)}/{y}"
def iso(m,d,y):   return f"{y}-{m:02d}-{d:02d}"

def patient():
    return f"{random.choice(LAST).lower()}, {random.choice(FIRST).lower()}"

# ---- finding builders: each returns (prose_sentence, result_dict_or_None, column_updates) ----

def build_completed_biopsy():
    """A finalized surgical-pathology report (timeframe = past)."""
    hosp = random.choice(HOSPITALS)
    name = patient()
    m, d, y = random.randint(1,12), random.randint(1,28), random.choice([2019,2020,2021,2022,2023])
    spec = random.choice(SPECIMENS)
    path = random.choice(PATHOLOGISTS)
    sex = random.choice(["m","f"])
    age = random.randint(29,74)
    cols = dict(steatosis="not mentioned", steatohepatitis="not mentioned", cirrhosis="not mentioned",
                fibrosis_severity="n", fibrosis_severity_negated="not mentioned",
                fibrosis_stage="not mentioned", fibrosis_staging_scale="not mentioned",
                consistent_with="", timeframe="past")
    results = []
    diag_bits = []

    # steatosis
    if random.random() < 0.7:
        pct = random.choice([15,25,40,55,70,80])
        sev = "mild" if pct<25 else ("moderate" if pct<55 else "severe")
        span = f"{sev} large-droplet macrovesicular steatosis involving approximately {pct}% of the hepatic parenchyma"
        diag_bits.append(span)
        results.append({"name":"steatosis","value":f"{pct}% of hepatic parenchyma","span":span})
        cols["steatosis"]="y"

    # steatohepatitis / NASH
    if random.random() < 0.55:
        span = "findings consistent with non-alcoholic steatohepatitis (nash)"
        diag_bits.append(span)
        results.append({"name":"non-alcoholic steatohepatitis (nash)","value":"yes","span":span})
        cols["steatohepatitis"]="y"; cols["consistent_with"]="NASH"

    # fibrosis
    if random.random() < 0.8:
        scale = random.choice(["Metavir","Ishak"])
        if scale=="Metavir":
            stage = random.choice([1,2,3,4]); smax=4
        else:
            stage = random.choice([1,2,3,4,5,6]); smax=6
        if stage>=(smax-0): sevtxt="cirrhosis"; cols["cirrhosis"]="y"
        elif stage>=max(1,smax-1): sevtxt="bridging fibrosis"
        else: sevtxt="portal fibrosis"
        span = f"{sevtxt} identified, fibrosis stage {stage} of {smax} on the {scale.lower()} scale"
        diag_bits.append(span)
        results.append({"name":sevtxt,"value":f"stage {stage}","span":span})
        cols["fibrosis_severity"]=sevtxt; cols["fibrosis_stage"]=str(stage); cols["fibrosis_staging_scale"]=scale
    else:
        span = "no significant fibrosis identified on trichrome stain"
        diag_bits.append(span); cols["fibrosis_severity_negated"]="y"

    # lobular inflammation flavor (prose only)
    infl = "scattered lobular inflammation composed of lymphocytes, histiocytes and rare neutrophils"
    if random.random()<0.6:
        diag_bits.append(infl)
        results.append({"name":"lobular inflammation","value":"scattered lymphocytes, histiocytes, rare neutrophils","span":infl})

    if not results:  # guarantee at least one finding
        span="mild nonspecific reactive changes without diagnostic abnormality"
        diag_bits.append(span)
        results.append({"name":"hepatic parenchyma","value":"nonspecific reactive changes","span":span})

    accession = f"SP{y%100}-{random.randint(10000,99999)}"
    nas = random.randint(3,7)
    prose = (
        f"{hosp[0]} anatomic pathology laboratory {hosp[1]} {hosp[2]} {hosp[3]} fax# {hosp[4]} "
        f"name: {name} path no.: {accession} mrn: {mrn()} "
        f"date obtained: {m}/{d}/{y} d.o.b. {dob()} (age: {age}) date received: {m}/{d}/{y} sex: {sex} "
        f"physician: {random.choice(CLINICIANS).lower()}, md location: gi endoscopy suite "
        f"surgical pathology specimen: {spec} "
        f"diagnosis(es): {spec}: " + ". ".join(diag_bits) + ". "
        f"note: the nas score = {nas}. "
        f"date dictated: {m}/{min(d+3,28)}/{y} clinical information: order diagnosis: nonspecific elevation of "
        f"transaminases, evaluation for chronic liver disease. gross description: the specimen is received fixed in "
        f"formalin in a container labeled with the patient's name, mrn and \"liver\". it consists of a single core of "
        f"tissue measuring {random.uniform(1.4,2.8):.1f} cm in length submitted in toto in one cassette labeled a. "
        f"microscopic description: sections demonstrate a single core of liver tissue for evaluation. "
        + ". ".join(diag_bits) + f". reviewed and signed out by {path.lower()}, md."
    )
    note_text = (
        f"procedure name: liver biopsy\n"
        f"procedure span: {spec}\n"
        f"date: {iso(m,d,y)}\n"
        f"date span: date obtained: {m}/{d}/{y}\n"
        f"results: {json.dumps(results, separators=(',',':'))}"
    )
    return cols, note_text, prose

def build_planned_consult():
    """An H&P / consult note that mentions a planned biopsy (timeframe = future)."""
    name_first = random.choice(FIRST).lower()
    attending = random.choice(CLINICIANS)
    requesting = random.choice(CLINICIANS)
    age = random.randint(31,72); sex=random.choice(["m","f"])
    m, d, y = random.randint(1,12), random.randint(1,28), random.choice([2022,2023,2024])
    cols = dict(steatosis="not mentioned", steatohepatitis="not mentioned", cirrhosis="not mentioned",
                fibrosis_severity="n", fibrosis_severity_negated="not mentioned",
                fibrosis_stage="", fibrosis_staging_scale="", consistent_with="", timeframe="future")
    concern = random.choice([
        ("hepatic disease","possible","hepatic work-up also concerning for possible autoimmune hepatitis"),
        ("cirrhosis","developing","imaging suggestive of developing cirrhosis, biopsy planned for staging"),
        ("primary biliary cholangitis","possible","cholestatic pattern raising concern for primary biliary cholangitis"),
    ])
    if concern[0]=="cirrhosis": cols["cirrhosis"]="developing"
    if "biliary" in concern[0]: cols["consistent_with"]="primary biliary cirrhosis"
    results=[{"name":concern[0],"value":concern[1],"span":concern[2]}]
    prose = (
        f"attestation i have seen and examined the patient and i concur with the findings of the history and physical "
        f"dated {m}/{max(d-1,1)}/{y}. any changes are noted as follows: none. {attending.lower()} md attending department "
        f"of surgery. chief complaint {sex=='m' and 'he' or 'she'} had gallbladder flare up two days ago, pain improving. "
        f"reason for consultation cholelithiasis, evaluation for cholecystectomy and liver biopsy. consulting attending "
        f"physician dr. {attending.split()[-1].lower()} requesting practitioner dr. {requesting.split()[-1].lower()}. "
        f"history of present illness {age}{sex} with a pmh of htn, gerd admitted for workup of epigastric abdominal pain, "
        f"nausea and transaminitis. plan for laparoscopic cholecystectomy {m}/{d} with liver biopsy. "
        f"{concern[2]}. assessment and plan proceed to operative liver biopsy for staging."
    )
    note_text = (
        f"procedure name: liver biopsy\n"
        f"procedure span: plan for laparoscopic cholecystectomy {m}/{d} with liver biopsy\n"
        f"date: {iso(m,d,y)}\n"
        f"date span: plan for laparoscopic cholecystectomy {m}/{d} with liver biopsy\n"
        f"results: {json.dumps(results, separators=(',',':'))}"
    )
    return cols, note_text, prose

def build_hypothetical():
    """A note discussing biopsy as a contingency (timeframe = hypothetical)."""
    age = random.randint(35,70); sex=random.choice(["m","f"])
    m, d, y = random.randint(1,12), random.randint(1,28), random.choice([2022,2023,2024])
    cols = dict(steatosis=random.choice(["not mentioned","y"]), steatohepatitis="mild", cirrhosis="not mentioned",
                fibrosis_severity="mild fibrosis", fibrosis_severity_negated="not mentioned",
                fibrosis_stage="1", fibrosis_staging_scale="Metavir", consistent_with="alcoholic liver disease",
                timeframe="hypothetical")
    span="if transaminases remain elevated we would consider liver biopsy to exclude steatohepatitis"
    results=[{"name":"steatohepatitis","value":"consider biopsy","span":span}]
    prose = (
        f"outpatient gastroenterology follow-up. {age}{sex} with a history of alcohol use and mild transaminase "
        f"elevation. abdominal ultrasound shows hepatic steatosis. discussed alcohol cessation. "
        f"{span}. no biopsy performed at this visit. return to clinic in three months for repeat liver panel."
    )
    note_text = (
        f"procedure name: liver biopsy\n"
        f"procedure span: consider liver biopsy to exclude steatohepatitis\n"
        f"date: {iso(m,d,y)}\n"
        f"date span: repeat liver panel in three months\n"
        f"results: {json.dumps(results, separators=(',',':'))}"
    )
    return cols, note_text, prose

BUILDERS = [build_completed_biopsy]*7 + [build_planned_consult]*2 + [build_hypothetical]*1

COLS = ["note_id","patient_id","procedure_id","steatosis","steatohepatitis","cirrhosis",
        "fibrosis_severity","fibrosis_severity_negated","fibrosis_stage","fibrosis_staging_scale",
        "consistent_with","timeframe","note_text","original_note_text"]

def main(n=107):
    rows=[]
    for _ in range(n):
        cols, note_text, prose = random.choice(BUILDERS)()
        row = {
            "note_id": str(random.randint(10000000, 89999999)),
            "patient_id": str(random.randint(1000000, 2999999)),
            "procedure_id": str(random.randint(1, 900)),
            **cols,
            "note_text": note_text,
            "original_note_text": prose,
        }
        rows.append(row)
    with open("public/sample_notes.csv","w",newline="") as f:
        w=csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows: w.writerow(r)
    print(f"wrote public/sample_notes.csv with {len(rows)} rows")

if __name__=="__main__":
    main()
