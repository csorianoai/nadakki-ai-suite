"""Export Service - CSV, JSON, Excel, PDF."""
import logging
import json
import csv
import io
from datetime import datetime
from typing import Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)


class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    PDF = "pdf"


class ExportService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str) -> str:
        if not data: return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
    
    def export_to_json(self, data: Any, filename: str) -> str:
        return json.dumps(data, indent=2, default=str, ensure_ascii=False)
    
    def export_campaigns(self, tenant_id: str, format: ExportFormat) -> Dict[str, Any]:
        campaigns_data = [
            {"id": "c1", "name": "Campaign 1", "status": "published", "engagement": 1500},
            {"id": "c2", "name": "Campaign 2", "status": "draft", "engagement": 0}
        ]
        if format == ExportFormat.CSV:
            return {"format": "csv", "content": self.export_to_csv(campaigns_data, f"campaigns_{tenant_id}.csv"), "rows": len(campaigns_data)}
        elif format == ExportFormat.JSON:
            return {"format": "json", "content": self.export_to_json(campaigns_data, f"campaigns_{tenant_id}.json"), "rows": len(campaigns_data)}
        return {"error": f"Format {format} not implemented"}
    
    def export_analytics_report(self, report_id: str, format: ExportFormat) -> Dict[str, Any]:
        from .analytics_service import analytics_service
        report = analytics_service.get_report(report_id)
        if not report: return {"error": "Report not found"}
        if format == ExportFormat.JSON:
            return {"format": "json", "content": self.export_to_json(report.to_dict(), f"report_{report_id}.json")}
        return {"error": f"Format {format} not implemented"}
    
    def get_export_formats(self) -> List[Dict[str, str]]:
        return [
            {"id": "csv", "name": "CSV", "extension": ".csv"},
            {"id": "json", "name": "JSON", "extension": ".json"},
            {"id": "excel", "name": "Excel", "extension": ".xlsx"},
            {"id": "pdf", "name": "PDF", "extension": ".pdf"}
        ]


export_service = ExportService()
