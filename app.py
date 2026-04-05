import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.constants import epsilon_0

st.set_page_config(layout="wide", page_title="Aditya EM-Simulator")

class EMSimulator:
    def __init__(self, grid_size=30):
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
        
        # Potensial
        self.V += q / (4 * np.pi * epsilon_0 * r)
        
        # Medan Listrik (Analitik)
        mag = q / (4 * np.pi * epsilon_0 * (r2**1.5))
        self.Ex += mag * dx
        self.Ey += mag * dy
        self.Ez += mag * dz

# --- UI SIDEBAR ---
st.sidebar.header("Editor Muatan")
if 'charge_list' not in st.session_state:
    st.session_state.charge_list = []

with st.sidebar:
    val_q = st.number_input("Besar Muatan (nC)", value=5.0)
    c1, c2, c3 = st.columns(3)
    x, y, z = c1.number_input("X", 0.0), c2.number_input("Y", 0.0), c3.number_input("Z", 0.0)
    if st.button("➕ Tambah"):
        st.session_state.charge_list.append({'q': val_q*1e-9, 'p': [x, y, z]})
    if st.button("🗑️ Reset"):
        st.session_state.charge_list = []; st.rerun()

# --- RENDERING ---
st.title("⚡ 3D Electric Field Simulator")
st.caption("Aditya - Unpad | Full Analysis Mode")

if st.session_state.charge_list:
    sim = EMSimulator()
    all_starts_x, all_starts_y, all_starts_z = [], [], []
    
    for c in st.session_state.charge_list:
        sim.add_point_charge(c['q'], c['p'])
        
        # SEEDING: Buat 25 titik awal di sekitar tiap muatan untuk Streamlines
        phi = np.random.uniform(0, 2*np.pi, 25)
        costheta = np.random.uniform(-1, 1, 25)
        theta = np.arccos(costheta)
        r_s = 0.6 # Radius pancaran awal
        all_starts_x.extend(c['p'][0] + r_s * np.sin(theta) * np.cos(phi))
        all_starts_y.extend(c['p'][1] + r_s * np.sin(theta) * np.sin(phi))
        all_starts_z.extend(c['p'][2] + r_s * np.cos(theta))

    fig = go.Figure()

    # 1. ISOSURFACE (Potensial V)
    fig.add_trace(go.Isosurface(
        x=sim.X.flatten(), y=sim.Y.flatten(), z=sim.Z.flatten(),
        value=sim.V.flatten(),
        surface_count=4, opacity=0.1, colorscale='Plasma', showscale=False
    ))

    # 2. STREAMLINES (Garis Medan Putih)
    # Normalisasi vektor agar aliran selang stabil
    E_mag = np.sqrt(sim.Ex**2 + sim.Ey**2 + sim.Ez**2) + 1e-12
    fig.add_trace(go.Streamtube(
        x=sim.X.flatten(), y=sim.Y.flatten(), z=sim.Z.flatten(),
        u=(sim.Ex/E_mag).flatten(), v=(sim.Ey/E_mag).flatten(), w=(sim.Ez/E_mag).flatten(),
        starts=dict(x=all_starts_x, y=all_starts_y, z=all_starts_z),
        sizeref=0.3, colorscale=[[0, 'white'], [1, 'white']], showscale=False,
        maxdisplayed=1000, name="Streamlines"
    ))

    # 3. VECTOR FIELD (Cones/Panah Renggang)
    step = 4
    skip = (slice(None, None, step), slice(None, None, step), slice(None, None, step))
    Ex_s, Ey_s, Ez_s = sim.Ex[skip], sim.Ey[skip], sim.Ez[skip]
    E_mag_s = np.sqrt(Ex_s**2 + Ey_s**2 + Ez_s**2) + 1e-12
    
    fig.add_trace(go.Cone(
        x=sim.X[skip].flatten(), y=sim.Y[skip].flatten(), z=sim.Z[skip].flatten(),
        u=(Ex_s/E_mag_s).flatten(), v=(Ey_s/E_mag_s).flatten(), w=(Ez_s/E_mag_s).flatten(),
        sizemode="absolute", sizeref=0.3, colorscale='Viridis', opacity=0.4, showscale=False
    ))

    # 4. MUATAN (Titik)
    for c in st.session_state.charge_list:
        fig.add_trace(go.Scatter3d(
            x=[c['p'][0]], y=[c['p'][1]], z=[c['p'][2]],
            mode='markers', marker=dict(size=8, color='#FF4B4B' if c['q'] > 0 else '#0068C9')
        ))

    fig.update_layout(
        scene=dict(bgcolor='black', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='cube'),
        margin=dict(l=0, r=0, b=0, t=0), template="plotly_dark"
    )

    st.plotly_chart(fig, width='stretch')
else:
    st.info("👈 Tambahkan muatan di sidebar.")