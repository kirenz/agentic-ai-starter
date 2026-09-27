"""List available Gemini Flash models and check the configured MODEL_ID."""

from google import genai

from helpdesk.config import MODEL_ID


def main() -> None:
    client = genai.Client()
    names = sorted(
        m.name.removeprefix("models/") for m in client.models.list() if "flash" in m.name
    )
    print("\n".join(names))
    status = "OK" if MODEL_ID in names else "NOT AVAILABLE"
    print(f"\nConfigured model: {MODEL_ID} -> {status}")


if __name__ == "__main__":
    main()
