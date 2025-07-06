from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, String, Text, Boolean, DateTime, Integer, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
import httpx
import json
import structlog
from keycloak import KeycloakOpenID, KeycloakAdmin
from contextlib import asynccontextmanager

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@localhost:5432/enterprise_reporting")
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:8001")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:4000")

# Setup logging
logger = structlog.get_logger()

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Keycloak setup
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_URL,
    client_id="reporting-app",
    realm_name="enterprise-reporting",
    verify=True
)

security = HTTPBearer()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keycloak_id = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ReportCategory(Base):
    __tablename__ = "report_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    sql_query = Column(Text, nullable=False)
    chart_config = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class LLMQuery(Base):
    __tablename__ = "llm_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    natural_language_query = Column(Text, nullable=False)
    generated_sql = Column(Text)
    execution_result = Column(JSONB)
    execution_time_ms = Column(Integer)
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class ReportCategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    sort_order: int
    
    class Config:
        from_attributes = True

class ReportResponse(BaseModel):
    id: str
    category_id: Optional[str]
    name: str
    description: Optional[str]
    chart_config: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class NaturalLanguageQuery(BaseModel):
    query: str

class QueryResponse(BaseModel):
    sql: Optional[str]
    result: Optional[Dict[str, Any]]
    success: bool
    error_message: Optional[str]
    execution_time_ms: Optional[int]

class UserInfo(BaseModel):
    id: str
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]

# FastAPI app setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API Gateway...")
    yield
    logger.info("Shutting down API Gateway...")

app = FastAPI(
    title="Enterprise Reporting API Gateway",
    description="API Gateway for Enterprise Reporting and Visualization Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        token = credentials.credentials
        user_info = keycloak_openid.userinfo(token)
        
        # Sync user with database
        user = db.query(User).filter(User.keycloak_id == user_info["sub"]).first()
        if not user:
            user = User(
                keycloak_id=user_info["sub"],
                username=user_info.get("preferred_username", ""),
                email=user_info.get("email", ""),
                first_name=user_info.get("given_name", ""),
                last_name=user_info.get("family_name", "")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Enterprise Reporting API Gateway", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/auth/me", response_model=UserInfo)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserInfo(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name
    )

@app.get("/categories", response_model=List[ReportCategoryResponse])
async def get_report_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    categories = db.query(ReportCategory).order_by(ReportCategory.sort_order).all()
    return [ReportCategoryResponse.from_orm(cat) for cat in categories]

@app.get("/reports", response_model=List[ReportResponse])
async def get_reports(
    category_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Report).filter(Report.is_active == True)
    if category_id:
        query = query.filter(Report.category_id == category_id)
    
    reports = query.order_by(Report.name).all()
    return [ReportResponse.from_orm(report) for report in reports]

@app.get("/reports/{report_id}/execute")
async def execute_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        # Execute SQL query
        result = db.execute(text(report.sql_query))
        rows = result.fetchall()
        columns = result.keys()
        
        # Convert to JSON serializable format
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif isinstance(value, uuid.UUID):
                    value = str(value)
                row_dict[col] = value
            data.append(row_dict)
        
        return {
            "success": True,
            "data": data,
            "chart_config": report.chart_config,
            "report_name": report.name
        }
    except Exception as e:
        logger.error(f"Error executing report {report_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error executing report: {str(e)}")

@app.post("/llm/query", response_model=QueryResponse)
async def natural_language_query(
    query_request: NaturalLanguageQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Forward to LLM service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLM_SERVICE_URL}/generate-sql",
                json={"query": query_request.query},
                timeout=30.0
            )
            
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="LLM service error")
        
        llm_result = response.json()
        
        # Log the query
        llm_query = LLMQuery(
            user_id=current_user.id,
            natural_language_query=query_request.query,
            generated_sql=llm_result.get("sql"),
            success=llm_result.get("success", False),
            error_message=llm_result.get("error")
        )
        
        # If SQL was generated successfully, execute it
        if llm_result.get("success") and llm_result.get("sql"):
            try:
                from sqlalchemy import text
                import time
                
                start_time = time.time()
                result = db.execute(text(llm_result["sql"]))
                execution_time = int((time.time() - start_time) * 1000)
                
                rows = result.fetchall()
                columns = result.keys()
                
                # Convert to JSON serializable format
                data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        if isinstance(value, datetime):
                            value = value.isoformat()
                        elif isinstance(value, uuid.UUID):
                            value = str(value)
                        row_dict[col] = value
                    data.append(row_dict)
                
                llm_query.execution_result = {"data": data, "columns": list(columns)}
                llm_query.execution_time_ms = execution_time
                llm_query.success = True
                
                db.add(llm_query)
                db.commit()
                
                return QueryResponse(
                    sql=llm_result["sql"],
                    result={"data": data, "columns": list(columns)},
                    success=True,
                    execution_time_ms=execution_time
                )
                
            except Exception as e:
                llm_query.error_message = str(e)
                llm_query.success = False
                db.add(llm_query)
                db.commit()
                
                return QueryResponse(
                    sql=llm_result["sql"],
                    success=False,
                    error_message=f"SQL execution error: {str(e)}"
                )
        else:
            db.add(llm_query)
            db.commit()
            
            return QueryResponse(
                sql=llm_result.get("sql"),
                success=False,
                error_message=llm_result.get("error", "Failed to generate SQL")
            )
            
    except Exception as e:
        logger.error(f"Error in natural language query: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")

@app.get("/analytics/cubes")
async def get_analytics_cubes(current_user: User = Depends(get_current_user)):
    """Proxy to analytics service for available cubes"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ANALYTICS_SERVICE_URL}/cubejs-api/v1/meta")
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching analytics cubes: {e}")
        raise HTTPException(status_code=500, detail="Analytics service error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)