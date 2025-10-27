import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Required for headless environments
from mplsoccer import Pitch
import numpy as np
import io
import base64
from matplotlib.colors import LinearSegmentedColormap

def generate_heatmap(density_data, player_name, display_in_notebook = False):
    """
    Generate a football pitch heatmap from density data using transposed orientation
    """
    # Reshape and transpose the data
    heatmap_data = np.array(density_data).reshape(10, 10).T
    
    # Create white-to-blue colormap
    colors = ['white', 'lightblue', 'blue', 'darkblue']
    cmap = LinearSegmentedColormap.from_list('white_to_blue', colors, N=256)
    
    # Create pitch with white background and black lines
    from mplsoccer import Pitch
    pitch = Pitch(
        pitch_type='wyscout', 
        corner_arcs=True, 
        pitch_color='white',
        line_color='black',
        linewidth=1.5
    )
    fig, ax = pitch.draw(figsize=(10, 6))
    
    # Set figure background to white
    fig.patch.set_facecolor('white')
    
    # Create coordinates and plot heatmap
    x_coords = np.linspace(0, 100, 10)
    y_coords = np.linspace(0, 100, 10)
    X, Y = np.meshgrid(x_coords, y_coords)
    
    ax.contourf(X, Y, heatmap_data, levels=100, cmap=cmap, alpha=0.5)
    
    # Display in notebook if requested
    if display_in_notebook:
        plt.show()
    
    # Convert to base64 with white background
    buffer = io.BytesIO()
    plt.savefig(
        buffer, 
        format='png', 
        bbox_inches='tight', 
        dpi=100, 
        facecolor='white',
        edgecolor='none',
        transparent=False
    )
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close(fig)
    
    image_url = f"data:image/png;base64,{image_base64}"
    
    # Also display as HTML in notebook if requested
    if display_in_notebook:
        from IPython.display import HTML, display
        html_code = f'<img src="{image_url}" alt="Heatmap" style="max-width: 600px; border: 1px solid #ccc; background: white;">'
        display(HTML(html_code))
    
    return image_url
