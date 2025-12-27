import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# --- Page Config ---
st.set_page_config(page_title="Triomino Tiling Visualizer", layout="wide")

st.title("🧩 Defective Checkerboard Tiling")
st.markdown("This interactive tool uses **Divide and Conquer** to solve the defective checkerboard problem.")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Project Settings")
    n = st.slider("Select n (Size = 2^n)", 1, 6, 3)
    size = 2**n
    
    st.subheader("Missing Square Location")
    m_row = st.number_input("Row index", 0, size-1, 0)
    m_col = st.number_input("Column index", 0, size-1, 0)
    
    speed = st.select_slider("Animation Speed", options=[0.5, 0.2, 0.1, 0.05, 0.01], value=0.1)
    
    start_btn = st.button("🚀 Start Recursive Tiling", use_container_width=True)
    reset_btn = st.button("🔄 Reset Board", use_container_width=True)

# --- State Management ---
if 'board' not in st.session_state or reset_btn:
    st.session_state.board = np.zeros((size, size))
    st.session_state.board[m_row, m_col] = -1
    st.session_state.counter = 0

# --- Helper: Render the Board ---
def render_board(b, sz):
    fig, ax = plt.subplots(figsize=(7, 7))
    # Using 'prism' or 'tab20' for vibrant triomino colors
    # We set vmin=-1 and vmax to at least 1 to avoid the ValueError
    max_val = max(1, int(b.max()))
    im = ax.imshow(b, cmap='tab20', vmin=-1, vmax=max_val)
    
    # Draw Grid
    ax.set_xticks(np.arange(-.5, sz, 1), minor=True)
    ax.set_yticks(np.arange(-.5, sz, 1), minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=1)
    
    # Clean up labels
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

    # Quadrant Logic: Place center triomino pieces
    # If the missing square is NOT in a quadrant, place a piece in that quadrant's corner at the center
    
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

    # Update UI
    placeholder.pyplot(render_board(st.session_state.board, size))
    log_placeholder.write(f"Placed Triomino #{count} at center of {sz}x{sz} block.")
    time.sleep(speed)

    # Recurse for each quadrant
    # 1. Top Left
    new_m_r = m_r if (m_r < mid_r and m_c < mid_c) else mid_r-1
    new_m_c = m_c if (m_r < mid_r and m_c < mid_c) else mid_c-1
    solve(top, left, new_m_r, new_m_c, half, placeholder, log_placeholder)
    
    # 2. Top Right
    new_m_r = m_r if (m_r < mid_r and m_c >= mid_c) else mid_r-1
    new_m_c = m_c if (m_r < mid_r and m_c >= mid_c) else mid_c
    solve(top, mid_c, new_m_r, new_m_c, half, placeholder, log_placeholder)
    
    # 3. Bottom Left
    new_m_r = m_r if (m_r >= mid_r and m_c < mid_c) else mid_r
    new_m_c = m_c if (m_r >= mid_r and m_c < mid_c) else mid_c-1
    solve(mid_r, left, new_m_r, new_m_c, half, placeholder, log_placeholder)
    
    # 4. Bottom Right
    new_m_r = m_r if (m_r >= mid_r and m_c >= mid_c) else mid_r
    new_m_c = m_c if (m_r >= mid_r and m_c >= mid_c) else mid_c
    solve(mid_r, mid_c, new_m_r, new_m_c, half, placeholder, log_placeholder)

# --- Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    board_plot = st.empty()
    board_plot.pyplot(render_board(st.session_state.board, size))

with col2:
    st.subheader("Process Log")
    log_info = st.empty()
    log_info.write("Waiting to start...")

if start_btn:
    solve(0, 0, m_row, m_col, size, board_plot, log_info)
    st.balloons()
    st.success(f"Finished! Total Triominoes: {st.session_state.counter}")
