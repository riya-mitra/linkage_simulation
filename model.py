# Revised code for modeling the linkage system with correct positions

# Import required libraries
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Link lengths and initial angles
l_a = 4.0  # Length of input rod A
l_b = 3.0  # Length of connecting rod B
l_c = 3.0  # Length of other connecting rod C (same length as B)
l_d = 2.5  # Length of rods D1 and D2
l_e = 2.5  # Length of rods E1 and E2 (same length as D)
theta_initial = np.radians(45)  # Initial angle for theta
alpha_initial = np.radians(60)  # Initial angle for alpha (between D and E)

# Function to calculate positions of the joints
def calculate_positions(theta, alpha, beta):
    # Starting positions
    a_x_start = 0
    a_y_start = 0
    a_x_end = a_x_start + l_a * np.cos(theta)
    a_y_end = a_y_start + l_a * np.sin(theta)

    # Position of B
    b_x = a_x_start + (l_a / 2) * np.cos(theta)
    b_y = a_y_start + (l_a / 2) * np.sin(theta)

    # Position of C
    c_x = b_x + l_c * np.cos(beta)
    c_y = b_y + l_c * np.sin(beta)

    # Position of D1
    d1_x = a_x_end
    d1_y = a_y_end

    # Position of D2
    d2_x = a_x_end
    d2_y = a_y_end

    # Position of E1
    e1_x = d1_x + l_e * np.cos(alpha)
    e1_y = d1_y + l_e * np.sin(alpha)

    # Position of E2
    e2_x = d2_x - l_e * np.cos(alpha)
    e2_y = d2_y - l_e * np.sin(alpha)

    # Position of F (midpoint between E1 and E2)
    f_x = (e1_x + e2_x) / 2
    f_y = (e1_y + e2_y) / 2

    return {
        'A': ((a_x_start, a_y_start), (a_x_end, a_y_end)),
        'B': ((b_x, b_y), (c_x, c_y)),
        'C': ((c_x, c_y), (f_x, f_y)),
        'D1': ((a_x_end, a_y_end), (e1_x, e1_y)),
        'D2': ((a_x_end, a_y_end), (e2_x, e2_y)),
        'E1': ((d1_x, d1_y), (f_x, f_y)),
        'E2': ((d2_x, d2_y), (f_x, f_y)),
        'F': ((f_x, f_y), (f_x, f_y))  # Represent F as a point
    }

# Initialize plot
fig, ax = plt.subplots()
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)

# Create lines for each rod and set colors
lines = {}
colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black']
for idx, (name, _) in enumerate(calculate_positions(theta_initial, alpha_initial, theta_initial).items()):
    lines[name], = ax.plot([], [], color=colors[idx % len(colors)], lw=2, label=name)

# Initialize function for the animation
def init():
    for line in lines.values():
        line.set_data([], [])
    return lines.values()

# Animation function: This is called sequentially
def animate(i):
    # Calculate the current angle for alpha and beta
    alpha = alpha_initial + (np.pi / 2 - alpha_initial) * np.abs(np.sin(i / 50.0))
    beta = theta_initial + (np.pi - theta_initial) * np.abs(np.sin(i / 50.0))
    
    # Update positions based on the current angles
    positions = calculate_positions(theta_initial, alpha, beta)
    
    # Update the data for each line
    for name, line in lines.items():
        line.set_data(*positions[name])
    
    return lines.values()

# Create the animation
anim = FuncAnimation(fig, animate, init_func=init, frames=200, interval=50, blit=True)

plt.legend()
plt.show()