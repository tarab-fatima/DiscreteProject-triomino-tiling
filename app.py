import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# Page Config
st.set_page_config(page_title="Tiling Visualizer", layout="centered")

st.title("🧩 Defective Checkerboard Tiling")
st.markdown("""
This project demonstrates **Mathematical Induction**. A $2^n \\times 2^n$ board with one missing square 
can always be tiled using $L$-shaped triominoes.
""")

# Sidebar Inputs
with st.sidebar:
    st.header("Settings")
    n = st.slider("Power of 2 (n)", 1, 6, 3)
    size = 2**n
    st.write(f"Board: {size}x{size}")
    
    m_row = st.number_input("Missing Row", 0, size-1, 0)
    m_col = st.number_input("Missing Col", 0, size-1, 0)
    
    speed = st.slider("Animation Speed", 0.0, 1.0, 0.2)
    start_btn = st.button("🚀 Start Tiling")

# Initialize Board
if 'board' not in st.session_state or st.sidebar.button("Reset"):
    st.session_state.board = np.zeros((size, size))
    st.session_state.board[m_row, m_col] = -1
    st.session_state.counter = 0

def solve(top, left, m_r, m_c, sz):
    if sz == 1: return
    
    st.session_state.counter += 1
    count = st.session_state.counter
    half = sz // 2
    mid_r, mid_c = top + half, left + half

    # Quadrant Logic & Center Triomino Placement
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

    # Show progress in UI
    placeholder.pyplot(render_board(st.session_state.board, size))
    time.sleep(speed)

    # Recursive calls
    solve(top, left, (m_r if m_r < mid_r and m_c < mid_c else mid_r-1), (m_c if m_r < mid_r and m_c < mid_c else mid_c-1), half)
    solve(top, mid_c, (m_r if m_r < mid_r and m_c >= mid_c else mid_r-1), (m_c if m_r < mid_r and m_c >= mid_c else mid_c), half)
    solve(mid_r, left, (m_r if m_r >= mid_r and m_c < mid_c else mid_r), (m_c if m_r >= mid_r and m_c < mid_c else mid_c-1), half)
    solve(mid_r, mid_c, (m_r if m_r >= mid_r and m_c >= mid_c else mid_r), (m_c if m_r >= mid_r and m_c >= mid_c else mid_c), half)

def render_board(b, sz):
    fig, ax = plt.subplots(figsize=(6, 6))
    cmap = plt.cm.get_cmap('viridis', int(b.max() + 2))
    cmap.set_under("black")
    ax.imshow(b, cmap=cmap, vmin=0.1)
    ax.set_xticks([])
    ax.set_yticks([])
    return fig

placeholder = st.empty()
placeholder.pyplot(render_board(st.session_state.board, size))

if start_btn:
    solve(0, 0, m_row, m_col, size)
    st.balloons()
    st.success("Tiling Complete!")