# config/olp_config.py - Configurações do OLP

# ============================================================================
# CONFIGURAÇÕES OLP
# ============================================================================

OLP_CONFIG = {
    # Modelo de ML
    'ml_model': {
        'use_real_model': True,
        'confidence_threshold': 0.999,  # 99.9%
        'cache_max_size': 100,
        'history_max_size': 1000
    },
    
    # Hardware
    'hardware': {
        'cpu_frequency_mhz': 3000,
        'enable_dma': True,
        'enable_rem': True
    },
    
    # API
    'api': {
        'enable_logging': True,
        'logging_level': 'INFO',
        'export_reports': True,
        'report_interval_seconds': 60
    },
    
    # Monitoramento
    'monitoring': {
        'enabled': True,
        'export_json': True,
        'export_path': './monitoring/reports/',
        'health_check_interval': 30,
        'min_pim_percentage': 80
    },
    
    # Alertas
    'alerts': {
        'enabled': True,
        'slack_enabled': False,
        'email_enabled': False,
        'high_recovery_threshold': 10,
        'low_pim_threshold': 80
    }
}

# Função helper
def get_olp_config(key=None):
    """Obter configuração OLP"""
    if key:
        return OLP_CONFIG.get(key, {})
    return OLP_CONFIG
