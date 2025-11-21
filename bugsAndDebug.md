## Bugs & Debugging Log

### Corrupted Commit Message (Fixed)
During development, a commit message for `8ccf41f` (later removed via force push) was accidentally corrupted, including unintended script usage output. This was due to an oversight in handling multi-line strings in the `git commit` command within the environment.

**Resolution:** The commit was completely removed from the repository history using `git reset --hard` and `git push --force`, and the changes were re-committed with a corrected message.

![Screenshot of corrupted commit message](docs/images/corrupted_commit_message.png)

### Database Backend Mismatch (Resolved)
After attempting to switch the database backend from SQLite to PostgreSQL and resolving a corrupted commit message via `git reset --hard` and re-commit, the project inexplicably reverted to using SQLite. This occurred despite `scout_hub/settings.py` being correctly configured for PostgreSQL via `DATABASE_URL` from `.env`. All migrations, superuser accounts, and fetched API data were being stored in `db.sqlite3`.

**Resolution:** The issue stemmed from an unclear state of the PostgreSQL database. The fix involved:
1.  **Ensuring PostgreSQL Database was Truly Empty:** Manually deleting and recreating the `neondb` on Neon.tech.
2.  **Cleaning Local State:** Deleting `db.sqlite3` and all existing `core` app migrations (`0*.py` files).
3.  **Rebuilding Database:** Running `makemigrations`, `migrate`, `createsuperuser`, and `fetch_football_data` to populate the newly reset PostgreSQL database.
This process successfully switched the project to use PostgreSQL as the backend database.

![Screenshot of database backend mismatch](docs/images/db_mismatch_error.png)

### Player Image Not Displayed (Resolved)
The player images were not displaying on the homepage due to a typo in the `web/templates/web/home.html` template. The template was incorrectly trying to access `player.image.url` assuming `image` was an ImageField, whereas the `Player` model uses a `URLField` named `image_url`.

**Resolution:** The template reference was corrected from `player.image.url` to `player.image_url`.

### NoReverseMatch for 'login' URL (Resolved)
When attempting to access the registration page (`/accounts/register/`), a `NoReverseMatch` exception was raised, indicating that the URL pattern named 'login' could not be found. This occurred because the registration template (`register.html`) contained a link to `{% url 'login' %}`, but the `login` URL pattern was defined within the `accounts` app namespace.

**Resolution:** The template reference in `accounts/templates/accounts/register.html` was corrected from `{% url 'login' %}` to `{% url 'accounts:login' %}` to use the namespaced URL.

### Logout URL Not Accessible (Pending Resolution)
When attempting to logout by clicking the "Logout" button/link, the application redirects to `/accounts/logout/` which results in a page not found error. This is because Django's built-in `LogoutView` primarily expects a POST request for security, whereas the link in the template is sending a GET request.

**Resolution:** _(Empty for now, pending implementation of the logout form in `base.html`)_

### Dependent Player Dropdown Not Populating (Resolved)
The "Create Report" form includes a "Team" dropdown and a "Player" dropdown that should be dynamically populated via JavaScript. When a team was selected, the player dropdown remained empty.

**Resolution:** The bug was traced through a multi-step debugging process.
1.  **Initial Hypothesis:** The first assumption was that the JSON data being passed from the Django view to the template was being improperly escaped. This was addressed by applying the `|safe` filter in the template, but the bug persisted.
2.  **Instrumenting the Code:** To get visibility into the script's execution, the JavaScript file (`report_form.js`) was modified to include extensive `console.log()` statements at every step: reading the data, parsing the JSON, finding the form elements, and handling the `change` event.
3.  **Browser Console Analysis:** The browser's developer console revealed the root cause. A "DEBUG" message showed that the script was finding a `<form>` element, but it was the wrong one: `<form action="/accounts/logout/">`.
4.  **Root Cause Identified:** The JavaScript selector `document.querySelector('form')` was too generic. It was selecting the first form in the DOM, which happened to be the logout form in the `base.html` navigation bar, not the intended report creation form. This logout form lacked the `data-players-data` attribute, causing the script to fail with an `"undefined" is not valid JSON` error.
5.  **The Fix:**
    *   A unique ID, `id="create-report-form"`, was added to the `<form>` tag in the `reports/templates/reports/create_report.html` template.
    *   The JavaScript selector was updated to the more specific `document.querySelector('#create-report-form')` to guarantee it selected the correct form.
This change resolved the issue, and the dropdowns now function as expected.