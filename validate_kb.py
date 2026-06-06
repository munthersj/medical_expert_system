from core.loader import load_knowledge_base
from core.validator import validate_knowledge_base


if __name__ == "__main__":
    kb = load_knowledge_base()
    errors = validate_knowledge_base(kb)

    if not errors:
        print("Knowledge base validation passed.")
    else:
        print("Knowledge base validation failed:")
        for error in errors:
            print("-", error)