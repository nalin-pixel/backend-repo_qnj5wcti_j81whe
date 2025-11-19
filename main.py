import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Inquiry, Project

app = FastAPI(title="Aurelia Interiors API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Aurelia Interiors API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Lead inquiry endpoint
@app.post("/api/contact")
def create_inquiry(inquiry: Inquiry):
    try:
        inquiry_id = create_document("inquiry", inquiry)
        return {"status": "ok", "id": inquiry_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: list a few projects (static seed via db if present)
@app.get("/api/projects", response_model=List[Project])
def list_projects() -> List[Project]:
    try:
        # If projects exist in db, return some; otherwise return curated defaults
        if db is not None and "project" in db.list_collection_names():
            docs = get_documents("project", limit=12)
            # Convert Mongo docs to Pydantic by mapping fields
            results = []
            for d in docs:
                results.append(Project(
                    title=d.get("title", "Untitled"),
                    category=d.get("category", "Uncategorized"),
                    location=d.get("location"),
                    cover_url=d.get("cover_url"),
                    description=d.get("description"),
                ))
            if results:
                return results
    except Exception:
        pass

    return [
        Project(title="Skyline Residence", category="Residential", cover_url="https://images.unsplash.com/photo-1524758631624-e2822e304c36?q=80&w=1600&auto=format&fit=crop"),
        Project(title="Atrium Workspace", category="Commercial", cover_url="https://images.unsplash.com/photo-1484154218962-a197022b5858?q=80&w=1600&auto=format&fit=crop"),
        Project(title="Minimal Loft", category="Residential", cover_url="https://images.unsplash.com/photo-1549187774-b4e9b0445b41?q=80&w=1600&auto=format&fit=crop"),
    ]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
