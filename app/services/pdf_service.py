from fastapi import HTTPException
def generate_pdf_logic(payload):
    if not payload and not payload.get("name"):
        raise HTTPException(404,"Missing required details")
    return "Htpps://www.google.com"