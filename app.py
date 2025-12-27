import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# --- Page Config ---
st.set_page_config(page_title="Triomino Tiling Solver", layout="wide")

st.title("🧩 Defective Checkerboard Tiling")
st.write("Solving $2^n \\times 2^n$ boards using Recursive Induction.")

# --- Sidebar ---
with st.sidebar:
    st.header("Configuration")
    n = st.slider("Select n (Size $2^n$)", 1, 6, 3)
    size = 2**n
    
    st.subheader("Missing Square")
    m_row = st.number_input("Row (0 to size-1)", 0, size-1, 0)
    m_col = st.number_input("Col (0 to size-1)", 0, size-1, 0)
    
    speed = st.select_slider("Speed", options=[0.5, 0.1, 0.05, 0.01, 0.0], value=0.1)
    
    start_btn = st.button("🚀 Start Tiling", use_container_width=True)

# --- The Core Algorithm ---
def solve_recursive(board, top, left, m_r, m_c, sz, plot_handle, status_handle, current_count):
    if sz == 1:
        return current_count
    
    current_count[0] += 1
    count = current_count[0]
    half = sz // 2
    mid_r, mid_c = top + half, left + half

    # Placement Logic
    if not (m_r < mid_r and m_c < mid_c): board[mid_r-1, mid_c-1] = count
    if not (m_r < mid_r and m_c >= mid_c): board[mid_r-1, mid_c] = count
    if not (m_r >= mid_r and m_c < mid_c): board[mid_r, mid_c-1] = count
    if not (m_r >= mid_r and m_c >= mid_c): board[mid_r, mid_c] = count

    # Visual Update
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(board, cmap='tab20b', vmin=-1, vmax=max(1, np.max(board)))
    ax.set_xticks([]); ax.set_yticks([])
    plot_handle.pyplot(fig)
    plt.close(fig) # Prevent memory warning
    
    status_handle.info(f"Placing Triomino #{count} (Grid size: {sz}x{sz})")
    if speed > 0: time.sleep(speed)

    # Recursive Calls
    # Top Left
    solve_recursive(board, top, left, (m_r if (m_r < mid_r and m_c < mid_c) else mid_r-1), 
                    (m_c if (m_r < mid_r and m_c < mid_c) else mid_c-1), half, plot_handle, status_handle, current_count)
    # Top Right
    solve_recursive(board, top, mid_c, (m_r if (m_r < mid_r and m_c >= mid_c) else mid_r-1), 
                    (m_c if (m_r < mid_r and m_c >= mid_c) else mid_c), half, plot_handle, status_handle, current_count)
    # Bottom Left
    solve_recursive(board, mid_r, left, (m_r if (m_r >= mid_r and m_c < mid_c) else mid_r), 
                    (m_c if (m_r >= mid_r and m_c < mid_c) else mid_c-1), half, plot_handle, status_handle, current_count)
    # Bottom Right
    solve_recursive(board, mid_r, mid_c, (m_r if (m_r >= mid_r and m_c >= mid_c) else mid_r), 
                    (m_c if (m_r >= mid_r and m_c >= mid_c) else mid_c), half, plot_handle, status_handle, current_count)

# --- Main Layout ---
col1, col2 = st.columns([2, 1])
with col1:
    board_display = st.empty()
    # Create a fresh temporary board just for display
    temp_board = np.zeros((size, size))
    temp_board[m_row, m_col] = -1
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(temp_board, cmap='binary', vmin=-1, vmax=0)
    ax.set_xticks([]); ax.set_yticks([])
    board_display.pyplot(fig)
    plt.close(fig)

with col2:
    status_display = st.empty()
    status_display.write("Configure settings and press Start.")

if start_btn:
    # 1. Start with a fresh board of the current size
    final_board = np.zeros((size, size))
    final_board[m_row, m_col] = -1
    
    # 2. Run the solver
    solve_recursive(final_board, 0, 0, m_row, m_col, size, board_display, status_display, [0])
    
    st.balloons()
    status_display.success("Tiling Completed Successfully!")
