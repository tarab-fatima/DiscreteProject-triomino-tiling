import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# --- Page Config & Classy Styling ---
st.set_page_config(page_title="Triomino Tiling Pro", layout="wide")

# Custom CSS for a Beige/Minimalist Theme
st.markdown("""
    <style>
    .stApp {
        background-color: #F5F5DC; /* Soft Beige */
    }
    .stMarkdown, .stHeader {
        color: #4b3621; /* Deep Earth Brown */
    }
    div.stButton > button {
        background-color: #d2b48c; /* Tan */
        color: white;
        border-radius: 5px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🗂️ Recursive Tiling Analysis")
st.markdown("### *A Study in Discrete Geometry and Induction*")

# --- Sidebar ---
with st.sidebar:
    st.header("Parameters")
    n = st.slider("Board Order (n)", 1, 6, 3)
    size = 2**n
    
    st.subheader("Defect Position")
    m_row = st.number_input("Row Index", 0, size-1, 0)
    m_col = st.number_input("Col Index", 0, size-1, 0)
    
    speed = st.select_slider("Animation Interval", options=[0.5, 0.1, 0.05, 0.01, 0.0], value=0.1)
    
    start_btn = st.button("Execute Algorithm", use_container_width=True)

# --- Helper: Classy Render ---
def render_board(b, sz):
    # Use a warm, professional color map
    fig, ax = plt.subplots(figsize=(8, 8), facecolor='#F5F5DC')
    
    # We use 'copper' for a metallic/beige gradient
    current_max = max(1, int(b.max()))
    ax.imshow(b, cmap='copper', vmin=-1, vmax=current_max)
    
    # Minimalist border instead of grid
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor('#4b3621')
        spine.set_linewidth(2)
        
    fig.tight_layout()
    return fig

# --- Recursive Solver ---
def solve_recursive(board, top, left, m_r, m_c, sz, plot_handle, status_handle, current_count):
    if sz == 1:
        return
    
    current_count[0] += 1
    count = current_count[0]
    half = sz // 2
    mid_r, mid_c = top + half, left + half

    # Logic: Place center triomino
    if not (m_r < mid_r and m_c < mid_c): board[mid_r-1, mid_c-1] = count
    if not (m_r < mid_r and m_c >= mid_c): board[mid_r-1, mid_c] = count
    if not (m_r >= mid_r and m_c < mid_c): board[mid_r, mid_c-1] = count
    if not (m_r >= mid_r and m_c >= mid_c): board[mid_r, mid_c] = count

    # Visual Refresh
    fig = render_board(st.session_state.board, size)
    plot_handle.pyplot(fig)
    plt.close(fig) 
    
    status_handle.caption(f"Iterating Step {count}...")
    if speed > 0: time.sleep(speed)

    # Quadrant Recursion
    solve_recursive(board, top, left, (m_r if (m_r < mid_r and m_c < mid_c) else mid_r-1), (m_c if (m_r < mid_r and m_c < mid_c) else mid_c-1), half, plot_handle, status_handle, current_count)
    solve_recursive(board, top, mid_c, (m_r if (m_r < mid_r and m_c >= mid_c) else mid_r-1), (m_c if (m_r < mid_r and m_c >= mid_c) else mid_c), half, plot_handle, status_handle, current_count)
    solve_recursive(board, mid_r, left, (m_r if (m_r >= mid_r and m_c < mid_c) else mid_r), (m_c if (m_r >= mid_r and m_c < mid_c) else mid_c-1), half, plot_handle, status_handle, current_count)
    solve_recursive(board, mid_r, mid_c, (m_r if (m_r >= mid_r and m_c >= mid_c) else mid_r), (m_c if (m_r >= mid_r and m_c >= mid_c) else mid_c), half, plot_handle, status_handle, current_count)

# --- Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    board_container = st.empty()
    # Initialize session board for rendering
    if 'board' not in st.session_state or st.session_state.board.shape[0] != size:
        st.session_state.board = np.zeros((size, size))
        st.session_state.board[m_row, m_col] = -1
    
    f = render_board(st.session_state.board, size)
    board_container.pyplot(f)
    plt.close(f)

with col2:
    st.info("The board is divided into four quadrants. One triomino is placed at the intersection to bridge the gaps, effectively creating one sub-problem per quadrant.")
    stat_box = st.empty()

if start_btn:
    st.session_state.board = np.zeros((size, size))
    st.session_state.board[m_row, m_col] = -1
    
    solve_recursive(st.session_state.board, 0, 0, m_row, m_col, size, board_container, stat_box, [0])
    st.snow() # Elegant alternative to balloons
    stat_box.success("Optimization Complete.")
