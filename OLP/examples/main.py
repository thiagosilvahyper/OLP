# main.py - Seu código principal integrado com OLP

import logging
from alp_model import ALP_MODEL
from olp_hal_driver import OLP_HAL
from olp_core_api import OLPCoreAPI
from monitoring.olp_monitor import OLPMonitor
from config.olp_config import get_olp_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# INICIALIZAR OLP
# ============================================================================

# 1. Criar API
api = OLPCoreAPI(
    use_real_ml_model=True,
    hal_driver=OLP_HAL,
    ml_model=ALP_MODEL
)

# 2. Criar monitor
monitor = OLPMonitor(api, get_olp_config('monitoring'))

logger.info("✓ Sistema OLP inicializado com sucesso")

# ============================================================================
# SEU CÓDIGO DE PRODUÇÃO
# ============================================================================

def seu_funcao_critica(dados):
    """Sua função que precisa de otimização"""
    # Implementar lógica
    return sum(dados) * 2

def main():
    """Função principal"""
    
    # Exemplo: Processamento de batches
    BATCH_SIZE = 100
    
    for batch_id in range(1, BATCH_SIZE + 1):
        try:
            # 1. DEFINIR CONTEXTO
            api.set_context("seu_funcao_critica", scope_id=batch_id)
            
            # 2. REGISTRAR CHECKPOINT
            checkpoint_addr = 0x10000 + batch_id * 16
            api.register_checkpoint(checkpoint_addr, f"batch_{batch_id}")
            
            # 3. PREPARAR DADOS
            dados = list(range(batch_id * 10))
            
            # 4. EXECUTAR COM OLP (AUTOMÁTICO!)
            resultado = api.execute_optimized(seu_funcao_critica, dados)
            
            # 5. PROCESSAR RESULTADO
            logger.info(f"Batch {batch_id}: Resultado = {resultado}")
            
            # 6. MONITORAR A CADA 25 BATCHES
            if batch_id % 25 == 0:
                summary = monitor.get_summary()
                logger.info(f"STATUS: {summary}")
                
                # Verificar saúde
                health = monitor.health_check()
                if not health['healthy']:
                    logger.warning(f"Alertas: {health['issues']}")
            
            # 7. EXPORTAR RELATÓRIO A CADA 50 BATCHES
            if batch_id % 50 == 0:
                monitor.export_report()
                
        except Exception as e:
            logger.error(f"Erro no batch {batch_id}: {e}")
            # Ativar recovery se necessário
            api.trigger_recovery(0xFF, f"Erro em batch {batch_id}")
    
    # ====================================================================
    # RELATÓRIO FINAL
    # ====================================================================
    
    print("\n" + "="*80)
    print("RELATÓRIO FINAL")
    print("="*80)
    
    final_report = monitor.collect_report()
    final_summary = monitor.get_summary(final_report)
    final_health = monitor.health_check(final_report)
    
    print(f"\nResumo Final:")
    for key, value in final_summary.items():
        print(f"  {key:20} = {value}")
    
    print(f"\nStatus de Saúde: {'✅ OK' if final_health['healthy'] else '❌ PROBLEMAS'}")
    if final_health['warnings']:
        print(f"Avisos: {final_health['warnings']}")
    
    # Exportar final
    monitor.export_report(final_report, "olp_final_report.json")
    
    logger.info("✓ Processamento concluído com sucesso")

if __name__ == "__main__":
    main()
