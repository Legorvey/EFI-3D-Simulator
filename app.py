import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.constants import epsilon_0

st.set_page_config(layout="wide", page_title="Aditya EM-Simulator")

class EMSimulator:
    def __init__(self, grid_size=30): # Grid optimal biar web enteng
        self.res = grid_size
        _range = np.linspace(-5, 5, self.res)
        self.X, self.Y, self.Z = np.meshgrid(_range, _range, _range, indexing='ij')
        self.V = np.zeros_like(self.X)
        self.spacing = (10) / (self.res - 1) # Hitung spacing untuk gradien

    def add_point_charge(self, q, pos):
        r = np.sqrt((self.X - pos[0])**2 + (self.Y - pos[1])**2 + (self.Z - pos[2])**2)
        r[r < 0.2] = 0.2 # Hindari singularity
        self.V += q / (4 * np.pi * epsilon_0 * r)

    def calculate_field(self):
        Ex, Ey, Ez = np.gradient(-self.V, self.spacing)
        return Ex, Ey, Ez

# --- UI SIDEBAR ---
st.sidebar.header("Editor Muatan")
if 'charge_list' not in st.session_state:
    st.session_state.charge_list = []

with st.sidebar:
    val_q = st.number_input("Besar Muatan (nC)", value=1.0)
    c1, c2, c3 = st.columns(3)
    x = c1.number_input("X", 0.0)
    y = c2.number_input("Y", 0.0)
    z = c3.number_input("Z", 0.0)
    if st.button("➕ Tambah Muatan"):
        st.session_state.charge_list.append({'q': val_q*1e-9, 'p': [x, y, z]})
    if st.button("🗑️ Reset"):
        st.session_state.charge_list = []; st.rerun()
    st.write("---")
    st.caption("Dikembangkan oleh Aditya - Unpad")

# --- VISUALISASI DENGAN PLOTLY ---
st.title("3D Electric Field Simulator (Stable)")

if st.session_state.charge_list:
    sim = EMSimulator()
    for c in st.session_state.charge_list:
        sim.add_point_charge(c['q'], c['p'])
    
    Ex, Ey, Ez = sim.calculate_field()
    
    fig = go.Figure()

    # 1. Plot Muatan (FIX: Pewarnaan pakai Hex Code beneran)
    for c in st.session_state.charge_list:
        fig.add_trace(go.Scatter3d(
            x=[c['p'][0]], y=[c['p'][1]], z=[c['p'][2]],
            mode='markers',
            marker=dict(
                size=12,
                color='#FF4B4B' if c['q'] > 0 else '#31333F', # Merah jika positif, Biru gelap jika negatif
                line=dict(color='white', width=2)
            ),
            name=f"{c['q']*1e9:.1f} nC"
        ))

    # 2. Plot Permukaan Ekipotensial (Awan Plasma V)
    fig.add_trace(go.Isosurface(
        x=sim.X.flatten(), y=sim.Y.flatten(), z=sim.Z.flatten(),
        value=sim.V.flatten(),
        surface_count=5, # Jumlah kontur
        opacity=0.3,
        colorscale='Plasma',
        showscale=False,
        name="Equipotential"
    ))

    # 3. Plot Garis Medan (High-Density Streamlines)
    # Kita buat titik awal selang mengelilingi setiap muatan agar aliran terlihat jelas
    all_starts_x = []
    all_starts_y = []
    all_starts_z = []
    
    for c in st.session_state.charge_list:
        # Generate 20 titik di sekitar setiap muatan (bentuk bola kecil)
        phi = np.random.uniform(0, 2*np.pi, 20)
        costheta = np.random.uniform(-1, 1, 20)
        theta = np.arccos(costheta)
        r = 0.4 # Jarak mulai selang dari pusat muatan
        
        all_starts_x.extend(c['p'][0] + r * np.sin(theta) * np.cos(phi))
        all_starts_y.extend(c['p'][1] + r * np.sin(theta) * np.sin(phi))
        all_starts_z.extend(c['p'][2] + r * np.cos(theta))

    fig.add_trace(go.Streamtube(
        x=sim.X.flatten(), y=sim.Y.flatten(), z=sim.Z.flatten(),
        u=Ex.flatten(), v=Ey.flatten(), w=Ez.flatten(),
        starts=dict(x=all_starts_x, y=all_starts_y, z=all_starts_z),
        sizeref=0.3, # Ketebalan selang
        colorscale=[[0, 'white'], [1, 'white']],
        showscale=False,
        maxdisplayed=1000,
        name="Field Lines"
    ))

    # Tampilan Akhir (Mode Gelap Unpad)
    fig.update_layout(
        scene=dict(
            bgcolor='#111111', # Hitung gelap total
            xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        template="plotly_dark",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
    st.info("Gunakan Mouse untuk putar/zoom. Klik 'Tambah' di kiri untuk update live.")

else:
    st.warning("Tambahkan muatan di menu kiri untuk memulai simulasi.")