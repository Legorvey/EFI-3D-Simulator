import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.constants import epsilon_0

st.set_page_config(layout="wide", page_title="Aditya EM-Simulator")

class EMSimulator:
    def __init__(self, grid_size=20): # Grid sedikit lebih renggang untuk Cone
        self.res = grid_size
        _range = np.linspace(-5, 5, self.res)
        self.X, self.Y, self.Z = np.meshgrid(_range, _range, _range, indexing='ij')
        self.V = np.zeros_like(self.X)
        self.Ex, self.Ey, self.Ez = [np.zeros_like(self.X) for _ in range(3)]

    def add_point_charge(self, q, pos):
        dx, dy, dz = self.X - pos[0], self.Y - pos[1], self.Z - pos[2]
        r2 = dx**2 + dy**2 + dz**2
        r2[r2 < 0.2] = 0.2 
        r = np.sqrt(r2)
        
        self.V += q / (4 * np.pi * epsilon_0 * r)
        mag = q / (4 * np.pi * epsilon_0 * (r2**1.5))
        self.Ex += mag * dx
        self.Ey += mag * dy
        self.Ez += mag * dz

# --- UI SIDEBAR ---
st.sidebar.header("Editor Muatan")
if 'charge_list' not in st.session_state:
    st.session_state.charge_list = []

with st.sidebar:
    val_q = st.number_input("Besar Muatan (nC)", value=1.0)
    c1, c2, c3 = st.columns(3)
    x, y, z = c1.number_input("X", 0.0), c2.number_input("Y", 0.0), c3.number_input("Z", 0.0)
    if st.button("➕ Tambah"):
        st.session_state.charge_list.append({'q': val_q*1e-9, 'p': [x, y, z]})
    if st.button("🗑️ Reset"):
        st.session_state.charge_list = []; st.rerun()

# --- RENDERING ---
st.title("⚡ 3D Electric Field Simulator")
st.caption("Aditya - Universitas Padjadjaran | Vector Field Mode")

if st.session_state.charge_list:
    sim = EMSimulator()
    for c in st.session_state.charge_list:
        sim.add_point_charge(c['q'], c['p'])
    
    fig = go.Figure()

    # 1. Muatan
    for c in st.session_state.charge_list:
        fig.add_trace(go.Scatter3d(
            x=[c['p'][0]], y=[c['p'][1]], z=[c['p'][2]],
            mode='markers', marker=dict(size=10, color='#FF4B4B' if c['q'] > 0 else '#0068C9')
        ))

    # 2. Isosurface (Potensial V)
    fig.add_trace(go.Isosurface(
        x=sim.X.flatten(), y=sim.Y.flatten(), z=sim.Z.flatten(),
        value=sim.V.flatten(), surface_count=3, opacity=0.2, colorscale='Plasma', showscale=False
    ))

    # 3. Vector Field (Cone - Arah Medan Listrik E)
    # Normalisasi agar semua panah ukurannya seragam tapi arah tetap benar
    E_mag = np.sqrt(sim.Ex**2 + sim.Ey**2 + sim.Ez**2) + 1e-12
    fig.add_trace(go.Cone(
        x=sim.X.flatten(), y=sim.Y.flatten(), z=sim.Z.flatten(),
        u=(sim.Ex/E_mag).flatten(), v=(sim.Ey/E_mag).flatten(), w=(sim.Ez/E_mag).flatten(),
        sizemode="scaled", sizeref=0.5, colorscale='Greys', showscale=False, opacity=0.8
    ))

    fig.update_layout(
        scene=dict(bgcolor='black', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False),
        margin=dict(l=0, r=0, b=0, t=0), template="plotly_dark"
    )

    st.plotly_chart(fig, width='stretch')
else:
    st.info("👈 Tambahkan muatan di sidebar.")