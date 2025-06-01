from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
import pandas as pd

app = FastAPI()

# 👇 Параметры, которые можно запрашивать из GPT
class FilterParams(BaseModel):
    city: str
    max_rent: float
    min_foot_traffic: int
    min_income: float = None
    require_refugee_center: bool = False

@app.get("/")
def root():
    return {"status": "OK", "message": "Приложение работает!"}

# 👇 Фильтрация и создание Excel по параметрам
@app.post("/export_excel")
def export_excel(params: FilterParams):
    df = pd.read_excel("locations.xlsx")

    # Обязательные фильтры
    filtered = df[
        (df["city"].str.lower() == params.city.lower()) &
        (df["rent"] <= params.max_rent) &
        (df["foot_traffic"] >= params.min_foot_traffic)
    ]

    # Необязательные фильтры
    if params.min_income is not None:
        filtered = filtered[filtered["income"] >= params.min_income]
    if params.require_refugee_center:
        filtered = filtered[filtered["refugee_center"] == True]

    output_path = "filtered_result.xlsx"
    filtered.to_excel(output_path, index=False)

    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="results.xlsx"
    )
