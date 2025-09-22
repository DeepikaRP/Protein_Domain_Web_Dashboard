import requests
import pandas as pd
from tqdm import tqdm
import time

# Read your domains CSV and extract transcript IDs
domains_df = pd.read_csv("/content/Domain_features.csv")
transcript_ids = domains_df["Canonical ID"].dropna().unique()
transcript_ids = [tid.split('.')[0] for tid in transcript_ids]  # Strip version numbers

# Set up Ensembl GRCh37 REST API
# Use "https://rest.ensembl.org" got GRCh 38 
server = "https://grch37.rest.ensembl.org"

exon_intron_results = []

for transcript_id in tqdm(transcript_ids):
    ext = f"/lookup/id/{transcript_id}?expand=1"
    headers = {"Content-Type": "application/json"}
    response = requests.get(server + ext, headers=headers)
    if not response.ok:
        continue

    data = response.json()

    exons = data.get('Exon', [])
    if not exons:
        continue

    # Sort exons by start position
    exons = sorted(exons, key=lambda x: x['start'])

    for idx, exon in enumerate(exons):
        # Add exon
        exon_intron_results.append({
            "Transcript ID": transcript_id,
            "Feature": f"Exon {idx + 1}",
            "Exon/Intron ID": exon['id'],
            "Start": exon['start'],
            "End": exon['end'],
            "Strand": exon['strand'],
            "Chromosome": exon['seq_region_name']
        })

        # Add intron after each exon except the last one
        if idx < len(exons) - 1:
            intron_start = exon['end'] + 1
            intron_end = exons[idx + 1]['start'] - 1
            exon_intron_results.append({
                "Transcript ID": transcript_id,
                "Feature": f"Intron {idx + 1}",
                "Exon/Intron ID": "",  # introns don’t have IDs
                "Start": intron_start,
                "End": intron_end,
                "Strand": exon['strand'],
                "Chromosome": exon['seq_region_name']
            })

    time.sleep(0.1) 

# Save to CSV
df = pd.DataFrame(exon_intron_results)
df.to_csv("exon_introns.csv", index=False)
