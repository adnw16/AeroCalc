
import numpy as np
import requests
from scipy.integrate import quad
import matplotlib.pyplot as plt
import os
import webbrowser
import sys
from pytsfoil import run_airfoil_analysis


# fetch api key from foil.tools
def get_airfoil_coords(airfoil_name):
    url = f"https://foil.tools/api/v1/airfoils/{airfoil_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        coords = data['coords']
        print(f"Successfully fetched data for {airfoil_name}")
        return coords
    except requests.exceptions.RequestException as error:
        print(f"Error fetching data: {error}")
        return None

# 2. Function to separate upper surface and fit a polynomial
def fit_upper_surface(coords, degree=7):
  
    points = np.array(coords)
    
    print(f"Points shape: {points.shape}") #should be a in form [x, 2], where x is the number of data points  
    # coordinate data goes from Trailing Edge (x = 1) then back to Leading Edge (x = 0)
    # filter for upper surface (y >= 0).
    upper_points = points[points[:, 1] >= 0]
    
    # sort by x for proper integration limits
    upper_points = upper_points[np.argsort(upper_points[:, 0])]
    
    x_upper = upper_points[:, 0]
    y_upper = upper_points[:, 1]
    
    # polynomial fit calculation using numpy
    try:
        coeffs = np.polyfit(x_upper, y_upper, degree)
        poly_func = np.poly1d(coeffs)
        
        r_squared = calculate_r_squared(y_upper, poly_func(x_upper))
        print(f"Fitted a {degree}-degree polynomial with R^2 = {r_squared:.4f}")
        return poly_func, x_upper, y_upper, r_squared
    except np.linalg.LinAlgError as e:
        print(f"Error fitting polynomial: {e}")
        print("Trying with a lower degree...")
        # try a lower degree in case of error
        coeffs = np.polyfit(x_upper, y_upper, min(degree-2, 5))
        poly_func = np.poly1d(coeffs)
        r_squared = calculate_r_squared(y_upper, poly_func(x_upper))
        print(f"Fitted a {min(degree-2, 5)}-degree polynomial with R^2 = {r_squared:.4f}")
        return poly_func, x_upper, y_upper, r_squared

def calculate_r_squared(y_true, y_pred): #using total and residual sum of squares
    ss_res = np.sum((y_true - y_pred) ** 2) 
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot) #how much variance is explained by the polyfit model

# integral function definitions
def volume(f, a, b):
    integrand = lambda x: np.pi * f(x)**2 #volume of revolution equation
    return quad(integrand, a, b)[0]

def surface_area(f, a, b): #using derived formula from paper
    def integrand(x):
        h = 1e-6 #step size for numeric integration
        # first principle derivative definition
        f_prime = (f(x + h) - f(x - h)) / (2 * h)
        return 2 * np.pi * f(x) * np.sqrt(1 + f_prime**2)
    return quad(integrand, a, b)[0]

#main execution
if __name__ == "__main__":
    # user input for name of airfoil
    airfoil_name = sys.argv[1].strip().lower()
    coords = get_airfoil_coords(airfoil_name)
    
    if coords is None:
        print("Exiting due to API error.")
        exit()
    
    # try different polynomial degrees
    degrees_to_try = [5, 6, 7, 8]
    results = []
    
    for degree in degrees_to_try:
        print(f"\n--- Trying degree {degree} ---")
        try:
            f_airfoil, x_upper, y_upper, r_squared = fit_upper_surface(coords, degree=degree)
            
            # integration limits (x from 0 to 1 for data from foil.tools)
            a, b = 0.0, 1.0
            
            # calculate volume and surface area
            V = volume(f_airfoil, a, b)
            SA = surface_area(f_airfoil, a, b)
            ratio = SA / V
            
            results.append({
                'degree': degree,
                'r_squared': r_squared,
                'volume': V,
                'surface_area': SA,
                'ratio': ratio
            })
            
            print(f"Degree {degree}: R²={r_squared:.4f}, SA:V={ratio:.5f}")
            
        except Exception as e:
            print(f"Failed for degree {degree}: {e}")
    
    # Show best result
    if results:
        best_result = max(results, key=lambda x: x['r_squared'])
        f_airfoil, _, _, _ = fit_upper_surface(coords, degree=best_result['degree'])
        
        x_plot = np.linspace(0.0, 1.0, 500)
        y_plot = f_airfoil(x_plot)
        
        # Get upper points for plotting
        if isinstance(coords[0], dict):
            points = np.array([[p['x'], p['y']] for p in coords])
        else:
            points = np.array(coords)
            upper_points = points[points[:, 1] >= 0]
            upper_points = upper_points[np.argsort(upper_points[:, 0])]
            
            # Create the figure
            plt.figure(figsize=(12, 5))
            
            # Left subplot: Upper surface
            plt.subplot(1, 2, 1)
            plt.plot(upper_points[:, 0], upper_points[:, 1], 'o', 
                    label='API Upper Surface Points', markersize=3, alpha=0.5)
            plt.plot(x_plot, y_plot, '-', 
                    label=f'{best_result["degree"]}-degree Polynomial Fit\n(R²={best_result["r_squared"]:.4f})', 
                    linewidth=2)
            plt.title(f'{airfoil_name.upper()} Airfoil: Upper Surface')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Right subplot: Body of revolution (cross-section)
            plt.subplot(1, 2, 2)
            plt.plot(x_plot, y_plot, '-', linewidth=2, label='Radius r(x)')
            plt.fill_between(x_plot, 0, y_plot, alpha=0.3)
            
            # Also show the negative side for symmetry
            plt.plot(x_plot, -y_plot, '--', linewidth=1, alpha=0.5, label='-r(x)')
            plt.title(f'{airfoil_name.upper()} Body of Revolution Cross-Section')
            plt.xlabel('x (along length)')
            plt.ylabel('r(x) (radius)')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.axis('equal')  # Makes the circle look round
            
            plt.tight_layout()
            
            # Display the plot with blocking
            print("\nDisplaying plot...")
            plt.show(block=True)  # <-- This ensures the plot stays open
            
            # Optional: Save the plot to a file
            # plt.savefig(f'{airfoil_name}_analysis.png', dpi=300, bbox_inches='tight')
            # print(f"Plot saved as {airfoil_name}_analysis.png")
            # --- SAVE THE PLOT AS IMAGE ---
        filename = f'{airfoil_name}_analysis.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Get the absolute path
        filepath = os.path.abspath(filename)
        print(f"\n✅ Plot saved as: {filepath}")
        
        # --- OPEN IN BROWSER ---
        try:
            webbrowser.open(filepath)
            print("🌐 Plot opened in your default browser!")
        except Exception as e:
            print(f"Could not open in browser automatically: {e}")
            print(f"Please manually open the file: {filepath}")
        
        # Close the figure to free memory
        plt.close()
        
        print("\n" + "="*50)
        print("✅ Analysis complete!")
        print("="*50)