import json
from typing import Dict, List, Optional
from snowflake.snowpark import Session

SEMANTIC_MODEL_PATH = "@CAUSAL_CHAIN.STAGES.SEMANTIC_MODELS/causal_chain_model.yaml"
SEARCH_SERVICE = "CAUSAL_CHAIN.STRATEGY_SIMULATOR.SUPPLY_CHAIN_CONTEXT_SEARCH"

def query_cortex_analyst(session: Session, question: str) -> Dict:
    prompt = f"""You are a supply chain finance analyst. Given this question about the causal chain data model, answer based on the semantic model context.
    
Question: {question}

The data model includes:
- performance: Monthly metrics (OTIF, ROCE, FCF, inventory values)
- inventory_structure: Inventory types and economic drivers
- scenarios: Strategy modes (GROWTH/MARGIN/CASH) and shock events
- predictions: ML-predicted outcomes

Provide a concise answer with specific metrics when relevant."""

    try:
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large2',
                $${prompt}$$
            ) as RESPONSE
        """).collect()[0]['RESPONSE']
        
        return {
            "success": True,
            "interpretation": result,
            "sql": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "interpretation": None
        }


def search_qbr_documents(session: Session, query: str, limit: int = 3) -> List[Dict]:
    try:
        result = session.sql(f"""
            SELECT 
                DOC_NAME,
                QUARTER,
                YEAR,
                CONTENT_TEXT
            FROM RAW.QBR_DOCUMENTS
            WHERE CONTAINS(LOWER(CONTENT_TEXT), LOWER('{query}'))
            OR CONTAINS(LOWER(DOC_NAME), LOWER('{query}'))
            LIMIT {limit}
        """).to_pandas()
        
        return result.to_dict('records')
    except Exception as e:
        return []


def generate_rag_response(session: Session, question: str, context: List[Dict]) -> str:
    if not context:
        return "No relevant documents found for your query."
    
    context_text = "\n\n".join([
        f"From {doc.get('DOC_NAME', 'Unknown')} ({doc.get('QUARTER', '')} {doc.get('YEAR', '')}):\n{str(doc.get('CONTENT_TEXT', ''))[:500]}..."
        for doc in context
    ])
    
    prompt = f"""Based on the following quarterly business review excerpts, answer this question concisely:

Question: {question}

Context:
{context_text}

Provide a brief answer citing specific documents. No preamble."""

    try:
        response = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', $${prompt}$$) as ANSWER
        """).collect()[0]['ANSWER']
        return response
    except Exception as e:
        return f"Unable to generate response: {str(e)}"
