<h2>Protein Domain Visualizer </h2><br>

<p> The domains features in proteins contribute greatly in scientific research </p><br>
<p> To visualize the Domain fetures along with exons and introns in a gene, here API and Flask is used to create a dashboard </p> <br>

<h3> Data fetching using API </h3> 
<p>The files Domain_features.py and exon_intron.py are python files that use API to fetch data from Ensemble database and save the data in form of CSV files in local folder. </p><br>
<p> URL "https://" is used to fetch data for GRCh38 and "" for data belonging to GRCh37. </p>

<h3> Visualization dashboarcd using Flask </h3>
<p> Flask is a lightweight, web-based visualization tool was implemented using Flask and Plotly to enable interactive exploration of gene features.</p><br>
<p> The application renders domain and transcript annotations as linear tracks aligned to genomic coordinates, with hover-enabled tooltips displaying accession IDs, feature names, and genomic positions. </p>
<br>
<p> Flask folder contain different folders and files that is used to create web interface for visualization</p><br>
<p>Data folder : CSV files</p><br>
<p>Static : style.css files</p><br>
<p>Templates: index.html file</p><br>
<p>app.py</p><br>
<p>utils.py</p><br>
<br>
<p> app.py file is run in Linux system as "python app.py" to launch the webpage and visualise. </p>
