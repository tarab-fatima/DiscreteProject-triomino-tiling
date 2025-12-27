import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# --- Page Config ---
st.set_page_config(page_title="Triomino Tiling Visualizer", layout="wide")

st.title("🧩 Defective Checkerboard Tiling")
st.markdown("A demonstration of **Recursive Divide & Conquer**.")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Project Settings")
    n = st.slider("Select n (Size = 2^n)", 1, 6, 3)
    size = 2**n
    
    st.subheader("Missing Square Location")
    m_row = st.number_input("Row index", 0, size-1, 0)
    m_col = st.number_input("Column index", 0, size-1, 0)
    
    speed = st.select_slider("Animation Speed", options=[0.5, 0.1, 0.05, 0.01, 0.0], value=0.1)
    
    start_btn = st.button("🚀 Start Recursive Tiling", use_container_width=True)
    
    if st.button("🔄 Reset Board", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- CRITICAL: Reset board if settings change to prevent IndexError ---
if 'board' not in st.session_state or st.session_state.board.shape[0] != size:
    st.session_state.board = np.zeros((size, size))
    st.session_state.board[m_row, m_col] = -1
    st.session_state.counter = 0

# Also check if the 'missing square' in memory matches the input
if st.session_state.board[m_row, m_col] != -1:
    st.session_state.board = np.zeros((size, size))
    st.session_state.board[m_row, m_col] = -1
    st.session_state.counter = 0

# --- Helper: Render the Board ---
def render_board(b, sz):
    fig, ax = plt.subplots(figsize=(8, 8)) 
    max_val = max(1, int(b.max()))
    
    # Using 'tab20' for colors
    ax.imshow(b, cmap='tab20', vmin=-1, vmax=max_val)
    
    if sz <= 16: # Only draw grid for smaller boards to save memory/space
        ax.set_xticks(np.arange(-.5, sz, 1), minor=True)
        ax.set_yticks(np.arange(-.5, sz, 1), minor=True)
        ax.grid(which='minor', color='white', linestyle='-', linewidth=1)
    
    ax.set_xticks([])
    ax.set_yticks([])
    return fig

# --- The Algorithm ---
def solve(top, left, m_r, m_c, sz, placeholder, log_placeholder):
    if sz == 1:
        return
    
    st.session_state.counter += 1
    count = st.session_state.counter
    half = sz // 2
    mid_r, mid_c = top + half, left + half

    # Place center triomino
    if not (m_r < mid_r and m_c < mid_c):
        st.session_state.board[mid_r-1, mid_c-1] = count
    if not (m_r < mid_r and m_c >= mid_c):
        st.session_state.board[mid_r-1, mid_c] = count
    if not (m_r >= mid_r and m_c < mid_c):
        st.session_state.board[mid_r, mid_c-1] = count
    if not (m_r >= mid_r and m_c >= mid_c):
        st.session_state.board[mid_r, mid_c] = count

    # Visual Update & Memory Management
    fig = render_board(st.session_state.board, size)
    placeholder.pyplot(fig)
    plt.close(fig) # THIS FIXES THE RUNTIME WARNING (Memory leak)
    
    log_placeholder.info(f"Step {count}: Tiling {sz}x{sz} section")
    if speed > 0:
        time.sleep(speed)

    # Recursive calls
    solve(top, left, (m_r if (m_r < mid_r and m_c < mid_c) else mid_r-1), 
          (m_c if (m_r < mid_r and m_c < mid_c) else mid_c-1), half, placeholder, log_placeholder)
    solve(top, mid_c, (m_r if (m_r < mid_r and m_c >= mid_c) else mid_r-1), 
          (m_c if (m_r < mid_r and m_c >= mid_c) else mid_c), half, placeholder, log_placeholder)
    solve(mid_r, left, (m_r if (m_r >= mid_r and m_c < mid_c) else mid_r), 
          (m_c if (m_r >= mid_r and m_c < mid_c) else mid_c-1), half, placeholder, log_placeholder)
    solve(mid_r, mid_c, (m_r if (m_r >= mid_r and m_c >= mid_c) else mid_r), 
          (m_c if (m_r >= mid_r and m_c >= mid_c) else mid_c), half, placeholder, log_placeholder)

# --- Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    board_plot = st.empty()
    initial_fig = render_board(st.session_state.board, size)
    board_plot.pyplot(initial_fig)
    plt.close(initial_fig)

with col2:
    status_box = st.empty()
    status_box.write("Click Start to begin.")
    
    with st.expander("How it works (Induction)"):
        st.write("""
        1. **Base Case**: A 2x2 board with 1 hole is an L-triomino.
        2. **Divide**: Split the board into 4 quadrants.
        3. **Bridge**: Place 1 triomino in the center to create a 'hole' in the 3 quadrants that didn't have one.
        4. **Conquer**: Now you have four smaller boards, each with 1 hole. Repeat!
        """)

if start_btn:
    st.session_state.counter = 0
    solve(0, 0, m_row, m_col, size, board_plot, status_box)
    st.balloons()
