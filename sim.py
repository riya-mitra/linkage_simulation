import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# global variables and initial inputs
# these are the lengths i made my prototype with but you can change them in order to test different values

l_a = 4.0 # Length of input rod A
l_f = l_a
l_d = 2.5  # Length of rods D
l_e = l_d  # Length of rods E (same length as D)
l_b = 3 # Length of rod B
l_c = l_b  # Length of rod C (same length as B)
l_p = 0.5

theta = np.radians(120)
alpha = np.radians(40)
gamma = np.radians(40)
omega = np.radians(50)

frozen = False
theta_snap_back = False

a_pos = 15
snap_frame = None
phase_offset = 0

alpha_max = np.radians(80)
alpha_min = np.radians(10)
theta_max = np.radians(160)
theta_min = np.radians(110)
gamma_min = np.radians(0)
gamma_max = np.radians(40)

max_height_tracker = {'max_height': 0}


def calculate_positions(a_x_start, theta, alpha, gamma, omega):
    

    fixed_point_x = 13.5
    fixed_point_y = 5
    
    # link A
    a_x = a_x_start - l_a
    a_y = 5
    
    # link B
    b_x = fixed_point_x - l_b * np.cos(gamma)
    b_y = fixed_point_y - l_b * np.sin(gamma)
    
    # link D
    d1_x = a_x + l_d * np.cos(theta)
    d1_y = a_y + l_d * np.sin(theta)
    
    d2_x = a_x + l_d * np.cos(theta)
    d2_y = a_y - l_d * np.sin(theta)
    
    # link E
    fixed_e_y = 5  # y-coordinate for E1 and E2

    # Link E1
    delta_y_e1 = fixed_e_y - d1_y
    delta_x_e1 = np.sqrt(l_e**2 - delta_y_e1**2) if l_e**2 >= delta_y_e1**2 else 0
    e1_x = d1_x + delta_x_e1 if d1_y < fixed_e_y else d1_x - delta_x_e1

    # Link E2
    delta_y_e2 = fixed_e_y - d2_y
    if l_e**2 >= delta_y_e2**2:
        delta_x_e2 = np.sqrt(l_e**2 - delta_y_e2**2)
        e2_x = d2_x - delta_x_e2 if theta <= np.pi else d2_x + delta_x_e2
    else:
        e2_x = d2_x 
        
    # link C

    common_end_x = (e1_x + e2_x) / 2
    common_end_y = 5  # Ensuring that the y-coordinate is exactly 5

    # Calculating the x-component based on the fixed length l_c
    dx = np.sqrt(l_c**2 - (common_end_y - b_y)**2) if l_c**2 >= (common_end_y - b_y)**2 else 0
    if common_end_x >= b_x:
        common_end_x = b_x + dx  # Assuming common_end_x should be to the right of B
    else:
        common_end_x = b_x - dx  # Assuming common_end_x should be to the left of B
    
    c_x = common_end_x
    c_y = common_end_y
    
    # link F
    
    f_start_x = e1_x
    f_start_y = fixed_e_y
    
    f_x = f_start_x - l_f
    f_y = f_start_y
    
    # pushdown link
    
    e1_mid_x = d1_x + (e1_x - d1_x) / 2
    e1_mid_y = d1_y + (fixed_point_y - d1_y) / 2
    
    e1_dir_x = e1_x - d1_x
    e1_dir_y = fixed_point_y - d1_y
    
    # The direction vector for E1
    length = np.sqrt(e1_dir_x**2 + e1_dir_y**2)
    e1_dir_x /= length
    e1_dir_y /= length
    
    cos_angle = np.cos(np.radians(80))
    sin_angle = np.sin(np.radians(80))
    pushdown_dir_x = e1_dir_x * cos_angle - e1_dir_y * sin_angle
    pushdown_dir_y = e1_dir_x * sin_angle + e1_dir_y * cos_angle
    
    pushdown_end_x = e1_mid_x + pushdown_dir_x * l_p
    pushdown_end_y = e1_mid_y + pushdown_dir_y * l_p


    max_height_tracker['max_height'] = max(max_height_tracker['max_height'], d1_y - 5, d2_y - 5)
    
    positions = {
        'A' : ([a_x, a_x_start], [a_y, a_y]),
        'B' : ([fixed_point_x, b_x], [fixed_point_y, b_y]),
        'C' : ([b_x, c_x], [b_y, c_y]), 
        'D1' : ([a_x, d1_x], [a_y, d1_y]), 
        'D2' : ([a_x, d2_x], [a_y, d2_y]), 
        'E1' : ([d1_x, e1_x], [d1_y, fixed_e_y]),
        'E2' : ([d2_x, e2_x], [d2_y, fixed_e_y]),
        'F' : ([e1_x, f_x], [fixed_e_y, f_y]),
        'Pushdown' : ([e1_mid_x, pushdown_end_x], [e1_mid_y, pushdown_end_y]),
        'Intersection1' : ([d1_x], [d1_y]),
        'Intersection2' : ([d2_x], [d2_y])
    }
    return positions


# Initialize the plot
initial_positions = calculate_positions(15, theta, alpha, gamma, omega)
lines = {}
markers = {}
colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'pink', 'purple', 'orange']
fig, ax = plt.subplots()
ax.set_xlim(0, 30)
ax.set_ylim(0, 15)  
ax.set_aspect('equal')

max_height_text = ax.text(1, 14, '', fontsize=9)

for idx, (name, coords) in enumerate(initial_positions.items()):
    if 'Intersection' in name:
        markers[name], = ax.plot(*coords, 'o', color='black')
    else:
        lines[name], = ax.plot(*coords, color=colors[idx % len(colors)], lw=2, label=name)

# plot the background of each frame
def init():
    for name, line in lines.items():
        line.set_data(*initial_positions[name])
    for name, marker in markers.items():
        marker.set_data([], [])
    max_height_text.set_text('')
    return list(lines.values()) + list(markers.values()) + [max_height_text]


def animate(frame):
    global theta, alpha, gamma, omega, frozen, theta_snap_back, snap_frame, phase_offset

    theta_mid = (theta_max + theta_min) / 2
    gamma_mid = (gamma_max + gamma_min) / 2
    
    theta_amp = (theta_max - theta_min) / 2
    gamma_amp = (gamma_max - gamma_min) / 2
    
    speed = 0.02
    
    a_x_offset = np.cos(frame * speed)
    
    a_x_start = 15 + a_x_offset * 2  # Oscillates A around x=15 with amplitude 2

    if not theta_snap_back:
        theta = theta_mid + theta_amp * np.cos(frame * speed)
        theta = np.clip(theta, theta_min, theta_max)
    else:
        # Maintain the snap and adjust phase to continue smoothly
        if snap_frame is None:
            snap_frame = frame
            theta = np.radians(120)
            arg = (theta - theta_mid) / theta_amp
            arg = np.clip(arg, -1, 1)
            phase_offset = np.arccos(arg)
            
            
            
        theta = theta_mid + theta_amp * np.cos(frame * speed + phase_offset)
        theta = np.clip(theta, theta_min, theta_max)
        gamma = gamma_mid + gamma_amp * np.cos(frame * speed + phase_offset)
        gamma = np.clip(gamma, gamma_min, gamma_max)

    positions = calculate_positions(a_x_start, theta, alpha, gamma, omega)
    
    pushdown_end_x, pushdown_end_y = positions['Pushdown'][0][-1], positions['Pushdown'][1][-1]
    
    b_y = positions['B'][1][1]
    
    if 4.9 <= b_y <= 5.5:
        frozen = True
        snap_frame = frame
    
    if not frozen:
        gamma = gamma_mid + gamma_amp * np.cos(frame * speed)
        gamma = np.clip(gamma, gamma_min, gamma_max)
        
    if frozen:
        gamma = 0
        b_y = 5
        if pushdown_end_y <= 5.1:
            frozen = False
            theta_snap_back = True
            snap_frame = None
            gamma = gamma_mid + gamma_amp * np.cos(frame * speed)
            gamma = np.clip(gamma, gamma_min, gamma_max)
            
    
    # if theta_snap_back:
    #     theta = np.radians(100)
    #     positions = calculate_positions(a, theta, alpha, gamma, omega)
    #     theta_snap_back = False
        
        # theta_snap_back = False
    # else:
    #     theta = theta_mid + theta_amp * np.cos(frame * speed)
    #     theta = np.clip(theta, theta_min, theta_max)
        
    
    positions = calculate_positions(a_x_start, theta, alpha, gamma, omega)
    print(frozen)
    
    
    # gamma = gamma_mid + gamma_amp * np.cos(frame * speed)
    # gamma = np.clip(gamma, gamma_min, gamma_max)

    
    for name, marker in markers.items():
        marker.set_data(*positions[name])
    
    max_height_text.set_text(f'Max Distance: {max_height_tracker["max_height"]:.2f}')
    
    # Update the lines with the new positions
    for name, line in lines.items():
        line.set_data(*positions[name])
    return list(lines.values()) + list(markers.values()) + [max_height_text]

# Create the animation object
anim = FuncAnimation(fig, animate, init_func=init, frames=360, interval=20, blit=False)

plt.legend()
plt.show()