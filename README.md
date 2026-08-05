# Malaria vs Typhoid Knowledge-Based System

## Project Overview

This project is a rule-based expert system developed using Python and Kanren. It assists users by evaluating symptoms and providing a possible diagnosis of either malaria or typhoid.
## Implementation

The system was originally designed with the knowledge base, rules, and inference logic implemented directly in JavaScript. This resulted in two separate implementations of the expert system logic, increasing the risk of inconsistencies and making maintenance more difficult.

The application has since been refactored to follow a client-server architecture. The frontend is now responsible only for the user interface, including presenting questions, collecting user responses, and displaying the diagnosis. All expert system logic has been moved to the backend, where `app.py` exposes a `/diagnose` API endpoint and `kbs_engine.py` contains the Kanren-based knowledge base and inference engine.

When a user submits their symptoms, the frontend sends the selected responses to the backend through the `/diagnose` API. The backend evaluates the symptoms using Kanren's rule-based inference mechanism and returns both the diagnosis and an explanation of the reasoning.

This design provides a single source of truth for the knowledge base, improves maintainability, eliminates duplicated logic between the frontend and backend, and demonstrates the use of a genuine Kanren-based expert system.

## Project Structure

```
APT3020-KBS-malaria-vs-typhoid-/
│── static/
│── templates/
│── app.py
│── kbs_engine.py
```

## Requirements

- Python 3.x
- Kanren

Install dependencies using:

```bash
pip install kanren
```

## Running the Project

Start the application with:

```bash
python app.py
```