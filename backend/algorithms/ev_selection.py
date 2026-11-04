def select_station(ev, stations):
    """
    ev: dict(location_km, energy_kwh, travel_cost_per_km, waiting_cost_per_hr)
    stations: list of dict(id, name, location_km, price, eta, wait_hr)
    """
    results = []
    for s in stations:
        d = abs(ev["location_km"] - s["location_km"])
        energy_service = ev["energy_kwh"] * (s["price"] + s["eta"])
        travel = ev["travel_cost_per_km"] * d
        waiting = s["wait_hr"] * ev["waiting_cost_per_hr"]
        
        total_cost = energy_service + travel + waiting
        results.append({
            "station_id": s["id"],
            "name": s["name"],
            "distance_km": round(d, 2),
            "energy_service_cost": round(energy_service, 2),
            "travel_cost": round(travel, 2),
            "waiting_cost": round(waiting, 2),
            "total_cost": round(total_cost, 2),
        })
        
    results.sort(key=lambda r: r["total_cost"])
    return results