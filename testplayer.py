from core.models import Team, Player

print("---\ Verifying Arsenal Data (Standings) ---")
try:
    arsenal = Team.objects.get(name="Arsenal")
    print(f"Position: {arsenal.position}")
    print(f"Points: {arsenal.points}")
    print(f"Form: {arsenal.form}")
    if arsenal.position and arsenal.points and arsenal.form:
        print("Success: Arsenal standings data is populated.")
    else:
        print("Failure: Arsenal standings data is incomplete.")
except Team.DoesNotExist:
    print("Error: Could not find a team named 'Arsenal' in the database.")

print("\n---\ Verifying Top Scorer Data (e.g., E. Haaland) ---")
try:
    # Use 'E. Haaland' as an example, as he was listed as updated in the output
    haaland = Player.objects.get(name="E. Haaland")
    print(f"Player: {haaland.name}")
    print(f"Team: {haaland.team.name}")
    print(f"Goals: {haaland.goals}")
    print(f"Assists: {haaland.assists}")
    if haaland.goals is not None and haaland.assists is not None:
        print("Success: E. Haaland's goals and assists are populated.")
    else:
        print("Failure: E. Haaland's goals and assists are incomplete.")
except Player.DoesNotExist:
    print("Error: Could not find player 'E. Haaland' in the database.")

#runs this only in django shell XD , thats not python at all , hate Django