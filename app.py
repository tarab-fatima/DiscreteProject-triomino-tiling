import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# --- Page Config ---
st.set_page_config(page_title="Triomino Tiling Visualizer", layout="wide")

st.title("🧩 Defective Checkerboard Tiling")
st.markdown("A demonstration of **Strong Induction** and **Recursive Divide & Conquer**.")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Project Settings")
    n = st.slider("Select n (Size = 2^n)", 1, 6, 3)
    size = 2**n
    
    st.subheader("Missing Square Location")
    # Dynamic bounds for inputs based on current 'size'
    m_row = st.number_input("Row index", 0, size-1, 0)
    m_col = st.number_input("Column index", 0, size-1, 0)
    
    speed = st.select_slider("Animation Speed", options=[0.5, 0.2, 0.1, 0.05, 0.01, 0.0], value=0.1)
    
    start_btn = st.button("🚀 Start Recursive Tiling", use_container_width=True)
    if st.button("🔄 Reset Board", use_container_width=True):
        st.session_state.board = np.zeros((size, size))
        st.session_state.board[m_row, m_col] = -1
        st.session_state.counter = 0
        st.rerun()

# --- Logic: Ensure Board matches current Slider Size ---
# This prevents the IndexError!
if 'board' not in st.session_state or st.session_state.board.shape[0] != size:
    st.session_state.board = np.zeros((size, size))
    st.session_state.board[m_row, m_col] = -1
    st.session_state.counter = 0

# --- Helper: Render the Board ---
def render_board(b, sz):
    # Set a consistent figure size that doesn't shrink
    fig, ax = plt.subplots(figsize=(10, 10)) 
    max_val = max(1, int(b.max()))
    
    # Using 'tab20b' for more distinct colors in large grids
    ax.imshow(b, cmap='tab20b', vmin=-1, vmax=max_val)
    
    # Grid lines - only show them for smaller N to keep it clean
    if sz <= 32:
        ax.set_xticks(np.arange(-.5, sz, 1), minor=True)
        ax.set_yticks(np.arange(-.5, sz, 1), minor=True)
        ax.grid(which='minor', color='white', linestyle='-', linewidth=0.5)
    
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    return fig

# --- The Algorithm ---
def solve(top, left, m_r, m_c, sz, placeholder, log_placeholder):
    if sz == 1:
        return
    
    st.session_state.counter += 1
    count = st.session_state.counter
    half = sz // 2
    mid_r, mid_c = top + half, left + half

    # 1. Place Triomino in the center (covering quadrants without the hole)
    # Top Left
    if not (m_r < mid_r and m_c < mid_c):
        st.session_state.board[mid_r-1, mid_c-1] = count
    # Top Right
    if not (m_r < mid_r and m_c >= mid_c):
        st.session_state.board[mid_r-1, mid_c] = count
    # Bottom Left
    if not (m_r >= mid_r and m_c < mid_c):
        st.session_state.board[mid_r, mid_c-1] = count
    # Bottom Right
    if not (m_r >= mid_r and m_c >= mid_c):
        st.session_state.board[mid_r, mid_c] = count

    # 2. Visual Update
    placeholder.pyplot(render_board(st.session_state.board, size))
    log_placeholder.info(f"Step {count}: Sub-problem size {sz}x{sz}")
    if speed > 0:
        time.sleep(speed)

    # 3. Recursive Calls for 4 quadrants
    # Top Left
    solve(top, left, (m_r if (m_r < mid_r and m_c < mid_c) else mid_r-1), 
          (m_c if (m_r < mid_r and m_c < mid_c) else mid_c-1), half, placeholder, log_placeholder)
    # Top Right
    solve(top, mid_c, (m_r if (m_r < mid_r and m_c >= mid_c) else mid_r-1), 
          (m_c if (m_r < mid_r and m_c >= mid_c) else mid_c), half, placeholder, log_placeholder)
    # Bottom Left
    solve(mid_r, left, (m_r if (m_r >= mid_r and m_c < mid_c) else mid_r), 
          (m_c if (m_r >= mid_r and m_c < mid_c) else mid_c-1), half, placeholder, log_placeholder)
    # Bottom Right
    solve(mid_r, mid_c, (m_r if (m_r >= mid_r and m_c >= mid_c) else mid_r), 
          (m_c if (m_r >= mid_r and m_c >= mid_c) else mid_c), half, placeholder, log_placeholder)

# --- Main UI Layout ---
col1, col2 = st.columns([3, 1])

with col1:
    # This container ensures the plot stays large
    with st.container():
        board_plot = st.empty()
        board_plot.pyplot(render_board(st.session_state.board, size))

with col2:
    st.subheader("Live Status")
    status_box = st.empty()
    status_box.write("Ready to begin...")
    
    if st.session_state.counter > 0:
        st.metric("Triominoes Placed", st.session_state.counter)

if start_btn:
    # Reset counter before starting
    st.session_state.counter = 0
    solve(0, 0, m_row, m_col, size, board_plot, status_box)
    st.balloons()
    status_box.success("Success! Board fully tiled.")
