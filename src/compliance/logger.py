"""Sistema de logging imutável para auditoria e compliance."""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from src.config import LOGS_DIR


class ComplianceLogger:
    """Logger para registrar operações ETL com rastreabilidade completa."""
    
    def __init__(self, supplier_id: str):
        self.supplier_id = supplier_id
        self.log_file = LOGS_DIR / f"{supplier_id}_etl_log.jsonl"
        
    def log_extraction(
        self,
        product_data: Dict[str, Any],
        source_url: str,
        status: str = "success"
    ) -> str:
        """Registra extração de produto com hash para auditoria."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "operation": "extraction",
            "supplier": self.supplier_id,
            "source_url": source_url,
            "status": status,
            "data_hash": self._generate_hash(product_data),
            "product_id": product_data.get("id", "unknown")
        }
        
        self._write_log(log_entry)
        return log_entry["data_hash"]
    
    def log_transformation(
        self,
        product_id: str,
        raw_hash: str,
        normalized_data: Dict[str, Any],
        status: str = "success"
    ) -> str:
        """Registra transformação de produto."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "operation": "transformation",
            "supplier": self.supplier_id,
            "product_id": product_id,
            "raw_data_hash": raw_hash,
            "normalized_hash": self._generate_hash(normalized_data),
            "status": status
        }
        
        self._write_log(log_entry)
        return log_entry["normalized_hash"]
    
    def log_validation(
        self,
        product_id: str,
        validation_result: bool,
        errors: Optional[list] = None
    ):
        """Registra validação de schema."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "operation": "validation",
            "supplier": self.supplier_id,
            "product_id": product_id,
            "valid": validation_result,
            "errors": errors or []
        }
        
        self._write_log(log_entry)
    
    def log_catalog_integration(
        self,
        product_id: str,
        catalog_id: str,
        status: str = "success"
    ):
        """Registra integração no catálogo central."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "operation": "catalog_integration",
            "supplier": self.supplier_id,
            "product_id": product_id,
            "catalog_id": catalog_id,
            "status": status
        }
        
        self._write_log(log_entry)
    
    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """Gera hash SHA-256 dos dados para rastreabilidade."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _write_log(self, log_entry: Dict[str, Any]):
        """Escreve entrada de log em formato JSONL (append-only)."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def get_logs(self, operation: Optional[str] = None) -> list:
        """Recupera logs para auditoria."""
        if not self.log_file.exists():
            return []
        
        logs = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                log = json.loads(line)
                if operation is None or log.get("operation") == operation:
                    logs.append(log)
        
        return logs
