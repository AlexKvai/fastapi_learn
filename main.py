from fastapi import FastAPI, HTTPException
from mongita import MongitaClientDisk
from pydantic import BaseModel

class Shape(BaseModel):
	name: str
	no_of_sides: int
	id: int

app = FastAPI()

client = MongitaClientDisk()
db = client.db
shapes = db.shapes


@app.get("/")
async def root():
	return {"message": "Hello World"}

@app.get("/shapes")
async def get_shapes():
	existing_shapes = shapes.find({})
	return [
		{key:shape[key] for key in shape if key != "_id"}
		for shape in existing_shapes
	]

@app.get("/shapes/{shape_id}")
async def get_shape_by_id(shape_id: int):
	if shapes.count_documents({"id": shape_id}) > 0:
		shape = shapes.find_one({"id": shape_id})
		return {key:shape[key] for key in shape if key != "_id"}
	raise HTTPException(status_code=404, detail=f"Shape not found: {shape_id}")

@app.post("/shapes")
async def create_shape(shape: Shape):
	shapes.insert_one(shape.dict())
	return shape