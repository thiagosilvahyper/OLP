# monitoring/alerts.py - Sistema de Alertas

import logging

logger = logging.getLogger(__name__)

class AlertSystem:
    """Gerenciar alertas do OLP"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.alert_history = []
    
    def check_recovery_events(self, recovery_count, threshold=10):
        """Verificar eventos de recovery"""
        if recovery_count > threshold:
            self.emit_alert(
                level="CRITICAL",
                message=f"Muitos eventos de recovery: {recovery_count} > {threshold}"
            )
            return False
        return True
    
    def check_pim_percentage(self, pim_pct, min_threshold=80):
        """Verificar taxa de seleção PIM"""
        pim_float = float(pim_pct.rstrip('%')) if isinstance(pim_pct, str) else pim_pct
        
        if pim_float < min_threshold:
            self.emit_alert(
                level="WARNING",
                message=f"Taxa PIM baixa: {pim_float:.1f}% < {min_threshold}%"
            )
            return False
        return True
    
    def check_system_health(self, report):
        """Verificação completa de saúde"""
        stats = report['api_stats']
        
        all_ok = True
        
        # Verificações
        all_ok &= self.check_recovery_events(stats['recovery_events'])
        all_ok &= self.check_pim_percentage(stats['pim_percentage'])
        
        if all_ok:
            self.emit_alert(level="INFO", message="Sistema saudável ✅")
        
        return all_ok
    
    def emit_alert(self, level, message):
        """Emitir alerta"""
        self.alert_history.append({
            'level': level,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        if level == "CRITICAL":
            logger.critical(f"🚨 {message}")
        elif level == "WARNING":
            logger.warning(f"⚠️ {message}")
        else:
            logger.info(f"ℹ️ {message}")
