from datetime import date
from pydantic import BaseModel, Field

class FarmerCreate(BaseModel):
    farmer_id: str = Field(min_length=1, max_length=10)
    name: str
    gender: str | None = None
    date_of_birth: date | None = None
    phone: str | None = None
    county: str = "Kisii"
    sub_county: str | None = None
    ward: str | None = None
    village: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    gps_accuracy_m: float | None = None

class FarmerOut(FarmerCreate):
    id: int
    active: bool
    class Config:
        from_attributes = True

class AnimalCreate(BaseModel):
    animal_id: str
    farmer_id: int
    name: str | None = None
    breed: str | None = None
    sex: str
    date_of_birth: date | None = None
    status: str = "Lactating"

class AnimalOut(AnimalCreate):
    id: int
    class Config:
        from_attributes = True

class MilkRecordCreate(BaseModel):
    farmer_id: int
    record_date: date
    morning_litres: float = Field(default=0, ge=0)
    evening_litres: float = Field(default=0, ge=0)
    collector: str | None = None

class MilkRecordOut(MilkRecordCreate):
    id: int
    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    farmer_id: int
    week_start: date
    week_end: date
    price_per_litre: float = Field(gt=0)
    deductions: float = Field(default=0, ge=0)
    payment_date: date
    method: str = "M-Pesa"
    reference: str | None = None

class PaymentOut(BaseModel):
    id: int
    farmer_id: int
    week_start: date
    week_end: date
    litres: float
    price_per_litre: float
    gross_amount: float
    deductions: float
    net_amount: float
    payment_date: date
    method: str
    reference: str | None
    class Config:
        from_attributes = True
