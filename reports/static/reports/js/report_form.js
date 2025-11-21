document.addEventListener('DOMContentLoaded', function() {
    // Find the form which holds our data attributes
    const form = document.querySelector('#create-report-form');
    if (!form) {
        // If this form isn't on the page, do nothing.
        return;
    }

    const playersData = JSON.parse(form.dataset.playersData);
    const teamSelectId = form.dataset.teamSelectId;
    const playerSelectId = form.dataset.playerSelectId;

    const teamSelect = document.getElementById(teamSelectId);
    const playerSelect = document.getElementById(playerSelectId);

    if (!teamSelect || !playerSelect) return;

    function updatePlayerOptions(selectedTeamId) {
        // Clear current player options
        playerSelect.innerHTML = ''; 

        if (selectedTeamId && playersData[selectedTeamId] && playersData[selectedTeamId].length > 0) {
            // Case 1: Team is selected and has players
            playerSelect.disabled = false;
            
            // Add a default placeholder first
            const placeholderOption = new Option('--- Select a Player ---', '');
            playerSelect.add(placeholderOption);

            // Populate with players of the selected team
            const players = playersData[selectedTeamId];
            players.forEach(player => {
                const option = new Option(player.name, player.id);
                playerSelect.add(option);
            });
        } else if (selectedTeamId) {
            // Case 2: Team is selected but has no players
            playerSelect.disabled = true;
            const noPlayersOption = new Option('No players found for this team', '');
            playerSelect.add(noPlayersOption);
        } else {
            // Case 3: No team is selected (initial state)
            playerSelect.disabled = true;
            const placeholderOption = new Option('--- Select a Team First ---', '');
            playerSelect.add(placeholderOption);
        }
    }

    // Add event listener to the team dropdown
    teamSelect.addEventListener('change', function() {
        const selectedTeamId = this.value;
        updatePlayerOptions(selectedTeamId);
    });

    // Initial state setup on page load
    updatePlayerOptions(teamSelect.value);
});
