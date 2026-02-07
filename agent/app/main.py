from agent.app.collector import collect
from agent.app.reporter import send

def main():
    results = collect()
    send(results)

if __name__ == "__main__":
    main()