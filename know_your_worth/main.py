import subprocess

# Lista dei comandi per avviare ogni Flask app
commands = [
    "python3 know_your_worth/worker_exploitation_checker/flask_exploitation_checker.py",
    "python3 know_your_worth/advice_generator/flask_advice_generator.py",
    "python3 know_your_worth/questionnaire/flask_questionnaire.py",
    "python3 know_your_worth/manager/manager.py",
]

processes = []

for cmd in commands:
    # Avvia ogni comando in un processo separato
    p = subprocess.Popen(cmd, shell=True)
    processes.append(p)

print("Tutti i Flask server sono stati avviati.")

# (Opzionale) aspetta che tutti i processi finiscano
for p in processes:
    p.wait()
