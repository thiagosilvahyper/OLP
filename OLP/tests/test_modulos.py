# test_modulos_corrigido.py - Versão Corrigida (100% de Sucesso)
# Execute: python test_modulos_corrigido.py

import sys
import os
import json
import time
from pathlib import Path

# Adicionar paths
sys.path.insert(0, r'C:\Users\PC\Desktop\HYPEROKBIT\OLP')
sys.path.insert(0, r'C:\Users\PC\Desktop\HYPEROKBIT\OLP\src')

# ============================================================================
# IMPORTAR MÓDULOS OLP
# ============================================================================

try:
    from alp_model import ALP_MODEL
    from olp_hal_driver import OLP_HAL
    from olp_core_api import OLPCoreAPI
    print("✓ Importações bem-sucedidas")
except Exception as e:
    print(f"✗ Erro ao importar: {e}")
    sys.exit(1)

# ============================================================================
# TESTES DO SISTEMA OLP
# ============================================================================

class OLPModuleTest:
    """Teste completo dos módulos OLP"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
        self.results = []
    
    def test(self, name, func):
        """Executar teste"""
        self.total += 1
        print(f"\n[Teste {self.total}] {name}")
        print("-" * 80)
        
        try:
            func()
            self.passed += 1
            self.results.append({
                'name': name,
                'status': 'PASS',
                'message': 'OK'
            })
            print("✅ PASSOU")
            return True
        except AssertionError as e:
            self.failed += 1
            self.results.append({
                'name': name,
                'status': 'FAIL',
                'message': str(e)
            })
            print(f"❌ FALHOU: {e}")
            return False
        except Exception as e:
            self.failed += 1
            self.results.append({
                'name': name,
                'status': 'ERROR',
                'message': str(e)
            })
            print(f"❌ ERRO: {e}")
            return False
    
    def print_summary(self):
        """Imprimir resumo"""
        print("\n" + "="*80)
        print("RESUMO DOS TESTES")
        print("="*80)
        print(f"\nTotal de testes:  {self.total}")
        print(f"Passou:           {self.passed} ✅")
        print(f"Falhou:           {self.failed} ❌")
        print(f"Taxa de sucesso:  {(self.passed/max(self.total,1)*100):.1f}%")
        
        if self.failed > 0:
            print(f"\n⚠️  {self.failed} teste(s) falharam:")
            for result in self.results:
                if result['status'] != 'PASS':
                    print(f"  - {result['name']}: {result['message']}")
        else:
            print("\n🎉 TODOS OS TESTES PASSARAM!")

# ============================================================================
# INSTANCIAR TESTER
# ============================================================================

tester = OLPModuleTest()

# ============================================================================
# TESTE 1: ALPModel - Inicialização
# ============================================================================

def test_alp_model_init():
    """Testar inicialização do ALPModel"""
    print("Verificando inicialização do ALPModel...")
    
    assert ALP_MODEL is not None, "ALP_MODEL é None"
    assert hasattr(ALP_MODEL, 'is_trained'), "Atributo is_trained não encontrado"
    assert ALP_MODEL.is_trained == True, "Modelo não está treinado"
    
    print(f"  Versão: {ALP_MODEL.model_version}")
    print(f"  Embedding size: {ALP_MODEL.embedding_size}")
    print(f"  Treinado: {ALP_MODEL.is_trained}")

tester.test("ALPModel - Inicialização", test_alp_model_init)

# ============================================================================
# TESTE 2: ALPModel - Preprocessamento
# ============================================================================

def test_alp_model_preprocess():
    """Testar preprocessamento de entrada"""
    print("Testando preprocessamento...")
    
    context = "test_context"
    accesses = [0x1000 + i*8 for i in range(10)]
    
    input_data = ALP_MODEL.preprocess_input(context, accesses)
    
    assert input_data is not None, "Preprocessamento retornou None"
    assert input_data.shape[0] == 1, "Batch size incorreto"
    assert input_data.shape[1] == ALP_MODEL.sequence_length, "Sequence length incorreto"
    
    print(f"  Input shape: {input_data.shape}")
    print(f"  Contexto: {context}")
    print(f"  Acessos: {len(accesses)}")

tester.test("ALPModel - Preprocessamento", test_alp_model_preprocess)

# ============================================================================
# TESTE 3: ALPModel - Previsão
# ============================================================================

def test_alp_model_predict():
    """Testar previsão do modelo"""
    print("Testando previsão do modelo...")
    
    context = "training_loop"
    accesses = [0x2000 + i*8 for i in range(10)]
    
    prediction = ALP_MODEL.predict(context, accesses)
    
    assert prediction is not None, "Previsão retornou None"
    assert 'blocks' in prediction, "Campo 'blocks' não encontrado"
    assert 'confidence' in prediction, "Campo 'confidence' não encontrado"
    assert 'ttid_pim' in prediction, "Campo 'ttid_pim' não encontrado"
    
    confidence = prediction['confidence']
    assert 0 <= confidence <= 1, f"Confiança fora do intervalo: {confidence}"
    
    print(f"  Confiança: {confidence*100:.2f}%")
    print(f"  TTID PIM: {prediction['ttid_pim']} ms")
    print(f"  Blocos previstos: {len(prediction['blocks'])}")
    print(f"  Padrão: {prediction['stride_pattern']}")

tester.test("ALPModel - Previsão", test_alp_model_predict)

# ============================================================================
# TESTE 4: OLPHALDriver - Inicialização
# ============================================================================

def test_hal_driver_init():
    """Testar inicialização do driver"""
    print("Verificando inicialização do OLP-HAL...")
    
    assert OLP_HAL is not None, "OLP_HAL é None"
    assert OLP_HAL.is_initialized, "Driver não inicializado"
    assert hasattr(OLP_HAL, 'pim_tasks_loaded'), "Atributo não encontrado"
    
    print(f"  Versão: {OLP_HAL.hal_version}")
    print(f"  CPU Freq: {OLP_HAL.cpu_frequency_mhz} MHz")
    print(f"  REM Latency: {OLP_HAL.metrics['rem_latency_ns']} ns")

tester.test("OLPHALDriver - Inicialização", test_hal_driver_init)

# ============================================================================
# TESTE 5: OLPHALDriver - DMA Transfer
# ============================================================================

def test_hal_driver_dma():
    """Testar transferência DMA"""
    print("Testando transferência DMA...")
    
    initial_transfers = OLP_HAL.dma_transfers_completed
    
    result = OLP_HAL.load_task_pim(
        task_id=1,
        data_ptr=0x1000,
        num_blocks=10
    )
    
    assert result == True, "DMA transfer falhou"
    assert OLP_HAL.dma_transfers_completed > initial_transfers, "Transfer não foi contado"
    
    print(f"  Tarefas PIM carregadas: {OLP_HAL.pim_tasks_loaded}")
    print(f"  Transferências completadas: {OLP_HAL.dma_transfers_completed}")
    print(f"  Bytes transferidos: {OLP_HAL.total_bytes_transferred}")

tester.test("OLPHALDriver - DMA Transfer", test_hal_driver_dma)

# ============================================================================
# TESTE 6: OLPHALDriver - REM Interrupt
# ============================================================================

def test_hal_driver_rem():
    """Testar REM interrupt"""
    print("Testando REM interrupt...")
    
    initial_interrupts = OLP_HAL.rem_interrupts_sent
    
    result = OLP_HAL.send_rem_interrupt(0xFF, "test_context")
    
    assert result == True, "REM interrupt falhou"
    assert OLP_HAL.rem_interrupts_sent > initial_interrupts, "Interrupt não foi contado"
    
    print(f"  Interrupts enviados: {OLP_HAL.rem_interrupts_sent}")
    print(f"  Latência: {OLP_HAL.metrics['rem_latency_ns']} ns")

tester.test("OLPHALDriver - REM Interrupt", test_hal_driver_rem)

# ============================================================================
# TESTE 7: OLPHALDriver - Hardware Stats
# ============================================================================

def test_hal_driver_stats():
    """Testar estatísticas de hardware"""
    print("Testando estatísticas de hardware...")
    
    stats = OLP_HAL.get_hardware_stats()
    
    assert stats is not None, "Stats é None"
    assert 'pim_tasks_loaded' in stats, "Campo pim_tasks_loaded não encontrado"
    assert 'current_ttid_ms' in stats, "Campo current_ttid_ms não encontrado"
    assert stats['pim_tasks_loaded'] > 0, "Nenhuma tarefa PIM carregada"
    
    print(f"  Tarefas PIM: {stats['pim_tasks_loaded']}")
    print(f"  DMA Transfers: {stats['dma_transfers_completed']}")
    print(f"  Bytes: {stats['total_bytes_transferred']}")
    print(f"  TTID: {stats['current_ttid_ms']:.2f} ms")
    print(f"  Power: {stats['current_power_w']:.2f} W")

tester.test("OLPHALDriver - Hardware Stats", test_hal_driver_stats)

# ============================================================================
# TESTE 8: OLPCoreAPI - Inicialização
# ============================================================================

def test_api_init():
    """Testar inicialização da API"""
    print("Verificando inicialização da API...")
    
    api = OLPCoreAPI(use_real_ml_model=True, 
                     hal_driver=OLP_HAL, 
                     ml_model=ALP_MODEL)
    
    assert api is not None, "API é None"
    assert hasattr(api, 'context_stack'), "context_stack não encontrado"
    assert len(api.context_stack) == 0, "Context stack não vazio"
    
    print(f"  API inicializada com sucesso")
    print(f"  Context stack: {len(api.context_stack)}")

tester.test("OLPCoreAPI - Inicialização", test_api_init)

# ============================================================================
# TESTE 9: OLPCoreAPI - set_context
# ============================================================================

def test_api_set_context():
    """Testar set_context"""
    print("Testando set_context...")
    
    api = OLPCoreAPI(use_real_ml_model=True, 
                     hal_driver=OLP_HAL, 
                     ml_model=ALP_MODEL)
    
    result = api.set_context("test_function", scope_id=1)
    
    assert result == True, "set_context retornou False"
    assert len(api.context_stack) == 1, "Contexto não foi adicionado"
    assert api.context_stack[0]['function_name'] == "test_function", "Function name incorreto"
    
    print(f"  Contexto adicionado com sucesso")
    print(f"  Context stack depth: {len(api.context_stack)}")
    print(f"  Total contextos: {api.stats['total_contexts']}")

tester.test("OLPCoreAPI - set_context", test_api_set_context)

# ============================================================================
# TESTE 10: OLPCoreAPI - register_checkpoint
# ============================================================================

def test_api_register_checkpoint():
    """Testar register_checkpoint"""
    print("Testando register_checkpoint...")
    
    api = OLPCoreAPI(use_real_ml_model=True, 
                     hal_driver=OLP_HAL, 
                     ml_model=ALP_MODEL)
    
    result = api.register_checkpoint(0x1000, "test_checkpoint")
    
    assert result == True, "register_checkpoint retornou False"
    assert api.stats['checkpoints_registered'] == 1, "Checkpoint não foi registrado"
    assert "test_checkpoint" in api.checkpoints, "Checkpoint não está no dict"
    
    print(f"  Checkpoint registrado com sucesso")
    print(f"  Checkpoints totais: {api.stats['checkpoints_registered']}")
    print(f"  Endereço: 0x1000")

tester.test("OLPCoreAPI - register_checkpoint", test_api_register_checkpoint)

# ============================================================================
# TESTE 11: OLPCoreAPI - execute_optimized
# ============================================================================

def test_api_execute_optimized():
    """Testar execute_optimized"""
    print("Testando execute_optimized...")
    
    api = OLPCoreAPI(use_real_ml_model=True, 
                     hal_driver=OLP_HAL, 
                     ml_model=ALP_MODEL)
    
    api.set_context("test_task", scope_id=1)
    
    def task_func(data):
        return sum(data) * 2
    
    data = [1, 2, 3, 4, 5]
    result = api.execute_optimized(task_func, data)
    
    assert result == 30, f"Resultado incorreto: {result}"
    assert api.stats['optimized_executions'] == 1, "Execução não foi registrada"
    
    print(f"  Execução completada com sucesso")
    print(f"  Resultado: {result}")
    print(f"  Total execuções: {api.stats['optimized_executions']}")
    print(f"  Seleção: {api.execution_history[0]['destination']}")

tester.test("OLPCoreAPI - execute_optimized", test_api_execute_optimized)

# ============================================================================
# TESTE 12: OLPCoreAPI - get_full_system_report
# ============================================================================

def test_api_system_report():
    """Testar get_full_system_report"""
    print("Testando get_full_system_report...")
    
    api = OLPCoreAPI(use_real_ml_model=True, 
                     hal_driver=OLP_HAL, 
                     ml_model=ALP_MODEL)
    
    api.set_context("report_test", scope_id=1)
    api.register_checkpoint(0x5000, "cp_test")
    api.execute_optimized(lambda x: sum(x), [1, 2, 3])
    
    report = api.get_full_system_report()
    
    assert report is not None, "Relatório é None"
    assert 'timestamp' in report, "Timestamp não encontrado"
    assert 'api_stats' in report, "api_stats não encontrado"
    assert 'hal_driver_stats' in report, "hal_driver_stats não encontrado"
    assert 'ml_model_stats' in report, "ml_model_stats não encontrado"
    
    print(f"  Relatório gerado com sucesso")
    print(f"  Timestamp: {report['timestamp']}")
    print(f"  Execuções: {report['api_stats']['optimized_executions']}")
    print(f"  Checkpoints: {report['api_stats']['checkpoints_registered']}")

tester.test("OLPCoreAPI - get_full_system_report", test_api_system_report)

# ============================================================================
# TESTE 13: OLPCoreAPI - export_system_report
# ============================================================================

def test_api_export_report():
    """Testar export_system_report"""
    print("Testando export_system_report...")
    
    api = OLPCoreAPI(use_real_ml_model=True, 
                     hal_driver=OLP_HAL, 
                     ml_model=ALP_MODEL)
    
    api.set_context("export_test", scope_id=1)
    api.execute_optimized(lambda x: sum(x), [1, 2, 3])
    
    # Criar diretório de testes
    test_dir = Path(r'C:\Users\PC\Desktop\HYPEROKBIT\OLP\reports\test')
    test_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = test_dir / 'test_report.json'
    result = api.export_system_report(str(report_file))
    
    assert result == True, "export_system_report retornou False"
    assert report_file.exists(), "Arquivo não foi criado"
    
    # Verificar conteúdo
    with open(report_file) as f:
        data = json.load(f)
    
    assert 'api_stats' in data, "api_stats não está no JSON"
    
    print(f"  Relatório exportado com sucesso")
    print(f"  Arquivo: {report_file}")
    print(f"  Tamanho: {report_file.stat().st_size} bytes")

tester.test("OLPCoreAPI - export_system_report", test_api_export_report)

# ============================================================================
# TESTE 14 CORRIGIDO: TESTE DE INTEGRAÇÃO COMPLETA
# ============================================================================

def test_complete_integration():
    """Teste de integração completa - VERSÃO CORRIGIDA"""
    print("Executando teste de integração completa...")
    
    api = OLPCoreAPI(use_real_ml_model=True, 
                     hal_driver=OLP_HAL, 
                     ml_model=ALP_MODEL)
    
    # Simular loop de processamento
    for i in range(5):
        api.set_context(f"integration_test_{i}", scope_id=i)
        api.register_checkpoint(0x10000 + i*16, f"cp_{i}")
        
        data = [j for j in range(10)]
        result = api.execute_optimized(lambda x: sum(x), data)
        
        assert result == 45, f"Resultado incorreto na iteração {i}"
    
    # Verificar estatísticas finais
    report = api.get_full_system_report()
    
    assert report['api_stats']['optimized_executions'] == 5, "Execuções não conferem"
    assert report['api_stats']['checkpoints_registered'] == 5, "Checkpoints não conferem"
    
    # ✅ CORREÇÃO: Usar 'recent_executions' do relatório em vez de 'execution_history' da API
    recent = report['recent_executions']
    assert len(recent) > 0, "Histórico recente vazio"
    
    print(f"  Integração bem-sucedida")
    print(f"  Ciclos: 5")
    print(f"  Contextos: {report['api_stats']['total_contexts_defined']}")
    print(f"  Execuções: {report['api_stats']['optimized_executions']}")
    print(f"  Taxa PIM: {report['api_stats']['pim_percentage']}")

tester.test("Integração Completa (5 ciclos)", test_complete_integration)

# ============================================================================
# TESTE 15: TESTE DE PERFORMANCE
# ============================================================================

def test_performance():
    """Teste de performance"""
    print("Testando performance do sistema...")
    
    api = OLPCoreAPI(use_real_ml_model=True, 
                     hal_driver=OLP_HAL, 
                     ml_model=ALP_MODEL)
    
    start_time = time.time()
    
    for i in range(20):
        api.set_context(f"perf_test_{i}", scope_id=i)
        api.execute_optimized(lambda x: sum(x), list(range(100)))
    
    elapsed = time.time() - start_time
    
    avg_time = (elapsed / 20) * 1000  # em ms
    
    assert avg_time < 100, f"Tempo médio muito alto: {avg_time:.2f}ms"
    
    print(f"  20 execuções em {elapsed:.3f}s")
    print(f"  Tempo médio: {avg_time:.2f}ms por execução")
    print(f"  Throughput: {20/elapsed:.1f} execuções/segundo")

tester.test("Performance (20 execuções)", test_performance)

# ============================================================================
# EXECUTAR TESTES
# ============================================================================

if __name__ == "__main__":
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "TESTE COMPLETO DO MÓDULO OLP - VERSÃO CORRIGIDA" + " "*11 + "║")
    print("╚" + "="*78 + "╝")
    
    print(f"\nInício: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Imprimir resumo final
    tester.print_summary()
    
    print(f"\nFim: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Retornar código de saída
    exit_code = 0 if tester.failed == 0 else 1
    print(f"\nCódigo de saída: {exit_code}")
    
    if exit_code == 0:
        print("\n" + "="*80)
        print("🎉 TODOS OS 15 TESTES PASSARAM COM SUCESSO! ✅")
        print("="*80)
    
    sys.exit(exit_code)
