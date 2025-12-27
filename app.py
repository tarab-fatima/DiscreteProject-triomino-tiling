import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import time

# --- Page Config & Luxury Styling ---
st.set_page_config(page_title="The Induction Pavillion", layout="wide")

# Sophisticated Beige Theme CSS
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #FDF5E6; } 
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FDF5E6 !important;
        border-right: 2px ridge #735240;
    }
    
    /* Typography */
    .stMarkdown, h1, h2, h3, p { 
        color: #4E342E !important; 
        font-family: 'Optima', 'Candara', 'Segoe UI', sans-serif; 
    }
    
    /* Buttons */
    div.stButton > button {
        background-color: white; color: #FDF5E6;
        border-radius: 4px; border: none; height: 3em; width: 100%;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #FDF5E6; color: white;
    }
    
    /* Inputs */
    .stNumberInput input { background-color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Header Section ---
st.title("🏛️ The Induction Pavillion")
st.markdown("""
*An exploration of recursive symmetry and discrete space.* This installation visualizes the mathematical proof that any square grid of $2^n$ dimensions, 
possessing a single defect, can be perfectly harmonized using L-shaped triominoes.
""")
st.write("---")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Gallery Settings")
    n = st.slider("Size 'n' (2^n )", 1, 6, 3)
    size = 2**n
    
    st.subheader("The Defect")
    m_row = st.number_input("Vertical Axis", 0, size-1, 0)
    m_col = st.number_input("Horizontal Axis", 0, size-1, 0)
    
    speed = st.select_slider("Animation Cadence", options=[0.5, 0.1, 0.05, 0.01, 0.0], value=0.1)
    
    st.write("")
    start_btn = st.button("BEGIN TILING")

# --- Logic: Checkerboard Generation ---
def get_checkerboard(sz):
    re = np.r_[sz*[0,1]]
    ro = np.r_[sz*[1,0]]
    return np.array([re if i%2==0 else ro for i in range(sz)])[:sz,:sz]

# --- Helper: Visual Rendering ---
def render_board(tiling_matrix, sz, m_r, m_c):
    fig, ax = plt.subplots(figsize=(10, 10), facecolor='#FDF5E6')
    
    # 1. Base Checkerboard
    base = get_checkerboard(sz)
    # Using subtle cream and sand colors for the background squares
    base_display = np.where(base == 0, 0.8, 0.9)
    ax.imshow(base_display, cmap='YlOrBr', vmin=0, vmax=2)
    
    # 2. Triomino Overlay
    # A palette of sophisticated earth tones
    shades = ["#A1887F", "#8D6E63", "#795548", "#6D4C41", "#5D4037", "#4E342E", "#D7CCC8", "#BCAAA4"]
    custom_cmap = mcolors.ListedColormap(shades)
    
    tiling_visible = np.ma.masked_where(tiling_matrix <= 0, tiling_matrix)
    ax.imshow(tiling_visible, cmap=custom_cmap)
    
    # 3. The Defect (Deep Espresso)
    ax.add_patch(plt.Rectangle((m_c-0.5, m_r-0.5), 1, 1, color='#211512', zorder=10))

    # 4. Architectural Grid
    ax.set_xticks(np.arange(-.5, sz, 1), minor=True)
    ax.set_yticks(np.arange(-.5, sz, 1), minor=True)
    ax.grid(which='minor', color='#D7CCC8', linestyle='-', linewidth=0.8)
    
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values(): spine.set_visible(False)
    
    fig.tight_layout()
    return fig

# --- Recursive Solver ---
def solve_recursive(board, top, left, m_r, m_c, sz, plot_handle, status_handle, current_count):
    if sz == 1: return
    current_count[0] += 1
    count = current_count[0]
    half = sz // 2
    mid_r, mid_c = top + half, left + half

    # Core Logic
    if not (m_r < mid_r and m_c < mid_c): board[mid_r-1, mid_c-1] = count
    if not (m_r < mid_r and m_c >= mid_c): board[mid_r-1, mid_c] = count
    if not (m_r >= mid_r and m_c < mid_c): board[mid_r, mid_c-1] = count
    if not (m_r >= mid_r and m_c >= mid_c): board[mid_r, mid_c] = count

    # Render Frame
    fig = render_board(board, size, m_row, m_col)
    plot_handle.pyplot(fig)
    plt.close(fig) 
    
    status_handle.write(f"🏷️ **Sequential Placement**: {count}")
    if speed > 0: time.sleep(speed)

    # Quadrant Transitions
    solve_recursive(board, top, left, (m_r if (m_r < mid_r and m_c < mid_c) else mid_r-1), (m_c if (m_r < mid_r and m_c < mid_c) else mid_c-1), half, plot_handle, status_handle, current_count)
    solve_recursive(board, top, mid_c, (m_r if (m_r < mid_r and m_c >= mid_c) else mid_r-1), (m_c if (m_r < mid_r and m_c >= mid_c) else mid_c), half, plot_handle, status_handle, current_count)
    solve_recursive(board, mid_r, left, (m_r if (m_r >= mid_r and m_c < mid_c) else mid_r), (m_c if (m_r >= mid_r and m_c < mid_c) else mid_c-1), half, plot_handle, status_handle, current_count)
    solve_recursive(board, mid_r, mid_c, (m_r if (m_r >= mid_r and m_c >= mid_c) else mid_r), (m_c if (m_r >= mid_r and m_c >= mid_c) else mid_c), half, plot_handle, status_handle, current_count)

# --- Layout Control ---
col1, col2 = st.columns([2, 1])

with col1:
    board_ui = st.empty()
    initial_state = np.zeros((size, size))
    f = render_board(initial_state, size, m_row, m_col)
    board_ui.pyplot(f)
    plt.close(f)

with col2:
    st.write("### Curatorial Notes")
    st.write("""
    Observe how the recursive process handles complexity. By addressing the 
    central intersection first, we ensure that every quadrant is reduced to a 
    known state: a smaller board with exactly one defect.
    """)
    stat_ui = st.empty()

if start_btn:
    main_board = np.zeros((size, size))
    solve_recursive(main_board, 0, 0, m_row, m_col, size, board_ui, stat_ui, [0])
    st.snow()
    stat_ui.write("✨ **Harmony Restored.**")



