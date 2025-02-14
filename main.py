from flask import Flask, render_template, request, session, redirect
import requests
import pandas as pd
import os


app = Flask(__name__)
app.secret_key = os.urandom(10).hex()

@app.route("/")
def index():
     return render_template("index.html") # flight map file

@app.route("/trivia")
def trivia():
    # Generate questions and restart if resubmitting
     if "questions" not in session:
        r = requests.get("https://opentdb.com/api.php?amount=10&category=22&type=multiple")
        trivia_data = r.json()
        questions = trivia_data['results']

        # Prepare options for each question
        for q in questions:
          q["options"] = q["incorrect_answers"] + [q["correct_answer"]] # list of all options

        session["questions"] = questions #questions for this round

     questions = session["questions"] #restores questions
     return render_template("trivia.html", questions=questions)

@app.route("/trivia-submit", methods=["POST"])
def trivia_submit():
    
    user_answers = []
    # Retrieve all submitted answers
    for i in range(10):
        user_answers.append(request.form.get(f"answer{i + 1}"))

    # Retrieve the questions from this specific session
    questions = session["questions"]
    
    # Check if the user answered correctly and create a score
    correct_answers = 0
    for i in range(10):
        question = questions[i] # get a specific question
        if user_answers[i] == question["correct_answer"]: # check if the answer matches the correct answer
            correct_answers += 1 # add to the score

    # Return the result to the user
    return render_template("results.html", score=correct_answers)

@app.route("/ctry-info", methods=["GET", "POST"])
def ctry_info():
    if request.method == 'POST':
        ctry = request.form.get("ctryname")
        r = requests.get("https://restcountries.com/v3.1/name/f'{ctry}?fields=name,capital,currencies,languages,car")
        response = r.json()

        for i in response[0]['currencies'].items():
            currency_list = []
            currency_list.append(i[1]['name'])

        for i in response[0]['languages'].items():
            lang_list = []
            lang_list.append(i[1])

        df = pd.DataFrame(data={
            "name": response[0]['name']['common'],
            "currencies": currency_list[0],
            "capital": response[0]['capital'],
            "languages": lang_list[0],
            'car': response[0]['car']['side']})
        
        return render_template("country-results.html", results=df)


if __name__ == "__main__":
    app.run(debug=True)