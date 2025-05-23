# Movie Review Log

A full-stack movie logging application with a Flask backend and React frontend. Users can create, read, update, and delete movie reviews including movie name, watch date, rating, and optional text review. The app validates input including preventing future watch dates.

---

## Features

- Add new movie reviews with movie name, watch date, rating (0-10), and optional review text
- Edit existing movie reviews
- Delete movie reviews
- View all reviews in a table sorted by watch date (newest first)
- Validation to prevent watch dates in the future
- Simple and clean UI using React

---

## Tech Stack

- Backend: Python, Flask, PostgreSQL, psycopg2, Flask-CORS
- Frontend: React, Axios
- Styling: Tailwind CSS (optional, fallback CSS included)

---

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL installed and running
- Node.js 16+ and npm or yarn

---

### Backend Setup

1. Clone the repo and navigate to the backend folder (or root if combined):

    ```bash
    git clone <your-repo-url>
    cd <backend-folder>
    ```

2. Create a Python virtual environment and activate it:

    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3. Install Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a PostgreSQL database for the app.

![App Screenshot](images/neondb.png)

5. Create a `.env` file in the backend folder with the following:

    ```
    DATABASE_URL=postgresql://username:password@localhost:5432/your_database_name
    ```

6. Run the Flask backend server:

    ```bash
    python app.py
    ```

7. (Optional) To create the database table and insert sample data, POST to:

    ```
    http://localhost:5000/api/debug/create-table
    ```

---

### Frontend Setup

1. Navigate to the React frontend folder (e.g., `client`):

    ```bash
    cd client
    ```

2. Install frontend dependencies:

    ```bash
    npm install
    ```

3. Start the React development server:

    ```bash
    npm start
    ```

4. The app will open at [http://localhost:3000](http://localhost:3000).

---

### Notes on Styling

- The React app uses Tailwind CSS for styling by default.
- If you cannot install or use Tailwind, replace `src/App.css` with the provided fallback CSS and import it into `App.js`.
- Tailwind installation requires Node.js and proper setup; consult [Tailwind docs](https://tailwindcss.com/docs/guides/create-react-app) if needed.

---

## API Endpoints

| Method | Endpoint               | Description                |
|--------|------------------------|----------------------------|
| GET    | `/api/health`          | Health check of backend    |
| GET    | `/api/movies`          | Get all movies             |
| POST   | `/api/movies`          | Create a new movie review  |
| GET    | `/api/movies/<id>`     | Get movie by ID            |
| PUT    | `/api/movies/<id>`     | Update movie by ID         |
| DELETE | `/api/movies/<id>`     | Delete movie by ID         |
| POST   | `/api/debug/create-table` | Create table and seed data (debug) |

---

## Usage

- Add a movie by filling the form and clicking **Add Movie**.
- Edit an existing movie by clicking **Edit**, modifying fields, then **Update Movie**.
- Delete a movie by clicking **Delete**.
- The watch date must not be a future date.
- Ratings must be between 0 and 10.

---

## Troubleshooting

- Make sure PostgreSQL is running and `DATABASE_URL` is correct.
- Backend runs on port `5000` by default.
- Frontend runs on port `3000` by default.
- If CORS issues occur, ensure Flask-CORS is enabled.
- For date validation, ensure your system date/time is correct.

---

## License

MIT License © Huseyin Samet Alemdar

---

## Contact

For questions or feedback, please contact [sametalemdar111@gmail.com].

