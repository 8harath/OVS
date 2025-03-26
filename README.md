# Online Voting System

## Project Description

This repository contains the code for an Online Voting System, which is a college project. The project aims to provide a secure and user-friendly platform for conducting online elections. It allows voters to register, log in, view candidates, and cast their votes electronically.

## Suggestions and Feedback

We welcome any suggestions and feedback to improve this project. Please feel free to open an issue or submit a pull request with your ideas and improvements.

## Project Setup and Installation

To set up and run the project locally, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/8harath/Online-Voting-System.git
   cd Online-Voting-System
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```
   python database.py
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Open your web browser and navigate to `http://127.0.0.1:5000` to access the application.


```

## Features and Functionalities

- **User Registration and Login**: Users can register with their details and log in to the system.
- **Dashboard**: After logging in, users can access their dashboard to view available candidates.
- **Candidate Details**: Users can view detailed information about each candidate, including their promises, assets, liabilities, background, political views, and regional views.
- **Voting**: Users can cast their vote for a candidate. Once a vote is cast, it is recorded in the database, and the user cannot vote again.
- **Vote Confirmation**: After voting, users receive a confirmation with a reference number for their vote.
- **Logout**: Users can log out of the system securely.

We hope this project serves as a useful tool for conducting online elections and provides a good learning experience for those interested in web development and database management.
---
