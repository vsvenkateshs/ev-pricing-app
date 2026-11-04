import numpy as np

def solve_nash(L, stations, mp):
    """
    Solves Nash Equilibrium prices and profits for N stations on a highway.
    """
    st = sorted(stations, key=lambda s: s["location_km"])
    N = len(st)
    if N < 2:
        raise ValueError("At least 2 stations required for Nash equilibrium game.")

    l = np.array([s["location_km"] for s in st], dtype=float)
    eta = np.array([s["eta"] for s in st], dtype=float)
    G = np.array([s["wait_hr"] for s in st], dtype=float)
    CT = np.array([s["terminal_cost"] for s in st], dtype=float)

    mu1, rho, Cw = mp["mu1"], mp["rho"], mp["Cw"]
    mu2 = mp["sigma"]**2 + mu1**2
    lam = np.log(mp["C_max"] / mp["C_min"]) / (mp["C_max"] - mp["C_min"])

    A = np.zeros((N, N))
    b = np.zeros(N)

    for n in range(N):
        A[n, n] = 1.0
        if n == 0:
            A[n, n+1] = -0.5
            b[n] = (mu1 * (l[0] + l[1]) / (2 * mu2 * lam) 
                    + (eta[1] - eta[0]) / 2 
                    + mu1 * (G[1] - G[0]) * Cw / (2 * mu2))
        elif n == N - 1:
            A[n, n-1] = -0.5
            b[n] = (mu1 * (2 * L - l[n] - l[n-1]) / (2 * mu2 * lam) 
                    + (eta[n] - eta[n-1]) / 2 
                    + mu1 * (G[n] - G[n-1]) * Cw / (2 * mu2))
        else:
            A[n, n-1] = A[n, n+1] = -0.25
            b[n] = (mu1 * (l[n+1] - l[n-1]) / (4 * mu2 * lam) 
                    + (eta[n+1] - 2 * eta[n] + eta[n-1]) / 4 
                    + mu1 * (G[n+1] - 2 * G[n] + G[n-1]) * Cw / (4 * mu2))

    P = np.linalg.solve(A, b)

    profits = np.zeros(N)
    for n in range(N):
        if n == 0:
            br = (mu1 * (l[0] + l[1]) / 2 + mu2 * lam * (P[1] - P[0]) / 2 
                  + mu2 * lam * (eta[1] - eta[0]) / 2 + mu1 * lam * (G[1] - G[0]) * Cw / 2)
        elif n == N - 1:
            br = (mu1 * (2 * L - l[n] - l[n-1]) / 2 + mu2 * lam * (P[n-1] - P[n]) / 2 
                  + mu2 * lam * (eta[n] - eta[n-1]) / 2 + mu1 * lam * (G[n] - G[n-1]) * Cw / 2)
        else:
            br = (mu1 * (l[n+1] - l[n-1]) / 2 + mu2 * lam * (P[n+1] - 2 * P[n] + P[n-1]) / 2 
                  + mu2 * lam * (eta[n+1] - 2 * eta[n] + eta[n-1]) / 2 
                  + mu1 * lam * (G[n+1] - 2 * G[n] + G[n-1]) * Cw / 2)
        
        profits[n] = rho * P[n] * br - CT[n]

    return st, P.tolist(), profits.tolist()