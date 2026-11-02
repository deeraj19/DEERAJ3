import math
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(page_title="Aircraft Performance Analysis |DEERAJ", page_icon="✈️", layout="wide")

# ---------------- FRONT PAGE / PROFILE HEADER ----------------
with st.container(border=True):
    profile_col, title_col = st.columns([1, 3], vertical_alignment="center")


    with title_col:
        st.markdown(
            """
            <div style="padding: 8px 0;">
                <p style="font-size: 15px; color: #64748b; margin-bottom: 4px;">
                    WELCOME TO MY PROJECT
                </p>
                <h1 style="margin: 0; font-size: 2.4rem;">Mohith</h1>
                <h2 style="margin: 5px 0 8px 0; font-size: 1.45rem;">
                    ✈️ Aircraft Performance Analysis
                </h2>
                <p style="font-size: 15px; color: #64748b; margin-top: 0;">
                    Thrust • Power • Rate of Climb • V-n Diagram • Gliding • Takeoff
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()

# ---------------- SIDEBAR: INPUT PARAMETERS ----------------
st.sidebar.header("Aircraft parameters")
S = st.sidebar.number_input("Wing area, S (m²)", min_value=1.0, value=47.0, step=1.0)
AR = st.sidebar.number_input("Aspect ratio, AR", min_value=1.0, value=6.5, step=0.1)
e = st.sidebar.number_input("Oswald efficiency, e", min_value=0.1, max_value=1.0, value=0.87, step=0.01)
CD0 = st.sidebar.number_input("Zero-lift drag coefficient, CD0", min_value=0.001, value=0.032, step=0.001, format="%.3f")
W = st.sidebar.number_input("Aircraft weight (N)", min_value=100.0, value=103047.0, step=100.0)
num_engines = st.sidebar.number_input("Number of engines", min_value=1, value=2, step=1)
thrust_per_engine = st.sidebar.number_input("Thrust per engine (N)", min_value=100.0, value=40298.0, step=100.0)

st.sidebar.header("Atmospheric conditions")
rho1 = st.sidebar.number_input("Air density 1 (kg/m³)", min_value=0.01, value=1.112, step=0.001, format="%.3f")
rho2 = st.sidebar.number_input("Air density 2 (kg/m³)", min_value=0.01, value=0.819, step=0.001, format="%.3f")
rho_sl = 1.225
velocity_min = st.sidebar.number_input("Minimum velocity (m/s)", min_value=1.0, value=30.0, step=1.0)
velocity_max = st.sidebar.number_input("Maximum velocity (m/s)", min_value=velocity_min + 1.0, value=350.0, step=5.0)
num_points = st.sidebar.slider("Number of velocity points", 100, 1000, 500, 50)

densities = [rho1, rho2]
velocity_range = np.linspace(velocity_min, velocity_max, num_points)
T_A_sea_level = num_engines * thrust_per_engine
K = 1.0 / (np.pi * e * AR)
TR_min = 2 * W * np.sqrt(K * CD0)

tabs = st.tabs([
    "Thrust", "Power", "Rate of climb", "V-n diagram",
    "Gliding", "Takeoff", "All summary"
])

# ---------------- THRUST REQUIRED / AVAILABLE ----------------
with tabs[0]:
    st.subheader("Thrust required and thrust available")
    fig, ax = plt.subplots(figsize=(10, 5.8))
    summary_thrust = []
    for rho in densities:
        T_A = T_A_sea_level * (rho / rho_sl)
        TR = 0.5 * rho * velocity_range**2 * S * CD0 + (2 * K * W**2) / (rho * velocity_range**2 * S)
        V_TR_min = np.sqrt((2 * W) / (rho * S) * np.sqrt(K / CD0))
        ax.plot(velocity_range, TR / 1000, linewidth=2, label=f"TR, ρ={rho:.3f} kg/m³")
        ax.plot(V_TR_min, TR_min / 1000, "o", markersize=6,
                label=f"Min TR: {V_TR_min:.1f} m/s, ρ={rho:.3f}")
        ax.plot(velocity_range, np.full(len(velocity_range), T_A / 1000), "--",
                linewidth=2, label=f"TA, ρ={rho:.3f} ({T_A/1000:.2f} kN)")
        summary_thrust.append({
            "Density (kg/m³)": rho,
            "TR_min (kN)": round(TR_min / 1000, 2),
            "V_TR_min (m/s)": round(V_TR_min, 2),
            "TA_at_altitude (kN)": round(T_A / 1000, 2)
        })
    ax.set_title("Thrust Required and Thrust Available vs Velocity")
    ax.set_xlabel("Velocity (m/s)")
    ax.set_ylabel("Thrust (kN)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.dataframe(pd.DataFrame(summary_thrust), use_container_width=True)

# ---------------- POWER REQUIRED / AVAILABLE ----------------
with tabs[1]:
    st.subheader("Power required and power available")
    fig, ax = plt.subplots(figsize=(10, 5.8))
    summary_power = []
    for rho in densities:
        T_A = T_A_sea_level * (rho / rho_sl)
        TR = 0.5 * rho * velocity_range**2 * S * CD0 + (2 * K * W**2) / (rho * velocity_range**2 * S)
        PR = TR * velocity_range
        PA = T_A * velocity_range
        V_PR_min = ((2 * K * W**2) / (1.5 * rho**2 * S**2 * CD0))**(1/4)
        PR_min_val = (0.5 * rho * V_PR_min**3 * S * CD0) + (2 * K * W**2) / (rho * V_PR_min * S)
        ax.plot(velocity_range, PR / 1000, linewidth=2, label=f"PR, ρ={rho:.3f}")
        ax.plot(velocity_range, PA / 1000, "--", linewidth=2, label=f"PA, ρ={rho:.3f}")
        ax.plot(V_PR_min, PR_min_val / 1000, "x", markersize=7,
                label=f"Min PR: {V_PR_min:.1f} m/s, ρ={rho:.3f}")
        summary_power.append({
            "Density (kg/m³)": rho,
            "PR_min (kW)": round(PR_min_val / 1000, 2),
            "V_PR_min (m/s)": round(V_PR_min, 2)
        })
    ax.set_title("Power Required and Power Available vs Velocity")
    ax.set_xlabel("Velocity (m/s)")
    ax.set_ylabel("Power (kW)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.dataframe(pd.DataFrame(summary_power), use_container_width=True)

# ---------------- RATE OF CLIMB ----------------
with tabs[2]:
    st.subheader("Rate of climb vs velocity")
    fig, ax = plt.subplots(figsize=(10, 5.8))
    summary_roc = []
    for rho in densities:
        T_A = T_A_sea_level * (rho / rho_sl)
        TR = 0.5 * rho * velocity_range**2 * S * CD0 + (2 * K * W**2) / (rho * velocity_range**2 * S)
        PR = TR * velocity_range
        PA = T_A * velocity_range
        RoC = (PA - PR) / W
        idx = int(np.argmax(RoC))
        max_roc = float(RoC[idx])
        v_at_max_roc = float(velocity_range[idx])
        ax.plot(velocity_range, RoC, linewidth=2, label=f"RoC, ρ={rho:.3f}")
        ax.plot(v_at_max_roc, max_roc, "s", markersize=6,
                label=f"Max RoC: {max_roc:.2f} m/s at {v_at_max_roc:.1f} m/s")
        summary_roc.append({
            "Density (kg/m³)": rho,
            "Max RoC (m/s)": round(max_roc, 2),
            "V_at_Max_RoC (m/s)": round(v_at_max_roc, 2)
        })
    ax.set_title("Rate of Climb vs Velocity")
    ax.set_xlabel("Velocity (m/s)")
    ax.set_ylabel("Rate of climb (m/s)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.dataframe(pd.DataFrame(summary_roc), use_container_width=True)

# ---------------- V-N DIAGRAM ----------------
with tabs[3]:
    st.subheader("V-n diagram comparison")
    col1, col2 = st.columns(2)
    with col1:
        CL_max_pos = st.number_input("Maximum positive lift coefficient", min_value=0.1, value=1.5, step=0.1)
        n_max_pos = st.number_input("Positive structural limit (g)", min_value=0.1, value=5.0, step=0.5)
    with col2:
        CL_max_neg = st.number_input("Maximum negative lift coefficient", min_value=-3.0, max_value=-0.1, value=-0.8, step=0.1)
        n_max_neg = st.number_input("Negative structural limit (g)", min_value=-10.0, max_value=-0.1, value=-3.0, step=0.5)

    fig, ax = plt.subplots(figsize=(10, 6))
    min_rho = min(densities)
    Vs_pos_min_rho = np.sqrt((2 * W) / (min_rho * S * CL_max_pos))
    Va_min_rho = Vs_pos_min_rho * np.sqrt(n_max_pos)
    Vc_min_rho = 1.5 * Va_min_rho
    Vne_min_rho = 1.2 * Vc_min_rho
    V_limit = Vne_min_rho + 20
    ax.axhline(n_max_pos, color="red", linewidth=1.5, label=f"Positive limit (+{n_max_pos:g}g)")
    ax.axhline(n_max_neg, color="red", linestyle="--", linewidth=1.5, label=f"Negative limit ({n_max_neg:g}g)")
    ax.axhline(1.0, color="gray", linestyle=":", alpha=0.6, label="1g level flight")
    ax.axhline(0.0, color="black", alpha=0.3)
    for rho in densities:
        Vs_pos = np.sqrt((2 * W) / (rho * S * CL_max_pos))
        Vs_neg = np.sqrt((2 * W) / (rho * S * abs(CL_max_neg)))
        Va = Vs_pos * np.sqrt(n_max_pos)
        Vc = 1.5 * Va
        Vne = 1.2 * Vc
        V_pos = np.linspace(0, Va, 200)
        n_stall_pos = (0.5 * rho * V_pos**2 * S * CL_max_pos) / W
        V_neg = np.linspace(0, Vs_neg * np.sqrt(abs(n_max_neg)), 200)
        n_stall_neg = -(0.5 * rho * V_neg**2 * S * abs(CL_max_neg)) / W
        ax.plot(V_pos, n_stall_pos, linewidth=2, label=f"Positive stall, ρ={rho:.3f}")
        ax.plot(V_neg, n_stall_neg, "--", linewidth=2, label=f"Negative stall, ρ={rho:.3f}")
        ax.plot([Vne, Vne], [n_max_neg, n_max_pos], ":", linewidth=2, label=f"Vne={Vne:.1f} m/s, ρ={rho:.3f}")
        ax.plot([Va, Vne], [n_max_pos, n_max_pos], "-.", alpha=0.7)
        ax.plot([Vs_neg * np.sqrt(abs(n_max_neg)), Vc], [n_max_neg, n_max_neg], "-.", alpha=0.7)
        ax.plot([Vc, Vne], [n_max_neg, 0], "-.", alpha=0.7)
    ax.set_title("V-n Diagram at Different Air Densities")
    ax.set_xlabel("Velocity (m/s)")
    ax.set_ylabel("Load factor (g)")
    ax.set_xlim(0, V_limit)
    ax.set_ylim(n_max_neg - 0.5, n_max_pos + 0.5)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# ---------------- GLIDING PERFORMANCE ----------------
with tabs[4]:
    st.subheader("Gliding flight performance")
    cd0_val = st.number_input("Glide CD0", min_value=0.001, value=float(CD0), step=0.001, format="%.3f")
    k_val = st.number_input("Glide induced drag factor, k", min_value=0.001, value=float(K), step=0.001, format="%.4f")
    rho_sl_std, T0, L, g_std, R_air = 1.225, 288.15, 0.0065, 9.80665, 287.05
    exponent = (g_std / (R_air * L)) - 1.0

    def density_to_altitude_km(rho):
        temp_ratio = (rho / rho_sl_std) ** (1.0 / exponent)
        return (T0 / L) * (1.0 - temp_ratio) / 1000.0

    glide_rows = []
    for rho in densities:
        h_km = density_to_altitude_km(rho)
        cl_cd_max = 1.0 / (2.0 * math.sqrt(cd0_val * k_val))
        theta_min = math.degrees(math.atan(1.0 / cl_cd_max))
        r_max = h_km * cl_cd_max
        glide_rows.append({
            "Density (kg/m³)": rho,
            "Approx. altitude (km)": round(h_km, 3),
            "(CL/CD)max": round(cl_cd_max, 4),
            "Minimum glide angle (°)": round(theta_min, 2),
            "Maximum glide range (km)": round(r_max, 3)
        })
    st.dataframe(pd.DataFrame(glide_rows), use_container_width=True)

# ---------------- TAKEOFF PERFORMANCE ----------------
with tabs[5]:
    st.subheader("Takeoff trajectory comparison")
    CL_max_takeoff = st.number_input("Takeoff maximum lift coefficient", min_value=0.1, value=2.8, step=0.1)
    S_g_baseline = st.number_input("Baseline ground roll (m) at density 0.819", min_value=0.0, value=789.32, step=10.0)
    R_baseline = st.number_input("Baseline transition radius (m)", min_value=0.0, value=1356.64, step=10.0)
    S_a_baseline = st.number_input("Baseline airborne distance (m)", min_value=0.0, value=364.92, step=10.0)
    rho_baseline = 0.819
    takeoff_rows = []
    for rho in densities:
        V_stall = math.sqrt((2.0 * W) / (rho * S * CL_max_takeoff))
        S_g = S_g_baseline * (rho_baseline / rho)
        R = R_baseline * (rho_baseline / rho)
        S_a = S_a_baseline * (rho_baseline / rho)
        S_to = S_g + S_a
        takeoff_rows.append({
            "Density (kg/m³)": rho,
            "Stall velocity (m/s)": round(V_stall, 2),
            "Ground roll (m)": round(S_g, 2),
            "Transition radius (m)": round(R, 2),
            "Airborne distance (m)": round(S_a, 2),
            "Total takeoff distance (m)": round(S_to, 2)
        })
    st.dataframe(pd.DataFrame(takeoff_rows), use_container_width=True)

# ---------------- COMBINED SUMMARY ----------------
with tabs[6]:
    st.subheader("Aircraft and atmosphere inputs")
    st.write({
        "Wing area (m²)": S, "Aspect ratio": AR, "Oswald efficiency": e,
        "CD0": CD0, "Weight (N)": W, "Total sea-level thrust (N)": T_A_sea_level,
        "Induced drag factor K": round(K, 6), "Air densities (kg/m³)": densities
    })
    st.info("Open each tab to view the corresponding performance plot or comparison table.")
    st.caption("These calculations reproduce the equations and baseline scaling assumptions in the supplied Python script.")
