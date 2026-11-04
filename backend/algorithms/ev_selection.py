def select_station(ev, stations):
    """
    Algorithm 1: Optimal EVCS Selection for an EV u_k (Gupta & Bhatnagar 2023)
    
    Inputs:
      ev: dict containing:
        - location_km (s_k): EV position on highway
        - energy_kwh (delta_k): EV energy requirement
        - travel_cost_per_km (C_k): Unit travel cost ($/km)
        - waiting_cost_per_hr (C_w): Unit waiting cost ($/hr)
      stations: list of dicts containing:
        - id, name, location_km (l_n), price (P_fn), eta (eta_n), wait_hr (Gamma_n)
    """
    delta_k = ev["energy_kwh"]
    C_k = ev["travel_cost_per_km"]
    C_w = ev["waiting_cost_per_hr"]
    s_k = ev["location_km"]

    results = []
    for st in stations:
        l_n = st["location_km"]
        P_fn = st["price"]
        eta_n = st["eta"]
        Gamma_n = st["wait_hr"]

        # Eq. 1b: Distance on 1D highway
        d_u_n = abs(s_k - l_n)

        # Eq. 1a: Effective charging cost components
        energy_service_cost = delta_k * (P_fn + eta_n)
        travel_cost = C_k * d_u_n
        waiting_cost = Gamma_n * C_w

        P_cn = energy_service_cost + travel_cost + waiting_cost

        results.append({
            "station_id": st["id"],
            "name": st["name"],
            "distance_km": round(d_u_n, 4),
            "energy_service_cost": round(energy_service_cost, 4),
            "travel_cost": round(travel_cost, 4),
            "waiting_cost": round(waiting_cost, 4),
            "total_cost": round(P_cn, 4),
        })

    # Step 3 of Algorithm 1: Sort by minimum cost P_cj
    results.sort(key=lambda r: r["total_cost"])
    return results