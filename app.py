from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import os
import json
from datetime import datetime
from source.heatmap_generator import generate_heatmap
import math

app = Flask(__name__, template_folder='templates', static_folder='static')

def capitalize_text(text):
    """
    Capitalize the first letter of each word in a string, handling special cases
    """
    if not text or pd.isna(text) or text == 'Unknown':
        return text
    
    # Convert to string and strip whitespace
    text = str(text).strip()
    
    # Handle common football-specific cases
    special_cases = {
        'fc': 'FC',
        'ac': 'AC',
        'as': 'AS',
        'ss': 'SS',
        'us': 'US',
        'rc': 'RC',
        'sc': 'SC',
        'cf': 'CF',
        'cd': 'CD',
        'ud': 'UD',
        'sd': 'SD',
        'afc': 'AFC',
        'cfc': 'CFC',
        'inter': 'Inter',
        'atalanta': 'Atalanta',
        'atalanta bc': 'Atalanta BC',
        'bsc': 'BSC',
        'bm': 'BM',
        'ol': 'OL',
        'og': 'OG',
        'psg': 'PSG',
        'as monaco': 'AS Monaco',
        'as roma': 'AS Roma',
        'manchester united': 'Manchester United',
        'manchester city': 'Manchester City',
        'manchester utd': 'Manchester Utd',
        'man utd': 'Man Utd',
        'man city': 'Man City',
        'tottenham hotspur': 'Tottenham Hotspur',
        'west ham united': 'West Ham United',
        'newcastle united': 'Newcastle United',
        'leicester city': 'Leicester City',
        'wolverhampton wanderers': 'Wolverhampton Wanderers',
        'real madrid': 'Real Madrid',
        'fc barcelona': 'FC Barcelona',
        'atletico madrid': 'Atletico Madrid',
        'atlético madrid': 'Atlético Madrid',
        'bayern munich': 'Bayern Munich',
        'bayern münchen': 'Bayern München',
        'borussia dortmund': 'Borussia Dortmund',
        'paris saint-germain': 'Paris Saint-Germain',
        'olympique lyonnais': 'Olympique Lyonnais',
        'olympique marseille': 'Olympique Marseille',
        'ajax amsterdam': 'Ajax Amsterdam',
        'fc porto': 'FC Porto',
        'sl benfica': 'SL Benfica',
        'sporting cp': 'Sporting CP',
        'inter milan': 'Inter Milan',
        'ac milan': 'AC Milan',
        'as monaco': 'AS Monaco'
    }
    
    # Check if the entire text matches a special case
    lower_text = text.lower()
    if lower_text in special_cases:
        return special_cases[lower_text]
    
    # Split into words and capitalize each one
    words = text.split()
    capitalized_words = []
    
    for word in words:
        lower_word = word.lower()
        if lower_word in special_cases:
            capitalized_words.append(special_cases[lower_word])
        else:
            # Capitalize first letter, keep the rest as is
            if word:
                capitalized_words.append(word[0].upper() + word[1:])
            else:
                capitalized_words.append(word)
    
    return ' '.join(capitalized_words)

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

def capitalize_player_data(player_data):
    """
    Apply capitalization to relevant fields in player data
    """
    fields_to_capitalize = [
        'full_name', 'firstname', 'lastname', 'club', 'national_team', 
        'country_of_birth', 'city_of_birth', 'position', 'role', 'agent_name'
    ]
    
    for field in fields_to_capitalize:
        if field in player_data and player_data[field]:
            player_data[field] = capitalize_text(player_data[field])
    
    return player_data

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
    # Capitalize player names for the frontend
    capitalized_names = [capitalize_text(name) for name in player_dict.keys()]
    return render_template('index.html', player_names=capitalized_names)

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
    
    # Apply capitalization to text fields
    row = capitalize_player_data(row)
    
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
    if player_id not in df.index:
        return jsonify({'error': 'Player not found'}), 404

    top_knn_ids_value = df.loc[player_id]['top_knn_ids']
    
    # Handle the top_knn_ids
    if isinstance(top_knn_ids_value, str) and top_knn_ids_value.strip():
        try:
            # Clean and parse the string
            cleaned = top_knn_ids_value.strip('[] ')
            number_strings = [s for s in cleaned.split() if s.strip()]
            all_ids = [int(num) for num in number_strings]
        except Exception as e:
            print(f"❌ Error parsing string: {e}")
            all_ids = []
    elif hasattr(top_knn_ids_value, '__iter__') and not isinstance(top_knn_ids_value, str):
        all_ids = list(top_knn_ids_value)
    else:
        all_ids = []

    # Remove duplicates while preserving order
    top_ids = list(dict.fromkeys(all_ids))
    
    players = []
    for sid in top_ids:
        # Skip the player themselves and check if ID is valid
        if sid != player_id and sid in df.index:
            row = df.loc[sid]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]

            # Create player data and capitalize it
            player_data = {
                'id': int(sid),
                'full_name': str(row.get('full_name', 'Unknown')),
                'club': str(row.get('club', 'Unknown')),
                'role': str(row.get('role', 'Unknown')),
                'image_url': str(row.get('image_url', ''))
            }
            
            # Apply capitalization
            player_data = capitalize_player_data(player_data)
            players.append(player_data)

    return jsonify({'similar_players': players})

@app.route('/get_player_id', methods=['POST'])
def get_player_id():
    name = request.json.get("name")
    
    # Capitalize the search query to match our stored names
    capitalized_name = capitalize_text(name)
    
    # Try to find the player with the capitalized name
    player_id = None
    for player_name, pid in player_dict.items():
        if capitalize_text(player_name) == capitalized_name:
            player_id = pid
            break
    
    return jsonify({"player_id": player_id})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0-0.0', port=port, debug=False)
