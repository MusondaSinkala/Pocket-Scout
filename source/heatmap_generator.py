import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Required for headless environments
from mplsoccer import Pitch
import numpy as np
import io
import base64

def generate_heatmap(density_data, player_name):
    """
    Generate a football pitch heatmap from density data and return as base64 encoded image
    """
    # Reshape the 100 values into 10x10 grid
    heatmap_data = np.array(density_data).reshape(10, 10)
    
    # Create a custom colormap (similar to your original)
    custom_cmap = plt.cm.hot
    
    # Create pitch
    pitch = Pitch(pitch_type='wyscout', corner_arcs=True)
    fig, ax = pitch.draw(figsize=(10, 6))
    
    # Create coordinates for the 10x10 grid
    # We need to convert our 10x10 grid to pitch coordinates (0-100 to 0-100)
    x_coords = np.linspace(0, 100, 10)
    y_coords = np.linspace(0, 100, 10)
    
    # Create meshgrid for the heatmap
    X, Y = np.meshgrid(x_coords, y_coords)
    
    # Plot the heatmap
    heatmap = ax.contourf(X, Y, heatmap_data, levels=100, cmap=custom_cmap, alpha=0.7)
    
    # Add colorbar
    plt.colorbar(heatmap, ax=ax, label='Activity Density')
    
    # Add title
    ax.set_title(f'Heatmap: {player_name}', fontsize=14, fontweight='bold')
    
    # Convert to base64 for web display
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100, transparent=True)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"
