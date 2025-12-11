import numpy as np
import json
import os

# --- Lattice / reciprocal geometry (Å⁻¹) ---
a = 2.46
sqrt3 = np.sqrt(3.0)

b1 = (2*np.pi/a) * np.array([1/np.sqrt(3), -1.0])
b2 = (2*np.pi/a) * np.array([1/np.sqrt(3),  1.0])

Gamma = np.array([0.0, 0.0])
K  = (2*b1 +   b2) / 3    # chosen K corner
M     = 0.5 * b1                 # only used if you want it later

# --- Segment density (how fine the sampling is) ---
nk_density = 2000  # points per 1 Å⁻¹

# --- Fixed segment length in k-space (Å⁻¹) ---
seg_len = 0.04

# Direction in q-space from K toward Γ
dist_K_to_G = np.linalg.norm(K - Gamma)
dir_q_to_G = (Gamma - K) / dist_K_to_G   # unit vector from K to Γ in q-space

# =========================
# 1) Horizontal segment in q
#    q: (-0.03, 0) -> (0, 0)
# =========================
n_horiz = int(seg_len * nk_density) + 1

qx_horiz = np.linspace(-seg_len, 0.0, n_horiz, endpoint=False)
qy_horiz = np.zeros_like(qx_horiz)

# =========================
# 2) Radial segment in q
#    q: (0, 0) -> seg_len * dir_q_to_G
# =========================
n_radial = int(seg_len * nk_density) + 1

q_end_radial = dir_q_to_G * seg_len
qx_radial = np.linspace(0.0, q_end_radial[0], n_radial)
qy_radial = np.linspace(0.0, q_end_radial[1], n_radial)

# =========================
# Concatenate full q-path
# =========================
qx = np.concatenate([qx_horiz, qx_radial])
qy = np.concatenate([qy_horiz, qy_radial])

# --- Convert back to absolute k if needed ---
kx_abs = qx + K[0]
ky_abs = qy + K[1]

zoom_data = {
    # relative coordinates (for continuum model around K)
    "qx": qx.tolist(),
    "qy": qy.tolist(),

    # absolute coordinates (for plotting, debugging)
    "kx": kx_abs.tolist(),
    "ky": ky_abs.tolist(),

    # the actual K used as origin
    "K": {"kx": float(K[0]), "ky": float(K[1])},

    "range_description": (
        "Two segments of length 0.03 Å⁻¹ in q-space: "
        "horizontal (qx: -0.03→0, qy=0) then radial toward Γ."
    ),
}

os.makedirs("kpaths", exist_ok=True)
with open("kpaths/kpath_zoomed.json", "w") as f:
    json.dump(zoom_data, f, indent=2)

print("✅ Saved kpaths/kpath_zoomed.json (K-centered, fixed 0.03 Å⁻¹ segments)")

# =========================
# Generate kpath.json: Γ → K → M0 → Γ (closed loop)
# =========================
M0 = 0.5 * b1  # M0 midpoint

# --- Number of points for each segment ---
n_points = 200  # points per segment

# Segment 1: Γ → K
kx_gamma_to_k = np.linspace(Gamma[0], K[0], n_points)
ky_gamma_to_k = np.linspace(Gamma[1], K[1], n_points)

# Segment 2: K → M0
kx_k_to_m0 = np.linspace(K[0], M0[0], n_points)
ky_k_to_m0 = np.linspace(K[1], M0[1], n_points)

# Segment 3: M0 → Γ (back to origin)
kx_m0_to_gamma = np.linspace(M0[0], Gamma[0], n_points)
ky_m0_to_gamma = np.linspace(M0[1], Gamma[1], n_points)

# Concatenate full path (closed loop)
kx_full = np.concatenate([kx_gamma_to_k, kx_k_to_m0, kx_m0_to_gamma])
ky_full = np.concatenate([ky_gamma_to_k, ky_k_to_m0, ky_m0_to_gamma])

# Create the kpath data structure
kpath_data = {
    "kx": kx_full.tolist(),
    "ky": ky_full.tolist(),
    
    # High symmetry points
    "Gamma": {"kx": float(Gamma[0]), "ky": float(Gamma[1])},
    "K": {"kx": float(K[0]), "ky": float(K[1])},
    "M0": {"kx": float(M0[0]), "ky": float(M0[1])},
    
    # Segment information
    "segments": [
        {"name": "Γ → K", "start": 0, "end": n_points},
        {"name": "K → M0", "start": n_points, "end": 2*n_points},
        {"name": "M0 → Γ", "start": 2*n_points, "end": 3*n_points}
    ],
    
    "description": "Kpath from origin (Γ) to K point to midpoint (M0) and back to Γ (closed loop)"
}

# Save to kpath.json
with open("kpaths/kpath.json", "w") as f:
    json.dump(kpath_data, f, indent=2)

print("✅ Saved kpaths/kpath.json")
print(f"   Path: Γ → K → M0 → Γ (closed loop)")
print(f"   Total points: {len(kx_full)}")
print(f"   Points per segment: {n_points}")



