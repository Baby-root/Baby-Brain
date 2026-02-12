#!/usr/bin/env python3
"""
API Template

A RESTful API built with FastAPI.
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

app = FastAPI(
    title="API Template",
    description="A RESTful API template",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================================
# Models
# ============================================================================

class UserCreate(BaseModel):
    """User creation request"""
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response"""
    id: str
    name: str
    email: str
    created_at: datetime

class TokenResponse(BaseModel):
    """Authentication response"""
    access_token: str
    token_type: str = "bearer"

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime

# ============================================================================
# In-Memory Database (replace with real DB in production)
# ============================================================================

users_db = {}
tokens_db = {}

# ============================================================================
# Health Check
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )

# ============================================================================
# Authentication
# ============================================================================

@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user"""
    if any(u["email"] == user.email for u in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid4())
    users_db[user_id] = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "password": user.password,  # Hash in production!
        "created_at": datetime.utcnow()
    }
    
    return UserResponse(
        id=user_id,
        name=user.name,
        email=user.email,
        created_at=users_db[user_id]["created_at"]
    )

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(email: EmailStr, password: str):
    """Login and get access token"""
    for user_id, user in users_db.items():
        if user["email"] == email and user["password"] == password:
            token = str(uuid4())
            tokens_db[token] = user_id
            return TokenResponse(access_token=token)
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ============================================================================
# Users
# ============================================================================

@app.get("/api/v1/users", response_model=List[UserResponse])
async def list_users():
    """List all users"""
    return [
        UserResponse(
            id=user_id,
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"]
        )
        for user_id, user in users_db.items()
    ]

@app.get("/api/v1/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get a specific user"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    return UserResponse(
        id=user_id,
        name=user["name"],
        email=user["email"],
        created_at=user["created_at"]
    )

@app.delete("/api/v1/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    del users_db[user_id]
    return {"message": "User deleted"}

# ============================================================================
# CRUD Operations Template
# ============================================================================

class ItemCreate(BaseModel):
    """Item creation request"""
    name: str
    description: Optional[str] = None
    price: float

class ItemUpdate(BaseModel):
    """Item update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class ItemResponse(BaseModel):
    """Item response"""
    id: str
    name: str
    description: Optional[str]
    price: float
    created_at: datetime

items_db = {}

@app.get("/api/v1/items", response_model=List[ItemResponse])
async def list_items():
    """List all items"""
    return [
        ItemResponse(
            id=item_id,
            **item_data,
            created_at=item_data["created_at"]
        )
        for item_id, item_data in items_db.items()
    ]

@app.post("/api/v1/items", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    """Create a new item"""
    item_id = str(uuid4())
    items_db[item_id] = {
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "created_at": datetime.utcnow()
    }
    return ItemResponse(
        id=item_id,
        **items_db[item_id],
        created_at=items_db[item_id]["created_at"]
    )

@app.get("/api/v1/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str):
    """Get a specific item"""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return ItemResponse(
        id=item_id,
        **items_db[item_id],
        created_at=items_db[item_id]["created_at"]
    )

@app.put("/api/v1/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item: ItemUpdate):
    """Update an item"""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item.model_dump(exclude_unset=True)
    items_db[item_id].update(update_data)
    
    return ItemResponse(
        id=item_id,
        **items_db[item_id],
        created_at=items_db[item_id]["created_at"]
    )

@app.delete("/api/v1/items/{item_id}")
async def delete_item(item_id: str):
    """Delete an item"""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    del items_db[item_id]
    return {"message": "Item deleted"}

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        debug=True
    )
