"""
main.py - The interactive command-line loop that ties everything together.

Pipeline
    input --> carefully built prompt --> model --> validated output --> use it 

"""


import argparse 
import sys 

# We need to make sure to the environment variable 
from dotenv import load_dotenv 
load_dotenv()


from coach import generate_questions, grade_answer 

def main():
    parser = argparse.ArgumentParser(description="AI Interview Coach")
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Creativity dial for question generation. ~0.0 = focused, ~1.2 = wild."
    )
    args = parser.parse_args()

    print("=" * 64)
    print(" AI INTERVIEW COACH")
    print("=" * 64)

    topic = input("\nWhat topic do you want to be interviewed on?\n> ").strip()

    if not topic:
        print("No topic given. Goodbye.")
        return 
    
    print(f"\nGenerating questioin on '{topic}' (temperature={args.temperature}) ...")
    try:
        question_set = generate_questions(topic, temperature=args.temperature)
    except RuntimeError as error:
        print(f"\n[!] {error}")
        sys.exit(1)

    total = len(question_set.questions)
    for index, q in enumerate(question_set.questions, start=1):
        print("\n"+"-" * 64)
        print(f"Question {index} of {total}")
        print(f" {q.question}")

        user_answer = input("\n Your answer (press Enter to skip and see the model answer):\n> ").strip()

        if not user_answer:
            print("\n Model answer:")
            print(f"    {q.model_answer}")
        else:
            print("\n Coach feedback:")
            print(" "+ "-" * 22)
            grade_answer(q.question, q.model_answer,user_answer)

        
        if q.follow_ups:
            print("\n Follow-up questions to think about:")
            for follow_up in q.follow_ups:
                print(f"    -{follow_up}")
    
    print("\n" + "=" * 64)
    print(" Session complete.")
    print(" Tip: run again with different --temperature and feel the difference.")
    print("=" * 64)

if __name__ == "__main__":
    main()

