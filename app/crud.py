from sqlalchemy.orm import Session
from . import models, schemas


def create_patient(
    db: Session,
    patient: schemas.PatientCreate,
    document_photo_path: str,
) -> models.Patient:
    db_patient = models.Patient(
        name=patient.name,
        email=patient.email,
        phone=patient.phone,
        document_photo=document_photo_path,
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient