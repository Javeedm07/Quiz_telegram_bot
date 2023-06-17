# Importing rqquired libraries and modules
import pandas as pd
import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from transformers import DistilBertTokenizer

# Adding .csv file
df = pd.read_csv('dataset.csv')

# Initialize the score variable
score = 0

# Counter for tracking the number of questions asked
question_counter = 0

# Total number of questions to ask in the quiz
total_questions = 0

# List to keep track of the questions asked
asked_questions = []

#To handle the missing values in your dataframe before fitting the vectorizer
df.dropna(subset=['question'], inplace=True)

# Tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

# Vectorizer
vectorizer = TfidfVectorizer(tokenizer=tokenizer.tokenize)

# Fit the vectorizer on the questions
vectorizer.fit(df['question'])

# Transform the questions into vectors
question_vectors = vectorizer.transform(df['question'])

# Model
model = SVC()

# Fit the model
model.fit(question_vectors, df['answer'])

# Define a callback function to handle the /start command
def start(update, context):
    global score, question_counter, asked_questions, total_questions
    score = 0
    question_counter = 0
    asked_questions = []
    total_questions = 0
    update.message.reply_text("Welcome to the Quiz! How many questions do you want to answer?")


# Define a callback function to handle the number of questions requested by the user
def handle_num_questions(update, context):
    global total_questions
    num_questions = update.message.text
    if num_questions.isdigit():
        total_questions = int(num_questions)
        if total_questions > 0:
            ask_question(update, context)
        else:
            update.message.reply_text("Invalid number of questions. Please enter a positive integer.")
    else:
        update.message.reply_text("Invalid input. Please enter a number.")

l=['Better Luck next time','Better Luck next time','Better Luck next time','Good. You can do better','Good job','Great job! You got a perfect score']

def handle_message(update, context):
    global score, question_counter, total_questions
    user_answer = update.message.text.lower()

    # Check if it's the first question being asked
    if question_counter == 0:
        try:
            total_questions = int(user_answer)
            if total_questions <= 0:
                update.message.reply_text("Please enter a valid number of questions.")
                return
        except ValueError:
            update.message.reply_text("Please enter a valid number of questions.")
            return
        update.message.reply_text(f"Great! I will ask you {total_questions} questions.")
        question_counter += 1
        ask_question(update, context)
        return

    # Check if the user's answer matches the correct answer
    if question_counter <= total_questions:
        correct_answer = df['answer'][asked_questions[question_counter - 1]]
        if user_answer == correct_answer.lower():
            score += 1
            update.message.reply_text("Correct answer! 👏")
        else:
            update.message.reply_text(f"Wrong answer! 😕 The correct answer is: {correct_answer}")
        question_counter += 1  # Increment question_counter here
        if question_counter <= total_questions:
            ask_question(update, context)
        else:
            half_percentage = ( (score/total_questions)*100 ) // 2
            update.message.reply_text(f"Quiz completed! Your score is {score}/{total_questions}.\n{l[int(half_percentage//10)]}")
            score = 0
            question_counter = 0
    else:
        update.message.reply_text("No more questions available. Quiz ended.")

# Function to ask a random question
def ask_question(update, context):
    global question_counter, asked_questions
    if question_counter == 1:
        update.message.reply_text("Let's begin the quiz!")
    # Randomly select a question that hasn't been asked before
    available_questions = [i for i in range(len(df)) if i not in asked_questions]
    if len(available_questions) == 0:
        # All questions have been asked, end the quiz
        update.message.reply_text("No more questions available. Quiz ended.")
        return
    random_question = random.choice(available_questions)
    question = df['question'][random_question]
    asked_questions.append(random_question)
    update.message.reply_text(f"Question {question_counter}: {question}")


# Set up the Telegram bot
def main():
    updater = Updater('YOUR_TELEGRAM_BOT_TOKEN', use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(MessageHandler(Filters.text & Filters.command, handle_num_questions))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()