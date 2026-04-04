import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.constants import epsilon_0

st.set_page_config(layout="wide", page_title="Aditya EM-Simulator")

class EMSimulator:
    def __init__(self, grid_size=25): # Grid lebih kecil biar web responsif
        self.res = grid_size
        _range = np.linspace(-5, 5, self.res)
        self.X, self.Y, self.Z = np.meshgrid(_range, _range, _range, indexing='ij')
        self.V = np.zeros_like(self.X)
        self.charges = []

    def add_point_charge(self, q, pos):
        r = np.sqrt((self.X - pos[0])**2 + (self.Y - pos[1])**2 + (self.Z - pos[2])**2)
        r[r < 0.2] = 0.2 
        self.V += q / (4 * np.pi * epsilon_0 * r)
        self.charges.append({'q': q, 'pos': pos})

    def calculate_field(self):
        # Hitung Gradien V untuk dapet E
        Ex, Ey, Ez = np.gradient(-self.V)
        return Ex, Ey, Ez

# --- UI SIDEBAR ---
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

# --- RENDERING DENGAN PLOTLY ---
st.title("⚡ 3D Electric Field Simulator (Stable Version)")
st.caption("Aditya - Universitas Padjadjaran")

if st.session_state.charge_list:
    sim = EMSimulator()
    for c in st.session_state.charge_list:
        sim.add_point_charge(c['q'], c['p'])
    
    Ex, Ey, Ez = sim.calculate_field()
    
    fig = go.Figure()

    # 1. Plot Muatan (Bola Merah/Biru)
    for c in st.session_state.charge_list:
        fig.add_trace(go.Scatter3d(
            x=[c['p'][0]], y=[c['p'][1]], z=[c['p'][2]],
            mode='markers',
            marker=dict(size=10, color='red' if c['q'] > 0 else 'blue'),
            name="Positive" if c['q'] > 0 else "Negative"
        ))

    # 2. Plot Permukaan Ekipotensial (Isosurface)
    fig.add_trace(go.Isosurface(
        x=sim.X.flatten(), y=sim.Y.flatten(), z=sim.Z.flatten(),
        value=sim.V.flatten(),
        isomin=np.percentile(sim.V, 10),
        isomax=np.percentile(sim.V, 90),
        surface_count=3,
        opacity=0.3,
        colorscale='Plasma',
        showscale=False
    ))

    # 3. Plot Garis Medan (Streamlines)
    fig.add_trace(go.Streamtube(
        x=sim.X.flatten(), y=sim.Y.flatten(), z=sim.Z.flatten(),
        u=Ex.flatten(), v=Ey.flatten(), w=Ez.flatten(),
        starts=dict(
            x=np.random.uniform(-4, 4, 30),
            y=np.random.uniform(-4, 4, 30),
            z=np.random.uniform(-4, 4, 30)
        ),
        sizeref=0.5,
        colorscale='Greys',
        showscale=False
    ))

    fig.update_layout(
        scene=dict(bgcolor='black', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False),
        margin=dict(l=0, r=0, b=0, t=0),
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("👈 Tambahkan muatan di menu kiri.")