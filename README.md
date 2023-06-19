QA Local Demo
=============

This is a demo of the QA system running locally. The demo is a simple Flask app that allows you to enter a question and get an answer from the QA system. 

 how to use
 ---
    1. install requirements, 'pip install -r requirements'
    2. add .env file, and add OPENAI_API_KEY=xxx item
    3. ingest local file, change file path in addLocalFile.py
    4. run 'python3 addLocalFile.py' to ingest local file
    5. run 'python3 app.py' to start server
    6. visit http://127.0.0.1:5002