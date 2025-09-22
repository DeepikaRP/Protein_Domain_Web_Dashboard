import plotly.graph_objs as go
import plotly.offline as pyo
import pandas as pd
import numpy as np



def prepare_plot_data(gene_name, domains_df, exons_df):
    gene_domains = domains_df[domains_df["Gene name"] == gene_name]
    if gene_domains.empty:
        return "<p>No domain data found.</p>"

    canonical_id = gene_domains["Canonical ID"].iloc[0].split('.')[0]
    gene_exons = exons_df[exons_df["Transcript ID"] == canonical_id]
    
    features = []

    exon_data = []
    intron_data = []
    domain_data = []

    legend_flags = {"Exon": False, "Intron": False, "Domain": False}


    # Plot exons (thicker lines)
    for _, row in gene_exons[gene_exons["Feature"].str.contains("Exon")].iterrows():
        features.append(go.Scatter(
            x=[row["Start"], row["End"]],
            y=[1, 1],
            hoverinfo = 'text', 
            mode='lines',
            line=dict(color="skyblue", width=18),  # thicker width for exon
            name="Coding Exon" if not legend_flags["Exon"] else "",
            hovertext=(f"{row['Feature']}<br>"
                       f"{row['Exon/Intron ID']}<br>"
                       f"Chr{row['Chromosome']}: {row['Start']}-{row['End']}"),
            showlegend=not legend_flags["Exon"],           
            hoverlabel=dict(
                bgcolor = "skyblue",
                font_size = 14,
            ),
        ))
        legend_flags["Exon"] = True

        exon_data.append({
            "Type": "Exon",
            "ID": row["Exon/Intron ID"],
            "Start": row["Start"],
            "End": row["End"]
        })    

    # Plot introns (thinner lines)
    for _, row in gene_exons[gene_exons["Feature"].str.contains("Intron")].iterrows():
        features.append(go.Scatter(
            x=[row["Start"], row["End"]],
            y=[1, 1],
            hoverinfo = 'text',
            mode='lines',
            line=dict(color="gray", width=6),  # thinner width for intron
            name="Intron" if not legend_flags["Intron"] else "",
            hovertext=(f"{row['Feature']}<br>"
                       f"Chr{row['Chromosome']}: {row['Start']}-{row['End']}"),
            showlegend=not legend_flags["Intron"],
            hoverlabel=dict(
                bgcolor = "white",
                font_size = 14, ),
        ))
        legend_flags["Intron"] = True

        intron_data.append({
            "Type": "Intron",
            "ID": "N/A",
            "Start": row["Start"],
            "End": row["End"]
        }) 

    # Plot domains (green lines above track)
    for _, row in gene_domains.iterrows():
        if pd.notna(row["Pfam ID"]):  # Filter to only Pfam domains
            features.append(go.Scatter(
                x=[row["Domain Genomic start"], row["Domain Genomic end"]],
                y=[1, 1],
                hoverinfo = 'text',
                mode="lines",
                line=dict(width=10, color="green"),
                name="Domain" if not legend_flags["Domain"] else "",
                hovertext=f"{row['Pfam ID']}<br>"
                          f"{row['InterPro Description']}<br>"    
                          f"Chr{row['Chromosome/scaffold name']}: {row['Domain Genomic start']} - {row['Domain Genomic end']}",
                showlegend=not legend_flags["Domain"],
                hoverlabel=dict(
                    bgcolor = "green",
                    font_size = 14,
                ),
                
            ))
            legend_flags["Domain"] = True 

            domain_data.append({
                "Type": "Domain",
                "ID": row["Pfam ID"],
                "Start": row["Domain Genomic start"],
                "End": row["Domain Genomic end"]
            })
    all_data = pd.DataFrame(exon_data + intron_data + domain_data)
    filename = f"{gene_name}_features.xlsx"
    all_data.to_excel(filename, index=False)

    layout = go.Layout(
        title=dict(
            text= f"Gene: {gene_name}",
            x=0.047,
            xanchor="left",
            font=dict(
                color="#255D94"
            )
    ),
        height=400,
        xaxis=dict(
            title=dict(
                text="Genomic Coordinate",
                font=dict(size=16, family='Arial', color='black')
            ),
            tickformat=",",
            tickfont=dict(size=12, family='Arial', color='black')
        ),

        yaxis=dict(title="", showticklabels=False),
        showlegend=True)
    


    fig = go.Figure(data=features, layout=layout)

    if "Chromosome" in gene_exons.columns and not gene_exons["Chromosome"].isna().all():
        fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0, y=1.15,
        text=f"Chromosome: {gene_exons['Chromosome'].iloc[0]}",
        showarrow=False,
        font=dict(size=17, color="#255D94")
    )
    
    plot_div = pyo.plot(fig, include_plotlyjs=False, output_type='div', auto_open=False)
    return plot_div, filename


