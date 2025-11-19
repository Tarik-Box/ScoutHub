# ScoutHub

## Technologies Used

This project utilizes the following technologies:

-   **Backend:**
    -   Python 3.x
    -   Django (Web Framework)
    -   PostgreSQL (Database)
-   **Frontend:**
    -   HTML5

## Known Bugs

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