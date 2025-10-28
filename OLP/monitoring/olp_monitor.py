# monitoring/olp_monitor.py - Monitoramento Centralizado

import json
import logging
from datetime import datetime
from pathlib import Path
from config.olp_config import get_olp_config

logger = logging.getLogger(__name__)

class OLPMonitor:
    """Gerenciar monitoramento do OLP em produção"""
    
    def __init__(self, api_instance, config=None):
        self.api = api_instance
        self.config = config or get_olp_config('monitoring')
        self.reports_path = Path(self.config.get('export_path', './reports/'))
        self.reports_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"OLPMonitor inicializado em {self.reports_path}")
    
    def collect_report(self):
        """Coletar relatório completo"""
        return self.api.get_full_system_report()
    
    def export_report(self, report=None, filename=None):
        """Exportar relatório para JSON"""
        if report is None:
            report = self.collect_report()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"olp_report_{timestamp}.json"
        
        filepath = self.reports_path / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Relatório exportado: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Erro ao exportar relatório: {e}")
            return None
    
    def health_check(self, report=None):
        """Verificar saúde do sistema"""
        if report is None:
            report = self.collect_report()
        
        stats = report['api_stats']
        
        issues = []
        warnings = []
        
        # Verificações críticas
        if stats['recovery_events'] > self.config.get('high_recovery_threshold', 10):
            issues.append(f"Muitos eventos de recovery: {stats['recovery_events']}")
        
        # Verificações de warning
        pim_pct = float(stats['pim_percentage'].rstrip('%'))
        if pim_pct < self.config.get('min_pim_percentage', 80):
            warnings.append(f"Taxa PIM baixa: {pim_pct:.1f}%")
        
        return {
            'healthy': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'timestamp': report['timestamp']
        }
    
    def get_summary(self, report=None):
        """Obter resumo rápido"""
        if report is None:
            report = self.collect_report()
        
        stats = report['api_stats']
        hal = report['hal_driver_stats']
        ml = report['ml_model_stats']
        
        return {
            'execuções': stats['optimized_executions'],
            'pim_pct': stats['pim_percentage'],
            'checkpoints': stats['checkpoints_registered'],
            'tarefas_pim': hal['pim_tasks_loaded'],
            'bytes': hal['total_bytes_transferred'],
            'contextos_ml': ml['contexts_analyzed']
        }
