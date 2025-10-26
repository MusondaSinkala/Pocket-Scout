from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import os
import json
from datetime import datetime
from source.heatmap_generator import generate_heatmap  # Import from source folder

app = Flask(__name__, template_folder='templates', static_folder='static')

# Load data from data/ folder
df = pd.read_csv('data/final_player_df.csv')
df.set_index('id', inplace=True)

# Load heatmap data from data/ folder
with open('data/player_heatmap_features.json', 'r') as f:
    heatmap_data = json.load(f)

# Create dictionaries for quick lookup
player_dict = {row['full_name']: idx for idx, row in df.iterrows()}
heatmap_dict = {item['playerId']: item['features'] for item in heatmap_data}

@app.route("/")
def home():
    return render_template('index.html', player_names=list(player_dict.keys()))

@app.route('/player/<int:player_id>')
def get_player(player_id):
    if player_id not in df.index:
        return jsonify({'error': 'Player not found'}), 404
    
    row = df.loc[player_id].drop('top_knn_ids').to_dict()
    
    # Generate heatmap on the fly using the density data
    if player_id in heatmap_dict:
        player_name = row['full_name']
        density_features = heatmap_dict[player_id]
        row['density_plot_url'] = generate_heatmap(density_features, player_name)
    else:
        row['density_plot_url'] = None
    
    row['contract_expiration_date'] = datetime.strptime(row['contract_expiration_date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    row['market_value_in_eur'] = "€{:,.0f}".format(row['market_value_in_eur'])
    
    return jsonify(row)

@app.route('/similar_players/<int:player_id>')
def get_similar(player_id):
    if player_id not in df.index:
        return jsonify({'error': 'Player not found'}), 404

    top_ids = pd.unique(df.loc[player_id]['top_knn_ids'])

    players = []
    for sid in top_ids:
        if sid in df.index:
            row = df.loc[sid]
            if isinstance(row, pd.DataFrame):  # If df.loc[sid] returns multiple rows, take the first one
                row = row.iloc[0]

            players.append({
                'id': int(sid),
                'full_name': str(row['full_name']),
                'club': str(row['club']),
                'role': str(row['role']),
                'image_url': str(row['image_url'])
            })

    return jsonify({'similar_players': players})

@app.route('/get_player_id', methods=['POST'])
def get_player_id():
    name = request.json.get("name")
    player_id = player_dict.get(name)
    return jsonify({"player_id": player_id})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
