import numpy as np

def solve_nash(L, stations, mp):
    """
    Algorithm 2: Nash Equilibrium of Hotelling's Game (Gupta & Bhatnagar 2023)
    
    Inputs:
      L: Length of major highway (km)
      stations: list of dicts containing:
        - id, name, location_km (l_n), eta (eta_n), wait_hr (Gamma_n), terminal_cost (C_Tn)
      mp: dict containing market parameters:
        - rho: EV density per km
        - mu1: E{delta_k} (mean energy demand)
        - sigma: Std dev of energy demand
        - C_min, C_max: Travel cost distribution limits ($/km)
        - Cw: Waiting cost per unit time ($/hr)
    """
    st = sorted(stations, key=lambda s: s["location_km"])
    N = len(st)
    if N < 2:
        raise ValueError("At least 2 stations required for Nash equilibrium game.")

    l = np.array([s["location_km"] for s in st], dtype=float)
    eta = np.array([s["eta"] for s in st], dtype=float)
    Gamma = np.array([s["wait_hr"] for s in st], dtype=float)
    CT = np.array([s["terminal_cost"] for s in st], dtype=float)

    rho = mp["rho"]
    mu1 = mp["mu1"]
    sigma = mp["sigma"]
    mu2 = sigma**2 + mu1**2
    Cw = mp["Cw"]
    
    # Lambda = E{1 / C_k} for uniform distribution [C_min, C_max]
    C_min, C_max = mp["C_min"], mp["C_max"]
    lam = np.log(C_max / C_min) / (C_max - C_min)

    # Step 4 & 5: Construct linear system A * P_f = b from Eq. (6)
    A = np.zeros((N, N))
    b = np.zeros(N)

    for n in range(N):
        A[n, n] = 1.0
        if n == 0:
            A[n, n+1] = -0.5
            b[n] = (mu1 * (l[0] + l[1]) / (2 * mu2 * lam) 
                    + (eta[1] - eta[0]) / 2 
                    + mu1 * (Gamma[1] - Gamma[0]) * Cw / (2 * mu2))
        elif n == N - 1:
            A[n, n-1] = -0.5
            b[n] = (mu1 * (2 * L - l[n] - l[n-1]) / (2 * mu2 * lam) 
                    - (eta[n] - eta[n-1]) / 2 
                    + mu1 * (Gamma[n] - Gamma[n-1]) * Cw / (2 * mu2))
        else:
            A[n, n-1] = -0.25
            A[n, n+1] = -0.25
            b[n] = (mu1 * (l[n+1] - l[n-1]) / (4 * mu2 * lam) 
                    + (eta[n+1] - 2 * eta[n] + eta[n-1]) / 4 
                    + mu1 * (Gamma[n+1] - 2 * Gamma[n] + Gamma[n-1]) * Cw / (4 * mu2))

    # Solve linear system for NE prices P_f*
    P_f = np.linalg.solve(A, b)

    # Compute Critical Points (Eq. 2)
    D = np.zeros(N - 1)
    for n in range(N - 1):
        D[n] = ((l[n] + l[n+1]) / 2 
                + (P_f[n+1] - P_f[n]) * mu1 / (2 * mu2 * lam) 
                + (eta[n+1] - eta[n]) / 2 
                + mu1 * (Gamma[n+1] - Gamma[n]) * Cw / (2 * mu2))

    # Compute Demand Lengths (Eq. 3)
    psi = np.zeros(N)
    for n in range(N):
        if n == 0:
            psi[n] = D[0]
        elif n == N - 1:
            psi[n] = L - D[N - 2]
        else:
            psi[n] = D[n] - D[n - 1]

    # Check Market Sharing Condition (Lemma 3): Demand lengths must be positive
    market_sharing_valid = all(p > 0 for p in psi)

    # Compute NE Profits (Eq. 4 & 5)
    profits = np.zeros(N)
    for n in range(N):
        profits[n] = rho * mu1 * psi[n] * P_f[n] - CT[n]

    return st, P_f.tolist(), profits.tolist(), psi.tolist(), market_sharing_valid