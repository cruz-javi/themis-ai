import os
import asyncpg
from typing import List, Dict, Any, Optional
from app.core.config import get_settings

async def get_db_connection() -> asyncpg.Connection:
    database_url = get_settings().database_url
    if not database_url:
        raise ValueError("DATABASE_URL no esta configurada en .env")
    return await asyncpg.connect(database_url, timeout=3.0)

async def get_active_election(conn: asyncpg.Connection) -> Optional[Dict[str, Any]]:
    query = """
        SELECT id, elegibilidad_facultad, elegibilidad_tipo_usuario, elegibilidad_estado_academico, votacion_inicio
        FROM elections
        WHERE estado IN ('VOTACION_ABIERTA', 'REGISTRO_ABIERTO', 'REGISTRO_CERRADO')
        ORDER BY created_at DESC
        LIMIT 1
    """
    row = await conn.fetchrow(query)
    if row:
        return dict(row)
    
    # Fallback
    query = "SELECT id, elegibilidad_facultad, elegibilidad_tipo_usuario, elegibilidad_estado_academico, votacion_inicio FROM elections ORDER BY created_at DESC LIMIT 1"
    row = await conn.fetchrow(query)
    if row:
        return dict(row)
    return None

async def calculate_cap(conn: asyncpg.Connection, election: Dict[str, Any]) -> int:
    conditions: List[str] = []
    values: List[Any] = []
    
    if election.get('elegibilidad_facultad'):
        conditions.append(f"facultad = ${len(values) + 1}")
        values.append(election['elegibilidad_facultad'])
    
    if election.get('elegibilidad_tipo_usuario'):
        conditions.append(f"tipo_usuario = ${len(values) + 1}")
        values.append(election['elegibilidad_tipo_usuario'])
        
    if election.get('elegibilidad_estado_academico'):
        conditions.append(f"estado_academico = ${len(values) + 1}")
        values.append(election['elegibilidad_estado_academico'])
        
    query = "SELECT COUNT(*) FROM mock_sso_users"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    count = await conn.fetchval(query, *values)
    return count or 0

async def get_registration_series(conn: asyncpg.Connection, election_id: str) -> List[Dict[str, Any]]:
    query = """
        SELECT 
            CAST(EXTRACT(EPOCH FROM (created_at - (SELECT MIN(created_at) FROM registration_requests WHERE election_id = $1))) / 60 AS INTEGER) as t,
            COUNT(*) OVER (ORDER BY created_at) as votes
        FROM registration_requests
        WHERE election_id = $1
        ORDER BY created_at ASC
    """
    rows = await conn.fetch(query, election_id)
    return [dict(r) for r in rows]

async def get_live_tally(conn: asyncpg.Connection, election_id: str) -> List[Dict[str, Any]]:
    query = """
        SELECT o.id, o.nombre, COUNT(v.id) as vote_count
        FROM options o
        LEFT JOIN vote_submissions v ON o.id = v.option_id
        WHERE o.election_id = $1
        GROUP BY o.id, o.nombre
        ORDER BY o.on_chain_index ASC
    """
    rows = await conn.fetch(query, election_id)
    return [dict(row) for row in rows]
