from datetime import date, timedelta
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from .database import Base, engine, get_db
from .models import Farmer, Animal, MilkRecord, Payment
from .schemas import FarmerCreate, FarmerOut, AnimalCreate, AnimalOut, MilkRecordCreate, MilkRecordOut, PaymentCreate, PaymentOut

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Dairy Link API", version="0.2.0")

@app.get("/health")
def health():
    return {"status": "ok", "service": "dairy-link-api", "version": "0.2.0"}

@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    farmers = db.scalar(select(func.count(Farmer.id))) or 0
    animals = db.scalar(select(func.count(Animal.id))) or 0
    milk = db.scalar(
        select(func.coalesce(func.sum(MilkRecord.morning_litres + MilkRecord.evening_litres), 0))
    ) or 0
    payments = db.scalar(select(func.coalesce(func.sum(Payment.net_amount), 0))) or 0
    return {"farmers": farmers, "animals": animals, "milk_litres": round(float(milk), 2), "payments": round(float(payments), 2)}

@app.get("/api/farmers", response_model=list[FarmerOut])
def list_farmers(db: Session = Depends(get_db)):
    return db.scalars(select(Farmer).order_by(Farmer.name)).all()

@app.post("/api/farmers", response_model=FarmerOut, status_code=201)
def create_farmer(payload: FarmerCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Farmer).where(Farmer.farmer_id == payload.farmer_id)):
        raise HTTPException(409, "Farmer ID already exists")
    farmer = Farmer(**payload.model_dump())
    db.add(farmer); db.commit(); db.refresh(farmer)
    return farmer

@app.get("/api/farmers/{farmer_id}", response_model=FarmerOut)
def get_farmer(farmer_id: int, db: Session = Depends(get_db)):
    farmer = db.get(Farmer, farmer_id)
    if not farmer: raise HTTPException(404, "Farmer not found")
    return farmer

@app.get("/api/farmers/{farmer_id}/summary")
def farmer_summary(farmer_id: int, db: Session = Depends(get_db)):
    if not db.get(Farmer, farmer_id):
        raise HTTPException(404, "Farmer not found")
    animal_count = db.scalar(select(func.count(Animal.id)).where(Animal.farmer_id == farmer_id)) or 0
    milk = db.scalar(select(func.coalesce(func.sum(MilkRecord.morning_litres + MilkRecord.evening_litres), 0)).where(MilkRecord.farmer_id == farmer_id)) or 0
    paid = db.scalar(select(func.coalesce(func.sum(Payment.net_amount), 0)).where(Payment.farmer_id == farmer_id)) or 0
    return {"animals": animal_count, "total_milk_litres": round(float(milk),2), "total_paid": round(float(paid),2)}

@app.get("/api/animals", response_model=list[AnimalOut])
def list_animals(db: Session = Depends(get_db)):
    return db.scalars(select(Animal).order_by(Animal.animal_id)).all()

@app.post("/api/animals", response_model=AnimalOut, status_code=201)
def create_animal(payload: AnimalCreate, db: Session = Depends(get_db)):
    if not db.get(Farmer, payload.farmer_id): raise HTTPException(404, "Farmer not found")
    if db.scalar(select(Animal).where(Animal.animal_id == payload.animal_id)):
        raise HTTPException(409, "Animal ID already exists")
    animal = Animal(**payload.model_dump())
    db.add(animal); db.commit(); db.refresh(animal)
    return animal

@app.get("/api/milk-records", response_model=list[MilkRecordOut])
def list_milk_records(db: Session = Depends(get_db)):
    return db.scalars(select(MilkRecord).order_by(MilkRecord.record_date.desc())).all()

@app.post("/api/milk-records", response_model=MilkRecordOut, status_code=201)
def create_milk_record(payload: MilkRecordCreate, db: Session = Depends(get_db)):
    if not db.get(Farmer, payload.farmer_id): raise HTTPException(404, "Farmer not found")
    if payload.morning_litres == 0 and payload.evening_litres == 0:
        raise HTTPException(400, "At least one milk quantity must be greater than zero")
    record = db.scalar(select(MilkRecord).where(and_(MilkRecord.farmer_id == payload.farmer_id, MilkRecord.record_date == payload.record_date)))
    if record:
        record.morning_litres = payload.morning_litres
        record.evening_litres = payload.evening_litres
        record.collector = payload.collector
    else:
        record = MilkRecord(**payload.model_dump())
        db.add(record)
    db.commit(); db.refresh(record)
    return record

@app.get("/api/milk-records/weekly")
def weekly_milk(farmer_id: int, week_start: date, db: Session = Depends(get_db)):
    week_end = week_start + timedelta(days=6)
    rows = db.scalars(select(MilkRecord).where(
        and_(MilkRecord.farmer_id == farmer_id, MilkRecord.record_date >= week_start, MilkRecord.record_date <= week_end)
    )).all()
    morning = sum(r.morning_litres for r in rows)
    evening = sum(r.evening_litres for r in rows)
    return {"farmer_id": farmer_id, "week_start": week_start, "week_end": week_end, "morning_litres": morning, "evening_litres": evening, "total_litres": morning + evening}

@app.get("/api/payments", response_model=list[PaymentOut])
def list_payments(db: Session = Depends(get_db)):
    return db.scalars(select(Payment).order_by(Payment.payment_date.desc())).all()

@app.post("/api/payments", response_model=PaymentOut, status_code=201)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    if not db.get(Farmer, payload.farmer_id): raise HTTPException(404, "Farmer not found")
    if payload.week_end < payload.week_start:
        raise HTTPException(400, "Week end cannot be before week start")
    rows = db.scalars(select(MilkRecord).where(and_(MilkRecord.farmer_id == payload.farmer_id, MilkRecord.record_date >= payload.week_start, MilkRecord.record_date <= payload.week_end))).all()
    litres = sum(r.morning_litres + r.evening_litres for r in rows)
    gross = litres * payload.price_per_litre
    net = gross - payload.deductions
    payment = Payment(
        **payload.model_dump(),
        litres=litres,
        gross_amount=gross,
        net_amount=net
    )
    db.add(payment); db.commit(); db.refresh(payment)
    return payment
