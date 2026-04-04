import streamlit as st
import numpy as np
import pyvista as pv
import streamlit.components.v1 as components
import tempfile
import os
from scipy.constants import epsilon_0

# Setup Headless Rendering untuk Cloud
if not os.environ.get("DISPLAY"):
    try:
        pv.start_xvfb()
    except:
        pass

pv.OFF_SCREEN = True
st.set_page_config(layout="wide", page_title="Aditya EM-Simulator")

class EMSimulator:
    def __init__(self, grid_size=30):
        _range = np.linspace(-5, 5, grid_size)
        self.X, self.Y, self.Z = np.meshgrid(_range, _range, _range, indexing='ij')
        self.V = np.zeros_like(self.X)

    def add_point_charge(self, q, pos):
        r = np.sqrt((self.X - pos[0])**2 + (self.Y - pos[1])**2 + (self.Z - pos[2])**2)
        r[r < 0.2] = 0.2 
        self.V += q / (4 * np.pi * epsilon_0 * r)

# --- UI ---
st.sidebar.header("📝 Editor Muatan")
if 'charge_list' not in st.session_state:
    st.session_state.charge_list = []

with st.sidebar:
    val_q = st.number_input("Besar Muatan (nC)", value=1.0)
    c1, c2, c3 = st.columns(3)
    x, y, z = c1.number_input("X", 0.0), c2.number_input("Y", 0.0), c3.number_input("Z", 0.0)
    if st.button("➕ Tambah Muatan"):
        st.session_state.charge_list.append({'q': val_q*1e-9, 'p': [x, y, z]})
    if st.button("🗑️ Reset"):
        st.session_state.charge_list = []; st.rerun()

# --- RENDER ---
st.title("⚡ 3D Electric Field Simulator")
if st.session_state.charge_list:
    sim = EMSimulator()
    for c in st.session_state.charge_list:
        sim.add_point_charge(c['q'], c['p'])

    grid = pv.StructuredGrid(sim.X, sim.Y, sim.Z)
    grid["V"] = sim.V.flatten()
    
    # Hitung Medan Listrik
    grad = np.gradient(-sim.V, 10/29) # spacing approx
    grid["E"] = np.c_[grad[0].flatten(), grad[1].flatten(), grad[2].flatten()]

    plotter = pv.Plotter(window_size=[800, 600])
    plotter.set_background("#121212")
    plotter.add_mesh(grid.contour(scalars="V"), opacity=0.3, cmap="plasma")
    
    # Garis Medan
    streamlines = grid.streamlines(vectors="E", n_points=80, source_radius=4)
    plotter.add_mesh(streamlines.tube(radius=0.015), color="white")

    # Export ke HTML
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        plotter.export_html(tmp.name) # Tanpa argumen backend biar nggak error
        with open(tmp.name, "r", encoding="utf-8") as f:
            components.html(f.read(), height=600)
else:
    st.info("👈 Tambahkan muatan di menu kiri.")