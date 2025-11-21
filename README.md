# ScoutHub

ScoutHub is a Django-based web application designed for football enthusiasts and scouts to track top league teams and players, as well as create and manage their personal scouting reports. The application integrates with an external Football API to provide up-to-date data.

## Features

### Core Functionality
-   **User Authentication:** Secure registration, login, and logout functionalities.
-   **Dashboard:** Personalized dashboard for logged-in users to manage their reports.
-   **Homepage Data Display:** Dynamically displays top 5 league teams (with position, points, form) and top 5 players (with goals, assists) from a selected league.
-   **Scouting Report Management (CRUD):**
    -   **Create:** Users can create new scouting reports using a dynamic form where team selection populates relevant players. Includes client-side validation and a disabled save button until the form is complete.
    -   **Read (List):** View a paginated list of all created reports on the user dashboard.
    -   **Read (Detail):** Access a detailed view for individual reports.
    -   **Edit:** Modify existing reports via a pre-filled form with data validation and success messages.
-   **Data Synchronization:** Management command to fetch and update football data from the API, respecting rate limits.

## Technologies Used

This project utilizes the following technologies:

-   **Backend:**
    -   Python 3.x
    -   Django (Web Framework)
    -   PostgreSQL (Database)
    -   `python-decouple`: For managing environment variables.
    -   `requests`: For making HTTP requests to external APIs.
    -   `dj-database-url`: For parsing database URLs.
    -   `Black`: Code formatter for consistent styling.
-   **Frontend:**
    -   HTML5
    -   CSS3 (leveraging Bootstrap 5 for responsive design and components)
    -   JavaScript (Vanilla JS for dynamic form elements and client-side validation)
-   **External API:**
    -   API-Football v3.co (for football data)

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

-   Python 3.8+
-   `pip` (Python package installer)
-   `git`
-   PostgreSQL database (local or remote, e.g., Neon.tech)
-   API-Football v3.co API Key

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Tarik-Box/ScoutHub.git
    cd ScoutHub
    ```

2.  **Set up a Virtual Environment:**
    It's recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    Create a `.env` file in the root directory of the project and add your database URL and API-Football API key:
    ```
    DATABASE_URL="postgres://user:password@host:port/dbname"
    API_KEY="your_api_football_v3_key_here"
    ```
    *Replace with your actual PostgreSQL connection string and API key.*
    
    To obtain your API-Football v3 key:
    1.  Go to [https://www.api-football.com/](https://www.api-football.com/)
    2.  Create a new account or log in.
    3.  Navigate to `Dashboard` > `Account` > `My Access` to find your API key.

5.  **Database Migrations:**
    Apply the database migrations to set up your database schema.
    ```bash
    .venv/bin/python manage.py migrate
    ```

6.  **Create a Superuser (for Admin access):**
    ```bash
    .venv/bin/python manage.py createsuperuser
    ```
    Follow the prompts to create your admin user.

7.  **Fetch Initial Football Data:**
    Populate your database with initial team and player data from the API. (Use `2023` for the season year for reliable data).
    ```bash
    .venv/bin/python manage.py fetch_football_data --season_year=2023 --force_update
    ```
    This command will fetch standings and top scorer data.

## Running the Application

To start the Django development server:

```bash
.venv/bin/python manage.py runserver
```

The application will be accessible at `http://127.0.0.1:8000/`.

## Usage

-   **Register/Login:** Create an account or log in to access personalized features.
-   **View Homepage:** See the top 5 league teams and players.
-   **Dashboard:** Access your created scouting reports.
-   **Create Report:** Fill out the form to save a new scouting report.
-   **View Report:** Click on a report title on the dashboard to see its details.
-   **Edit Report:** Modify your existing scouting reports.

## Deployment

*(To be detailed later: Considerations for deploying to a production environment.)*

## Contributing

*(To be detailed later: Guidelines for contributing to the project.)*

## Testing

*(To be detailed later: Information about testing methodologies, tools, and instructions on how to run tests.)*

## Design Thinking

*(To be detailed later: Explanation of the design process, user research, and UX/UI decisions.)*

## Agile Methodology

*(To be detailed later: Details about the Agile methodology followed, including user stories, sprints, and project management tools.)*

## Credits

*(To be detailed later: Acknowledgments for libraries, resources, or individuals who contributed.)*

## License

This project is licensed under the MIT License - see the LICENSE.md file for details. *(Note: LICENSE.md file may need to be created.)*
