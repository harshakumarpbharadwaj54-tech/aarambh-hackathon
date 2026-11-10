from datetime import timedelta

from storage import load_trips


def summarize(trips):
    distance = sum(trip["distance_km"] for trip in trips)
    energy = sum(trip["energy_kwh"] for trip in trips)

    if not trips or distance == 0:
        return None

    city_trips = sum(
        trip["trip_type"].lower() == "city"
        for trip in trips
    )

    return {
        "trip_count": len(trips),
        "distance_km": distance,
        "energy_kwh": energy,
        "energy_per_100_km": energy / distance * 100,
        "average_trip_km": distance / len(trips),
        "city_percent": city_trips / len(trips) * 100,
    }


def compare_periods():
    trips = load_trips()

    if not trips:
        print("I don't have enough trip data to answer.")
        return

    latest_date = max(trip["date"] for trip in trips)
    recent_start = latest_date - timedelta(days=13)
    previous_start = latest_date - timedelta(days=27)

    recent_trips = [
        trip for trip in trips
        if recent_start <= trip["date"] <= latest_date
    ]
    previous_trips = [
        trip for trip in trips
        if previous_start <= trip["date"] < recent_start
    ]

    recent = summarize(recent_trips)
    previous = summarize(previous_trips)

    if recent is None or previous is None:
        print("I don't have enough data in both periods to compare.")
        return

    old_use = previous["energy_per_100_km"]
    new_use = recent["energy_per_100_km"]
    change = (new_use - old_use) / old_use * 100

    print(f"Earlier period: {previous_start} to {recent_start - timedelta(days=1)}")
    print(f"Recent period:  {recent_start} to {latest_date}")
    print()
    print(f"Earlier energy use: {old_use:.1f} kWh per 100 km")
    print(f"Recent energy use:  {new_use:.1f} kWh per 100 km")
    print(f"Change: {change:.1f}% more energy per 100 km")
    print()
    print(f"Earlier city trips: {previous['city_percent']:.0f}%")
    print(f"Recent city trips:  {recent['city_percent']:.0f}%")
    print(f"Earlier average trip: {previous['average_trip_km']:.1f} km")
    print(f"Recent average trip:  {recent['average_trip_km']:.1f} km")
    print()
    print(
        "Possible explanation: recent trips were shorter and more often in "
        "the city. That pattern happened alongside higher energy use. "
        "The records show a connection, but do not prove it caused the "
        "range to drop."
    )