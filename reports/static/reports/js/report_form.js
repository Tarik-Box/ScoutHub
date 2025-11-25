document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#create-report-form');
    if (!form) {
        return;
    }

    // --- Get Element References ---
    const rawPlayersData = form.dataset.playersData;
    const playersData = JSON.parse(rawPlayersData);

    const teamSelect = document.getElementById(form.dataset.teamSelectId);
    const playerSelect = document.getElementById(form.dataset.playerSelectId);
    const titleInput = document.getElementById('id_title');
    const contentInput = document.getElementById('id_content'); // Django's default ID for a textarea
    const saveReportBtn = document.getElementById('save-report-btn');
    let initialPlayerId = form.dataset.initialPlayerId; // Use 'let' for reassignability

    if (!teamSelect || !playerSelect || !titleInput || !contentInput || !saveReportBtn) {
        return;
    }

    // --- Core Logic Functions ---
    
    function checkFormValidityAndToggleButton() {
        const isTitleValid = titleInput.value.trim() !== '';
        const isContentValid = contentInput.value.trim() !== '';
        const isTeamValid = teamSelect.value !== '';
        const isPlayerValid = playerSelect.value !== '' && !playerSelect.disabled;
        
        // Enable the button only if all conditions are met
        if (isTitleValid && isContentValid && isTeamValid && isPlayerValid) {
            saveReportBtn.disabled = false;
        } else {
            saveReportBtn.disabled = true;
        }
    }

    function updatePlayerOptions(selectedTeamId) {
        playerSelect.innerHTML = ''; // Clear current player options

        if (selectedTeamId && playersData[selectedTeamId] && playersData[selectedTeamId].length > 0) {
            playerSelect.disabled = false;
            const placeholderOption = new Option('--- Select a Player ---', '');
            playerSelect.add(placeholderOption);

            const players = playersData[selectedTeamId];
            players.forEach(player => {
                const option = new Option(player.name, player.id);
                playerSelect.add(option);
            });
            // --- Try to select initial player if editing ---
            if (initialPlayerId && teamSelect.value === selectedTeamId) {
                playerSelect.value = Number(initialPlayerId); // Convert to number for strict comparison
                // Clear initialPlayerId after it's used to prevent re-selection if team changes
                initialPlayerId = null;
            }
        } else if (selectedTeamId) {
            playerSelect.disabled = true;
            const noPlayersOption = new Option('No players found for this team', '');
            playerSelect.add(noPlayersOption);
        } else {
            playerSelect.disabled = true;
            const placeholderOption = new Option('--- Select a Team First ---', '');
            playerSelect.add(placeholderOption);
        }
        // After updating player options, check the form's overall validity
        checkFormValidityAndToggleButton();
    }


    // --- Attach Event Listeners ---
    
    titleInput.addEventListener('input', checkFormValidityAndToggleButton);
    contentInput.addEventListener('input', checkFormValidityAndToggleButton);
    playerSelect.addEventListener('change', checkFormValidityAndToggleButton);
    
    teamSelect.addEventListener('change', function() {
        // When the team changes, we must first update the player options,
        // which then triggers its own validity check.
        updatePlayerOptions(teamSelect.value);
    });

    // --- Initial State Setup ---
    updatePlayerOptions(teamSelect.value);
});