# exemplo_integracao_olp.py - Exemplo Completo de Integração OLP
# Demonstra como usar os 3 arquivos criados em conjunto

import sys
sys.path.insert(0, r'C:\Users\PC\Desktop\HYPEROKBIT\OLP')

from alp_model import ALP_MODEL
from olp_hal_driver import OLP_HAL
from olp_core_api import OLPCoreAPI, initialize_olp_api

import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def exemplo_1_basico():
    """Exemplo 1: Uso básico com 3 chamadas simples"""
    
    print("\n" + "="*80)
    print("EXEMPLO 1: USO BÁSICO - 3 CHAMADAS ESSENCIAIS")
    print("="*80)
    
    # Inicializar a API
    api = OLPCoreAPI(use_real_ml_model=True, hal_driver=OLP_HAL, ml_model=ALP_MODEL)
    
    # 1. Definir contexto
    api.set_context("training_loop_forward_pass", scope_id=1)
    
    # 2. Registrar checkpoint
    api.register_checkpoint(0x500, checkpoint_name="batch_1_start")
    
    # 3. Executar tarefa otimizada
    def minha_tarefa(dados):
        """Tarefa de exemplo"""
        return sum(dados) * 2
    
    dados = [0x1000 + i*8 for i in range(10)]
    resultado = api.execute_optimized(minha_tarefa, dados)
    
    print(f"\nResultado: {resultado}")
    
    # Visualizar estatísticas
    api.print_system_status()


def exemplo_2_loop_treinamento():
    """Exemplo 2: Loop de treinamento com múltiplas iterações"""
    
    print("\n" + "="*80)
    print("EXEMPLO 2: LOOP DE TREINAMENTO (100 BATCHES)")
    print("="*80)
    
    api = OLPCoreAPI(use_real_ml_model=True, hal_driver=OLP_HAL, ml_model=ALP_MODEL)
    
    def forward_pass(batch_data):
        """Passe forward de rede neural"""
        result = 0
        for x in batch_data:
            result += x ** 2
        return result
    
    # Loop de treinamento
    BATCHES = 10  # Use 100 em produção
    
    for batch_id in range(1, BATCHES + 1):
        # 1. Definir contexto específico da iteração
        api.set_context("training_loop_forward_pass", scope_id=batch_id)
        
        # 2. Registrar checkpoint
        checkpoint_addr = 0x500 + (batch_id * 8)
        api.register_checkpoint(checkpoint_addr, f"batch_{batch_id}_start")
        
        # 3. Preparar dados (simulando sequência linear de acessos)
        batch_data = [0x2000 + i*8 for i in range(batch_id * 5)]
        
        # 4. Executar com OLP
        loss = api.execute_optimized(forward_pass, batch_data, task_id=batch_id)
        
        if batch_id % 5 == 0:
            print(f"\nBatch {batch_id:3d} completado. Loss: {loss}")
    
    # Relatório final
    print("\n" + "-"*80)
    print("RELATÓRIO FINAL DO TREINAMENTO")
    print("-"*80)
    api.print_system_status()


def exemplo_3_big_data():
    """Exemplo 3: Processamento Big Data com padrão previsível"""
    
    print("\n" + "="*80)
    print("EXEMPLO 3: BIG DATA PROCESSING (50 CHUNKS)")
    print("="*80)
    
    api = OLPCoreAPI(use_real_ml_model=True, hal_driver=OLP_HAL, ml_model=ALP_MODEL)
    
    def aggregate_data(addresses):
        """Agregar dados com padrão linear"""
        if len(addresses) == 0:
            return 0
        total = sum(addresses)
        return total // len(addresses)
    
    # Processar 50 chunks de dados
    for chunk_id in range(1, 51):
        # 1. Contexto
        api.set_context("big_data_aggregation", scope_id=chunk_id)
        
        # 2. Checkpoint
        api.register_checkpoint(0x5000 + chunk_id * 8, f"chunk_{chunk_id}")
        
        # 3. Dados com padrão LINEAR previsível (ÓTIMO para PIM)
        chunk_addresses = [0x10000 + i*64 for i in range(100)]
        
        # 4. Executar
        result = api.execute_optimized(aggregate_data, chunk_addresses, task_id=chunk_id)
        
        if chunk_id % 10 == 0:
            print(f"  Chunk {chunk_id:2d} processado. Resultado: {result}")
    
    # Estatísticas finais
    stats = api.get_api_stats()
    print(f"\n✓ Total de chunks: 50")
    print(f"✓ Seleções PIM: {stats['pim_selections']} ({stats['pim_percentage']})")
    print(f"✓ Execuções na CPU: {stats['cpu_selections']}")


def exemplo_4_recovery():
    """Exemplo 4: Teste de Recovery automático"""
    
    print("\n" + "="*80)
    print("EXEMPLO 4: TESTE DE RECOVERY (SIMULAÇÃO DE FALHA)")
    print("="*80)
    
    api = OLPCoreAPI(use_real_ml_model=True, hal_driver=OLP_HAL, ml_model=ALP_MODEL)
    
    # 1. Definir contexto
    api.set_context("risky_computation", scope_id=1)
    
    # 2. Registrar checkpoint para segurança
    api.register_checkpoint(0x6000, checkpoint_name="safe_recovery_point")
    print("\n✓ Checkpoint de segurança registrado")
    
    # 3. Simular execução normal
    def task(data):
        return sum(data)
    
    data = [0x3000 + i*8 for i in range(20)]
    result = api.execute_optimized(task, data)
    print(f"✓ Execução normal completada: {result}")
    
    # 4. Simular FALHA CRÍTICA
    print("\n⚠️ Simulando FALHA CRÍTICA no PIM...")
    api.trigger_recovery(
        error_code=0xFF,
        context_info="Simulated PIM Failure - ECC Error"
    )
    
    print("\n✓ Recovery completado com sucesso")
    print(f"✓ Total de eventos de recovery: {api.stats['recovery_events']}")


def exemplo_5_analise_completa():
    """Exemplo 5: Análise completa do sistema"""
    
    print("\n" + "="*80)
    print("EXEMPLO 5: ANÁLISE COMPLETA DO SISTEMA OLP")
    print("="*80)
    
    api = OLPCoreAPI(use_real_ml_model=True, hal_driver=OLP_HAL, ml_model=ALP_MODEL)
    
    # Executar várias tarefas
    for i in range(5):
        api.set_context(f"analysis_task_{i}", scope_id=i)
        api.register_checkpoint(0x7000 + i*16, f"checkpoint_{i}")
        
        task = lambda data: sum(data) * len(data)
        data = [0x4000 + j*8 for j in range(10 + i*5)]
        api.execute_optimized(task, data)
    
    # Obter relatório completo
    report = api.get_full_system_report()
    
    print("\n" + "-"*80)
    print("RELATÓRIO COMPLETO DO SISTEMA")
    print("-"*80)
    
    print("\n[API STATISTICS]")
    for key, value in report['api_stats'].items():
        print(f"  {key:40} = {value}")
    
    print("\n[CHECKPOINTS]")
    for name, info in report['checkpoints'].items():
        print(f"  {name:40} @ {hex(info['address'])}")
    
    if 'hal_driver_stats' in report:
        print("\n[HARDWARE STATISTICS]")
        hal = report['hal_driver_stats']
        print(f"  PIM Tasks Loaded:                         {hal['pim_tasks_loaded']}")
        print(f"  REM Interrupts Sent:                      {hal['rem_interrupts_sent']}")
        print(f"  DMA Transfers:                            {hal['dma_transfers_completed']}")
        print(f"  Total Bytes Transferred:                  {hal['total_bytes_transferred']:,}")
        print(f"  Current TTID:                             {hal['current_ttid_ms']:.2f} ms")
        print(f"  Current Power Consumption:                {hal['current_power_w']:.2f} W")
    
    if 'ml_model_stats' in report:
        print("\n[ML MODEL STATISTICS]")
        ml = report['ml_model_stats']
        print(f"  Model Version:                            {ml.get('model_version', 'N/A')}")
        print(f"  Contexts Analyzed:                        {ml.get('contexts_analyzed', 0)}")
        print(f"  Total Predictions:                        {ml.get('total_predictions', 0)}")
        print(f"  Cache Size:                               {ml.get('cache_size', 0)}")
    
    print("\n[EXECUTION HISTORY - ÚLTIMAS 5]")
    for idx, exec_rec in enumerate(report['recent_executions'][-5:], 1):
        print(f"  {idx}. {exec_rec['function_name']} → "
              f"{exec_rec['destination']} "
              f"(conf: {exec_rec['confidence']*100:.1f}%)")
    
    # Exportar relatório
    api.export_system_report("olp_system_report_example.json")
    print("\n✓ Relatório exportado para olp_system_report_example.json")


def main():
    """Executar todos os exemplos"""
    
    print("\n" + "="*80)
    print("DEMONSTRAÇÃO COMPLETA DE INTEGRAÇÃO OLP")
    print("="*80)
    print("\nArquivos integrados:")
    print("  ✓ alp_model.py (Modelo de ML)")
    print("  ✓ olp_hal_driver.py (Driver de Hardware)")
    print("  ✓ olp_core_api.py (Interface Principal)")
    print("\n" + "="*80)
    
    # Executar exemplos
    try:
        exemplo_1_basico()
        input("\nPressione ENTER para continuar para o próximo exemplo...")
        
        exemplo_2_loop_treinamento()
        input("\nPressione ENTER para continuar...")
        
        exemplo_3_big_data()
        input("\nPressione ENTER para continuar...")
        
        exemplo_4_recovery()
        input("\nPressione ENTER para continuar...")
        
        exemplo_5_analise_completa()
        
        print("\n" + "="*80)
        print("✅ TODOS OS EXEMPLOS COMPLETADOS COM SUCESSO!")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()