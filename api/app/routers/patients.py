# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_active_user
from app.models import (
    PatientRecord,
    User,
)
from app.pydantic_models import (
    PatientModel,
)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=list[PatientModel])
async def get_patients(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[PatientModel]:
    if current_user.is_superuser:
        patients = await PatientRecord.all()
    elif not current_user.data_source:
        raise HTTPException(
            status_code=400,
            detail="User does not have a data source associated with it.",
        )
    else:
        patients = await PatientRecord.filter(data_source__name=current_user.data_source.name)
    return [await patient.to_pydantic_model() for patient in patients]


@router.post("", response_model=PatientModel, status_code=201)
async def create_patient(
    current_user: Annotated[User, Depends(get_current_active_user)],
    patient_input: PatientModel,
) -> PatientModel:
    if not current_user.data_source:
        raise HTTPException(
            status_code=400,
            detail="User does not have a data source associated with it.",
        )
    patient_input.data_source_name = current_user.data_source.name
    patient = await PatientRecord.create_from_pydantic_model(patient_input)
    return await patient.to_pydantic_model()
