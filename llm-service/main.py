from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import openai
import structlog
import sqlparse
from sqlalchemy import create_engine, text, inspect
from datetime import datetime
import re
from contextlib import asynccontextmanager

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@localhost:5432/enterprise_reporting")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")

# Setup logging
logger = structlog.get_logger()

# Database setup for schema inspection
engine = create_engine(DATABASE_URL)

# OpenAI setup
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Pydantic Models
class NaturalLanguageQuery(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class SQLResponse(BaseModel):
    sql: Optional[str]
    success: bool
    error: Optional[str]
    explanation: Optional[str]
    confidence: Optional[float]

class SchemaInfo(BaseModel):
    tables: List[Dict[str, Any]]
    columns: Dict[str, List[Dict[str, Any]]]

# Database schema inspection
def get_database_schema():
    """Get database schema information for better SQL generation"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        schema_info = {
            "tables": [],
            "columns": {}
        }
        
        for table in tables:
            # Get table columns
            columns = inspector.get_columns(table)
            schema_info["columns"][table] = [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "default": col.get("default")
                }
                for col in columns
            ]
            
            # Get table info
            schema_info["tables"].append({
                "name": table,
                "column_count": len(columns)
            })
        
        return schema_info
    except Exception as e:
        logger.error(f"Error getting database schema: {e}")
        return None

# LLM prompt templates
def create_sql_prompt(query: str, schema_info: Dict[str, Any]) -> str:
    """Create a prompt for SQL generation"""
    
    # Create schema description
    schema_desc = "Database Schema:\n"
    for table in schema_info["tables"]:
        table_name = table["name"]
        columns = schema_info["columns"][table_name]
        
        schema_desc += f"\nTable: {table_name}\n"
        for col in columns:
            schema_desc += f"  - {col['name']} ({col['type']})"
            if not col["nullable"]:
                schema_desc += " NOT NULL"
            schema_desc += "\n"
    
    prompt = f"""You are an expert SQL query generator for a PostgreSQL database. Your task is to convert natural language questions into valid SQL queries.

{schema_desc}

Instructions:
1. Generate ONLY valid PostgreSQL SQL queries
2. Use proper JOIN syntax when multiple tables are involved
3. Include appropriate WHERE clauses for filtering
4. Use aggregate functions (SUM, COUNT, AVG, etc.) when needed
5. Format dates properly using PostgreSQL date functions
6. Limit results when appropriate (use LIMIT clause)
7. Order results logically (usually by date or amount)
8. Handle case-insensitive text searches with ILIKE
9. Use proper SQL comments if the query is complex

Natural Language Query: "{query}"

Generate a SQL query that answers this question. Return ONLY the SQL query without any explanation or formatting.
"""
    
    return prompt

async def generate_sql_with_openai(query: str, schema_info: Dict[str, Any]) -> SQLResponse:
    """Generate SQL using OpenAI GPT"""
    try:
        if not OPENAI_API_KEY:
            return SQLResponse(
                sql=None,
                success=False,
                error="OpenAI API key not configured"
            )
        
        prompt = create_sql_prompt(query, schema_info)
        
        response = openai.ChatCompletion.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert SQL query generator. Generate only valid PostgreSQL SQL queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Clean up the SQL query
        sql_query = clean_sql_query(sql_query)
        
        # Validate SQL syntax
        is_valid, error_msg = validate_sql_syntax(sql_query)
        
        if is_valid:
            return SQLResponse(
                sql=sql_query,
                success=True,
                explanation=f"Generated SQL query for: {query}",
                confidence=0.9
            )
        else:
            return SQLResponse(
                sql=sql_query,
                success=False,
                error=f"Generated invalid SQL: {error_msg}"
            )
            
    except Exception as e:
        logger.error(f"Error generating SQL with OpenAI: {e}")
        return SQLResponse(
            sql=None,
            success=False,
            error=f"OpenAI API error: {str(e)}"
        )

def clean_sql_query(sql: str) -> str:
    """Clean and format SQL query"""
    # Remove markdown code blocks if present
    sql = re.sub(r'```sql\s*', '', sql)
    sql = re.sub(r'```\s*', '', sql)
    
    # Remove extra whitespace
    sql = ' '.join(sql.split())
    
    # Ensure query ends with semicolon
    if not sql.strip().endswith(';'):
        sql += ';'
    
    return sql.strip()

def validate_sql_syntax(sql: str) -> tuple[bool, Optional[str]]:
    """Validate SQL syntax using sqlparse"""
    try:
        parsed = sqlparse.parse(sql)
        if not parsed:
            return False, "Empty or invalid SQL"
        
        # Basic validation - check for dangerous operations
        sql_lower = sql.lower()
        dangerous_keywords = ['drop', 'delete', 'truncate', 'alter', 'create', 'insert', 'update']
        
        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                return False, f"Dangerous operation detected: {keyword}"
        
        return True, None
    except Exception as e:
        return False, str(e)

def generate_fallback_sql(query: str, schema_info: Dict[str, Any]) -> SQLResponse:
    """Generate simple SQL queries for common patterns without LLM"""
    query_lower = query.lower()
    
    # Simple pattern matching for common queries
    if "sales" in query_lower and "total" in query_lower:
        return SQLResponse(
            sql="SELECT SUM(total_amount) as total_sales FROM sales_data;",
            success=True,
            explanation="Simple total sales query",
            confidence=0.7
        )
    elif "customer" in query_lower and "count" in query_lower:
        return SQLResponse(
            sql="SELECT COUNT(*) as customer_count FROM customers;",
            success=True,
            explanation="Simple customer count query",
            confidence=0.7
        )
    elif "product" in query_lower and "top" in query_lower:
        return SQLResponse(
            sql="SELECT product_name, SUM(total_amount) as revenue FROM sales_data GROUP BY product_name ORDER BY revenue DESC LIMIT 10;",
            success=True,
            explanation="Top products by revenue",
            confidence=0.6
        )
    
    return SQLResponse(
        sql=None,
        success=False,
        error="Could not generate SQL query. Please try a more specific query or check if OpenAI API is configured."
    )

# FastAPI app setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LLM Service...")
    yield
    logger.info("Shutting down LLM Service...")

app = FastAPI(
    title="LLM Query Service",
    description="Natural Language to SQL conversion service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "LLM Query Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/schema", response_model=SchemaInfo)
async def get_schema():
    """Get database schema information"""
    schema_info = get_database_schema()
    if schema_info:
        return SchemaInfo(**schema_info)
    else:
        raise HTTPException(status_code=500, detail="Could not retrieve database schema")

@app.post("/generate-sql", response_model=SQLResponse)
async def generate_sql(query_request: NaturalLanguageQuery):
    """Convert natural language query to SQL"""
    try:
        # Get database schema
        schema_info = get_database_schema()
        if not schema_info:
            raise HTTPException(status_code=500, detail="Could not retrieve database schema")
        
        # Try to generate SQL with OpenAI first
        if OPENAI_API_KEY:
            result = await generate_sql_with_openai(query_request.query, schema_info)
        else:
            # Fallback to pattern matching
            result = generate_fallback_sql(query_request.query, schema_info)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_sql: {e}")
        return SQLResponse(
            sql=None,
            success=False,
            error=f"Service error: {str(e)}"
        )

@app.post("/validate-sql")
async def validate_sql(sql_query: str):
    """Validate SQL query syntax"""
    is_valid, error_msg = validate_sql_syntax(sql_query)
    return {
        "valid": is_valid,
        "error": error_msg,
        "formatted_sql": sqlparse.format(sql_query, reindent=True) if is_valid else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)