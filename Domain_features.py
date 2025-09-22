#import libraries
import requests
import pandas as pd
from tqdm import tqdm
import time

#Define ensemble url for GRCh37
#use "https://rest.ensembl.org" url for GRCh38
ENSEMBL_REST = "https://grch37.rest.ensembl.org"

def get_gene_info(gene_id):
    url = f"{ENSEMBL_REST}/lookup/id/{gene_id}?expand=1"
    headers = {"Content-Type": "application/json"}
    r = requests.get(url, headers=headers)
    if not r.ok:
        return None
    return r.json()

def get_canonical(gene_id):
    url = f"{ENSEMBL_REST}/lookup/id/{gene_id}?"
    headers = {"Content-Type": "application/json"}
    r = requests.get(url, headers=headers)
    if not r.ok:
        return None
    return r.json()

def get_ensembl_gene_id(gene_name, species="homo_sapiens"):
    url = f"{ENSEMBL_REST}/xrefs/symbol/{species}/{gene_name}"
    headers = {"Content-Type": "application/json"}
    r = requests.get(url, headers=headers)
    if not r.ok:
        return None
    data = r.json()
    for entry in data:
        if entry.get("type") == "gene":
            return entry.get("id")  # Ensembl Gene ID
    return None

def get_domains(translation_id):
    url = f"{ENSEMBL_REST}/overlap/translation/{translation_id}?feature=protein_feature"
    headers = {"Content-Type": "application/json"}
    r = requests.get(url, headers=headers)
    if not r.ok:
        return []
    return r.json()

def map_protein_to_genomic(translation_id, protein_start, protein_end):
    url = f"https://grch37.rest.ensembl.org/map/translation/{translation_id}/{protein_start}..{protein_end}"
    headers = {"Content-Type": "application/json"}

    response = requests.get(url, headers=headers)
    if not response.ok:
        return None

    data = response.json()
    return data.get("mappings", [])



#### MAIN CODE TO GET GENE INFO #####
with open(r"/content/gene_namelist.txt", "r") as gene_list:
    gene_names = [line.strip() for line in gene_list]
gene_ids = [get_ensembl_gene_id(name) for name in gene_names]
gene_ids = [g for g in gene_ids if g is not None]


results = []

for gene_id in tqdm(gene_ids):
    gene_info = get_gene_info(gene_id)
    if not gene_info:
        continue

    canonical = get_canonical(gene_id)
    canonical_id = canonical.get('canonical_transcript', '')
    if not canonical_id:
        continue

    transcripts = gene_info.get('Transcript', [])
    if not transcripts:
        continue

    canonical_transcript = next(
        (t for t in transcripts if t.get('is_canonical') == 1),
        None
    )
    if not canonical_transcript:
        continue

    translation_id = canonical_transcript.get('Translation', {}).get('id')
    if not translation_id:
        continue

    canonical_length = canonical_transcript.get('length')
    domains = get_domains(translation_id)

    seen_domains = set()
    for domain in domains:
        interpro_id = domain.get('interpro')
        feature_id = domain.get('id')

        is_pfam = feature_id and feature_id.startswith('PF')
        is_interpro = bool(interpro_id)
        if not (is_pfam or is_interpro):
            continue

        domain_key = (
            interpro_id if is_interpro else '',
            feature_id if is_pfam else '',
            domain.get('start'),
            domain.get('end'),
        )

        if domain_key in seen_domains:
            continue

        seen_domains.add(domain_key)

        # Get genomic coordinates
        mappings = map_protein_to_genomic(translation_id, domain.get('start'), domain.get('end'))
        if mappings:
            genomic_start = mappings[0].get('start')
            genomic_end = mappings[-1].get('end')
            genomic_chr = mappings[0].get('seq_region_name')
            genomic_strand = mappings[0].get('strand')
        else:
            genomic_start = genomic_end = genomic_chr = genomic_strand = None

        row = {
            "Gene stable ID version": gene_info.get('id', '') + "." + str(gene_info.get('version', '')),
            "Canonical ID": canonical_id,
            "Gene start (bp)": gene_info.get('start'),
            "Gene end (bp)": gene_info.get('end'),
            "Chromosome/scaffold name": gene_info.get('seq_region_name'),
            "Gene name": gene_info.get('display_name', ''),
            "Transcript length (including UTRs and CDS)": canonical_length,
            "InterPro ID": interpro_id if is_interpro else '',
            "InterPro Description": domain.get('description') if is_interpro else '',
            "InterPro start": domain.get('start') if is_interpro else '',
            "InterPro end": domain.get('end') if is_interpro else '',
            "Pfam ID": feature_id if is_pfam else '',
            "Pfam start": domain.get('start') if is_pfam else '',
            "Pfam end": domain.get('end') if is_pfam else '',
            "Domain Genomic start": genomic_start,
            "Domain Genomic end": genomic_end,
            "Genomic strand": genomic_strand,
        }

        results.append(row)

        time.sleep(0.1)  # avoid hammering the server

df = pd.DataFrame(results)
df.to_csv("Domain_features.csv", index=False)
