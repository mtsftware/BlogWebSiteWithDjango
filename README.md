# Blog Website

This website, developed with Django, was created entirely to test and practice my backend skills. I couldn't upload the original project to GitHub because I didn't pay attention to sensitive information in the `settings.py` file during development. I copied the final version of the project to a new Django project and published it on GitHub with the necessary security measures.

## Main Features

- **Login & Signup**: Users activate their accounts via the activation link sent to their email after registration and then log in.
- **E-Mail API**: Email validation and sending are done using a third-party API.
- **Page Creation**: Users can create their own or public blog pages.
- **Blog Publishing**: Users can publish blogs on their own pages or on pages created by other users.
- **Tags and SEO Optimization**: Users add various tags to their blogs to create additional tag fields for blog page access. The goal is to create a completely SEO-friendly site using Django's slugify features.

## Installation

1. Clone the Project:
   
  ```bash
     git clone https://github.com/mtsftware/BlogWebSiteWithDjango
  ```

2. Create and Activate the Virtual Environment:

   ```bash
      python -m venv .venv
      source .venv/bin/activate  # Linux/macOS
      .venv\Scripts\activate      # Windows
   ```

3. Install Dependencies:

     ```bash
    pip install -r requirements.txt
     ```

4. Create the .env file and configure it:

     ```bash
     cp .env.example .env
     ```

5. Create the database and apply migrations:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. Create an admin user (optional):

     ```bash
      python manage.py createsuperuser
     ```

7. Start the development server:

   ```bash
    python manage.py runserver
   ```



