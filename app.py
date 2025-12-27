import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import time

# --- Page Config & Styling ---
st.set_page_config(page_title="Triomino Tiling Pro", layout="wide")

# Custom CSS for the Beige Theme
st.markdown("""
    <style>
    .stApp { background-color: #FDF5E6; } /* Old Lace Beige */
    .stMarkdown, h1, h2, h3 { color: #5D4037; font-family: 'Georgia', serif; }
    div.stButton > button {
        background-color: #8D6E63; color: white;
        border-radius: 2px; border: none; height: 3em; width: 100%;
    }
    /* Removes the blue background from info/success boxes */
    .stAlert { background-color: transparent !important; border: 1px solid #D7CCC8 !important; color: #5D4037 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Discrete Geometry: Triomino Tiling")

# --- Sidebar ---
with st.sidebar:
    st.header("Parameters")
    n = st.slider("Board Order (n)", 1, 6, 3)
    size = 2**n
    m_row = st.number_input("Missing Row", 0, size-1, 0)
    m_col = st.number_input("Missing Col", 0, size-1, 0)
    speed = st.select_slider("Animation Speed", options=[0.5, 0.1, 0.05, 0.01, 0.0], value=0.1)
    start_btn = st.button("EXECUTE TILING")

# --- Logic: Create a True Checkerboard Background ---
def get_checkerboard(sz):
    # Creates an alternating 0 and 1 pattern
    re = np.r_[sz*[0,1]]
    ro = np.r_[sz*[1,0]]
    return np.array([re if i%2==0 else ro for i in range(sz)])[:sz,:sz]

# --- Helper: Classy Render ---
def render_board(tiling_matrix, sz, m_r, m_c):
    fig, ax = plt.subplots(figsize=(10, 10), facecolor='#FDF5E6')
    
    # 1. Base Checkerboard (Beige and Cream)
    base = get_checkerboard(sz)
    # Map 0 -> 0.4 (Cream), 1 -> 0.5 (Light Beige)
    base_display = np.where(base == 0, 0.4, 0.5)
    
    # 2. Overlay the Triominoes
    # We use a custom brown/gold colormap
    colors = ["#3E2723", "#D7CCC8", "#F5F5DC", "#BCAAA4", "#A1887F", "#8D6E63", "#795548", "#6D4C41", "#5D4037"]
    custom_cmap = mcolors.ListedColormap(colors)
    
    # Show base checkerboard
    ax.imshow(base_display, cmap='YlOrBr', vmin=0, vmax=1)
    
    # Show triominoes on top (ignoring 0 and -1)
    tiling_visible = np.ma.masked_where(tiling_matrix <= 0, tiling_matrix)
    ax.imshow(tiling_visible, cmap=custom_cmap)
    
    # 3. Mark the Missing Square (Deep Bronze)
    ax.add_patch(plt.Rectangle((m_c-0.5, m_r-0.5), 1, 1, color='#3E2723', zorder=5))

    # 4. Clean Grid Lines
    ax.set_xticks(np.arange(-.5, sz, 1), minor=True)
    ax.set_yticks(np.arange(-.5, sz, 1), minor=True)
    ax.grid(which='minor', color='#A1887F', linestyle='-', linewidth=0.5)
    
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values(): spine.set_visible(False)
    
    fig.tight_layout()
    return fig

# --- Solver ---
def solve_recursive(board, top, left, m_r, m_c, sz, plot_handle, status_handle, current_count):
    if sz == 1: return
    current_count[0] += 1
    count = current_count[0]
    half = sz // 2
    mid_r, mid_c = top + half, left + half

    if not (m_r < mid_r and m_c < mid_c): board[mid_r-1, mid_c-1] = count
    if not (m_r < mid_r and m_c >= mid_c): board[mid_r-1, mid_c] = count
    if not (m_r >= mid_r and m_c < mid_c): board[mid_r, mid_c-1] = count
    if not (m_r >= mid_r and m_c >= mid_c): board[mid_r, mid_c] = count

    fig = render_board(board, size, m_row, m_col)
    plot_handle.pyplot(fig)
    plt.close(fig) 
    
    status_handle.write(f"**Step {count}**: Partitioning {sz}x{sz} sector...")
    if speed > 0: time.sleep(speed)

    solve_recursive(board, top, left, (m_r if (m_r < mid_r and m_c < mid_c) else mid_r-1), (m_c if (m_r < mid_r and m_c < mid_c) else mid_c-1), half, plot_handle, status_handle, current_count)
    solve_recursive(board, top, mid_c, (m_r if (m_r < mid_r and m_c >= mid_c) else mid_r-1), (m_c if (m_r < mid_r and m_c >= mid_c) else mid_c), half, plot_handle, status_handle, current_count)
    solve_recursive(board, mid_r, left, (m_r if (m_r >= mid_r and m_c < mid_c) else mid_r), (m_c if (m_r >= mid_r and m_c < mid_c) else mid_c-1), half, plot_handle, status_handle, current_count)
    solve_recursive(board, mid_r, mid_c, (m_r if (m_r >= mid_r and m_c >= mid_c) else mid_r), (m_c if (m_r >= mid_r and m_c >= mid_c) else mid_c), half, plot_handle, status_handle, current_count)

# --- Main Layout ---
col1, col2 = st.columns([2, 1])
with col1:
    board_container = st.empty()
    initial_board = np.zeros((size, size))
    f = render_board(initial_board, size, m_row, m_col)
    board_container.pyplot(f)
    plt.close(f)

with col2:
    st.write("### Methodology")
    st.write("This algorithm utilizes **Strong Induction**. By placing a central triomino, we reduce one $2^n$ problem into four $2^{n-1}$ sub-problems.")
    stat_box = st.empty()

if start_btn:
    main_board = np.zeros((size, size))
    solve_recursive(main_board, 0, 0, m_row, m_col, size, board_container, stat_box, [0])
    st.snow()
    stat_box.write("**Tiling Complete.**")
