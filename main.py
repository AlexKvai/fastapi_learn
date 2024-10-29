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

@app.put("/shapes/{shape_id}")
async def update_shape(shape_id: int, shape: Shape):
	if shapes.count_documents({"id": shape_id}) > 0:
		shapes.replace_one({"id": shape_id}, shape.dict())
		return shape
	raise HTTPException(status_code=404, detail=f"Shape not found: {shape_id}")

@app.put("/shapes/upsert/{shape_id}")
async def update_shape(shape_id: int, shape: Shape):
	shapes.replace_one({"id": shape_id}, shape.dict(), upsert=True)
	return shape

@app.delete("/shapes/{shape_id}")
async def delete_shape(shape_id: int):
	delete_result = shapes.delete_one({"id": shape_id})
	if delete_result.deleted_count == 0:
		raise HTTPException(status_code=404, detail=f"Shape not found: {shape_id}")
	return {"OK": True}