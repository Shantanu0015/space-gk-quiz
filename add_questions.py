import sqlite3

db = sqlite3.connect("quiz.db")

questions = [
    (1, "Who became the Prime Minister of India in 1974?",
     "Indira Gandhi", "Jawaharlal Nehru", "Rajiv Gandhi", "Morarji Desai",
     "Indira Gandhi"),

    (2, "India conducted its first nuclear test in which year?",
     "1968", "1971", "1974", "1980",
     "1974"),

    (3, "Which country won the FIFA World Cup 1974?",
     "Brazil", "Germany", "Argentina", "Italy",
     "Germany"),

    (4, "Who was the first woman Prime Minister of India?",
     "Sarojini Naidu", "Indira Gandhi", "Pratibha Patil", "Sonia Gandhi",
     "Indira Gandhi"),

    (5, "The Emergency in India was declared in which year?",
     "1972", "1973", "1975", "1977",
     "1975"),

    (6, "Who was the President of India in 1980?",
     "Zail Singh", "R. D. Sharma", "Neelam Sanjiva Reddy", "Rajendra Prasad",
     "Neelam Sanjiva Reddy"),

    (7, "Which Indian satellite was launched in 1975?",
     "INSAT-1A", "Aryabhata", "Bhaskara", "Rohini",
     "Aryabhata"),

    (8, "Who won the Cricket World Cup 1983?",
     "Australia", "England", "West Indies", "India",
     "India"),

    (9, "Which year did the Berlin Wall fall?",
     "1985", "1987", "1989", "1991",
     "1989"),

    (10, "Who is known as the Missile Man of India?",
     "C. V. Raman", "Homi Bhabha", "A. P. J. Abdul Kalam", "Vikram Sarabhai",
     "A. P. J. Abdul Kalam"),

    (11, "India’s economic liberalization started in which year?",
     "1985", "1988", "1991", "1995",
     "1991"),

    (12, "Who became the Prime Minister of India in 2014?",
     "Rahul Gandhi", "Narendra Modi", "Manmohan Singh", "Amit Shah",
     "Narendra Modi"),

    (13, "Which country hosted the 2016 Olympics?",
     "China", "Brazil", "UK", "Japan",
     "Brazil"),

    (14, "Which pandemic affected the world in 2020?",
     "SARS", "Ebola", "COVID-19", "Zika",
     "COVID-19"),

    (15, "Who is the current Prime Minister of India (2025)?",
     "Narendra Modi", "Rahul Gandhi", "Amit Shah", "Arvind Kejriwal",
     "Narendra Modi"),
]
for q in questions:
    try:
        db.execute("INSERT INTO questions VALUES (?,?,?,?,?,?,?)", q)
    except sqlite3.IntegrityError:
        print(f"Question with id {q[0]} already exists, skipping...")

db.commit()
db.close()

print("Questions added successfully!")