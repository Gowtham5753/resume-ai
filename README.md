# 🧠 AI Resume Builder & ATS Reviewer

## Overview

This is a full-stack web application designed to assist job seekers by generating professional, ATS-compliant resumes and analyzing existing PDF resumes against specific job descriptions. The application uses **Flask (Python)** for the backend API and the **Gemini API** for all generative and analytical tasks.

### Features

  * **Two-Column UI:** Separates the **Generation** feature (Form 1) from the **ATS Review** feature (Form 2) for a clean user experience.
  * **Resume Generation:** Creates a new resume based on user input, strictly following a quantifiable, **Software Engineer** ATS format.
  * **ATS Resume Review:** Allows users to **upload an existing PDF resume** and paste a job description (JD) to receive a detailed compatibility report, including a score and suggestions.
  * **Secure Deployment:** Utilizes the `.env` file for API key protection, ensuring your key is **never** committed to the public repository.
  * **PDF Output:** Generates the final output (resume or review report) as a professional PDF file.

-----

## 🔒 Security and API Key Setup (CRITICAL)

**Your secret key is not in this repository.** This project uses `python-dotenv` to securely load the key from an ignored local file.

### Setup Instructions for Reviewer:

1.  **Get API Key:** Obtain a free Gemini API Key from [Google AI Studio].

2.  **Create `.env` File:** In the root directory of this project, create a file named **`.env`**.

3.  **Insert Key:** Copy the following content into your new **`.env`** file, replacing `YOUR_KEY_HERE` with your actual Gemini API Key:

    ```env
    # .env
    # This file is ignored by .gitignore and WILL NOT be uploaded to GitHub.
    GEMINI_API_KEY="YOUR_KEY_HERE"
    ```

-----

## 🚀 Setup and Run Instructions

Ensure you have Python (3.9+) and Git installed.

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/Gowtham5753/resume-ai.git
    cd resume-ai
    ```

2.  **Install Dependencies:**

      * This project requires a few external libraries for PDF handling and AI:

    <!-- end list -->

    ```bash
    pip install Flask google-generativeai reportlab pypdf python-dotenv
    ```

3.  **Activate Virtual Environment (Recommended):**

    ```bash
    # On Windows:
    .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```

4.  **Run the Flask Server:**

    ```bash
    python server.py
    ```

    The server must remain running for the application to work.

5.  **Open the Application:** Open your web browser and navigate directly to the `index.html` file in your project folder (e.g., `file:///path/to/resume-ai/index.html`).

-----

## 📝 Usage

The web page is divided into two independent sections:

### Section 1: Resume Generation

  * **Function:** Creates a brand new resume from scratch.
  * **Process:** Fill out all input fields and click **"Generate & Review Resume."**
  * **Output:** The generated, ATS-friendly resume text appears in the results area.

### Section 2: ATS Resume Review

  * **Function:** Analyzes an existing resume against a job description.
  * **Process:**
    1.  Click **"Upload Existing Resume (PDF Only)"** to select a file.
    2.  Paste the full text of the **Target Job Description**.
    3.  Click **"Get ATS Review & Score."**
  * **Output:** The result area displays a detailed ATS report, including a match score and suggestions for improvement.

### PDF Download

  * After running either feature, click **"Download Report as PDF"** to save the resulting content (the resume or the ATS report) as a professional PDF file.
