import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# --- Page Config ---
st.set_page_config(page_title="Triomino Tiling Visualizer", layout="wide")

st.title("🧩 Defective Checkerboard Tiling")
st.markdown("This project uses **Mathematical Induction** to tile a board with a missing square.")

# --- Sidebar ---
with st.sidebar:
    st.header("Project Settings")
    n = st.slider("Select n (Size = 2^n)", 1, 6, 3)
    size = 2**n
    
    st.subheader("Missing Square Location")
    m_row = st.number_input("Row index", 0, size-1, 0)
    m_col = st.number_input("Column index", 0, size-1, 0)
    
    speed = st.select_slider("Animation Speed", options=[0.5, 0.1, 0.05, 0.01, 0.0], value=0.1)
    
    start_btn = st.button("🚀 Start Recursive Tiling", use_container_width=True)
    
    if st.button("🔄 Reset Everything", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Initialize State ---
if 'board' not in st.session_state or st.session_state.get('last_n') != n:
    st.session_state.board = np.zeros((size, size))
    st.session_state.board[m_row, m_col] = -1
    st.session_state.counter = 0
    st.session_state.last_n = n

# --- Helper: Render the Board ---
def render_board(b, sz):
    fig, ax = plt.subplots(figsize=(8, 8)) 
    # vmin/vmax ensures the colormap doesn't crash even if board is empty
    current_max = max(1, int(b.max()))
    
    # Modern matplotlib colormap access
    im = ax.imshow(b, cmap='tab20b', vmin=-1, vmax=current_max)
    
    if sz <= 16:
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

    # 1. Place the L-triomino at the center
    # Top Left quadrant
    if not (m_r < mid_r and m_c < mid_c):
        st.session_state.board[mid_r-1, mid_c-1] = count
    # Top Right quadrant
    if not (m_r < mid_r and m_c >= mid_c):
        st.session_state.board[mid_r-1, mid_c] = count
    # Bottom Left quadrant
    if not (m_r >= mid_r and m_c < mid_c):
        st.session_state.board[mid_r, mid_c-1] = count
    # Bottom Right quadrant
    if not (m_r >= mid_r and m_c >= mid_c):
        st.session_state.board[mid_r, mid_c] = count

    # 2. Update UI and prevent Memory Leak
    fig = render_board(st.session_state.board, size)
    placeholder.pyplot(fig)
    plt.close(fig) 
    
    log_placeholder.info(f"Step {count}: Tiling {sz}x{sz} section")
    if speed > 0:
        time.sleep(speed)

    # 3. Recurse for each quadrant
    solve(top, left, (m_r if (m_r < mid_r and m_c < mid_c) else mid_r-1), 
          (m_c if (m_r < mid_r and m_c < mid_c) else mid_c-1), half, placeholder, log_placeholder)
    solve(top, mid_c, (m_r if (m_r < mid_r and m_c >= mid_c) else mid_r-1), 
          (m_c if (m_r < mid_r and m_c >= mid_c) else mid_c), half, placeholder, log_placeholder)
    solve(mid_r, left, (m_r if (m_r >= mid_r and m_c < mid_c) else mid_r), 
          (m_c if (m_r >= mid_r and m_c < mid_c) else mid_c-1), half, placeholder, log_placeholder)
    solve(mid_r, mid_c, (m_r if (m_r >= mid_r and m_c >= mid_c) else mid_r), 
          (m_c if (m_r >= mid_r and m_c >= mid_c) else mid_c), half, placeholder, log_placeholder)

# --- Main Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    board_plot = st.empty()
    # Initial render
    f = render_board(st.session_state.board, size)
    board_plot.pyplot(f)
    plt.close(f)

with col2:
    status_box = st.empty()
    status_box.write("Click the button to start the recursion.")
    
    if st.session_state.counter > 0:
        st.metric("Total Triominoes", st.session_state.counter)

if start_btn:
    st.session_state.counter = 0
    # Clear board before starting a new run
    st.session_state.board = np.zeros((size, size))
    st.session_state.board[m_row, m_col] = -1
    
    solve(0, 0, m_row, m_col, size, board_plot, status_box)
    st.balloons()
    status_box.success("Board fully tiled!")
