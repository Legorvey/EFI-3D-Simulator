import streamlit as st
import numpy as np
import pyvista as pv
import streamlit.components.v1 as components
import tempfile
from scipy.constants import epsilon_0

st.set_page_config(layout="wide", page_title="Aditya EM-Simulator")

class EMSimulator:
    def __init__(self, grid_size=35, bounds=(-5, 5)):
        self.res = grid_size
        self.limit = bounds
        _range = np.linspace(bounds[0], bounds[1], self.res)
        self.X, self.Y, self.Z = np.meshgrid(_range, _range, _range, indexing='ij')
        self.V = np.zeros_like(self.X)

    def add_point_charge(self, q, pos):
        r = np.sqrt((self.X - pos[0])**2 + (self.Y - pos[1])**2 + (self.Z - pos[2])**2)
        r[r < 0.2] = 0.2 
        self.V += q / (4 * np.pi * epsilon_0 * r)

    def calculate_field(self):
        spacing = (self.limit[1] - self.limit[0]) / (self.res - 1)
        grad = np.gradient(-self.V, spacing)
        return grad[0], grad[1], grad[2]

# --- UI INTERFACE ---
st.sidebar.header("📝 Editor Muatan (Desmos Style)")
if 'charge_list' not in st.session_state:
    st.session_state.charge_list = []

with st.sidebar:
    type_m = st.selectbox("Tipe", ["Titik", "Garis"])
    val_q = st.number_input("Besar Muatan (nC)", value=1.0)
    c1, c2, c3 = st.columns(3)
    x1 = c1.number_input("X", value=0.0)
    y1 = c2.number_input("Y", value=0.0)
    z1 = c3.number_input("Z", value=0.0)
    
    if type_m == "Garis":
        c4, c5, c6 = st.columns(3)
        x2, y2, z2 = c4.number_input("X2", 0.0), c5.number_input("Y2", 2.0), c6.number_input("Z2", 0.0)

    if st.button("➕ Tambah Muatan"):
        if type_m == "Titik":
            st.session_state.charge_list.append({'t':'p','q':val_q*1e-9,'p':[x1,y1,z1]})
        else:
            st.session_state.charge_list.append({'t':'l','q':val_q*1e-9,'s':[x1,y1,z1],'e':[x2,y2,z2]})

    if st.button("🗑️ Reset"):
        st.session_state.charge_list = []; st.rerun()

# --- RENDERING ---
st.title("⚡ 3D Electric Field Simulator")
if st.session_state.charge_list:
    sim = EMSimulator()
    for c in st.session_state.charge_list:
        if c['t'] == 'p': sim.add_point_charge(c['q'], c['p'])
        else:
            pts = np.linspace(0, 1, 10)
            s, e = np.array(c['s']), np.array(c['e'])
            for t_val in pts: sim.add_point_charge((c['q']*np.linalg.norm(e-s))/10, s + t_val*(e-s))

    grid = pv.StructuredGrid(sim.X, sim.Y, sim.Z)
    grid["V"] = sim.V.flatten()
    Ex, Ey, Ez = sim.calculate_field()
    grid["E"] = np.c_[Ex.flatten(), Ey.flatten(), Ez.flatten()]

    plotter = pv.Plotter(window_size=[800, 600])
    plotter.add_mesh(grid.contour(scalars="V"), opacity=0.3, cmap="plasma")
    streamlines = grid.streamlines(vectors="E", n_points=100, source_radius=4)
    plotter.add_mesh(streamlines.tube(radius=0.01), color="white")

    # Export ke format HTML yang bisa dibaca Streamlit
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        plotter.export_html(tmp.name)
        with open(tmp.name, "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=600)
else:
    st.info("👈 Tambahkan muatan di menu kiri untuk memulai.")