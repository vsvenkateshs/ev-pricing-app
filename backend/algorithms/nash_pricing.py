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

    Returns (sorted_stations, prices, profits, demand_lengths, market_sharing_valid)

    Notes on the maths (see paper, Eqs. 2-6):
      * The expected profit of station n is  rho * Pf_n * E[delta * psi_n] - C_Tn.
      * E[delta * psi_n] is built from the critical points D_{n,n+1}; it is the
        quantity W_n below (Eq. 5, bracketed term).
      * Setting d(profit)/d(Pf_n) = 0 gives the linear reaction functions of
        Eq. (6); the equilibrium is the solution of that linear system.
      * The "demand length" reported to the UI is W_n / mu1, i.e. the effective
        length of highway (km) captured by station n. The lengths sum to L.
    """
    st = sorted(stations, key=lambda s: s["location_km"])
    N = len(st)
    if N < 2:
        raise ValueError("At least 2 stations required for Nash equilibrium game.")

    l = np.array([s["location_km"] for s in st], dtype=float)
    eta = np.array([s["eta"] for s in st], dtype=float)
    Gamma = np.array([s["wait_hr"] for s in st], dtype=float)
    CT = np.array([s["terminal_cost"] for s in st], dtype=float)

    if l[0] < 0 or l[-1] > L:
        raise ValueError(f"All station locations must lie within [0, {L}] km.")

    rho = mp["rho"]
    mu1 = mp["mu1"]
    sigma = mp["sigma"]
    mu2 = sigma ** 2 + mu1 ** 2          # E{delta^2}
    Cw = mp["Cw"]

    # lambda = E{1 / C_k} for C_k ~ Uniform[C_min, C_max]
    C_min, C_max = mp["C_min"], mp["C_max"]
    if C_min <= 0 or C_max <= C_min:
        raise ValueError("Need 0 < C_min < C_max.")
    lam = np.log(C_max / C_min) / (C_max - C_min)

    # ---- Steps 4 & 5: build and solve the linear system A * Pf = b (Eq. 6) ----
    A = np.zeros((N, N))
    b = np.zeros(N)

    for n in range(N):
        A[n, n] = 1.0
        if n == 0:
            A[n, n + 1] = -0.5
            b[n] = (mu1 * (l[0] + l[1]) / (2 * mu2 * lam)
                    + (eta[1] - eta[0]) / 2
                    + mu1 * (Gamma[1] - Gamma[0]) * Cw / (2 * mu2))
        elif n == N - 1:
            A[n, n - 1] = -0.5
            # Eq. (6) last row is "... - I3" and I3 contains BOTH the eta and the
            # Gamma difference, so both terms are subtracted. (Eq. 13c in the
            # paper's appendix has a typo with a "+" on the Gamma term; Eq. 7a
            # and the paper's numerical results agree with the "-" version.)
            b[n] = (mu1 * (2 * L - l[n] - l[n - 1]) / (2 * mu2 * lam)
                    - (eta[n] - eta[n - 1]) / 2
                    - mu1 * (Gamma[n] - Gamma[n - 1]) * Cw / (2 * mu2))
        else:
            A[n, n - 1] = -0.25
            A[n, n + 1] = -0.25
            b[n] = (mu1 * (l[n + 1] - l[n - 1]) / (4 * mu2 * lam)
                    + (eta[n + 1] - 2 * eta[n] + eta[n - 1]) / 4
                    + mu1 * (Gamma[n + 1] - 2 * Gamma[n] + Gamma[n - 1]) * Cw / (4 * mu2))

    P_f = np.linalg.solve(A, b)

    # ---- Step 2: expected critical points, in "km" units (Eq. 2 averaged) ----
    # E[delta * D_{n,n+1}] / mu1
    D = np.zeros(N - 1)
    for n in range(N - 1):
        D[n] = ((l[n] + l[n + 1]) / 2
                + mu2 * lam * ((P_f[n + 1] - P_f[n]) + (eta[n + 1] - eta[n])) / (2 * mu1)
                + lam * (Gamma[n + 1] - Gamma[n]) * Cw / 2)

    # ---- Eq. (3): demand lengths (effective km captured by each station) ----
    psi = np.zeros(N)
    for n in range(N):
        if n == 0:
            psi[n] = D[0]
        elif n == N - 1:
            psi[n] = L - D[N - 2]
        else:
            psi[n] = D[n] - D[n - 1]

    # ---- Lemma 3 (market sharing), evaluated at mean parameters ----
    # |Pf_n - Pf_{n+1} - zeta| < (l_{n+1} - l_n) * C_mu / mu1
    C_mu = (C_min + C_max) / 2
    lemma3_ok = True
    for n in range(N - 1):
        zeta = (Gamma[n + 1] - Gamma[n]) * Cw / mu1 + (eta[n + 1] - eta[n])
        nu = (l[n + 1] - l[n]) * C_mu / mu1
        if not (abs(P_f[n] - P_f[n + 1] - zeta) < nu):
            lemma3_ok = False
    market_sharing_valid = bool(lemma3_ok and np.all(psi > 0) and np.all(np.diff(D) > 0)
                                and D[0] > 0 and D[-1] < L)

    # ---- Eq. (4)/(5): NE profits = rho * Pf * E[delta * psi] - C_T ----
    profits = rho * P_f * (mu1 * psi) - CT

    return st, P_f.tolist(), profits.tolist(), psi.tolist(), market_sharing_valid
