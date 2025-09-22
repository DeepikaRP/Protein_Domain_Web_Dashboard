from flask import Flask, render_template, request, send_file
import os
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo
from utils import prepare_plot_data

app = Flask(__name__)

# Load data once
domains_df = pd.read_csv("data/Domain_features.csv")
exons_df = pd.read_csv("data/intron_exon.csv")

@app.route("/", methods=["GET", "POST"])
def index():
    gene_plot = ""
    gene_name = ""
    download_link = ""

    if request.method == "POST":
        gene_name = request.form.get("gene_name", "").strip()
        if gene_name:
            gene_plot, filename = prepare_plot_data(gene_name, domains_df, exons_df)
            if filename:
                download_link = f"/download/{filename}"

    return render_template("index.html", gene_name=gene_name, plot_div=gene_plot, download_link=download_link)

@app.route('/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
