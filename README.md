<<<<<<< HEAD
# Perf - School Performance Management App

Perf is a Streamlit-based web application for managing and visualizing school performance data, including teacher management, attendance, journals, cahiers, materials, rapports, devoirs, and more.

## Features

- **Teacher Management:** Add, edit, delete, and visualize teacher data.
- **Attendance:** Record and review daily attendance for teachers.
- **Journal:** Track teacher journals and observations.
- **Cahiers:** Validate and inspect lesson books.
- **Materials:** Distribute and track teaching materials.
- **Rapport:** Manage and track report submissions and deliveries.
- **Devoir:** Monitor homework (devoir) submissions by teachers for their classes.
- **Settings:** CRUD for subjects, classes, modules, submodules, materials, and more.
- **Data Visualizations:** Insights on teachers, attendance, devoir status, and more.

## Project Structure

```
Perf/
├── app.py
├── config.py
├── database.py
├── teacher_menu.py
├── attendance_menu.py
├── journal_menu.py
├── cahiers_menu.py
├── materials_menu.py
├── rapport_menu.py
├── devoir_menu.py
├── settings_menu.py
├── teachers_visual_menu.py
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [SQLite3](https://www.sqlite.org/index.html)

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/Perf.git
    cd Perf
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the app:**
    ```sh
    streamlit run app.py
    ```

### Configuration

- Edit `config.py` to set up your subjects, classes, modules, submodules, and materials.

### Database

- The app uses an SQLite database (`attendance.db`) and will initialize all required tables on first run.

## Deployment

You can deploy this app for free using [Streamlit Community Cloud](https://share.streamlit.io/):

1. Push your code to GitHub.
2. Go to [Streamlit Cloud](https://share.streamlit.io/), sign in, and create a new app from your repo.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)

## Acknowledgements

- Built with [Streamlit](https://streamlit.io/)
- Inspired by real-world school management needs
=======
# Perf - School Performance Management App

Perf is a Streamlit-based web application for managing and visualizing school performance data, including teacher management, attendance, journals, cahiers, materials, rapports, devoirs, and more.

## Features

- **Teacher Management:** Add, edit, delete, and visualize teacher data.
- **Attendance:** Record and review daily attendance for teachers.
- **Journal:** Track teacher journals and observations.
- **Cahiers:** Validate and inspect lesson books.
- **Materials:** Distribute and track teaching materials.
- **Rapport:** Manage and track report submissions and deliveries.
- **Devoir:** Monitor homework (devoir) submissions by teachers for their classes.
- **Settings:** CRUD for subjects, classes, modules, submodules, materials, and more.
- **Data Visualizations:** Insights on teachers, attendance, devoir status, and more.

## Project Structure

```
Perf/
├── app.py
├── config.py
├── database.py
├── teacher_menu.py
├── attendance_menu.py
├── journal_menu.py
├── cahiers_menu.py
├── materials_menu.py
├── rapport_menu.py
├── devoir_menu.py
├── settings_menu.py
├── teachers_visual_menu.py
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [SQLite3](https://www.sqlite.org/index.html)

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/Perf.git
    cd Perf
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the app:**
    ```sh
    streamlit run app.py
    ```

### Configuration

- Edit `config.py` to set up your subjects, classes, modules, submodules, and materials.

### Database

- The app uses an SQLite database (`attendance.db`) and will initialize all required tables on first run.

## Deployment

You can deploy this app for free using [Streamlit Community Cloud](https://share.streamlit.io/):

1. Push your code to GitHub.
2. Go to [Streamlit Cloud](https://share.streamlit.io/), sign in, and create a new app from your repo.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)

## Acknowledgements

- Built with [Streamlit](https://streamlit.io/)
- Inspired by real-world school management needs
>>>>>>> 7a70e5efef2ce3ca2f1cdc291bf43c6062b79df7
