from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import os
import json
from datetime import datetime
from source.heatmap_generator import generate_heatmap
import math

app = Flask(__name__, template_folder='templates', static_folder='static')

def clean_nan_values(obj):
    """Recursively replace NaN values with None"""
    if isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(v) for v in obj]
    elif pd.isna(obj) or (isinstance(obj, float) and math.isnan(obj)):
        return None
    else:
        return obj

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
    
    # Get row and convert to dict, handling potential DataFrame case
    row_data = df.loc[player_id]
    if isinstance(row_data, pd.DataFrame):
        row_data = row_data.iloc[0]
    
    # Drop top_knn_ids if it exists and convert to dict
    if 'top_knn_ids' in row_data:
        row = row_data.drop('top_knn_ids').to_dict()
    else:
        row = row_data.to_dict()
    
    # Clean NaN values
    row = clean_nan_values(row)
    
    # Generate heatmap on the fly using the density data
    if player_id in heatmap_dict:
        player_name = row.get('full_name', 'Unknown Player')
        density_features = heatmap_dict[player_id]
        row['density_plot_url'] = generate_heatmap(density_features, player_name)
    else:
        row['density_plot_url'] = None
    
    # Handle date formatting safely
    contract_date = row.get('contract_expiration_date')
    if contract_date and contract_date != 'NaN':
        try:
            row['contract_expiration_date'] = datetime.strptime(
                str(contract_date), '%Y-%m-%d %H:%M:%S'
            ).strftime('%Y-%m-%d')
        except:
            row['contract_expiration_date'] = "Unknown"
    else:
        row['contract_expiration_date'] = "Unknown"
    
    # Format market value safely
    market_value = row.get('market_value_in_eur')
    if market_value and market_value != 'NaN':
        try:
            row['market_value_in_eur'] = "€{:,.0f}".format(float(market_value))
        except:
            row['market_value_in_eur'] = "Unknown"
    else:
        row['market_value_in_eur'] = "Unknown"
    
    return jsonify(row)

@app.route('/similar_players/<int:player_id>')
def get_similar(player_id):
    print(f"🔍 DEBUG: Getting similar players for player_id: {player_id}")
    
    if player_id not in df.index:
        return jsonify({'error': 'Player not found'}), 404

    top_knn_ids_value = df.loc[player_id]['top_knn_ids']
    print(f"🔍 DEBUG: top_knn_ids_value: {top_knn_ids_value}")
    print(f"🔍 DEBUG: Type: {type(top_knn_ids_value)}")
    
    # Handle the top_knn_ids
    if isinstance(top_knn_ids_value, str) and top_knn_ids_value.strip():
        print(f"🔍 DEBUG: Processing as string")
        try:
            # Convert numpy-style string to Python list format
            python_list_string = top_knn_ids_value.strip().replace(' ', ', ')
            print(f"🔍 DEBUG: Converted to Python format: {python_list_string}")
            
            # Now eval should work
            top_ids = eval(python_list_string)
            print(f"🔍 DEBUG: Parsed IDs: {top_ids}")
            
        except Exception as e:
            print(f"❌ Error parsing string: {e}")
            top_ids = []
    elif hasattr(top_knn_ids_value, '__iter__') and not isinstance(top_knn_ids_value, str):
        top_ids = list(top_knn_ids_value)
        print(f"🔍 DEBUG: Converted iterable to list: {top_ids}")
    else:
        print(f"❌ Unhandled type or empty: {type(top_knn_ids_value)}")
        top_ids = []

    print(f"🔍 DEBUG: Final top_ids: {top_ids}")
    
    players = []
    for sid in top_ids:
        # Skip the player themselves and check if ID is valid
        if sid != player_id and sid in df.index:
            row = df.loc[sid]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]

            player_data = {
                'id': int(sid),
                'full_name': str(row.get('full_name', 'Unknown')),
                'club': str(row.get('club', 'Unknown')),
                'role': str(row.get('role', 'Unknown')),
                'image_url': str(row.get('image_url', ''))
            }
            players.append(player_data)
            print(f"✅ Added similar player: {player_data['full_name']} (ID: {sid})")

    print(f"🔍 DEBUG: Returning {len(players)} similar players")
    return jsonify({'similar_players': players})

@app.route('/get_player_id', methods=['POST'])
def get_player_id():
    name = request.json.get("name")
    player_id = player_dict.get(name)
    return jsonify({"player_id": player_id})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


