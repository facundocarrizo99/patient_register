from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import os
import imghdr
from . import models, schemas, crud, database, email_utils


app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db() -> Session:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )


def _build_document_filename(email: str, original_filename: str) -> str:
    file_ext = os.path.splitext(original_filename)[1]
    sanitized_email = email.replace("@", "_at_")
    return f"{sanitized_email}{file_ext}"


@app.post("/patients", response_model=schemas.PatientOut)
async def register_patient(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    document_photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    patient_in = schemas.PatientCreate(name=name, email=email, phone=phone)

    if db.query(models.Patient).filter(models.Patient.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if not document_photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    contents = await document_photo.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB).")

    if imghdr.what(None, h=contents) not in ["jpeg", "png"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid image format. Only JPEG and PNG are allowed.",
        )

    file_name = _build_document_filename(email, document_photo.filename)
    file_path = os.path.join(UPLOAD_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(contents)

    try:
        patient = crud.create_patient(db, patient_in, document_photo_path=file_path)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error.")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error.")

    background_tasks.add_task(email_utils.send_confirmation_email, email, name)

    return patient


@app.get("/")
def root() -> dict:
    return {"message": "Patient Registration API"}