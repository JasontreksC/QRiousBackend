import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Charm
from app.schemas import CharmCreate, CharmRead, CharmUpdate

router = APIRouter(prefix="/charms", tags=["charms"])


@router.get("", response_model=list[CharmRead])
def list_charms(db: Session = Depends(get_db)) -> list[Charm]:
    return list(db.scalars(select(Charm).order_by(Charm.name)).all())


@router.get("/{charm_id}", response_model=CharmRead)
def get_charm(charm_id: uuid.UUID, db: Session = Depends(get_db)) -> Charm:
    charm = db.get(Charm, charm_id)
    if charm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Charm not found"
        )
    return charm


@router.post("", response_model=CharmRead, status_code=status.HTTP_201_CREATED)
def create_charm(payload: CharmCreate, db: Session = Depends(get_db)) -> Charm:
    charm = Charm(name=payload.name)
    db.add(charm)
    db.commit()
    db.refresh(charm)
    return charm


@router.patch("/{charm_id}", response_model=CharmRead)
def update_charm(
    charm_id: uuid.UUID, payload: CharmUpdate, db: Session = Depends(get_db)
) -> Charm:
    charm = db.get(Charm, charm_id)
    if charm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Charm not found"
        )

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(charm, field, value)

    db.commit()
    db.refresh(charm)
    return charm


@router.delete("/{charm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_charm(charm_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    charm = db.get(Charm, charm_id)
    if charm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Charm not found"
        )
    db.delete(charm)
    db.commit()
