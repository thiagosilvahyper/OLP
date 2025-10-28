# test_olp.py

import unittest
from unittest.mock import MagicMock, patch

# Importar todos os módulos e simulações necessárias
from runtime_tracer import RuntimeTracer
from prediction_engine import PredictionEngine
from pim_recovery import PIMRecoveryModule
from rem_sync import REMSyncModule
from utils import ML_MODEL, PIM_UNIT, CPU_CORE

class TestOLPRigor(unittest.TestCase):

    def setUp(self):
        """Prepara os módulos e objetos para cada teste."""
        
        # Mock dos componentes de hardware/ML para isolar a lógica do OLP
        self.mock_ml_model = MagicMock(spec=ML_MODEL)
        self.mock_pim_unit = MagicMock(spec=PIM_UNIT)
        self.mock_cpu_core = MagicMock(spec=CPU_CORE)
        self.mock_rem_sync = MagicMock(spec=REMSyncModule)
        
        # Configuração do OLP
        self.tracer = RuntimeTracer()
        self.engine = PredictionEngine(self.mock_ml_model, latency_threshold=0.30, confidence_threshold=0.999)
        self.recovery = PIMRecoveryModule(self.engine, self.mock_rem_sync)
        
        # Injetar mocks nos módulos para que eles usem as simulações
        self.engine.ml_model = self.mock_ml_model
        
        # Usar patch para substituir as instâncias globais (PIM_UNIT, CPU_CORE) nos módulos
        PIMRecoveryModule.REM_SYNCHRONIZER = self.mock_rem_sync
        
        # O PIMRecoveryModule é o único que precisa dos Mocks de Hardware/Utils
        
        # Configurar tracer para ter dados
        self.tracer.set_context("test_func", 10)
        for i in range(10):
            self.tracer.log_access(0x1000 + i * 8)

    # =================================================================
    # TESTES DE RIGOR PARA O MÓDULO 2 (PREDICTION ENGINE)
    # =================================================================

    def test_01_rigor_fp_critico_confidence_fail(self):
        """
        Teste: Confiança abaixo de 0.999. Decisão deve ser 'CPU' (Evitar FP).
        """
        # Simula um ML Model com confiança baixa (Falso Positivo em potencial)
        self.mock_ml_model.predict.return_value = {
            'blocks': [0x1050], 'confidence': 0.9980, # FALHA NA CONFIANÇA
            'ttid_pim': 80, 'ttid_cpu': 150 # Ganho alto (46.6%)
        }
        
        context, accesses = self.tracer.get_context_data()
        decision, _ = self.engine.assess_and_decide(context, accesses)
        
        self.assertEqual(decision, 'CPU', "Decisão deve ser CPU quando a confiança é < 0.999.")
        
    def test_02_rigor_ttid_gain_fail(self):
        """
        Teste: Ganho de TTID abaixo de 30%. Decisão deve ser 'CPU' (Rigor Energético).
        """
        # Simula um ML Model com confiança alta, mas ganho de TTID baixo (5% de ganho)
        self.mock_ml_model.predict.return_value = {
            'blocks': [0x1050], 'confidence': 0.9995, 
            'ttid_pim': 142.5, 'ttid_cpu': 150 # Ganho: 5%. FALHA NO RIGOR
        }
        
        context, accesses = self.tracer.get_context_data()
        decision, _ = self.engine.assess_and_decide(context, accesses)
        
        self.assertEqual(decision, 'CPU', "Decisão deve ser CPU quando o ganho de TTID é < 30%.")

    def test_03_rigor_success_pim_offload(self):
        """
        Teste: Condições ideais. Decisão deve ser 'PIM'.
        """
        # Simula um ML Model com confiança e ganho altos (Sucesso)
        self.mock_ml_model.predict.return_value = {
            'blocks': [0x1050, 0x1058], 'confidence': 0.9999, 
            'ttid_pim': 80, 'ttid_cpu': 150 # Ganho: 46.6%
        }
        
        context, accesses = self.tracer.get_context_data()
        decision, blocks = self.engine.assess_and_decide(context, accesses)
        
        self.assertEqual(decision, 'PIM', "Decisão deve ser PIM quando as condições de rigor são atendidas.")
        self.assertGreater(len(blocks), 0, "Deve haver blocos de prefetch para o PIM.")

    # =================================================================
    # TESTES DE RIGOR PARA O MÓDULO 3 E 4 (RECOVERY E REM-SYNC)
    # =================================================================

    @patch('pim_recovery.PIM_UNIT', new_callable=MagicMock)
    @patch('pim_recovery.CPU_CORE', new_callable=MagicMock)
    def test_04_rigor_critical_interrupt_mitigation(self, MockCPU, MockPIM):
        """
        Teste: Simulação de Falso Positivo (FP) no PIM e o fluxo de recuperação.
        """
        # Configurar o Mock PIM Recovery para usar os mocks de hardware
        self.recovery.LAST_GOOD_CHECKPOINT = 0x500 # Simulação do Checkpoint
        
        # 1. Acionamento da interrupção (Simula a detecção de erro pelo hardware PIM)
        error_type = "PREFETCH_MISMATCH"
        faulty_context = self.tracer.context_id
        
        self.recovery.handle_critical_interrupt(error_type, faulty_context)

        # 2. VALIDAÇÃO DO FLUXO DE RIGOR
        
        # A. Rigor: Interrupção e Power Gating Imediato (M3)
        MockPIM.halt_execution.assert_called_once()
        MockPIM.power_gate_partial.assert_called_once()
        
        # B. Rigor: Uso do REM-Sync (M4)
        self.mock_rem_sync.send_critical_interrupt.assert_called_once_with(error_type)
        
        # C. Rigor: Rollback e Retomada na CPU (M3)
        MockPIM.retrieve_state_at.assert_called_once_with(0x500)
        MockCPU.resume_execution.assert_called_once()
        
        # D. Rigor: Aumento da Confiança Pós-Falha
        self.assertEqual(self.engine.MIN_CONFIDENCE, 0.99999, "A confiança mínima deve ser aumentada após um FP Crítico.")

if __name__ == '__main__':
    # Esta linha garante que os testes sejam executados com o máximo de detalhes
    unittest.main(argv=['first-arg-is-ignored'], exit=False)